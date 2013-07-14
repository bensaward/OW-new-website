var canvas=document.getElementById('border-right');
var ctx=canvas.getContext('2d');

ctx.beginPath();

ctx.arc(50, 50, 50, 1.5*Math.PI, Math.PI, true);
ctx.lineTo(0, 700);
ctx.arc(50, 700, 50, Math.PI, 0.5*Math.PI, true);
ctx.lineTo(350, 750);
ctx.arc(350, 700, 50, 0.5*Math.PI, 0, true);
ctx.lineTo(400, 50);
ctx.arc(350, 50, 50, 0, 1.5*Math.PI, true);
ctx.lineTo(50, 0);

ctx.closePath();
ctx.fill();
ctx.brush();
