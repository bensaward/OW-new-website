var border_left=document.getElementById('border-left');
var context=border_left.getContext('2d');

context.beginPath();
context.moveTo(0, 50);
context.lineTo(0, 500);
context.arc(50, 50, 50, Math.PI, 1.5*Math.PI, false);
context.arc(50, 500, 50, Math.PI, 0.5*Math.PI, true);
context.moveTo(50, 500);
context.lineTo(400, 500);

context.strokeStyle='blue';
context.stroke();