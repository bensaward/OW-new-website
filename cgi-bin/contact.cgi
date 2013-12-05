#!/usr/bin/env perl

use warnings;
use strict;
use CGI::Carp;
use CGI;
use File::Basename;

###################################################################################################
# The request comes in the form $url?data=$request ## mysql table for contacts:                   #
#                                                  ##                                             #
# Where $request can be:                           ## create table $DB_TABLE(                     #
# - committee                                      ##       id int not null auto_increment,       #
#       this fetches basic info on all committee   ##       name varchar(100) not null,           #
#       members and image location                 ##       position varchar(100) not null,       #
#                                                  ##       committee bool not null,              #
# - $position (eg: president, captain, etc)        ##       college_capt bool not null,           #
#       retuns more info on a certain position     ##       email varchar(100) not null,          #
#       eg roles in the club, small personal       ##       statement varchar(300),               #
#       statement, etc.                            ##       role_info varchar(300),               #
#                                                  ##       image_file varchar(50),               #
# - college                                        ##       college varchar(50),                  #
#       returns the basic info (email and names)   ##       primary key(id),                      #
#       of the college captains                    ##       );                                    #
###################################################################################################

####################################################
###                 CONFIG                       ###

my $DB_UNAME ="";
my $DB_PASS ="";
my $DB_TABLE="";
my $DB_NAME = "";
my $DB_HOST ="";

###               END CONFIG                    ####
####################################################

my $q=CGI->new;
my $request = $q->param("data");
my $dbh = DBI->connect("DBI:mysql:database=$DB_NAME;host=$DB_HOST", $DB_UNAME , $DB_PASS, {'RaiseError' => 1}) or die "Couldn't connect to the database, stopped";
print $q->header(-type=>"text/plain",);

sub print_committee
{
    my (@name, @position, @email, @image_file, $i);
    my $db_query_string = "SELECT * FROM $DB_TABLE WHERE committee != 0";
    my $db_query = $dbh->prepare($db_query_string);
    $db_query->execute();
    $i=0;
    while ($db_query->fetchrow_array())
    {
        ($name[$i],$position[$i],$email[$i],$image_file[$i])=@_[1,2,5,8];
        $i++;
    }
    
    my $a = 0;
    while ($a < $i)
    {
        if ($image_file[$i] == "")
        {
            $image_file[$i] = "NULL";
        }
    }
    $a=0;
    my $ret_string = $i+1;
    while ($a < $i)
    {
        $ret_string = "::$ret_string::$name[$i]::$position[$i]::$email[$i]::$image_file[$i]"
    }
    print $ret_string;
}

sub print_position ## eg print_position
{
    my $position = $_[0];
    my $dbq_string = "SELECT * FROM $DB_TABLE WHERE position = '$position'";
    my $dbq = $dbh->prepare($dbq_string);
    my ($name, $committee, $college_captain, $email, $statement, $role_info, $image_file, $college);
    $dbq->execute();
    if ($dbq->rows == 0)
    {
        print "NULL::";
    }
    
    else
    {
        ($name, $committee, $college_captain, $email, $statement, $role_info, $image_file, $college) = ($dbq->fetchrow_array)[1,3,4,5,6,7,8,9];
        print "1::$name::$position::$committee::$college_captain::$email::$statement::$role_info::$image_file::$college"
    }
}