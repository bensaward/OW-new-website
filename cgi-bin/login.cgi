#!/usr/bin/env perl

use strict;
use warnings;
use CGI;
use DBI();

my $query = new CGI();
my $dbh = DBI->connect("DBI:mysql:database=name;host=localhost", "user", "pass", {'RaiseError' => 1}); #change to webserver DB credentials

open(NONCE, 'server_challenge.txt');
my $snonce = $_;
close NONCE;
