#!/usr/bin/env perl

use strict;
use warnings;
use CGI;
use DBI();
use Digest::SHA qw(sha256_hex);

### CONFIG ###

my $DBNAME='';
my $DBHOST='';
my $DBUNAME='';
my $DBPASS='';
my $TABLENAME='';

### END CONFIG ###

### Errors ###
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
### END ERRORS ###

#Collect the client's results
my $query = CGI->new;
my $username = $query->param('uname');
my $client_result = $query->param('hash');
my $cnonce = $query->param('nonce');

#Collect the SHA256 hash from the DB
my $hash;
my @data;
my $dbh = DBI->connect("DBI:mysql:database=$DBNAME;host=$DBHOST", $DBUNAME , $DBPASS, {'RaiseError' => 1}); #change to webserver DB credentials
my $db_query = $dbh->prepare('SELECT hash FROM $TABLENAME WHERE user = ?');
$db_query->execute($username);
while (@data=$db_query->fetchrow_array())
{
    $hash = $data[0];
}
if ($db_query->rows == 0)
{
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