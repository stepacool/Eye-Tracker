var canvas = document.querySelector('canvas')

canvas.width = window.innerWidth;
console.log(canvas.width)
canvas.height = window.innerHeight;

var c = canvas.getContext('2d');

//A class is easier to edit
function Circle(x, y, dx, dy, radius, color){
    this.x = x;
    this.y = y;
    this.dx = dx;
    this.dy = dy;
    this.radius = radius;
    this.color = color;


    this.draw_frame = function(){
        c.clearRect(0, 0, innerWidth, innerHeight);
        c.beginPath();
        c.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        c.strokeStyle = 'blue'
        c.stroke();
    }

    this.update = function(){
        this.x += this.dx;
        this.y += this.dy;
        this.draw_frame();

    }

}
gaze = new Circle(canvas.width / 2, canvas.height / 2, 1, 1, 50, 'blue')

function animate(){
    window.requestAnimationFrame(animate);
    gaze.update();
}

animate();
