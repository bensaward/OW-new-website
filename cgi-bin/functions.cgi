#!/usr/bin/env perl

######################################################################
###  Order of table is "id title pub_date author content image_src" ##
###  must be obeyed by all scripts                                  ##
######################################################################
### create table $TNAMES_POSTS(                                     ##
###     id not null auto_increment,                                 ##
###     title varchar(200) not null,                                ##
###     pub_date date not null,                                     ##
###     author varchar(100) not null,                               ##
###     content text not null,                                      ##
###     image_src varchar(100),                                     ##
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
my $TNAME_PW = "";  #table name for users and password hashes
my $TNAME_POSTS = "";   #table name for db containing hashes
my $FILE_LOCATION = "";
my $DOCUMENT_ROOT = "";
my $WEBADDRESS = "";

### ENG CFG ###

### SUBS ###

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

sub authenticated ## authenticated(sessionid) -> returns 1 if authenticated, 0 if not
{
    my ($session, $current_time) = ($_[0], time);
    open (session_file, "$DOCUMENT_ROOT/data/sessions.txt") or die $!;
    while (<session_file>)
    {
        if ($_ =~ /$session/ && $_ =~ /authenticated/)
        {
            my @words = split(/ /);  ## format: sessionID=$session snonce=$snonce authenticated until $year/$month/$day $hour:$minute:$second
            my ($exp_date, $exp_time) = (@words)[4,5];
            my ($exp_year, $exp_month, $exp_day) = (split(/\//, $exp_date))[0,1,2];
            my ($exp_hour, $exp_minute, $exp_second) = (split(/:/))[0,1,2];
            my $expire_time = DateTime->new(
                -year=>$exp_year,
                -month=>$exp_month,
                -day=>$exp_day,
                -hour=>$exp_hour,
                -minute=>$exp_minute,
                -second=>$exp_second,
            );
            if ($current_time < $exp_time)
            {
                return 1;
            }
            else
            {
                return 0;
            }
        }
    }
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
        $string = "SELECT hash FROM $TNAME_PW WHERE user = \'$user\'";
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
            
            if ($hash == $server_result)
            {
                my $cookie1 = CGI::Cookie -> new (
                    -name=>'SessionID',
                    -value=>"$session",
                    -expires=>'+3h',
                    -httponly=>1,
                    -secure=>0,
                );
                
                my $time = time;
                my ($seconds, $minute, $hour, $day, $month, $year) = (gmtime($time))[0,1,2,3,4,5];
                $year += 1900;
                $month += 1;

                open(out_file, ">>", "$DOCUMENT_ROOT/data/authed.txt") or die $!;
                $_ = "sessionID=$session snonce=$snonce authorised until $year/$month/$day $hour:$minute:$seconds\n";
                print out_file $_;
                close out_file;
                
                print "Status: 303 Other\n";
                print "Location: $WEBADDRESS/cgi-bin/manager.cgi\n";
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

sub upload_image ## upload_image(filename, db_id, file_handle)
{    
    my ($filename, $db_id, $file_handle) = @_[0,1,2];
    my $result;
    $FILE_LOCATION = "$FILE_LOCATION/posts";
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my ($dbqstring, $check_string) = ("UPDATE $TNAME_POSTS SET image_src=$FILE_LOCATION/$filename WHERE id=$db_id", "SELECT \'image\' FROM $TNAME_POSTS WHERE id=\'$db_id\'");
    my $dbquery = $dbh->prepare($dbqstring);
    $dbquery->execute();
    my $db_check = $dbh->prepare($check_string);
    $db_check->execute();
    if ($db_check->rows == 0)
    {
        my $q = CGI->new;   
        print $q->header(-type=>'text/plain',);
        print "error";
        die "Could not add image_src to the database, stopped";
    }
    else
    {
        $result = $db_check->fetchrow_array();
        if (!(defined($result)))
        {
            my $q = CGI->new;   
            print $q->header(-type=>'text/plain',);
            print "error";
            die "Something went wrong, stopped";
        }
        open(image_out, ">", "$FILE_LOCATION/$filename");
        binmode image_out;
        while (<$file_handle>)
        {
            print image_out;
        }
        close image_out;
    }
}

sub get_title   ## get_title(DATE) -> returns the 5 most recent article names.
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
        my $q = CGI->new;   
        print $q->header(-type=>'text/plain',);
        print "Could not retrieve posts";
        die "could not retrieve posts before $day-$month-$year, stopped";
    }
    else
    {
        while (@results = dbq->fetchrow_array())
        {
            $id[$count]=$results[0];
            $name[$count]=$results[1];
            $published[$count]=$results[2];
            $author[$count]=$results[3];
            $count+=1;
        }
        my ($i, $string) = (0, $count+1);
        while ($i < $count)
        {
            $string = "$string::$id[$i]::$name[$i]::$published[$i]::$author[$i]";
            $i++;
        }
        my $q = CGI->new;   
        print $q->header(-type=>'text/plain',);
        print "$string";
    }
}

sub delete_post ## delete_post(ID) -> deletes post with said ID in the database : returns "success" or "error"
{
    my $id=$_[0];
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $string = "DELETE FROM $TNAME_POSTS WHERE id = $id";
    my $dbq = $dbh->prepare($string);
    $dbq->execute();
    my $db_check = "SELECT * FROM $TNAME_POSTS WHERE id = \'$id\'";
    my $db_exec = $dbh->prepare($db_check);
    $db_exec->execute();
    my $q = CGI->new;   
    print $q->header(-type=>'text/plain',);
    if (!($db_exec->rows == 0))
    {
        print "Could not delete post";
        die "could not delete post id=$id, stopped";
    }
    else
    {
        print "Post was deleted";
    }
}

sub get_content ## get_content(ID) ->  returns the content of an article as a string... returns "fail" on fail
{
    my $id = $_;
    my $content;
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $dbquery = "SELECT content FROM $TNAME_POSTS WHERE id = $id";
    my $dbq = $dbh->prepare($dbquery);
    $dbq->execute();
    my $q = CGI->new;   
    print $q->header(-type=>'text/plain',);
    if ($dbq->rows == 0 || $dbq->rows > 1)
    {
        print "fail";
        die "Could not retrieve post $id, stopped";
    }
    else
    {
        $content = $dbq->fetchrow_array();
        print "$content";
    }
}

sub get_image ## get_image(ID) -> returns a string containing the src of an image... returns "none" on fail
{
    my $id = $_;
    my $image_src;
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME, $DBPASS, {'RaiseError' => 1});
    my $query = "SELECT image_src FROM $TNAME_POSTS where id=$id";
    my $dbq = $dbh->prepare($query);
    my $q = CGI->new;
    print $q->header(-type=>'text/plain');
    $dbq->execute();
    if ($dbq->rows == 0)
    {
        print "none";
    }
    else
    {
        $image_src=$dbq->fetchrow_array();
        if (!(defined($image_src)))
        {
            $image_src="none";
        }
        print "$image_src";
    }
}

sub replace_unsafe ## replace_unsafe(string, encode|decode)
{
    my ($string,$code) = @_[0,1];
    if ($code =~ /encode/)
    {
        if ($string =~ /\'/){$string =~ s/\'/\&apost/g;}
        if ($string =~ /\"/){$string =~ s/\"/\&quot/g;}
        if ($string =~ /\:/){$string =~ s/\:/&colon/g;}
        if ($string =~ /\;/){$string =~ s/\;/&semicol/g;}
        if ($string =~ /\$/){$string =~ s/\$/&dolar/g;}
        if ($string =~ /\@/){$string =~ s/\@/&at/g;}
        if ($string =~ /\%/){$string =~ s/\%/&percent/g;}
    }
    else
    {
        if ($string =~ /&apost/){$string =~ s/&apost/\'/g;}
        if ($string =~ /&quot/){$string =~ s/&quot/\"/g;}
        if ($string =~ /&colon/){$string =~ s/&colon/\:/g}
        if ($string =~ /&semicol/){$string =~ s/&semicol/\;/g;}
        if ($string =~ /&dolar/){$string =~ s/&dolar/\$/g;}
        if ($string =~ /\&at/){$string =~ s/&at/\@/g;}
        if ($string =~ /&percent/){$string =~ s/&percent/\%/}
    }
}

sub add_content ## add_content(title, date, author, content, image_src, filehandle) -> returns true if content is added successfully, error if not.
{
    my ($title, $date, $author, $content, $image_src, $filehandle) = @_[0,1,2,3,4,5];
    my ($day, $month, $year) = (gmtime($date))[3,4,5];
    $year = $year + 1900;
    replace_unsafe($content, "encode");
    replace_unsafe($author, "encode");
    replace_unsafe($title, "encode");
    
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $dbquery = "INSERT INTO $TNAME_POSTS (title, date, author, content) VALUES ('$title', '$year-$month-$day', '$author', '$content')";
    my $dbq = $dbh->prepare($dbquery);
    $dbq->execute();
    
    my $dbstring = "SELECT * FROM $TNAME_POSTS WHERE title = \'$title\'";
    my $dbhandle = $dbh->prepare($dbstring);
    $dbhandle->execute();
    my @results;
    my $q = CGI->new;   
    print $q->header(-type=>'text/plain',);
    if ($dbhandle->rows == 0)
    {
        print "There was an error in adding the content";
        die "Could not add content, stopped";
    }
    else
    {
        print "The post has been added!";
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
    my ($id, $session) = ($query->param('id'), $query->param('session'));
    if (authenticated($session) == 1)
    {
        delete_post($id);
    }
    else
    {
        print "error, you do not have permission to do that";
        die "Could not delete post id=$id, session=$session is not authenticated. Stopped";
    }
}

if ($reqfunct =~ /add_content/)
{
    my ($session, $title, $date, $author, $content, $filename, $filehandle) = ($query->param('session'), $query->param('title'), time, $query->param('author'), $query->param('content'), $query->param('image_src'), $query->upload('image_src'));
    my $safe_chars = "a-zA-Z0-9.-_";
    if (verify($filename) == 1 && authenticated($session) == 1)
    {
        add_content($title, $date, $author, $content, $filename, $filehandle);
    }
    else
    {
        if ( $filename =~ /^[$safe_chars]+)$/)
        {
            print "error, illegal characters in the filename";
            die "Could not add content, illegal filename. Stopped";
        }
        else
        {
            print "error, you do not have permission to do that";
            die "Could not add content, session=$session is not authenticated. Stopped";
        }
    }
}

if ($reqfunct =~ /get_content/) ## content in db has "+" instead of " ". Will need to modify JS to replace this.
{
    my $id = $query->param('id');
    get_content($id);
}
