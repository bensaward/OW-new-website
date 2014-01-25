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
my $TNAME_POSTS = "posts";   #table name for db containing posts
my $DOCUMENT_ROOT = "";


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
    return $string;
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
    my $string = "SELECT * FROM $TNAME_POSTS WHERE published < \'$date\' ORDER BY published DESC LIMIT 5";
    my $dbq = $dbh->prepare($string);
    $dbq->execute();
    if ($dbq->rows > 0)
    {
        while (@results = $dbq->fetchrow_array())
        {
            $id[$count]=$results[0];
            $name[$count]=$results[1];
            $published[$count]=$results[2];
            $author[$count]=$results[3];
            
            $author[$count]=replace_unsafe($author[$count], "decode");
            $name[$count]=replace_unsafe($name[$count], "decode");
            $count++;
        }
        my ($i, $post_count) = (0, $count);
        my $response = "$post_count\::$id[$i]::$name[$i]::$published[$i]::$author[$i]";
        $i++;
        while ($i < $count)
        {
            $response = "$response::$id[$i]::$name[$i]::$published[$i]::$author[$i]";
            $i++;
        }
        my $q = CGI->new;   
        print $q->header(-type=>'text/plain',);
        print "$response";
    }
    else
    {
        my $q = CGI->new;   
        print $q->header(-type=>'text/plain',);
        print "0";
        die "could not retrieve posts before $day-$month-$year, stopped";
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
    my $id = $_[0];
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
        $content = replace_unsafe($content, "decode");
        print "$content";
    }
}

sub get_image ## get_image(ID) -> returns a string containing the src of an image... returns "none" on fail
{
    my $id = $_[0];
    my $image_src;
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME, $DBPASS, {'RaiseError' => 1});
    my $query = "SELECT image FROM $TNAME_POSTS where id=\'$id\'";
    my $dbq = $dbh->prepare($query);
    my $q = CGI->new;
    print $q->header(-type=>'text/plain');
    $dbq->execute();
    if ($dbq->rows == 0)
    {
        print "article not found";
        exit 1;
    }
    else
    {
        $image_src=$dbq->fetchrow_array();
        if ("$image_src" == "" || $image_src =~ /NULL/)
        {
            $image_src="none";
        }
        print "$image_src";
    }
}

sub get_articles
{
    my ($date, $count) =($_[0],0);
    my ($day,$month,$year) = (gmtime($date))[3,4,5];
    $month++;
    $year = $year+1900;
    my $sql_date = "$year-$month-$day";
    my $query_string = "SELECT * FROM $TNAME_POSTS WHERE published < \'$sql_date\' ORDER BY published DESC LIMIT 5";
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my $query = $dbh->prepare($query_string);
    my $q = CGI->new;
    print $q->header(-type=>'text/plain');
    
    $query->execute();
    if ($query->rows == 0)
    {
        print "NULL";
        exit 1;
    }
    else
    {
        my ($i,$x)= (0,0);
        my (@table_output, @data);
        while (@table_output = $query->fetchrow_array())
        {
            $data[$i]="$table_output[0]\:\:$table_output[1]\:\:$table_output[2]\:\:$table_output[3]\:\:$table_output[4]\:\:$table_output[5]";
            $i++;
        }
        my $retstring = "$i";
        while ($x < $i)
        {
            $retstring="$retstring\:\:$data[$x]";
            $x++;
        }
        print "$retstring";
    }
}

##### END SUBS ###

my $query = CGI->new;
my ($reqfunct) = ($query->param('request'));
if ($reqfunct =~ /get_title/)
{
    if (defined($query->param('date')))
    {
        my $date = $query->param('date');
        get_title($date);
    }
    else
    {
        get_title(time);
    }
}

elsif ($reqfunct =~ /delete_post/)
{
    my ($id, $session) = ($query->param('id'), $query->param('session'));
    if (authenticated($session) == 1)
    {
        delete_post($id);
    }
    else
    {
        print "error, you do not have permission to do that";
        exit 1; 
    }
}

elsif ($reqfunct =~ /get_content/)
{
    my $id = $query->param('id');
    get_content($id);
}

elsif ($reqfunct =~ /get_image/)
{
    my $id = $query->param('id');
    get_image($id);
}

elsif($reqfunct =~ /get_articles/)
{
    if (defined($query->param('date')))
    {
        my $date = $query->param('date');
        get_articles($date);
    }
    else
    {
        get_articles(time);
    }
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

