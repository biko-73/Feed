#!/bin/bash

FEED="/etc/opkg/*.conf"
left=">>>>"
right="<<<<"
LINE1="---------------------------------------------------------"
LINE2="-------------------------------------------------------------------------------------"

echo "$LINE1"
echo "> Installing dependencies be patient ...
> it takes 2 to 15 minutes please wait..."
echo "$LINE1"
sleep 5s

echo "> start of process ..."
sleep 3s

# Check python
pyVersion=$(python -c"from sys import version_info; print(version_info[0])")

deps=("wget" "alsa-plugins" "alsa-utils" "alsa-utils-aplay" "astra-sm" "bzip2" "curl" "duktape" "dvbsnoop" "exteplayer3" "ffmpeg" "gstplayer" "libusb-1.0-0" "libxml2" "libxslt" "openvpn" "p7zip" "rtmpdump" "enigma2-plugin-systemplugins-serviceapp" "unrar" "zip" "xz")

if [ "$pyVersion" = 3 ]; then
  deps+=( "livestreamersrv" "python3-backports-lzma" "python3-beautifulsoup4" "python3-certifi" "python3-chardet" "python3-cfscrape" "python3-codecs" "python3-core" "python3-compression" "python3-cryptography" "python3-difflib" "python3-e2icjson" "python3-futures3" "python3-html" "python3-image" "python3-imaging" "python3-js2py" "python3-json" "python3-lxml" "python3-mmap" "python3-misc" "python3-mechanize" "python3-multiprocessing" "python3-ndg-httpsclient" "python3-netclient" "python3-pillow" "python3-pkgutil" "python3-pycurl" "python3-pycrypto" "python3-pydoc" "python3-pyexecjs" "python3-pyopenssl" "python3-pysocks" "python3-robotparser" "python3-requests" "python3-shell" "python3-sqlite3" "python3-six" "python3-treq" "python3-twisted-web" "python3-unixadmin" "python3-urllib3" "python3-xmlrpc" )

else
  
deps+=( "f4mdump" "hlsdl" "kodi-addon-pvr-iptvsimple" "python-lzma" "python-argparse" "python-beautifulsoup4" "python-certifi" "python-chardet" "python-codecs" "python-compression" "python-core" "python-pycurl" "python-cryptography" "python-difflib" "python-futures" "python-html" "python-image" "python-imaging" "python-json" "python-js2py" "python-lxml" "python-lzma" "python-mechanize" "python-multiprocessing" "python-misc" "python-mmap" "python-ndg-httpsclient" "python-netclient" "python-pycrypto" "python-pyexecjs" "python-pydoc" "python-pyopenssl" "python-requests" "python-robotparser" "python-six" "python-shell" "python-sqlite3" "python-pysocks" "python-subprocess" "python-twisted-web" "python-unixadmin" "python-urllib3" "python-xmlrpc" )
fi

if [ -f /etc/opkg/opkg.conf ]; then
  STATUS='/var/lib/opkg/status'
  OSTYPE='Opensource'
  OPKG='opkg update'
  OPKGINSTAL='opkg install'
elif [ -f /etc/apt/apt.conf ]; then
  STATUS='/var/lib/dpkg/status'
  OSTYPE='DreamOS'
  OPKG='apt-get update'
  OPKGINSTAL='apt-get install -y'
fi

install() {
  if ! grep -qs "Package: $1" "$STATUS"; then
    $OPKG >/dev/null 2>&1
    rm -rf /run/opkg.lock
    echo -e "> Need to install ${left} $1 ${right} please wait..."
    echo "$LINE2"
    sleep 0.8
    echo
    if [ "$OSTYPE" = "Opensource" ]; then
      $OPKGINSTAL "$1"
      sleep 1
      clear
    elif [ "$OSTYPE" = "DreamOS" ]; then
      $OPKGINSTAL "$1" -y
      sleep 1
      clear
    fi
  fi
}

for i in "${deps[@]}"; do
  install "$i"
done

rm -rf /var/cache/opkg/*
rm -rf /var/lib/opkg/lists/*
rm -rf /run/opkg.lock
echo "> cache is cleaned...
updating feeds please wait..."
sleep 3s

opkg update

echo "> end of process...
> your box will reboot now..."
sleep 3s 

reboot

exit 0