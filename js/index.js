var center_div = document.getElementById("content");
var init_request = new XMLHttpRequest;

function text_decode (text)
{
    if (text.search(/\+/) >= 0){text = text.replace(/\+/g, " ");}
    if (text.search(/\&quot/ ) >= 0){text = text.replace(/\&quot/g, "\"");}
    if (text.search(/\&apost/) >= 0){text = text.replace(/\&apost/g, "'");}
    if (text.search(/\&colon/) >= 0){text = text.replace(/\&colon/g, ":");}
    if (text.search(/\&semicol/) >= 0){text = text.replace(/\&semicol/g, ";");}
    if (text.search(/\&dolar/) >= 0){text = text.replace(/\&dolar/g, "$");}
    if (text.search(/\&at/) >= 0){text = text.replace(/\&at/g, "@");}
    if (text.search(/\&percent/) >= 0){text = text.replace(/\&percent/g, "%");}
    return text;
}

function process_3 (xml, div_id)
{
    if (xml.readyState == 4 && xml.status == 200)
    {
        var div = document.getElementById(div_id);
        var content = xml.responseText;
        text_decode(content);
        var paragraph = document.createElement("p");
        var text = document.createTextNode(content);
        paragraph.appendChild(text);
        div.attributes.class="article";
        div.appendChild(paragraph);
        center_div.appendChild(div);
    }
}

function process_2(xml, div_id, article_id)
{
    if (xml.status == 200 && xml.readyState == 4)
    {
        var response = xml.responseText;
        var image = document.createElement("img");
        if (response.search("none") < 0)
        {
            image.attributes.src = response;
            var a_div = document.getElementById(div_id);
            a_div.appendChild(image);
        }
        request.open("GET","/cgi-bin/functions.cgi?request=get_content&article="+article_id,true);
        request.onReadyStateChange = process_3(request, div_id);
        request.send(null);
    }
}

function process_1(xml)
{
    if (xml.status == 200 && xml.readyState == 4)
    {
        var response = xml.responseText;
        var posts = response.slice(0,1);
        response = response.slice(2);
        var a, b, c, d, id = new Array(), author = new Array(), title = new Array(), date_pub = new Array();
        // format that is sent back is posts::id::title::date::author
        var i = 0;
        while (i < 0)
        {
            a = response.search("::");
            id[i] = response.slice(0, a);
            response = response.slice(a+2);
            
            b = response.search("::");
            title[i] = response.slice(0, b);
            response = response.slice(b+2);
            
            c = response.search("::");
            date_pub[i] = response.slice(0, c);
            response = response.slice(c+2);
            
            if (i == posts-1){author[i]=response;}
            else
            {
                d = response.search("::");
                author[i] = response.slice (0, d);
                response = response.slice(d+2);
            }
            i++;
        }
        i=0;
        var a_div = document.createElement("div");
        var t_div = document.createElement("div");
        var p_div = document.createElement("div");
        var header = document.createElement("H2");
        while (i < posts)
        {
            var text = document.createTextNode(title[i]);
            header.appendChild(text);
            a_div.attributes.id="a_div_"+id[i];
            a_div.appendChild(header);
            switch (i)
            {
                case(0):
                {
                    var xml1=new XMLHttpRequest;
                    xml1.onreadystatechange = process_2(xml1, "a_div"+id[0], id[0]);
                    xml1.open("GET","/cgi-bin/functions.cgi?request=get_image&id="+id[0],true);
                    xml1.send(null);
                    break;
                }
                case(1):
                {
                    var xml2=new XMLHttpRequest;
                    xml2.onreadystatechange = process_2(xml2, "a_div"+id[1], id[1]);
                    xml2.open("GET", "/cgi-bin/functions.cgi?request_image&id="+id[1],true);
                    xml2.send(null);
                    break;
                }
                case(2):
                {
                    var xml3 = new XMLHttpRequest;
                    xml3.onreadystatechange = process_2(xml3, "a_div"+id[2], id[2]);
                    xml3.open("GET", "/cgi-bin/functions.cgi?request_image&id="+id[2],true);
                    xml3.send(null);
                    break;
                }
            }
            
        }
    }
}

function textScroll(text, widget, speed) // want to create a server script that creates *endofline* between news lines
{
    if (document.getElementById(widget)!=null)
    {
        if (text.search(/\*endofline\*/) >= 0){text = text.replace(/\*endofline\*/g, "        ");}
        text = text_decode(text);
        var news_text = document.createTextNode(text);
        var screen = document.getElementById(widget);
        var text_holder= document.createElement("div");
        var screen_text = document.createElement("p");
        
        text_holder.id = "text-holder";
        screen_text.appendChild(news_text);
        text_holder.appendChild(screen_text);
        
        var screen_width = parseInt(window.getComputedStyle(screen).width.replace("px", ""));
        text_holder.style.left = screen_width+"px";
        screen.appendChild(text_holder);
        var text_width = parseInt(window.getComputedStyle(text_holder).width.replace("px", ""));
        var i = screen_width;
        console.log("screen_width="+screen_width+"; text_width="+text_width+"; i="+i+";");
        setInterval(function()
                    {
                        var text_position = parseInt(text_holder.style.left.replace("px", ""));
                        if ( text_position >= -text_width)
                        {
                            text_holder.style.left=i+"px";
                            i--;
                        }
                        else
                        {
                            i = screen_width;
                            text_holder.style.left=i+"px";
                        }
                        console.log("text_position="+text_position+";");
                    }, 50);
    }
}
    