

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
        
        var snonce;
        var seed1 = Math.floor((Math.random()*100000)+1);
        var seed2 = Math.floor((Math.random()*100000)+1);
        seed1 = seed1.toString();
        seed2 = seed2.toString();
        
        var sessionID = CryptoJS.SHA256(seed1);
        sessionID = sessionID.toString(CryptoJS.enc.Hex);                   
        var cnonce = CryptoJS.SHA256(seed2);
        cnonce = cnonce.toString(CryptoJS.enc.Hex);            
        xml.onreadystatechange = function()
        {
            console.log("XMLHttpRequest Changed state to "+xml.readyState+" and state"+xml.status);
            if (xml.readyState == 4 && xml.status == 200)
            {
                console.log("snonce = "+xml.responseText);
                snonce = xml.responseText;
                var hash_string = CryptoJS.SHA256(password).toString(CryptoJS.enc.Hex);
                var internal = hash_string+cnonce+snonce;
                var result = CryptoJS.SHA256(internal);
                result = result.toString(CryptoJS.enc.Hex);
                //console.log("result = "+result+" cnonce="+cnonce+" snonce="+snonce+" initial result="+hash_string);
                xml1.onreadystatechange = function()
                {
                    if (xml1.readyState == 4 && xml1.status == 200)
                    {
                        var passfail = xml1.responseText;
                        var fail = passfail.search("fail");
                        console.log("fail position "+fail);
                        if (fail >= 0)
                        {
                            alert("Incorrect username or password!");
                        }
                        else
                        {
                            return;
                        }
                    }
                }
                var string = "session="+sessionID+"&request=login&hash="+result+"&cnonce="+cnonce+"&user="+username;
                xml1.open("POST","/cgi-bin/functions.cgi");
                xml1.setRequestHeader('Content-type','application/x-www-form-urlencoded');
                xml1.setRequestHeader('Content-length',string.length);
                xml1.send(string);
            }
        }
        xml.open("GET","/cgi-bin/functions.cgi?session="+sessionID+"&request=snonce",true);
        xml.send();
    }
}