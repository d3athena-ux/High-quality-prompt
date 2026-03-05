import pygame
import math
import sys

# Screen and simulation parameters
WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_RADIUS = 200
NUM_SIDES = 6

# Physics parameters
GRAVITY = 0.3         # gravitational acceleration
AIR_FRICTION = 0.999  # slight damping on ball velocity each frame
RESTITUTION = 0.9     # energy loss on bounce (0 to 1)
HEX_ANGULAR_VEL = 0.02  # rotation speed in radians per frame

# Ball parameters
BALL_RADIUS = 10
ball_pos = [CENTER[0] + 50, CENTER[1] - 100]  # start a bit off-center
ball_vel = [3.0, -5.0]  # initial velocity

def get_hexagon_vertices(center, radius, angle_offset):
    """Return the vertices of a regular hexagon centered at center,
    rotated by angle_offset (in radians)."""
    vertices = []
    for i in range(NUM_SIDES):
        theta = angle_offset + i * (2 * math.pi / NUM_SIDES)
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        vertices.append((x, y))
    return vertices

def line_circle_collision(circle_pos, circle_radius, p1, p2):
    """Check for collision between a circle and a line segment.
    Returns (colliding, projection point, distance, t) where t is the
    clamped parameter (0..1) along the line."""
    cx, cy = circle_pos
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    # Project circle center onto the line (p1->p2)
    t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
    t_clamped = max(0, min(1, t))
    proj_x = x1 + t_clamped * dx
    proj_y = y1 + t_clamped * dy
    # Distance from circle center to projection
    dist = math.hypot(cx - proj_x, cy - proj_y)
    return (dist < circle_radius), (proj_x, proj_y), dist, t_clamped

def reflect_velocity(ball_vel, wall_normal, wall_vel):
    """
    Reflect the ball's velocity relative to the moving wall.
    ball_vel and wall_vel are (vx, vy) tuples;
    wall_normal is a unit vector pointing inward.
    """
    # Relative velocity: velocity of ball in wall's frame
    rel_vx = ball_vel[0] - wall_vel[0]
    rel_vy = ball_vel[1] - wall_vel[1]
    # Dot product with normal
    dot = rel_vx * wall_normal[0] + rel_vy * wall_normal[1]
    # Reflection: v' = v - 2*(v·n)*n
    refl_rel_vx = rel_vx - 2 * dot * wall_normal[0]
    refl_rel_vy = rel_vy - 2 * dot * wall_normal[1]
    # Transform back to world frame
    new_vx = refl_rel_vx + wall_vel[0]
    new_vy = refl_rel_vy + wall_vel[1]
    return new_vx, new_vy

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")
    clock = pygame.time.Clock()

    hex_angle = 0  # current rotation angle of the hexagon

    running = True
    while running:
        dt = clock.tick(60)  # aim for 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update hexagon rotation
        hex_angle += HEX_ANGULAR_VEL

        # Update ball physics: gravity and air friction
        ball_vel[1] += GRAVITY
        ball_vel[0] *= AIR_FRICTION
        ball_vel[1] *= AIR_FRICTION

        # Update ball position
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]

        # Compute hexagon vertices in current orientation
        vertices = get_hexagon_vertices(CENTER, HEX_RADIUS, hex_angle)

        # Collision detection: Check against each edge of the hexagon.
        collisions = []
        for i in range(NUM_SIDES):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % NUM_SIDES]
            collided, proj_point, dist, t_val = line_circle_collision(ball_pos, BALL_RADIUS, p1, p2)
            if collided:
                penetration = BALL_RADIUS - dist
                collisions.append({
                    "penetration": penetration,
                    "p1": p1,
                    "p2": p2,
                    "proj": proj_point,
                    "dist": dist
                })

        # If a collision occurred, resolve using the one with greatest penetration.
        if collisions:
            collision = max(collisions, key=lambda c: c["penetration"])
            p1 = collision["p1"]
            p2 = collision["p2"]
            proj_point = collision["proj"]
            penetration = collision["penetration"]

            # Compute the edge vector and two candidate normals
            edge_dx = p2[0] - p1[0]
            edge_dy = p2[1] - p1[1]
            # Two perpendicular directions
            cand1 = (edge_dy, -edge_dx)
            cand2 = (-edge_dy, edge_dx)
            # Normalize them
            mag1 = math.hypot(cand1[0], cand1[1])
            norm1 = (cand1[0] / mag1, cand1[1] / mag1)
            mag2 = math.hypot(cand2[0], cand2[1])
            norm2 = (cand2[0] / mag2, cand2[1] / mag2)
            # Choose the normal that points inward toward the hexagon center.
            # (i.e. the one that makes (center - proj_point) have a positive dot product)
            to_center = (CENTER[0] - proj_point[0], CENTER[1] - proj_point[1])
            if (norm1[0] * to_center[0] + norm1[1] * to_center[1]) >= (norm2[0] * to_center[0] + norm2[1] * to_center[1]):
                wall_normal = norm1
            else:
                wall_normal = norm2

            # Compute the wall’s velocity at the collision point.
            # For a rotating hexagon, velocity = ω x r, where r = (proj_point - CENTER)
            r_vec = (proj_point[0] - CENTER[0], proj_point[1] - CENTER[1])
            # For counterclockwise rotation, the perpendicular vector is (-r_y, r_x)
            wall_vel = (HEX_ANGULAR_VEL * (-r_vec[1]), HEX_ANGULAR_VEL * (r_vec[0]))

            # Reflect the ball's velocity relative to the wall's velocity.
            new_vx, new_vy = reflect_velocity(ball_vel, wall_normal, wall_vel)
            # Apply restitution (simulate energy loss on collision)
            ball_vel[0] = new_vx * RESTITUTION
            ball_vel[1] = new_vy * RESTITUTION

            # Push the ball out of penetration so it doesn't stick
            ball_pos[0] += wall_normal[0] * penetration
            ball_pos[1] += wall_normal[1] * penetration

        # Drawing
        screen.fill((30, 30, 30))  # dark background

        # Draw hexagon (draw lines between vertices)
        pygame.draw.polygon(screen, (200, 200, 200), vertices, 3)

        # Draw the ball
        pygame.draw.circle(screen, (255, 100, 100), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()