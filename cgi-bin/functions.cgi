#!/usr/bin/env perl

use warnings;
use strict;
use CGI;
use DBI();
use Digest::SHA;
use CGI::Cookie;

### CONFIG ###

my $DBNAME = "";
my $DBUNAME = "";
my $DBPASS = "";
my $DBHOST = "";
my $TNAME_PW = "";  #table name for users and password hashes
my $TNAME_POSTS = "";   #table name for db containing hashes
### ENG CFG ###

my $user = '';
my $hash = '';
my $sessionID = '';

### SUBS ###

sub snonce ## eg snonce(sessionID) -> returns nonce written to file
{
    my $sessionID=$_[0];
    my $snonce=sha256_hex(int(rand(1000000)));
    open (session_file, '>>../data/sessions.txt');
    print 'sessionID=$sessionID snonce=$snonce';
    close session_file;
    print '$snonce';
}

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

sub login  ## eg login(user, hash, SessionID, cnonce) -> returns: auth cookie or redirect to login
{
    my $user = $_[0];
    my $hash = $_[1];
    my $session = $_[2];
    my $cnonce = $_[3];
    my $snonce;
    
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    if (verify($user) == 0)
    {
        my $q=CGI->new();
        print $q->redirect(
            -uri=>'../content-manager/login.html',
            -nph=>1,
            -status=>'303 See Other');
    }
    else
    {
        my @data;
        my $db_hash;
        my @results;
        my $dbq = $dbh->prepare('SELECT hash FROM $TNAME_PW WHERE user = ?');
        $dbq->execute('$user');
        while (@data = $dbq->fetchrow_array())
        {
            $db_hash = $data[0];
        }
        if ($dbq->rows == 0)
        {
            my $q=CGI->new();
            print $q->redirect(
                -uri=>'../content-manager/login.html',
                -nph=>1,
                -status=>'303 See Other');
        }
        else
        {
            my $server_result;
            open (snonce_file, "../data/sessions.txt");
            while (<snonce_file>)
            {
                if ( $_ =~ /'$session'/)
                {
                    @results=split(/ /);
                    my @variables=split(/=/, $results[1]);
                    $snonce=$variables[1];
                } 
            }
            
            $server_result=sha256_hex('$db_hash$cnonce$snonce');
            
            if ($hash == $server_result)
            {
                my $cookie1 = CGI::Cookie -> new (
                    -name=>'SessionID',
                    -value=>'$session',
                    -expires=>'+1h'
                    -domain=>'/content-manager/manager.html'
                );
                
                $cookie1->bake();
                
                my $q=CGI->new();
                print $q->redirect(
                -uri=>'../content-manager/manager.html',
                -nph=>1,
                -status=>'303 See Other');
            }
        }
    }
}

sub get_title   ## get_title(DATE) -> returns the 5 most recent article names. table order: id name date author content
{
    my @results, my @id, my @name, my $date=$_[0], my $count=0, my @author, my @published;
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $dbq = $dbh->prepare('SELECT * FROM $TNAME_POSTS WHERE date < ? ORDER BY date DESC LIMIT 5');
    $dbq->execute('$date');
    while (@results = dbq->fetchrow_array())
    {
        $id[$count]=$results[0];
        $name[$count]=$results[1];
        $author[$count]=$results[2];
        $published[$count]=$results[3];
        $count+=1;
    }
    
    print '$id[0]:$name[0]:$author[0]:$published[0]:$id[1]:$name[1]:$author[1]:$published[1]:$id[2]:$name[2]:$author[2]:$published[2]:$id[3]:$name[3]:$author[3]:$published[3]:$id[4]:$name[4]:$author[4]:$published[4]';
}

sub delete_post ## delete_post(ID) -> deletes post with said ID in the database
{
    my $id=$_[0];
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $dbq = $dbh->prepare('DELETE FROM $TNAME_POSTS WHERE ID = ?');
    $dbq->execute('$id');
}
## END SUBS ###

my $query = CGI->new();
my $reqfunct=$query->param('request');
if ($reqfunct =~ /snonce/)
{
    my $session = $query->param('session');
    snonce($session);
}

if ($reqfunct =~ /login/)
{
    my $user = $query->param('user');
    my $session = $query->param('session');
    my $hash = $query->param('hash');
    my $cnonce = $query->param('cnonce');
    login($user, $hash, $session, $cnonce);
}
