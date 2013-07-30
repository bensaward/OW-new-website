function drawRoundedRectangle(canvasID, x, y, width, height, color_hex) // x and y are of the top left co-ordinates (as if it was a rectangle)
{
    if (!(width < 100 || height < 100))
    {
        var canvas = document.getElementById(canvasID);
        var ctx = canvas.getContext('2d');
    
        ctx.beginPath();
        ctx.arc(x+50, y+50, 50, 1.5*Math.PI, Math.PI, true);
        ctx.lineTo(x, y+height-50);
        ctx.arc(x+50, y+height-50, 50, Math.PI, 0.5*Math.PI, true);
        ctx.lineTo(x+width-50, y+height);
        ctx.arc(x+width-50, y+height-50, 50, 0.5*Math.PI, 0, true);
        ctx.lineTo(x+width, y+50);
        ctx.arc(x+width-50, y+50, 50, 0, 1.5*Math.PI, true);
        ctx.lineTo(x+50, y);
        ctx.closePath();
        
        if (!color_hex)
        {
            ctx.fillStyle='#000000';
        }
        
        else
        {
            color_code='#'+color_hex;
            ctx.fillStyle=color_code;
        }
        
        ctx.fill();
        ctx.stroke();
    }
}

function drawEdges()
{
    
}