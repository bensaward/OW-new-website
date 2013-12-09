var center_div = document.getElementById("content");
var init_request = new XMLHttpRequest;
var GlobalExpandLinkCount = 0;

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

function process_3 (response, div_id, holder)
{
        var div = document.getElementById(div_id);
        text_decode(response);
        var paragraph = document.createElement("p");
        var text = document.createTextNode(response);
        paragraph.appendChild(text);
        div.class="article";
        div.appendChild(paragraph);
        holder.appendChild(div);
}

function process_2(response, div_id, article_id, holder)
{
        var image = document.createElement("img");
        if (response.search("none") < 0)
        {
            image.src = response;
            var a_div = document.getElementById(div_id);
            a_div.appendChild(image);
        }
        request.open("GET","/cgi-bin/posts.cgi?request=get_content&article="+article_id,true);
        request.onReadyStateChange = process_3(request, div_id, holder);
        request.send(null);
}

function process_1(response, holder)
{
        var posts = response.slice(0,1);
        response = response.slice(2);
        var a, b, c, d, id = new Array(), author = new Array(), title = new Array(), date_pub = new Array();
        // format that is sent back is posts::id::title::date::author
        var i = 0;
        while (i < posts)
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
            a_div.id="a_div_"+id[i];
            a_div.appendChild(header);
            var xml = new XMLHttpRequest;
            xml.onreadystatechange = function()
            {
                if (xml.readyState == 4 && xml.status == 200)
                {
                    process_2(xml.responseText, "a_div"+id[i], id[i], holder);
                }
            }
            xml.open("GET","/cgi-bin/posts.cgi?request=get_image&id="+id[i],true);
            xml.send();
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
        //console.log("screen_width="+screen_width+"; text_width="+text_width+"; i="+i+";");
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
                        //console.log("text_position="+text_position+";");
                    }, 50);
    }
}

function resizeDiv(parentDiv)
{
    var parentD = document.getElementByID(parentDiv);
    var parentH = parseInt(window.getComputedStyle(parentD).offsetHeight.replace("px",""));
    var para = parentD.getElementByTagName("p");
    var paraH = parseInt(window.getComputedStyle(para).offsetHeight.replace("px",""));
    var header = parentD.getElementByTagName("h2");
    var headerH = parseInt(window.getComputedStyle(header).offsetHeight.replace("px",""));
    var img = parentD.getElementByTagName("img");
    var maxSize = parseInt(window.getComputedStyle(parentD).maxHeight.replace("px","")); //should this default to a set value???
    if (img != null)
    {
        var imgH = parseInt(window.getComputedStyle(img).offsetHeight.replace("px",""));
        if ((headerH+paraH+imgH) > maxSize)
        {
            parentD.style.overflow = "hidden";
            var expandDiv = document.createElement("div");
            var expandLink = document.createElement("pre");
            var text = document.createTextNode("-- Show More --");
            
            expandLink.appendChild(text);
            expandDiv.appendChild(expandLink);
            expandDiv.onclick =function(){expandArticle(parentDiv)};
            expandDiv.class = "expand_link";
            expandDiv.id="expand_link"+GlobalExpandLinkCount;
            GlobalExpandLinkCount++;
            parentD.parentNode.insertBefore(expandDiv, parentD.nextSibling);
            
            var expandDivH = parseInt(window.getComputedStyle.getElementById("expand_link"+GlobalExpandLinkCount-1).offsetHeight.replace("px",""));
            parentD.style.height = maxSize - expandDivH + "px";
        }
        else
        {
            parentD.style.height = headerH + paraH + imgH +"px";
        }
    }
    else
    {
        if ((headerH+paraH)>maxSize)
        {
            parentD.style.overflow="hidden";
            var expandDiv = document.createElement("div");
            var expandLink = document.createElement("pre");
            var text = document.createTextNode("-- Show More --");
            expandLink.appendChild(text);
            expandDiv.appendChild(expandLink);
            
            expandDiv.onclick =function(){expandArticle(parentDiv)};
            expandDiv.class = "expand_link";
            expandDiv.id="expand_link"+GlobalExpandLinkCount;
            GlobalExpandLinkCount++;
            parentD.parentNode.insertBefore(expandDiv, parentD.nextSibling);
            
            var expandDivH = parseInt(window.getComputedStyle.getElementById("expand_link"+GlobalExpandLinkCount-1).offsetHeight.replace("px",""));
            parentD.style.height = maxSize - expandDivH + "px";
        }
        else
        {
            parentD.style.height = headerH + paraH +"px";
        }
    }
}