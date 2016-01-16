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

# Get the source for the build from git
# Note that git archive doesn't work with relative paths and does something
# odd with shell expansion - so we move up to the base dir to run the cmd
cd ..
git archive master | bzip2 > $TARBZ2
cp $TARBZ2 package/
cd package
echo -n "."
echo "done"

# Create the source build dir
mkdir $SOURCE_DIR
tar -xvf $TARBZ2 -C $SOURCE_DIR

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
