#!/usr/bin/env perl

use warnings;
use strict;
use CGI;
use DBI();
use Digest::SHA;
use CGI::Cookie;
use File::Basename;

### CONFIG ###

my $DBNAME = "";
my $DBUNAME = "";
my $DBPASS = "";
my $DBHOST = "";
my $TNAME_PW = "";  #table name for users and password hashes
my $TNAME_POSTS = "";   #table name for db containing hashes
my $FILE_LOCATION = "";

### ENG CFG ###

### SUBS ###

sub snonce ## eg snonce(sessionID) -> returns nonce written to file
{
    my $sessionID=$_[0];
    my $snonce=sha256_hex(int(rand(1000000)));
    open (session_file, '>>../data/sessions.txt');
    print "sessionID=$sessionID snonce=$snonce";
    close session_file;
    print "$snonce";
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
    my ($user, $hash, $session, $cnonce, $snonce) = ($_[0], $_[1], $_[2], $_[3], undef);    
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    if (verify($user) == 0)
    {
        my $q=CGI->new();
        print $q->redirect(
            -uri=>'../content-manager/login.html',
            -nph=>1,
            -status=>'303 See Other');
        
        die "USER string contained illegal characters, stopped";
    }
    else
    {
        my (@data, $db_hash, @results, $string);
        $string = "SELECT hash FROM $TNAME_PW WHERE user = $user";
        my $dbq = $dbh->prepare($string);
        $dbq->execute();
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
                if ( $_ =~ /"$session"/)
                {
                    @results=split(/ /);
                    my @variables=split(/=/, $results[1]);
                    $snonce=$variables[1];
                } 
            }
            
            $server_result=sha256_hex("$db_hash$cnonce$snonce");
            
            if ($hash == $server_result)
            {
                my $cookie1 = CGI::Cookie -> new (
                    -name=>'SessionID',
                    -value=>"$session",
                    -expires=>'+3h'
                    -domain=>'/content-manager/manager.html'
                );
                
                my $time = time;
                my ($seconds, $minute, $hour, $day, $month, $year) = (gmtime($time))[0,1,2,3,4,5];
                $year += 1900;
                $month += 1;

                open(in_file, "../data/sessions.txt");
                open(out_file, "../data/sessions.txt");
                
                while (<in_file>)
                {
                    if ($_ =~ /"$session"/) {
                        $_ = "sessionID=$session snonce=$snonce authorised until $year/$month/$day $hour:$minute:$seconds\n";
                    }
                    print out_file $_;
                }
                close in_file;
                close out_file;
                
                $cookie1->bake();
                
                my $q=CGI->new();
                print $q->redirect(
                -uri=>'../content-manager/manager.html',
                -nph=>1,
                -status=>'303 See Other');
            }
            else
            {
                my $q=CGI->new();
                print $q->redirect(
                    -uri=>'../content-manager/login.html',
                    -nph=>1,
                    -status=>'303 See Other'
                    );
            }
        }
    }
}

sub upload_image ## upload_image(image_src, db_id)
{
    my $image_src = $_[0];
    my $filename;
    $FILE_LOCATION = "$FILE_LOCATION/posts";
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $dbqstring = "UPDATE $TNAME_POSTS SET image=$FILE_LOCATION/$filename";
}

sub get_title   ## get_title(DATE) -> returns the 5 most recent article names. table order: id name date author content image
{               ## returns "error" if posts cannot be retrieved.
    my ($date_seconds, $count) = ($_[0], 0);
    my (@results, @id, @name, @author, @published);
    my ($day, $month, $year) = (gmtime($date_seconds))[3,4,5];
    $year += 1900;
    $month += 1;
    my $date =  "$year-$month-$day";
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $string = "SELECT * FROM $TNAME_POSTS WHERE date < $date ORDER BY date DESC LIMIT 5";
    my $dbq = $dbh->prepare($string);
    $dbq->execute();
    if ($dbq->rows == 0)
    {
        return "error";
        die "could not retrieve posts before $day-$month-$year, stopped";
    }
    else
    {
        while (@results = dbq->fetchrow_array())
        {
            $id[$count]=$results[0];
            $name[$count]=$results[1];
            $author[$count]=$results[2];
            $published[$count]=$results[3];
            $count+=1;
        }
    
        print "$id[0]:$name[0]:$author[0]:$published[0]:$id[1]:$name[1]:$author[1]:$published[1]:$id[2]:$name[2]:$author[2]:$published[2]:$id[3]:$name[3]:$author[3]:$published[3]:$id[4]:$name[4]:$author[4]:$published[4]";
    }
}

sub delete_post ## delete_post(ID) -> deletes post with said ID in the database : returns "success" or "error"
{
    my $id=$_[0];
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $string = "DELETE FROM $TNAME_POSTS WHERE id = $id";
    my $dbq = $dbh->prepare($string);
    $dbq->execute();
    my $db_check = "SELECT * FROM $TNAME_POSTS WHERE id = $id";
    my $db_exec = $dbh->prepare($db_check);
    $db_exec->execute();
    if (!($db_exec->rows == 0))
    {
        print "error";
        die "could not delete post id=$id, stopped";
    }
    else
    {
        print "success";
    }
}

sub get_content ## get_content(ID) ->  returns a string containing the table information... returns "error" on error
{
    my $id = $_[0];
    my ($title, $author, $content, $date, $image);
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $dbquery = "SELECT * FROM $TNAME_POSTS WHERE id = $id";
    my $dbq = $dbh->prepare($dbquery);
    $dbq->execute();
    my @results;
    while (@results=fetchrow_array())
    {
        ($title, $author, $content, $date, $image) = ($_[1], $_[2], $_[3], $_[4], $_[5]);
    }
    if ($dbq->rows == 0 || $dbq->rows > 1)
    {
        print 'error';
        die "Could not retrieve post $id, stopped";
    }
    else
    {
        if ($image == "" || !$image)
        {
            $image = "none";
        }
        print '$id:$author:$content:$date:$image';
    }
    
}
sub add_content ## add_content(title, date, author, content, image_src) -> returns true if content is added successfully, error if not.
{
    my ($title, $date, $author, $content, $image_src) = ($_[0], $_[1], $_[2], $_[3], $_[4]);
    my ($day, $month, $year) = (gmtime($date))[3,4,5];
    $year = $year + 1900;
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $dbquery = "INSERT INTO $TNAME_POSTS (title, date, author, content) VALUES ($title, $year-$month-$day, $author, $content)";
    my $dbq = $dbh->prepare($dbquery);
    $dbq->execute();
    my $dbstring = "SELECT * FROM $TNAME_POSTS WHERE title = $title";
    my $dbhandle = $dbh->prepare($dbstring);
    $dbhandle->execute();
    my @results;
    if ($dbhandle->rows == 0)
    {
        print "error";
        die "Could not add content, stopped";
    }
    else
    {
        print "sucess";
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

if ($reqfunct =~ /login/)
{
    my $user = $query->param('user');
    my $session = $query->param('session');
    my $hash = $query->param('hash');
    my $cnonce = $query->param('cnonce');
    login($user, $hash, $session, $cnonce);
}

if ($reqfunct =~ /get_title/)
{
    my $date = $query->param('date');
    get_title($date);
}

if ($reqfunct =~ /delete_post/)
{
    my $id = $query->param('id');
    delete_post($id);
}

if ($reqfunct =~ /add_content/)
{
    my ($title, $date, $author, $content, $upload) = ($query->param('title'), time, $query->param('author'), $query->param('content'), $query->param('image_src'));
    my ($day, $month, $year) = (gmtime($date))[3,4,5];
    $month += 1;
    $year += 1900;
    my $published = "$year-$month-$day";
}

if ($reqfunct =~ /get_content/)
{
    #code
}
