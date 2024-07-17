#!/bin/bash

device=$(head -n 1 /etc/hostname)
image='openatv'
version='6.4'

#check image name
imgnm=$(curl -s "http://images.mynonpublic.com/openatv/6.4/index.php?open=$device" | grep -o "$device/.*\.zip" | tail -n 1 | sed "s/$device\///" | cut -d '>' -f1 | tr -d "'" )

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

wget -O $ms/images/$imgnm http://images.mynonpublic.com/openatv/6.4/current.php?open=$device

for dir in "/media/hdd/ImagesUpload/" "/media/hdd/open-multiboot-upload/" "/media/hdd/OPDBootUpload/" "/media/hdd/EgamiBootUpload/"
do
echo ""
if [ -d $dir ] ; then
cp $ms/images/$imgnm $dir >/dev/null 2>&1
fi
done

echo '> Download '$image'-'$version' to '$ms'/images finished 
> Biko_73 upload... '
sleep 3s 
fi
exit 0