function parseCommittee(responseText)
{
    var committeeDiv = document.getElementById("committee");
    var members = responseText.slice(0,1);
    responseText=responseText.slice(3);
    var a,b,c,d, i=0, name = new Array, position = new Array, email = new Array, image_location = new Array;
    while (i<members)
    {
        a = responseText.search("::");
        name[i] = responseText.slice(0,a);
        responseText = responseText.slice(a+2);
        
        b = responseText.search("::");
        position[i] = responseText.slice(0,b);
        responseText = responseText.slice(b+2);
        
        c = responseText.search("::");
        email[i] = responseText.slice(0,c);
        responseText = responseText.slice(c+2);
        
        if (i+1 == members)
        {
            image_location[i] = responseText;
        }
        else
        {
            d = responseText.search("::");
            image_location[i] = responseText.slice(0,d);
            responseText = responseText.slice(d+2);
        }
    }
    var lines = members/3;
    var linesRemainer = members%3;
    if (linesRemainder > 0)
    {
        lines++;
    }

    var lineDiv = new Array, lineNumber = 0;
    for (var i=0; i<lines; i++)
    {
        lineDiv[i] = document.createElement("div");
    }
    for (var i=0; i<members; i++)
    {
        if (i !== 0 && i%3==0)
        {
            lineNumber++;
        }
        var memberDiv = document.createElement("div");
        if (i%3 == 0)
        {
            memberDiv.className = "member_left";
        }
        if (i%3 == 1)
        {
            memberDiv.className = "member_middle";
        }
        if (i%3 == 2)
        {
            memberDiv.className = "member_right";
        }
        var nameText = document.createElement("h3");
        var image = document.createElement("img");
        var emailLink = document.createElement("a");
        var positionText = document.createElement("h4");
        
        nameText.innerHTML = name[i];
        nameText.className = "member_title";
        image.src = image_location[i];
        image.className = "member_image";
        emailLink.href = "mailto:"+email[i];
        emailLink.innerHTML = "Email";
        emailLink.className = "member_email";
        positionText.innerHTML = position[i];
        positionText.className = "member_position";
        
        memberDiv.appendChild(nameText);
        memberDiv.appendChild(positionText);
        memberDiv.appendChild(image);
        memberDiv.appendChild(emailLink);
        lineDiv[lineNumber].appendChild(memberDiv);
    }
    for (var x=0; x<lines; x++)
    {
        committeeDiv.appendChild(lineDiv[x]);
    }
}

var committeeRequest = new xmlHttpRequest;
comitteeRequest.open("GET","/cgi-bin/contact.cgi?data=committee");
committeeRequest.onreadystatechange = function()
{
    if (committeeRequest.readyState == 4 && committeeRequest.status == 200)
    {
        parseCommittee(committeeRequest.responseText);
    }
}
committeeRequest.send();
