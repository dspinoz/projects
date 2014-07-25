#!/bin/bash -x

ROOT=/var/root1
ROOTUSER=user1
ROOTUID=6001
ROOTGROUP=rooted
ROOTGID=6000
ROOTPW=password
YUMREPO=/rheldvd
HASSUDO=1
AUTOSSH=1

sestatus | grep enabled
if [ $? -eq 0 ]
then
  echo "Does not yet work with selinux."
  echo "To disable, edit /etc/sysconfig/selinux and set to disabled"
  exit 1
fi

mkdir -p $ROOT

yum --installroot=$ROOT groupinstall core

getent group $ROOTGID
if [ $? -ne 0 ]
then
  groupadd --gid $ROOTGID $ROOTGROUP
  echo -e "Match Group $ROOTGROUP\n  ChrootDirectory $ROOT" >> /etc/ssh/sshd_config
  service sshd restart
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

mount --bind /proc $ROOT/proc
mount --bind /dev $ROOT/dev

if [ -d $YUMREPO ]
then
  mkdir -p $ROOT/$YUMREPO
  mount --bind $YUMREPO $ROOT/$YUMREPO
  cat > $ROOT/etc/yum.repos.d/a.repo <<EOF
[repo]
name=REPO
baseurl=file://$YUMREPO
enabled=1
gpgcheck=0
EOF
fi






