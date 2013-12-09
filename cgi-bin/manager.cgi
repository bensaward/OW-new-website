#!/usr/bin/env perl

use warnings;
use strict;
use CGI;
use DateTime;
use CGI::Cookie;

my $WEBADDRESS = "";
my $cookie = CGI->new();
my $response = CGI->new();
my $session = $cookie->cookie('SessionID');

sub print_html
{
    print <<"EOF";
<!DOCTYPE html>
<html>
<head>
    <title>Content Manager</title>
    <link rel="stylesheet" type="text/css" href="../content-manager/manager.css">
    <meta charset="utf-8">
    <script type="text/javascript" src="../content-manager/manager.js"></script>
</head>
<body>
    <div id="wrap">
        <h1 class="text">Content Manager</h1>
        <div class="update-form">
            <div id="update-header" class="header-style">
                <h2 class="text">Create A New Article:</h2>
                <input type="button" value="toggle" onclick="show_hide('update-form-handle', 'show-update');" id="show-update" class="button-style">
            </div>
            <div id="update-form-handle" style="display: none;" class="internal-style">
                <form enctype="multipart/form-data" action="upload.cgi" method="POST">
                    <label for="title">Title:</label>
                    <input type="text" id="title" name="title" class="add-style">
                    <label for="author">Author:</label>
                    <input type"text" id="author" name="author" class="add-style">
                    <label for="body">Content:</label>
                    <textarea id="body" name="content">What do you want to write about?</textarea>
                    <label for="image_src" id="src-label">Image (optional):</label>
                    <input type="file" id="image_src" name="image_src" class="add-style-no-border">
                    <input type="hidden" id="session" value="$session">
                    <input type="submit" value="Add Content" id="add-button">
                </form>
            </div>
        </div>
        <div class="manage-posts">
            <div id="manage-header" class="header-style">
                <h2 class="text">Manage Posts:</h2>
                <input type="button" value="toggle" onclick="expand_manage()" id="show-manage" class="button-style">
            </div>
            <div id="manage-posts-handle" class="internal-style" style="display: none;">
            </div>
        </div>
    </div>
</body>
</html>
EOF
}

if (!(defined($session)))
{
#    die "no session cookie recovered";
    print "Status: 303 Authorisation Required\n";
    print "Location: http://$WEBADDRESS/cgi-bin/login.cgi\n";
    print $response->header(-type=>'text/plain',);
    print "Not Authenticated";
}
else
{
    open(session_file, "../data/authed.txt") or die "could not open file, error: $!, stopped";
    while (<session_file>)
    {
        if ($_ =~ /$session/ && $_ =~ /authorised/)
        ##format in file is "sessionID=$session snonce=$snonce authorised until $year/$month/$day $hour:$minutes:$seconds"
        {
            my $server_time = DateTime->now->epoch();
            my @words = split(/ /);
            my ($date, $time) = ($words[4], $words[5]);
            my ($year, $month, $day) = (split(/\//, $date))[0,1,2];
            my ($hour, $minute, $second) =  (split(/:/, $time))[0,1,2];
            my $expires = DateTime->new(
                year=>$year,
                month=>$month,
                day=>$day,
                hour=>$hour,
                minute=>$minute,
                second=>$second,
            );
            my $cookie_expire = $expires->epoch();
#           die "cookie expires = $cookie_expire; server-time = $server_time;";
            if ($cookie_expire > $server_time)
            {
#                die "authed";
                print $response->header(-type=>'text/html');
                print_html;
            }
            else
            {
#                die "not authed";
                print "Status: 303 Authorisation Required\n";
                print "Location: http://$WEBADDRESS/cgi-bin/login.cgi\n";
                print $response->header(-type=>'text/plain',);
                print "Not Authenticated";
            }
        }
    }
}
