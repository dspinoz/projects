#!/usr/bin/perl
# Submit memory usage
# See proc(5), /proc/meminfo for more details 

use strict;
use warnings;

use Sys::Hostname;

use cube_emitter;

my @lines = cube_emitter::get_lines('/proc/meminfo');

my %mem;
$mem{host} = hostname;

foreach my $line (@lines)
{
  if ($line =~ m/^(.*):\s+(.*) kB$/)
  {
    $mem{$1} = $2 *1;
  }
}

my @events;
push @events, {type=>'loadavg', data=>\%mem};

cube_emitter::submit(\@events);
