#!/usr/bin/env perl

use warnings;
use strict;
use DBI();
use CGI;
use CGI::Cookie;
use File::Basename;

### CONFIG ###

my $DBNAME = "";
my $DBUNAME = "";
my $DBPASS = "";
my $DBHOST = "";
my $TNAME_POSTS = "posts";   #table name for db containing hashes
my $FILE_LOCATION = "";
my $DOCUMENT_ROOT = "";
my $WEBADDRESS = "";

### END CONFIG ###

##### SUBROUTINES #####
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

sub authenticated ## authenticated(sessionid) -> returns 1 if authenticated, 0 if not
{
    my ($session, $current_time, $authed) = ($_[0], DateTime->now()->epoch(), 0);
    open (session_file, "$DOCUMENT_ROOT/data/authed.txt") or die $!;
    while (<session_file>)
    {
        if ($_ =~ /$session/ && $_ =~ /authenticated/)
        {
            my @words = split(/ /);  ## format: sessionID=$session snonce=$snonce authenticated until $year/$month/$day $hour:$minute:$second
            my ($exp_date, $exp_time) = (@words)[4,5];
            my ($exp_year, $exp_month, $exp_day) = (split(/\//, $exp_date))[0,1,2];
            my ($exp_hour, $exp_minute, $exp_second) = (split(/:/))[0,1,2];
            my $expire_time = DateTime->new(
                year=>$exp_year,
                month=>$exp_month,
                day=>$exp_day,
                hour=>$exp_hour,
                minute=>$exp_minute,
                second=>$exp_second,
            );
            if ($current_time < $expire_time->epoch())
            {
                $authed=1;
            }
        }
    }
    return $authed;
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
    my $string = "SELECT * FROM $TNAME_POSTS WHERE published < '$date' ORDER BY published DESC LIMIT 5";
    my $dbq = $dbh->prepare($string);
    $dbq->execute();
    if ($dbq->rows == 0)
    {
        my $q = CGI->new;   
        print $q->header(-type=>'text/plain',);
        print "0";
        die "could not retrieve posts before $day-$month-$year, stopped";
    }
    else
    {
        while (@results = dbq->fetchrow_array())
        {
            $id[$count]=$results[0];
            $name[$count]=replace_unsafe($results[1], "decode");
            $published[$count]=$results[2];
            $author[$count]=replace_unsafe($results[3], "decode");
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
    my $db_check = "SELECT * FROM $TNAME_POSTS WHERE id = '$id'";
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
    my $query = "SELECT image FROM $TNAME_POSTS where id=$id";
    my $dbq = $dbh->prepare($query);
    my $q = CGI->new;
    print $q->header(-type=>'text/plain');
    $dbq->execute();
    if ($dbq->rows == 0)
    {
        print "article not found";
        die "incorrect id of article, stopped";
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

##### END SUBS ###

my $query = CGI->new;
my ($reqfunct) = ($query->param('request'));
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

if ($reqfunct =~ /get_content/)
{
    my $id = $query->param('id');
    get_content($id);
}

if ($reqfunct =~ /get_image/)
{
    my $id = $query->param('id');
    get_image($id);
}

else
{
    print $query->header(-type=>'text/html',);
    print<< "EOF";
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

