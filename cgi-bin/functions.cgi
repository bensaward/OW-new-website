#!/usr/bin/env perl

######################################################################
###  Order of table is "id title pub_date author content image_src" ##
###  must be obeyed by all scripts                                  ##
######################################################################
### create table $TNAME_POSTS(                                      ##
###     id int not null auto_increment,                             ##
###     title varchar(200) not null,                                ##
###     published date not null,                                    ##
###     author varchar(100) not null,                               ##
###     content text not null,                                      ##
###     image varchar(100),                                         ##
###     primary key(id)                                             ##
###     );                                                          ##
######################################################################
### create table $TNAME_PW(                                         ##
###     id int not null auto_increment,                             ##
###     user varchar(50) not null,                                  ##
###     hash varchar(64) not null,                                  ##
###     primary key(id)                                             ##
###     );                                                          ##
######################################################################

use v5.10.1;
use warnings;
use strict;
use CGI qw(redirect);
use DBI();
use Digest::SHA qw(sha256_hex);
use CGI::Cookie;
use File::Basename;

### CONFIG ###

my $DBNAME = "";
my $DBUNAME = "";
my $DBPASS = "";
my $DBHOST = "";
my $TNAME_PW = "login";  #table name for users and password hashes
my $WEBADDRESS = "";
my $DOCUMENT_ROOT = "";
### ENG CFG ###

### SUBS ###

sub verify ## verify (string) -> returns: 0 on non-alphanum else 1
{
    my $string=$_;
    
    if ($string =~ /\W/)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

sub snonce ## eg snonce(sessionID) -> returns nonce written to file
{
    my $q = CGI->new;   
    my $sessionID=$_[0];
    my $snonce=sha256_hex(int(rand(1000000)));
    open (session_file, ">>", "$DOCUMENT_ROOT/data/sessions.txt") or die $!; ##need to fix this with "chmod a+w" 
    print session_file "sessionID=$sessionID snonce=$snonce\n";
    close session_file;
    print $q->header(-type=>"text/plain",);
    print "$snonce";
}

sub login  ## eg login(user, hash, SessionID, cnonce) -> returns: auth cookie or redirect to login
{
    my ($user, $hash, $session, $cnonce, $snonce) = ($_[0], $_[1], $_[2], $_[3], undef);    
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1}) or die "Couldn't connect to the database, stopped";
    my $q = CGI->new;   
    if (verify($user) == 0)
    {
        print "fail";
        die "USER string contained illegal characters, stopped";
    }
    else
    {
        my (@data, $db_hash, @results, $string);
        $string = "SELECT hash FROM $TNAME_PW WHERE user = '$user'";
        my $dbq = $dbh->prepare($string);
        $dbq->execute();
        while (@data = $dbq->fetchrow_array())
        {
            $db_hash = $data[0];
        }
        if ($dbq->rows == 0)
        {
            print $q->header(-type=>'text/plain',);
            print "fail no rows found";
        }
        else
        {
            my $server_result;
            open (snonce_file, "$DOCUMENT_ROOT/data/sessions.txt") or die $!;
            while (<snonce_file>)
            {
                chomp;
                if ( $_ =~ /$session/)
                {
                    @results=split(/ /);
                    my @variables=split(/=/, $results[1]);
                    $snonce=$variables[1];
                } 
            }
            my $internal = "$db_hash$cnonce$snonce";
            $server_result=sha256_hex("$internal");
            
            if ("$hash" == "$server_result")
            {
                my $cookie1 = CGI::Cookie -> new (
                    -name=>'SessionID',
                    -value=>"$session",
                    -expires=>'+3h',
                    -httponly=>1,
                    -secure=>0,
                );
                
                my $time = time;
                $time=$time+(3*60*60);
                my ($seconds, $minute, $hour, $day, $month, $year) = (gmtime($time))[0,1,2,3,4,5];
                $year += 1900;
                $month += 1;

                open(out_file, ">>", "$DOCUMENT_ROOT/data/authed.txt") or die $!;
                $_ = "sessionID=$session snonce=$snonce authorised until $year/$month/$day $hour:$minute:$seconds\n";
                print out_file;
                close out_file;
                
                print "Status: 303 Other\n";
                print "Location: http://$WEBADDRESS/cgi-bin/manager.cgi\n";
                print "Set-Cookie: $cookie1\n";
                print $q->header(-type=>'text/plain',);
            }
            else
            {
                print $q->header(-type=>'text/plain',);
                print "fail, incorrect password";
            }
        }
    }
}


## END SUBS ###

my $query = CGI->new();
my $reqfunct=$query->param('request');

if ($reqfunct =~ /snonce/)
{
    my $session = $query->param('session');
    snonce($session);
}

elsif ($reqfunct =~ /login/)
{
    my $user = $query->param('user');
    my $session = $query->param('session');
    my $hash = $query->param('hash');
    my $cnonce = $query->param('cnonce');
    login($user, $hash, $session, $cnonce);
}

else
{
    print $query->header(-type=>'text/html',);
    print<< " EOF";
    <html>
    <head>
        <title>Error</title>
    </head>
    <body>
        <h1>Posts.cgi</h1>
        <p>There was an error in your request</p>
    </body>
    </html>
 EOF

}