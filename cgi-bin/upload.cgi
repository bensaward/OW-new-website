#!/usr/bin/env perl

######################################################################
###  Order of table is "id title pub_date author content image_src" ##
###  must be obeyed by all scripts                                  ##
######################################################################
### create table $TNAMES_POSTS(                                     ##
###     id int not null auto_increment,                             ##
###     title varchar(200) not null,                                ##
###     published date not null,                                    ##
###     author varchar(100) not null,                               ##
###     content text not null,                                      ##
###     image varchar(200),                                         ##
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
my $TNAME_POSTS = "posts";   #table name for db containing hashes
my $FILE_LOCATION = "";
my $DOCUMENT_ROOT = "";
my $WEBADDRESS = "";

### ENG CFG ###

### SUBS ###
sub print_error
{
    my ($title, $message) = @_[0,1];
    my $q = CGI->new;
    print $q->header(-type=>'text/html',);
    print <<"EOF";
<!DOCTYPE html>
<html>
<head>
    <title>$title</title>
    <meta charset="utf-8">
    <script type="text/javascript">
        setInterval(
            function(){
                document.location("$WEBADDRESS/cgi-bin/manager.cgi");
            },15000);
    </script>
    <style type="text/css">
        a
        {
            color: #000;
        }
    </style>
</head>

<body>
    <p><b>$message</b></p>
    <p>(click <a href="$WEBADDRESS/cgi-bin/manager.cgi">here</a> if you are not automatically redirected)</p>
</body>
EOF
}

sub print_success
{
    my $q = CGI->new;
    print $q->header(-type=>'text/html',);
    print <<"EOF";
    <!DOCTYPE html>
<html>
<head>
    <title>Thanks...</title>
    <meta charset="utf-8">
    <script type="text/javascript">
        setInterval(
            function(){
                document.location("$WEBADDRESS/cgi-bin/manager.cgi");
            },10000);
    </script>
    <style type="text/css">
        a
        {
            color: #000;
        }
    </style>
</head>

<body>
    <p><b>Your post was added successfully! Thank you for contributing.</b></p>
    <p>(click <a href="$WEBADDRESS/cgi-bin/manager.cgi">here</a> if you are not automatically redirected)</p>
</body>
EOF
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

sub upload_image ## upload_image(filename, db_id, file_handle)
{    
    my ($filename, $db_id, $file_handle, $referred) = @_[0,1,2,3];
    my $result;
    $FILE_LOCATION = "$FILE_LOCATION/posts";
    my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
    my ($dbqstring, $check_string) = ("UPDATE $TNAME_POSTS SET image='$FILE_LOCATION/$filename' WHERE id=$db_id", "SELECT image FROM $TNAME_POSTS WHERE id='$db_id'");
    my $dbquery = $dbh->prepare($dbqstring);
    $dbquery->execute();
    my $db_check = $dbh->prepare($check_string);
    $db_check->execute();
    if ($db_check->rows == 0)
    {
        print_error("Ooops...", "There was an error uploading the file. Please try again later.");
        die "Could not add image_src to the database, stopped";
    }
    else
    {
        $result = $db_check->fetchrow_array();
        if (!(defined($result)))
        {
            print_error("Ooops...", "There was an error uploading the file. Please try again later.");
            die "Something went wrong, db check failed, stopped";
        }
        open(image_out, ">", "$FILE_LOCATION/$filename");
        binmode image_out;
        while (<$file_handle>)
        {
            print image_out;
        }
        close image_out;
        print_success;
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
    my $dbquery = "INSERT INTO $TNAME_POSTS (title, published, author, content) VALUES ('$title', '$year-$month-$day', '$author', '$content')";
    my $dbq = $dbh->prepare($dbquery);
    $dbq->execute();
    
    my $dbstring = "SELECT id FROM $TNAME_POSTS WHERE title = '$title'";
    my $dbhandle = $dbh->prepare($dbstring);
    $dbhandle->execute();
    my (@results, $id);
    if ($dbhandle->rows == 0)
    {
        print_error("Ooops...","There was a problem adding the post to the database. Please try again later.");
        die "Content upload check failed, stopped";
    }
    else
    {
        $id = $dbhandle->fetchrow_array();    
    }
    if (defined($image_src) && defined($filehandle))
    {
        ## upload_image(filename, db_id, file_handle)
        upload_image($image_src, $id, $filehandle);
    } 
}

### END SUBS ###

my $query = CGI->new;
my $safe_chars = "a-zA-Z0-9.-_";
my ($session, $title, $date, $author, $content, $filename, $filehandle) = ($query->param('session'), $query->param('title'), time, $query->param('author'), $query->param('content'), $query->param('image_src'), $query->upload('image_src'));

if (authenticated($session) == 1 && defined($filehandle))
{
    if ($filename =~ /^[$safe_chars]+)$/)
    {
        print_error("Ooops...","The filename contained illegal characters, please rename it so it contains only [a-zA-Z._-] and try again");
        die "Could not add content, illegal filename. Stopped";
    }
    add_content($title, $date, $author, $content, $filename, $filehandle);
}   
elsif (authenticated($session) == 1 && !(defined($filehandle)))
{
    add_content($title, $date, $author, $content);    
}
elsif (autheticated($session) == 0)
{
    print_error("Ooops...","You are not logged in, please login...");
    die "Could not add content, session=$session is not authenticated. Stopped";
}
default
{
    print_error("Ooops...","Something went wrong, not sure what...");
    die "Default action triggered, stopped";
}
