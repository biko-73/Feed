#!/bin/sh

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/DD_RSS ]; then
echo "> removing package please wait..."
sleep 3s 
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/DD_RSS > /dev/null 2>&1

status='/var/lib/opkg/status'
package='enigma2-plugin-extensions-DD_RSS'

if grep -q $package $status; then
opkg remove $package
fi

echo "************************************"
echo "*          Uninstall DD_RSS        *"
echo "************************************"
sleep 3s

rm -rf /usr/lib/enigma2/python/Plugins/Extensions/DD_RSS > /dev/null 2>&1

#config
plugin=DD_RSS
version=0.4
url=https://github.com/Belfagor2005/DDRSSReader/raw/main/$plugin-$version.tar.gz

package=/var/volatile/tmp/$plugin-$version.tar.gz

#download & install
echo "> Downloading $plugin-$version package  please wait ..."
sleep 3s

wget -O $package --no-check-certificate $url
tar -xzf $package -C /
extract=$?
rm -rf $package >/dev/null 2>&1

echo ''
if [ $extract -eq 0 ]; then
echo "> $plugin-$version package installed successfully"
echo "> Uploaded By ElieSat"
sleep 3s

else

echo "> $plugin-$version package installation failed"
sleep 3s
fi

fi
exit 0
