let bird;
let pipes = [];
let gravity = 0.6;
let jump = -10;
let score = 0;

function setup() {
  createCanvas(400, 600);
  bird = new Bird();
  pipes.push(new Pipe());
}

function draw() {
  background(135, 206, 235); // Sky blue background

  // Update and show bird
  bird.update();
  bird.show();

  // Handle pipes
  if (frameCount % 100 == 0) {
    pipes.push(new Pipe());
  }

  for (let i = pipes.length - 1; i >= 0; i--) {
    pipes[i].update();
    pipes[i].show();

    // Check collision
    if (pipes[i].hits(bird)) {
      gameOver();
      return;
    }

    // Update score
    if (pipes[i].passes(bird)) {
      score++;
    }

    // Remove offscreen pipes
    if (pipes[i].offscreen()) {
      pipes.splice(i, 1);
    }
  }

  // Display score
  fill(255);
  textSize(32);
  textAlign(CENTER);
  text(score, width/2, 50);
}

function keyPressed() {
  if (key == ' ') {
    bird.up();
  }
}

function mousePressed() {
  bird.up();
}

class Bird {
  constructor() {
    this.y = height/2;
    this.x = 64;
    this.velocity = 0;
    this.size = 32;
  }

  update() {
    this.velocity += gravity;
    this.velocity *= 0.9; // Air resistance
    this.y += this.velocity;

    // Keep bird in bounds
    if (this.y > height) {
      this.y = height;
      this.velocity = 0;
    }
    if (this.y < 0) {
      this.y = 0;
      this.velocity = 0;
    }
  }

  show() {
    fill(255, 204, 0);
    ellipse(this.x, this.y, this.size, this.size);
  }

  up() {
    this.velocity += jump;
  }
}

class Pipe {
  constructor() {
    this.spacing = 120;
    this.top = random(height/6, 3/4 * height);
    this.bottom = height - (this.top + this.spacing);
    this.x = width;
    this.w = 60;
    this.speed = 2;
    this.passed = false;
  }

  show() {
    fill(0, 255, 0);
    rect(this.x, 0, this.w, this.top);
    rect(this.x, height - this.bottom, this.w, this.bottom);
  }

  update() {
    this.x -= this.speed;
  }

  offscreen() {
    return this.x < -this.w;
  }

  hits(bird) {
    if (bird.y - bird.size/2 < this.top || bird.y + bird.size/2 > height - this.bottom) {
      if (bird.x + bird.size/2 > this.x && bird.x - bird.size/2 < this.x + this.w) {
        return true;
      }
    }
    return false;
  }

  passes(bird) {
    if (!this.passed && bird.x > this.x + this.w) {
      this.passed = true;
      return true;
    }
    return false;
  }
}

function gameOver() {
  fill(255, 0, 0);
  textSize(40);
  textAlign(CENTER);
  text("GAME OVER", width/2, height/2);
  text("Score: " + score, width/2, height/2 + 50);
  noLoop();
}