function expand_update()
{
    var expandable = document.getElementById("update-form-handle");
    expandable.style.display = "block";
}

function expand_manage()
{
    var expandable = document.getElementById("manage-posts-handle"), xml, response;
    var title = new array(), id = new array(), date_published = new array(), author = new array();
    if (window.XMLHTTPRequest)
    {
        xml = new XMLHttpRequest();
    }
    else
    {
        xml = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xml.open("GET","../cgi-bin/functions.cgi?request=get_title&date="+datenow,true);
    xml.onreadystatechange=function()
    {
        if (xml.readyState == 4 && xml.status == 200)
        {
            var count=0;
            response = xml.responseText;
            while (true)
            {
                var a = response.search(":");
                id[count] = response.slice(0, a-1);
                response = response.slice(a+1);
                
                var b = response.search(":");
                title[count] = response.slice(0 , b-1);
                response = response.slice(b+1);
                
                var c = response.search(":");
                author[count] = response.slice(0, c-1);
                response = response.slice(c+1);
                
                if (count == 4)
                {
                    date_published[4] = response;
                    break;
                }
                
                var d = response.search(":");
                date_published[count] = response.slice(0, d-1);
                response = response.slice(d+1);
                
                count += 1;
            }
            
            
        }
    }
    
    expandable.style.display = "block";
}