#!/bin/bash
VERSION=`cat ../VERSION`
SOURCE_DIR=snapfly-$VERSION
TARBZ2=$SOURCE_DIR.tar.bz2
ORIGTBZ=$SOURCE_DIR.orig.tar.bz2
DEBPKG=$SOURCE_DIR.deb
echo $SOURCE_DIR
if test -d $SOURCE_DIR; then
	sudo rm -r $SOURCE_DIR
fi
if test -x $TARBZ2; then
	sudo rm $TARBZ2
fi
echo -n "creating $TARBZ2 "
svn export .. $SOURCE_DIR > /dev/null
tar -cjf $TARBZ2 $SOURCE_DIR
echo -n "."
echo "done"
echo -n "creating debian package "
ln -s $TARBZ2 $ORIGTBZ
cd $SOURCE_DIR
sudo rm -rf debian
cp -Rf ../debian .
echo -n '.'
sudo dpkg-buildpackage -rfakeroot 2> /dev/null > /dev/null

cd ..
echo -n "...."
echo "done"

sudo rm -rf $SOURCE_DIR $ORIGTBZ *.tar.gz
WHOAMI=`whoami`
chown -Rf $WHOAMI .

exit
