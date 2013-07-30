#!/usr/bin/env perl

use warnings;
use strict;
use CGI;
use DBI();

my $query = new CGI();
my $dbh = DBI->connect("DBI:mysql:database=name;host=localhost", "user", "pass", {'RaiseError' => 1}); #change to webserver DB credentials
my $random = int(rand(100000000))+10000; #change as see fit... should be a semi cryptographically secure number

print "content-type: text/html\n\n";
print <<HTML;
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
        </form>
    </div>
</body>
HTML
exit;