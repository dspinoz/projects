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

my $disable_submit = 0;
my $disable_print = 0;

sub get_lines($)
{
  my $file = shift;
  open my $fd, '<', $file;
  chomp(my @lines = <$fd>);
  close $fd;
  
  return @lines;
}

sub disable_submit()
{
  $disable_submit = 1;
}
sub disable_print()
{
  $disable_print = 1;
}

sub submit($)
{
  my $ref = shift;
  
  # TBD verbose mode
  if ($disable_print)
  {
    print "Print disabled\n";
    return 1;
  }
  
  print JSON::to_json($ref, {pretty => 1})."\n";

  if ($disable_submit)
  {
    print "Submit disabled\n";
    return 1;
  }

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
