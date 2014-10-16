#!/usr/bin/perl
# Submit memory usage
# See proc(5), /proc/net/dev for more details 

use strict;
use warnings;

use Sys::Hostname;

use cube_emitter;

my @lines = cube_emitter::get_lines('/proc/net/dev');

my %net;
$net{host} = hostname;

if (scalar(@lines) >= 2)
{
  my @first = split(/\|/, shift(@lines));
  shift(@first); #Interface column
  @first = grep(/\S/, @first);
  foreach my $f (@first)
  {
    #print "f $f\n";
  }
  
  my @hdr = split(/\|/, shift(@lines));
  shift(@hdr); #Interface column
  @hdr = grep(/\S/, @hdr);
  foreach my $f (@hdr)
  {
    #print "h $f\n";
  }
  
  # assign groups and columns to indexes
  if (scalar(@hdr) != scalar(@first))
  {
    print STDERR "Invalid columns in headers\n";
  }
  
  my @column_defs;
  
  for(my $i = 0; $i < scalar(@first); $i++)
  {
    my $type = $first[$i];
    $type =~ s/^\s+|\s+$//g;
    my @cols = split(/:|\s+/,$hdr[$i]);
    
    foreach my $c (@cols)
    {
      #print "c $type $c\n";
      push @column_defs, "$type,$c";
    }
  }
  
  foreach my $line (@lines)
  {
    my @info = split(/:|\s+/, $line);
    @info = grep(/\S/, @info);
    
    my $interface = shift(@info);
    
    if (scalar(@column_defs) != scalar(@info))
    {
      print STDERR "Invalid column defs\n";
      next;
    }
    
    for(my $i = 0; $i < scalar(@info); $i++)
    {
      my @c = split(/,/, $column_defs[$i]);
      
      #print "i $interface @c $info[$i]\n";
      $net{$interface}{$c[0]}{$c[1]} = $info[$i] *1; #number
    }
  }
}

my @events;
push @events, {type=>'loadavg', data=>\%net};

cube_emitter::submit(\@events);
