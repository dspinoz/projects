#!/usr/bin/perl
# Submit machine load average to cube
# See proc(5), /proc/loadavg and /proc/cpuinfo for more details 

use strict;
use warnings;

use Sys::Hostname;

use cube_emitter;

my @lines = cube_emitter::get_lines('/proc/loadavg');
my @cpu = cube_emitter::get_lines('/proc/cpuinfo');

my %loadavg;
$loadavg{host} = hostname;
$loadavg{num_cpus} = grep(/processor\s+:/, @cpu);

if (scalar(@lines) == 1)
{
  my @tok = split(/\s+/, $lines[0]);
  if (scalar(@tok) == 5)
  {
    $loadavg{low} = $tok[0] *1; #convert to number
    $loadavg{mid} = $tok[1] *1;
    $loadavg{high} = $tok[2] *1;
    $loadavg{last_pid} = $tok[4] *1; #number
    
    @tok = split('/', $tok[3]);
    if (scalar(@tok) == 2)
    {
      $loadavg{kernel}{executing} = $tok[0] *1; #number 
      $loadavg{kernel}{total} = $tok[1] *1; #number
    }
    
  }
}

my @events;
push @events, {type=>'loadavg', data=>\%loadavg};

cube_emitter::submit(\@events);
