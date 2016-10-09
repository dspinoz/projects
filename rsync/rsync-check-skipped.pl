#!/usr/bin/perl

use strict;
use warnings;
use File::Basename;
use Getopt::Long;
use Pod::Usage;

my $man = 0;
my $help = 0;
my @files = ();
my @opt_ignore_ext = ();
my $show_skipped = 0;

GetOptions('help|?' => \$help, 
           man => \$man, 
           'i|ignore-extension=s' => \@opt_ignore_ext,
           's|show-skipped' => \$show_skipped,
           'f|file=s' => \@files) or pod2usage(2);
pod2usage(1) if $help;
pod2usage(-exitval => 0, -verbose => 2) if $man;

foreach my $f (@files) {
  print "INFO: Processing rsync log $f\n";
}
if (scalar(@opt_ignore_ext)) {
	foreach my $ig (@opt_ignore_ext) {
    print "INFO: Ignoring extension $ig\n";
  }
}

my %allfilehash = ();
my %backupfilehash = ();
my %deletedhash = ();

for my $i (0 .. $#files) {
  my $f = $files[$i];
  print "INFO: Processing file $f\n";
  
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
  if ($fn =~ m/^.*\.(.*)$/) {
    if (!exists($extensions{$1})) {
      $extensions{$1} = 1;
    } else {
      $extensions{$1} = $extensions{$1} + 1;
    }
  }
}

my $haserr = 0;

foreach my $e (sort {$extensions{$b} <=> $extensions{$a}} keys %extensions) {
  
  my $ignored = 0;
  
  foreach my $ignore (@opt_ignore_ext) {
    if ($e =~ m/$ignore/) {
      $ignored = 1;
    }
  }
  
  if ($ignored) {
    print "DEBUG: Ignored extension: $e ($extensions{$e} matches)\n";
    next;
  }
  
  print "ERROR: Files with .$e not in backup ($extensions{$e} matches)\n";
  $haserr = 1;
  
  if ($show_skipped) {
    foreach my $f (sort keys %allfilehash) {
      my $fn = basename($f);
      if ($fn =~ m/^.*\.(.*)$/) {
        
        if ($1 =~ m/$e/) {
          print "INFO: $f\n";
        }
      }
    }
  }
}

exit $haserr;

__END__

=head1 NAME

rsync-check-skipped

=head1 SYNOPSIS

rsync-check-skipped.pl [options] [file ...]

 Options:
   --help                     Brief help message
   -s, --show-skipped         Show files that have been skipped in backups
   -i, --ignore-extension=ext Ignore files with extension ext that have 
                              been skipped

=head1 DESCRIPTION

Read multiple rsync log files to determine those files that have not 
been transferred.

=cut
