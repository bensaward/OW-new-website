#!/usr/bin/env perl

use strict;
use warnings;
use CGI;
use Crypt::CBC;
use Crypt::OpenSSL::AES; #http://search.cpan.org/~ttar/Crypt-OpenSSL-AES-0.01/lib/Crypt/OpenSSL/AES.pm
use Digest::SHA;

my $q = CGI->new;
my $c_result = $q->param('client_result');
my $session_ID = $q->param('session_ID');
my @fragments;
my $secret;
my $mod;

open(dh_key_file, ">>dh_key_file.txt");
while (<dh_key_file>)
{
    if ($_ =~ /ID=$session_ID/)
    {
        @fragments = split(/ +/, /=/);
        if ($fragments[2] =~ /secret/)
        {
            $secret = $fragments[3];
        }
        if ($fragments[4] =~ /mod/)
        {
            $mod = $fragments[5];
        }
    }
}

my $shared_secret = ($c_result ** $secret) % $mod;

my $auth_key = int(rand(100000))+1000;
my $crypt_key = sha256_hex("$shared_secret");
my $iv = sha1(int(rand(100000)));

open(key_hive, '>>keyhive.txt'); ## ensure this cannot be read by the public or any attacker
print key_hive "ID=$session_ID auth_key=$auth_key crypt_key=$shared_secret";
close key_hive;

my $aes = Crypt::CBC->new
(
    -key => $crypt_key,
    -cipher => "Crypt::OpenSSL::AES",
    -padding => 'null',
    -iv => $iv
);

$aes->start('encrypting');
my $encryped = $aes->crypt("$auth_key");
$encrypted = $aes->finish();