#!/bin/bash

#configuration
#########################################
device=$(head -n 1 /etc/hostname)
image='openblackhole'
version='5.5.1'
url=https://images.openbh.net/latest/$version/$device
today=$(date +%Y%m%d)

case $device in
pulse4k|pulse4kmini)
brand=abcom;;
osmini4k|osmio4kplus)
brand=edision;;
gbip4k|gbquad4k|gbtrio4k|gbtri4kpro|gbue4k)
brand=gigablue;;
novaler4kpro)
brand=novaler;;
sf8008|sfx6008|sx88v2|sx988)
brand=octagon;;
dual)
brand=qviart;;
ustym4kpro)
brand=uclan;;
vuduo2|vuduo4k|vuduo4kse|vusolo2|vusolo4kse|vusolo4k|vuultimo|vuultimo4k|vuuno4k|vuuno4kse|vuzero|vuzero4k)
brand=vuplus;;
zgemmah7|zgemmah11s|zgemmah82h|zgemmah9twinse|h7)
brand=zgemma;; 
*) echo "> your device is not supported"
exit 1
esac

#detetmine image name
#########################################
imgnm=$(curl -s  "https://images.openbh.net/?b=$version%2F$brand%2F$device" | grep -o 'href="[^"]*\.zip"' | awk -F'"' '{print $2}'| sed 's/^.*openbh/openbh/' | sed '/recovery/d')
echo "> "$imgnm" image found ..."
sleep 5

#check mounted storage
#########################################
for ms in "/media/hdd" "/media/usb" "/media/mmc"
do
    if mount|grep $ms >/dev/null 2>&1; then
    echo "> Mounted storage found at: $ms"
    mkdir "$ms"/images >/dev/null 2>&1
    break
    fi
done

if [ -z "$ms" ]; then
echo "> Mount your external memory and try again"
exit 1
fi
sleep 3

#download image to mounted storage
#########################################
echo "> Downloading "$image"-"$version" image to "$ms"/images please wait..."
sleep 3

if wget -q --method=HEAD $url;
 then
wget --show-progress -qO $ms/images/$imgnm $url
else
echo "> check your internet connection and try again or your device is not supported..."
exit 1
fi

echo "> Download of "$image"-"$version" image to "$ms"/images is finished"
sleep 3

#copy image to multiboot upload folders
#########################################
for dir in "/media/hdd/ImagesUpload/" "/media/hdd/open-multiboot-upload/" "/media/hdd/OPDBootUpload/" "/media/hdd/EgamiBootUpload/"
do
if [ -d $dir ] ; then
echo "> "$dir" folder found ..."
sleep 1
echo "> copying image to "$dir" folder please wait ..."
sleep 1
cp $ms/images/$imgnm $dir >/dev/null 2>&1
fi
done

echo "> enjoy..."
