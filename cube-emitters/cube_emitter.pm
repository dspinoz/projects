#!/usr/bin/perl

use strict;
use warnings;

use JSON;
use LWP::UserAgent;
use HTTP::Request;

package cube_emitter;

use constant {
   CUBE_HOST => "localhost",
   CUBE_PORT => 1080
};

sub get_lines($)
{
  my $file = shift;
  open my $fd, '<', $file;
  chomp(my @lines = <$fd>);
  close $fd;
  
  return @lines;
}

sub submit($)
{
  my $ref = shift;
  
  # TBD verbose mode
  print JSON::to_json($ref, {pretty => 1})."\n";

  my $req = HTTP::Request->new('POST', "http://".CUBE_HOST.":".CUBE_PORT."/1.0/event/put");
  $req->header("Content-type" => "application/json");
  $req->content(JSON::to_json($ref));

  my $www = LWP::UserAgent->new;
  my $res = $www->request($req);

  if ($res->is_success)
  {
    print "OK\n";
    return 1;
  }
  else
  {
    die $res->status_line;
  }
}

1;
