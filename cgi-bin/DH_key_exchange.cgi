#!/usr/bin/env perl

use strict;
use warnings;
use CGI;
use Crypt::OpenSSL::AES; #http://search.cpan.org/~ttar/Crypt-OpenSSL-AES-0.01/lib/Crypt/OpenSSL/AES.pm

my $q = CGI->new;
my $c_result = $q->param('client_result');

my $secret = ''; #read somehow
my $mod = ''; #read somehow from local file
my $session_ID = '';

my $key = ($c_result ** $secret) % $mod;
my $session_key = '';

##write all these to file

open(key_hive, '>>keyhive.txt'); ## ensure this cannot be read by the public or any attacker
print key_hive "ID=$session_ID s_key=$session_key key=$key";
close key_hive;
