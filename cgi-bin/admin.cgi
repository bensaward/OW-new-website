#!/usr/bin/env perl

use warnings;
use strict;
use CGI;

my $q = CGI->new;
my $redirected = $q->param('incorrect');

my $random = int(rand(100000000))+10000; #change as see fit... should be a semi cryptographically secure number

open(SNONCE_FILE, '>server_challenge.txt');
print SNONCE_FILE $random;
close SNONCE_FILE;

if ($redirected == "yes")
{
    print <<HTML;
    content-type: text/html
    
    <!DOCTYPE html>
    <head>
    <meta charset="utf-8">
    <title>Admin Login</title>
    <link rel="stylesheet" type="text/css" href="css/admin.css">
    <script type="application/x-javascript" src="../js/crypto.js"></script>
    </head>
    <body>
        <div class="center_content">
            <form>
                <h1>Admin Login</h1>
                User: <input type="text" name="user" id="user"><br>
                Password: <input type="password" name="passwd" id="password"><br>
                <input type="hidden" name="servernonce" value=$random>
                <input type="submit" value="Login" id="button" onclick="hash(this.form)">
                <h2>Incorrect Username or Password</h2>
                <noscript>
                    <p>Please enable JavaScript in your browser!</p>
                </noscript>
            </form>
        </div>
    </body>
HTML
}

else
{
    print <<HTML;
    content-type: text/html
    <!DOCTYPE html>
    <head>
        <meta charset="utf-8">
        <title>Admin Login</title>
        <link rel="stylesheet" type="text/css" href="css/admin.css">
        <script type="application/x-javascript" src="../js/crypto.js"></script>
    </head>
    <body>
        <div class="center_content">
            <form>
                <h1>Admin Login</h1>
                User: <input type="text" name="user" id="user"><br>
                Password: <input type="password" name="passwd" id="password"><br>
                <input type="hidden" name="servernonce" value=$random>
                <input type="submit" value="Login" id="button" onclick="hash(this.form)">
                <noscript>
                    <p>Please enable JavaScript in your browser!</p>
                </noscript>
            </form>
        </div>
    </body>
HTML
}
