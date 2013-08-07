#!/usr/bin/env perl

use strict;
use warnings;
use CGI;
use DBI();
use Digest::SHA qw(sha256_hex);
use Time::localtime;

### CONFIG ###

my $DBNAME='';
my $DBHOST='';
my $DBUNAME='';
my $DBPASS='';
my $TABLENAME='';

### END CONFIG ###

### subs ###
sub incorrect
{
    
    print <<"    Error";
    context: text/html
    
    <!DOCTYPE html>
    <html>
        <body>
            <script>
                xmlhttp.open("POST", "admin.cgi");
                xmlhttp.send("incorrect=1");
            </script>
        </body>
    </html>
    Error
}

sub throw_auth
{
    my $gen = 23;
    my $snonce = int(rand(10000))+1000;
    my $mod = 6551;
    my $s_result = ($gen ** $snonce) % $mod;
    my $session_ID = int(rand(10000))+10;
    
    open(dh_key_file, ">>dh_key_file.txt");
    print dh_key_file "ID=$session_ID  secret=$snonce mod=$mod";
    close dh_key_file;
    
    print <<'    DH';
    context: text/html;
    
    <!DOCTYPE html>
    <head>
        <title>Redirecting...</title>
        <script src="../js/crypto.js" type="application/x-javascript"></script>
    </head>
    <body>
        <script>
            DH_key_exchange($mod, $gen, $s_result, $session_ID)
        </script>
    </body>
    DH
}
### END subs ###

#Collect the client's results
my $query = CGI->new;
my $username = $query->param('uname');
my $client_result = $query->param('hash');
my $cnonce = $query->param('nonce');

#Collect the SHA256 hash from the DB
my $hash;
my @data;
my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1});
my $db_query = $dbh->prepare('SELECT hash FROM $TABLENAME WHERE user = ?');
$db_query->execute($username);
while (@data=$db_query->fetchrow_array())
{
    $hash = $data[0];
}
$db_query->close;
if ($db_query->rows == 0)
{
    $db_query->close;
    incorrect();
}

#Collect the server challange from the file
open(NONCE, 'server_challenge.txt');
my $snonce = $_;
close NONCE;

#Compute result of SHA256(SHA256(pass), cnonce, snonce) and compare
my $server_result = sha256_hex("$hash$cnonce$snonce");
if ($server_result == $client_result)
{
    #throw auth
}
else
{
    incorrect();
}
