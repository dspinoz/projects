#!/usr/bin/perl
# Submit machine load average to cube
# See proc(5) and /proc/loadavg for more details 
# TBD Module for common code

use strict;
use warnings;

use Sys::Hostname;
use LWP::UserAgent;
use HTTP::Request;
use JSON;

open my $fd, '<', '/proc/loadavg';
chomp(my @lines = <$fd>);
close $fd;

my %loadavg;
$loadavg{host} = hostname;

if (scalar(@lines) == 1)
{
  my @tok = split(/\s+/, $lines[0]);
  if (scalar(@tok) == 5)
  {
    $loadavg{low} = $tok[0] *1; #convert to number
    $loadavg{mid} = $tok[1] *1;
    $loadavg{high} = $tok[2] *1;
    
    my @tok2 = split('/', $tok[3]);
    if (scalar(@tok2) == 2)
    {
      $loadavg{kernel}{executing} = $tok2[0] *1; #number 
      $loadavg{kernel}{total} = $tok2[1] *1; #number
    }
    
    $loadavg{last_pid} = $tok[4] *1; #number
  }
}

my @events;
push @events, {type=>'loadavg', data=>\%loadavg};

print to_json(\@events, {pretty => 1})."\n";

my $req = HTTP::Request->new('POST', "http://localhost:1080/1.0/event/put");
$req->header("Content-type" => "application/json");
$req->content(to_json(\@events));

my $www = LWP::UserAgent->new;
my $res = $www->request($req);

if ($res->is_success)
{
  print "OK\n";
}
else
{
  die $res->status_line;
}
