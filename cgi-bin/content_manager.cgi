#!/usr/bin/env perl

use strict;
use warnings;
use DBI;
use CGI;

### CONFIG ###
my $DBNAME = '';
my $TABLENAME = '';
my $DBUSER = '';
my $DBPASS = '';


my $q = CGI->new;