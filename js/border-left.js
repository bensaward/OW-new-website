var border_left=document.getElementById('border-left');
var context=border_left.getContext('2d');

context.beginPath();
context.arc(50, 50, 50, 1.5*Math.PI, Math.PI, true);
context.lineTo(0, 500);
context.arc(50, 500, 50, Math.PI, 0.5*Math.PI, true);
context.lineTo(350, 550);
context.arc(350, 500, 50, 0.5*Math.PI, 0, true);
context.lineTo(400, 50);
context.arc(350, 50, 50, 0, 1.5*Math.PI, true);
context.lineTo(50, 0);
context.closePath();

context.fillStyle='#0B004F';
context.fill();
context.stroke();