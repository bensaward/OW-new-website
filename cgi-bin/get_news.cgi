#!/usr/bin/env perl

use warnings;
use strict;
use CGI;

my $document_root = "";
my $news;
open (news_file, "$document_root/data/news.txt") or die "could not open file, stopped";
while (<news_file>)
{
    chomp;
    if (!(defined($news)))
    {
        $news = $_;
    }
    else
    {
        $news = "$news*endofline*$_";
    }
}

my $query = CGI->new();
print $query->header(-type=>'text/plain',);
print $news;