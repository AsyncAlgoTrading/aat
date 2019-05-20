#!/bin/bash
VERSION=`git log --tags --decorate --simplify-by-decoration | grep ^commit|grep tag|sed -e 's/^.*: //' -e 's/)$//' -e 's/,.*$//' | head -n1 | cut -c2-`
if [ -z $1 ]; then
    echo "Bumping micro"
    VERSION=`python3 -c "version='$VERSION'.split('.'); version[2] = str(int(version[2]) + 1); print('.'.join(version));"`
    echo $VERSION

elif [ $1 = "MICRO" ]; then
    echo "Bumping micro"
    VERSION=`python3 -c "version='$VERSION'.split('.'); version[2] = str(int(version[2]) + 1); print('.'.join(version));"`

elif [ $1 = "MINOR" ]; then
    echo "Bumping minor"
    VERSION=`python3 -c "version='$VERSION'.split('.'); version[1] = str(int(version[1]) + 1); version[2] = '0'; print('.'.join(version));"`

elif [ $1 = "MAJOR" ]; then
    echo "Bumping major"
    VERSION=`python3 -c "version='$VERSION'.split('.'); version[0] = str(int(version[0]) + 1); version[2] = '0'; version[1] = '0'; print('.'.join(version));"`
fi

python3 scripts/deploy.py  --repourl https://github.com/timkpaine/aat --version $VERSION
