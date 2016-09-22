#!/usr/bin/perl

use strict;
use warnings;
use File::Basename;

my @files = ("/tmp/rsync-photos.log", "/tmp/rsync-videos.log");

my %allfilehash = ();
my %backupfilehash = ();
my %deletedhash = ();

for my $i (0 .. $#files) {
  my $f = $files[$i];
  print STDERR "$files[$i]\n";
  
  open(my $fh, '<:encoding(UTF-8)', $f)
    or die "Could not open file '$f' $!";
  
  while (my $row = <$fh>) {
    chomp $row;
    
    # first file builds the all list

    if ($i == 0) {
      if ($row =~ m/hiding file (.*) because of pattern (.*)/) {
        if ($allfilehash{$1}) {
          die "File $1 detected twice! hiding $f";
        }
        $allfilehash{$1} = $f;
      }
      if ($row =~ m/showing file (.*) because of pattern (.*)/) {
        if ($allfilehash{$1}) {
          die "File $1 detected twice! showing $f";
        }
        $allfilehash{$1} = $f;
      }
    }
    
    # remaining files populate backup
    
    if ($row =~ m/risking file (.*) because of pattern (.*)/)
    {
      if ($backupfilehash{$f}) {
        print "File risked multiple times! $1 $f";
      }
      
      $backupfilehash{$1} = $f;
      #print "$1 $2\n";
    }
  }
}


# see which files have been backed up and remove from the all list
foreach (sort keys %backupfilehash) {
  my $f = $_;
  if (exists($allfilehash{$f})) {
    delete $allfilehash{$f};
    $deletedhash{$f} = 1;
  } elsif (!exists($deletedhash{$f})) {
    die "File $f was not detected in all!";
  }
}

# remaining files have not been backed up

my %extensions = ();

foreach my $f (sort keys %allfilehash) {
  my $fn = basename($f);
  if ($fn =~ m/^.*(\..*)$/) {
    if (!exists($extensions{$1})) {
      $extensions{$1} = 1;
    } else {
      $extensions{$1} = $extensions{$1} + 1;
    }
  }
}

foreach my $e (sort {$extensions{$b} <=> $extensions{$a}} keys %extensions) {
  print "$extensions{$e} $e\n";
}
