/* create table $TNAME_POSTS(                                      
*     id int not null auto_increment,
*     title varchar(200) not null,                                
*     published date not null,                                    
*     author varchar(100) not null,                               
*     content text not null,                                      
*     image varchar(100),                                         
*     primary key(id)                                             
*     );               
*/

// global vars

var center_div = document.getElementById("content");
var init_request = new XMLHttpRequest;
var GlobalExpandLinkCount = 0;

// functions
function proccess(responseText) // cgi-bin outputs table format in top of the file
{
    if (responseText == "NULL")
    {
        console.log("[Error] - no posts found in the database");
    }
    else
    {
        var postCount = responseText[0];
        responseText = responseText.slice(3);
        var id = new Array, title = new Array, published = new Array, author = new Array, content = new Array, image = new Array;
        var clone = responseText;
        var location = new Array;
        for (var i = 0; clone.search("::")>=-1; i++) // this will not catch the last image section returned to us
        {
            location[i]=clone.search("::");
            clone=clone.slice(location[i]+2);
            if (i>0)
            {
                location[i]=location[i]+location[i-1]+2; // correction for chopping out everything before the "::" we already found
            }
        }
        
        for (var i = 0; i<postCount; i++)
        {
            id[i] = responseText.slice(0,location[5*i]);
            title[i] = responseText.slice(location[5*i]+2, location[(5*i)+1]);
            published[i] = responseText.slice(location[(5*i)+1]+2, location[(5*i)+2]);
            author[i] = responseText.slice(location[(5*i)+2]+2, location[(5*i)+3]);
            content[i] = responseText.slice(location[(5*i)+3]+2, location[(5*i)+4]);
            if (i !== postCount-1) {
                image[i] = responseText.slice(location[(5*i)+4]+2, location[(5*i)+5]);
            }
            else
            {
                image[i] = responseText;
            }
        }
        // proccessing done, add to page
        
        var articleParentDiv = document.getElementById("article-holder");
        var articleHolder = new Array, header = new Array, imageBox = new Array, articleText = new Array, footer = new Array;
        for (i=0; i<postCount; i++)
        {
            articleHolder[i] = document.createElement("div");
            articleHolder[i].id = "articleID_"+id[i];
            header[i] = document.createElement("h2");
            header[i].className = "article-header";
            header[i].innerHTML = title[i];
            imageBox[i] = document.createElement("img");
            if (image[i]!== "NULL")
            {
                imageBox.src = image[i];
                imageBox.className = "article-imagebox"
            }
            else
            {
                // label this image box to not be included <-- image without src shouldnt add anything I guess
            }
            articleText[i] = document.createElement("p");
            articleText[i].innerHTML = article[i];
            articleText[i].className = "article-text";
            footer[i] = document.createElement("div");
            footer[i].innerHTML = "Published on "+published +" by "+author[i];
            footer[i].className = "article-footer";
            
            articleHolder[i].appendChild(header[i]);
            articleHolder[i].appendChild(imageBox[i]);
            articleHolder[i].appendChild(articleText[i]);
            articleHolder[i].appendChild(footer[i]);
            articleParentDiv.appendChild(articleHolder[i]);
        }
        
    }
}
function textScroll(text, widget, speed) // want to create a server script that creates *endofline* between news lines
{
    if (document.getElementById(widget)!=null)
    {
        if (text.search(/\*endofline\*/) >= 0){text = text.replace(/\*endofline\*/g, "        ");}
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

init_request.open("GET", "/cgi-bin/posts.cgi?request=get_article", true);
init_request.onreadystatechange = function () {
    if (init_request.readyState == 4 && init_request.status == 200)
    {
        process(init_request.responseText);
    }
}
