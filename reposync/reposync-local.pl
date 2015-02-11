#!/usr/bin/perl
# Utilities for maintaining a number of repositories locally
# - incrementally updating packages as they become available

use strict;
use warnings;

use Getopt::Long;

Getopt::Long::Configure('bundling');

sub show_usage(;$) {
  my $exit_code = shift;

  print "reposync-local [-h]\n";
  print "  -h\tShow help\n";

  if (defined($exit_code)) {
    exit($exit_code);
  }
}

my %args;

if (!GetOptions('help|h' => \$args{help})) {
  show_usage(1);
}

if ($args{help}) {
  show_usage(0);
}

print "reposync-local\n";

