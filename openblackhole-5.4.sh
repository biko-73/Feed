#!/bin/bash

# ***************************************************************************************************************
# wget -q "--no-check-certificate" https://github.com/biko-73/Feed/raw/main/openblackhole-5.4.sh -O - | /bin/sh
# ***************************************************************************************************************

device=$(head -n 1 /etc/hostname)
image='openblackhole'
version='5.4'
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

#check mounted storage
msp=("/media/hdd" "/media/usb" "/media/usb")

for ms in "${msp[@]}"; do
if [ -d "$ms" ]; then
echo ""
break
fi
done

if [ -z "$ms" ]; then
echo "> Mount your external memory and try again"
exit 1
else

#check images path
if [ -d $ms/images ]; then
echo ""
else
echo ""
mkdir $ms/images
fi


echo '> Downloading '$image'-'$version' image to '$ms'/images please wait...'
sleep 7s
imgnm=$(curl -s  "https://images.openbh.net/?b=5.4%2F$brand%2F$device" | grep -o 'href="[^"]*\.zip"' | awk -F'"' '{print $2}'| sed 's/^.*openbh/openbh/' | sed '/recovery/d')

url=https://images.openbh.net/latest/5.4/$device

wget -O $ms/images/$imgnm $url
download=$?

for dir in "/media/hdd/ImagesUpload/" "/media/hdd/open-multiboot-upload/" "/media/hdd/OPDBootUpload/" "/media/hdd/EgamiBootUpload/"
do
echo ""
if [ -d $dir ] ; then
cp $ms/images/$imgnm $dir >/dev/null 2>&1
fi
done

fi
echo ''
if [ $download -eq 0 ]; then
echo ""
else
wget -O $ms/images/openbh-5.4-$device-"$today"_multi.zip $url
fi
echo '> Download '$image'-'$version' to '$ms'/images finished 
> Biko_73 upload... '
sleep 3s 
exit 0
