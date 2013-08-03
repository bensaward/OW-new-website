#!/usr/bin/env perl

use strict;
use warnings;
use CGI;
use Crypt::OpenSSL::AES; #http://search.cpan.org/~ttar/Crypt-OpenSSL-AES-0.01/lib/Crypt/OpenSSL/AES.pm

my $q = CGI->new;
my $c_result = $q->param('client_result');
my $secret = ''; #read somehow
my $mod = ''; #read somehow from local file

my $key = ($c_result ** $secret) % $mod;
my $session_ID = '';
my $session_key = '';

##write all these to file

print <<EOF;
content-type: txt/html

<!DOCTYPE html>
<html>
<head>
    <title>Redirecting...</title>
    <script type="application/x-javascript" src="../js/crypto.js"></script>
</head>
<body>
    <script>
        var date_now=new Date();
        date_now.setTime(date_now.getTime()+(60*60*1000)); // 1 hour session
        date_now.toUTCString();
        
        
    </script>
</body>
</html>