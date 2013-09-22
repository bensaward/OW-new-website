#!/usr/bin/env perl

use warnings;
use strict;
use CGI;
use DateTime;
use CGI::Cookie;

my ($cookie, $redirect) = (CGI->new(), CGI->new());
my $session = $cookie->cookie('SessionID') || undef;

sub print_html
{
    print <<"EOF";
Content Type: text/html\n\n
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
                Image (optional): <input type="file" id="image_src" name="image_src">
                <input type="hidden" id="request" value="add_content">
                <input type="hidden" id="session" value="$session">
                <input type="submit" value="Add Content">
            </form>
        </div>
    </div>
    <div class="manage-posts">
        <h2>Manage Posts:</h2>
        <input type="button" value="toggle" onclick="expand_manage()" id="show-manage">
        <div id="manage-posts-handle">
        </div>
    </div>
</body>
EOF
}

if (!(defined($session)))
{
    print <<"EOF";
Content Type: text/html\n\n
<html>
<head>
    <title>Authorisation Required!</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>Authorisation Required<h1>
    <p>Please <a href="../cgi-bin/login.cgi">log in</a>!
    </body>
</html>
EOF
}
else
{
    open(session_file, "../data/authed.txt");
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
                print <<"                EOF";
                Content Type: text/html\n\n
                <html>
                <head>
                    <title>Authorisation Required!</title>
                    <meta charset="utf-8">
                </head>
                <body>
                    <h1>Authorisation Required<h1>
                    <p>Please <a href="../cgi-bin/login.cgi">log in</a>!
                </body>
                </html>
                EOF
            }
        }
    }
}
