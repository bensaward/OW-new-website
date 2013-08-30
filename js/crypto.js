function authenticate(form)
{
    var username = form.username.value;
    var password = form.password.value;
    
    if (username == "" || password == "")
    {
        alert("Incorrect username or password");
    }
    
    else
    {
        var xml, xml1;
        
        if (window.XMLHttpRequest)
        {
            xml = new XMLHttpRequest();
            xml1 = new XMLHttpRequest();
        }
        
        else
        {
            xml = new ActiveXObject("Microsoft.XMLHTTP");
            xml1 = new ActiveXObject("Microsoft.XMLHTTP");
        }
        
        var snonce,
        sessionID = CryptoJS.SHA256(Math.floor((Math.random()*100000)+1)),
        cnonce = CryptoJS.SHA256(Math.floor((Math.random()*100000)+1));
        xml.open("POST","../cgi-bin/functions.cgi",false);
        xml.send("session="+sessionID+"&request=snonce");
        
        var snonce = xml.responseText,
        server = snonce.toString(),
        client = cnonse.toString(),
        hash_string= CryptoJS.SHA256(password).toString(),
        result= CryptoJS.SHA256(hash_string+client+server);
        
        xml1.open("POST","../cgi-bin/functions.cgi",true);
        xml1.send("session="+sessionID+"&request=login&hash="+result+"&cnonce="+cnonce+"&user="+username);
    
    }
}