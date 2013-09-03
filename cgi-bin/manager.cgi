#!/usr/bin/env perl

use warnings;
use strict;
use CGI;
use DateTime;
use CGI::Cookie;

sub print_html
{
    print <<"EOF";
content-type: text/html
        
        
<!DOCTYPE html>
<head>
    <title>Content Manager</title>
    <link rel="stylesheet" type="text/css" src="../content-manager/manager.css">
    <meta charset="utf-8">
    <script type="text/javascript" src="../content-manager/manager.js"></script>
</head>
<body>
    <h1>Content Manager</h1>
    <div class="update-form">
        <h2>Create A New Article:</h2>
        <input type="button" value="toggle" onclick="expand_update()" id="show-update">
        <div id="update-form-handle" style="display: none;">
            <form enctype="multipart/form-data" action="upload.cgi" method="POST">
                Title: <input type="text" id="title" name="title">
                Author: <input type"text" id="author" name="author">
                Text: <textarea id="body" name="body">What do you want to write about?</textarea>
                Image Location(optional): <input type="file" id="image_src" name="image_src">
                <input type="hidden" id="request" value="add_content">
                <input type="submit" value="Add Content">
            </form>
        </div>
    </div>
    <div class="manage-posts">
        <h2>Manage Posts:</h2>
        <input type="button" value="toggle" onclick="expand_manage()" id="show-manage">
        <div id="manage-posts-handle">
            <div class="manage-posts-table" style="display: none;">
                <table>
                    <tr>
                        <td>ID:</td>
                        <td>Title:</td>
                        <td>Author:</td>
                        <td>Date:</td>
                    </tr>
                    <tr>
                        <td id="i1"></td>
                        <td id="t1"></td>
                        <td id="a1"></td>
                        <td id="d1"></td>
                    </tr>
                    <tr>
                        <td id="i2"></td>
                        <td id="t2"></td>
                        <td id="a2"></td>
                        <td id="d2"></td>
                    </tr>
                    <tr>
                        <td id="i3"></td>
                        <td id="t3"></td>
                        <td id="a3"></td>
                        <td id="d3"></td>
                    </tr>
                    <tr>
                        <td id="i4"></td>
                        <td id="t4"></td>
                        <td id="a4"></td>
                        <td id="d4"></td>
                    </tr>
                    <tr>
                        <td id="i5"></td>
                        <td id="t5"></td>
                        <td id="a5"></td>
                        <td id="d5"></td>
                    </tr>
                </table>
            </div>
            <div class="manage-posts-delete">
                <form>
                    <input type="button" id="del1" value="delete">
                    <input type="button" id="del2" value="delete" onclick="delete_post(2);">
                    <input type="button" id="del3" value="delete" onclick="delete_post(3);">
                    <input type="button" id="del4" value="delete" onclick="delete_post(4);">
                    <input type="button" id="del5" value="delete" onclcik="delete_post(5);">
                </form>
            </div>
            <div class="manage-posts-edit">
                <form>
                    <input type="button" id="edit1" value="edit" onclick="edit_post(1);">
                    <input type="button" id="edit2" value="edit" onclick="edit_post(2);">
                    <input type="button" id="edit3" value="edit" onclick="edit_post(3);">
                    <input type="button" id="edit4" value="edit" onclick="edit_post(4);">
                    <input type="button" id="edit5" value="edit" onclick="edit_post(5);">
                </form>
            </div>
        </div>
    </div>
</body>
EOF
}

my %cookie = CGI::Cookie->fetch;
my $redirect = CGI->new();
my $session = $cookie{'SessionID'}->value;

open(session_file, "../data/sessions.txt");
while (<session_file>)
{
    if ($_ =~ /"$session"/ && $_ =~ /authorised/)
    ##format in file is "sessionID=$session snonce=$snonce authorised until $year/$month/$day $hour:$minutes:$seconds"
    {
        my $server_time = time;
        my @words = split (/ /);
        my ($date, $time) = ($words[4], $words[5]);
        my ($year, $month, $day) = (split(/\//, $date))[0,1,2];
        my ($hour, $minute, $second) =  (split(/:/, $time))[0,1,2];
        my $expires = DateTime->new(
            -year=>$year,
            -month=>$month,
            -day=>$day,
            -hour=>$hour,
            -minute=>$minute,
            -second=>$second,
        );
        
        if ($expires->epoch() < $server_time)
        {
            print_html;
        }
        else
        {
            print $redirect->header(
                -type=>'text/html',
                -nph=>1,
                -status=>'401 Authorisation Required',
            );
            print <<"            EOF";
            content-type: text/html
            
            <html>
            <head>
                <title>Authorisation Required!</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>Authorisation Required<h1>
                <p>Please <a href="../content-manager/login.html>log in</a>!
            </body>
            </html>
            EOF
        }
    }
    
}

