#!/usr/bin/env perl

use warnings;
use strict;
use CGI();
use CGI::Cookie;
use DateTime;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);

my $q = CGI->new;
my $session = $q->cookie('SessionID');

my $serverURL = "";

sub print_login
{
    print $q->header(-type=>"text/html",);
    print <<"EOF";
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" src="../css/login.css">
    <script type="text/javascript" src="http://crypto-js.googlecode.com/svn/tags/3.0.1/build/rollups/sha256.js"></script>
    <script type="text/javascript" src="../js/crypto.js"></script>
    <meta charset="utf-8">
    <title>OUUC Login Page</title>
</head>
<body>
    <div id="center-content">
    <h1>Login:</h1>
        <form id="login-form">
            Username: <input type="text" id="username">
            Password: <input type="password" id="password" onkeypress="if (event.keyCode == 13)authenticate(this.form);">
            <input type="button" value="login" onclick="authenticate(this.form);">
        </form>
        <div id="error">
        </div>
    </div>
</body>
</html>
EOF
}

sub print_manager
{
    print "Status: 303 Authorised\n";
    print "Location: $serverURL/cgi-bin/manager.cgi\n";
    print $q->header(-type=>"text/html",);
}
if (!(defined($session)))
{
    print_login;
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
            if ($cookie_expire > $server_time)
            {
                print_manager;
            }
            else
            {
                print_login;
            }
        }
    }
}
