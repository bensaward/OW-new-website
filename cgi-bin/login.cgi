#!/usr/bin/env perl

use warnings;
use strict;
use CGI();

my $q = CGI->new;
print $q->header(-type=>"text/html",
                 -origin=>"http://192.168.0.10",);
print <<"EOF";
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" src="../css/login.css">
    <script type="text/javascript" src="http://crypto-js.googlecode.com/svn/tags/3.0.1/build/rollups/sha256.js"></script>
    <script type="text/javascript" src="../js/crypto.js"></script>
    <meta charset="utf-8">
    <title>Admin Login Page</title>
</head>
<body>
    <div class="center_content">
        <form>
            Username: <input type="text" id="username">
            Password: <input type="password" id="password">
            <input type="button" value="login" onclick="authenticate(this.form);">
        </form>
        <div id="error">
        </div>
    </div>
</body>
</html>
EOF