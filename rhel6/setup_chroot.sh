#!/bin/bash
# easily create a chroot environment

ROOT=
ROOTUSER=user1
ROOTUID=6001
ROOTGROUP=rooted
ROOTGID=6000
ROOTPW=password
YUMREPO=/media/rheldvd
HASSUDO=0
AUTOSSH=0

usage()
{
  echo "$0 [-u `tput smul`username`tput rmul`] [-U `tput smul`uid`tput rmul`] [-g `tput smul`group`tput rmul`] [-G `tput smul`gid`tput rmul`] [-p `tput smul`password`tput rmul`] [-K] [-S] -r `tput smul`path`tput rmul`"
  echo -e "  -r path\tlocation of the chroot"
  echo -e "  -u username\tName of the user account accessing the chroot"
  echo -e "  -U uid\tUID for `tput smul`username`tput rmul`"
  echo -e "  -g group\tName of the primary group for `tput smul`username`tput rmul`"
  echo -e "  -G gid\tGID for `tput smul`group`tput rmul`"
  echo -e "  -p password\t`tput smul`username`tput rmul`'s login password"
  echo -e "  -y yumrepo\tPath to yum repository to use when building the chroot"
  echo -e "  -K\t\tSetup ssh keys for automatic access from account $USER"
  echo -e "  -S\t\tGive `tput smul`username`tput rmul` sudo access within the chroot"
  exit 1
}

while getopts "hr:u:g:U:G:p:y:KS" opt; do
  case $opt in
    h) usage;;
    r) ROOT=$OPTARG;;
    u) ROOTUSER=$OPTARG;;
    U) ROOTUID=$OPTARG;;
    g) ROOTGROUP=$OPTARG;;
    G) ROOTGID=$OPTARG;;
    p) ROOTPW=$OPTARG;;
    y) YUMREPO=$OPTARG;;
    K) AUTOSSH=1;;
    S) HASSUDO=1;;
    *) usage;;
  esac
done

if [[ $OPTIND -eq 1 || -z "$ROOT" ]]
then
  echo "Must specify a chroot"
  usage
fi

echo "New chroot at $ROOT"
echo "User $ROOTUSER ($ROOTUID)"
echo "Group $ROOTGROUP ($ROOTGID)"
echo "Password \"$ROOTPW\""
if [ $AUTOSSH -eq 1 ]
then
  echo "Auto login supported from $USER account"
fi
if [ $HASSUDO -eq 1 ]
then
  echo "$ROOTUSER will be a sudoer under the chroot"
fi

set -x

sestatus | grep enabled
if [ $? -eq 0 ]
then
  echo "Does not yet work with selinux."
  echo "To disable, edit /etc/sysconfig/selinux and set to disabled"
  exit 1
fi
mkdir -p $ROOT

yumargs=""
yumrepofile=`mktemp`

# Create repo file
if [ -d $YUMREPO ]
then
  cat > $yumrepofile <<EOF
[repo]
name=REPO
baseurl=file://$YUMREPO
enabled=1
gpgcheck=0
EOF
  yumargs="--config=$yumrepofile"
fi

yum $yumargs --installroot=$ROOT groupinstall core

getent group $ROOTGID
if [ $? -ne 0 ]
then
  groupadd --gid $ROOTGID $ROOTGROUP
  echo -e "Match Group $ROOTGROUP\n  ChrootDirectory $ROOT" >> /etc/ssh/sshd_config

  if [ -z "`which systemctl`" ]
  then
    service sshd restart
  else
    systemctl restart sshd
  fi
fi

getent passwd $ROOTUID
if [ $? -ne 0 ]
then
  useradd --create-home --gid $ROOTGID --uid $ROOTUID $ROOTUSER
  echo $ROOTPW | passwd --stdin $ROOTUSER
fi

chroot $ROOT groupadd --gid $ROOTGID $ROOTGROUP
chroot $ROOT useradd --create-home --gid $ROOTGID --uid $ROOTUID $ROOTUSER
echo $ROOTPW | chroot $ROOT passwd --stdin $ROOTUSER

if [ $AUTOSSH -eq 1 ]
then
  if [[ ! -f $HOME/.ssh/id_rsa || ! -f $HOME/.ssh/id_rsa.pub ]]
  then
    ssh-keygen -t rsa -N "" -f $HOME/.ssh/id_rsa
  fi

  mkdir -p /home/$ROOTUSER/.ssh $ROOT/home/$ROOTUSER/.ssh
  chmod 0700 /home/$ROOTUSER/.ssh $ROOT/home/$ROOTUSER/.ssh
  cp $HOME/.ssh/id_rsa.pub /home/$ROOTUSER/.ssh/authorized_keys
  cp $HOME/.ssh/id_rsa.pub $ROOT/home/$ROOTUSER/.ssh/authorized_keys 
  chown -R $ROOTUSER:$ROOTGROUP /home/$ROOTUSER/.ssh $ROOT/home/$ROOTUSER/.ssh
fi


if [ $HASSUDO -eq 1 ]
then
  cat > $ROOT/etc/sudoers.d/$ROOTUSER <<EOF
$ROOTUSER	ALL=(ALL) 	ALL
EOF
  chmod 0440 $ROOT/etc/sudoers.d/$ROOTUSER
fi

# TODO add to fstab - persist after reboot
mount --bind /proc $ROOT/proc
mount --bind /dev $ROOT/dev

if [ -d $YUMREPO ]
then
  mkdir -p $ROOT/$YUMREPO
  mount --bind $YUMREPO $ROOT/$YUMREPO
  cat $yumrepofile > $ROOT/etc/yum.repos.d/media.repo
fi

rm $yumrepofile

dir=$ROOT
err=0

while [ -d $dir ]
do
  if [[ ! -O $dir && -G $dir ]]
  then
    echo "Directory $dir not owned by $USER"
    err=1
    break
  fi

  stat -c %A $dir | egrep -q 'd.......w.'
  if [ $? -eq 0 ]
  then
    echo "Directory $dir is writable by others! Permissions `stat -c %A $dir`"
    err=1
    break
  fi

  if [ $dir == "/" ]
  then
    break
  fi

  dir=`dirname $dir`

done

if [ $err -eq 1 ]
then
  echo "Bad permissions to chroot $ROOT. Will not be able to ssh"
fi

