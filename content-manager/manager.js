function show_hide(element, button)
{
    var handle = document.getElementById(element);
    var toggle = document.getElementById(button);
    if (window.getComputedStyle(handle) && window.getComputedStyle(toggle))
    {
        var displayStyle = window.getComputedStyle(handle).display;
        if (displayStyle != "none")
        {
            handle.style.display = "none";
        }
        else
        {
            handle.style.display = "block";
        }
        toggle.attributes.onclick = "show_hide("+element+", "+button+")";
    }
}

function expand_manage()
{
    var expandable = document.getElementById("manage-posts-handle"), xml, response;
    var title = new Array(), id = new Array(), date_published = new Array(), author = new Array();
    var date = new Date();
    var datenow = date.getTime(); // THIS IS IN MILLISECONDS.
    datenow = Math.floor(datenow/1000); // now in seconds.
    
    xml = new XMLHttpRequest();
    xml.open("GET","../cgi-bin/functions.cgi?request=get_title&date="+datenow,true);
    xml.send();
    xml.onreadystatechange=function()
    {
        if (xml.readyState == 4 && xml.status == 200)
        {
            response = xml.responseText;
            if (response.search("Could not retrieve posts"))
            {
                alert("There was an error in retrieving the posts from the Database!");
                return;
            }
            var post_count = responce.slice(0, 1);
            response = response.slice(3);
            
            var i=0;
            while (i < post_count)
            {
                var a = response.search("::");
                id[i] = response.slice(0, a);
                response = response.slice(a+2);
                
                var b = response.search("::");
                title[i] = response.slice(0 , b);
                response = response.slice(b+2);
                
                var d = response.search("::");
                date_published[i] = response.slice(0, d);
                response = response.slice(d+2);
                
                if (i+1 == post_count)
                {
                    author[i] = response;
                    break;
                }
                else
                {
                    var c = response.search("::");
                    author[i] = response.slice(0, c);
                    response = response.slice(c+2);
                    i++;
                }
            }
            
            var contentManagerDiv = document.getElementById("manager-posts-handle");
            
            var managerTableDiv = document.createElement("div");
            var managerFormDeleteDiv = document.createElement("div");
            var managerFormEditDiv = document.createElement("div");
            var managerFormDiv = document.createElement("div");
            
            managerTableDiv.attributes.id = "manager-table";
            managerFormDeleteDiv.attributes.id = "manager-form-delete";
            managerFormEditDiv.attributes.id = "manager-form-edit";
            managerFormDiv.attributes.id = "manager-form";
            
            var managerTable = document.createElement("table");
            var td = document.createElement("td");
            var tr = document.createElement("tr");
            var button = document.createElement("button");
            var edit_text = document.createTextNode("Edit");
            var delete_text = document.createTextNode("Delete");
            
            td.attributes.innerHTML="ID";
            tr.appendChild(td);
            td.a
            ttributes.innerHTML="Title";
            tr.appendChild(td);
            td.attributes.innerHTML="Author";
            tr.appendChild(td);
            td.attributes.innerHTML="Date";
            tr.appendChild(td);
            managerTable.appendChild(tr);
            
            i=0;
            while (i < post_count)
            {
                td.attributes.innerHTML=id[i];
                tr.appendChild(td);
                td.attributes.innerHTML=title[i];
                tr.appendChild(td);
                td.attributes.innerHTML=author[i];
                tr.appendChild(td);
                td.attributes.innerHTML=date_published[i];
                tr.appendChild(td);
                managerTable.appendChild(tr);
                
                button.attributes.onclick="delete_post("+id[i]+")";
                button.appendChild=(delete_text);
                managerFormDeleteDiv.appendChild(button);
                
                button.attributes.onclick="edit_post("+id[i]+")";
                button.appendChild(edit_text);
                managerFormEditDiv.appendChild(button);
                i++;
            }
            managerFormDiv.appendChild(managerFormDeleteDiv);
            managerFormDiv.appendChild(managerFormEditDiv);
        }
    }
    var toggle_button = document.getElementById("show-button");
    toggle_button.attributes.onclick="show_hide('manage-posts-handle', 'show-button')";
    expandable.style.display = "block";
}

function delete_post(id)
{
    var xml;
    if (window.XMLHttpRequest)
    {
        xml = new XMLHttpRequest();
    }
    else
    {
        xml = new ActiveXObject("Microsoft.XMLHTTP"); //again no html5 support in legacy IE...
    }
    xml.open("GET","../cgi-bin/functions.cgi?function=delete_post&id="+id,true);
    xml.send();
    xml.onreadystatechange = function ()
    {
        if (xml.status == 200 && xml.readyState == 4)
        {
            var returned = xml.responseText;
            alert(returned);
        }
    }
}
