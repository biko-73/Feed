#!/bin/bash

#determine device brand
#determine device & image name 
device=$(head -n 1 /etc/hostname)
image='pure'
version='7.4'

case $device in
zgemmah7|zgemmah9combo|zgemmah9sse|zgemmah9twin|zgemmah11s|h7)
brand='airdigital';;
viper4k|viper4kv20|viper4kv30|viper4kv40)
brand='amiko';;
anadol4k)
brand='anadol';;
ax51|ax61)
brand='ax';;
axashis4kcomboplus)
brand='axas';;
dinobot4kplus)
brand='dinobot';;
dm920|dm900)
brand='dreambox';;
osmini4k|osmio4k|osmio4kplus)
brand='edision';;
gbquad4k|gbtrio4k|gbtrio4kpro|gbue4k)
brand='gigablue';;
hitube4k)
brand='hitube';;
mutant66se)
brand='mutant';;
novaler4k|novaler4kse|novaler4kpro)
brand='novaler';;
sf4008|sf8008|sf8008m)
brand='octagon';;
dual)
brand='qviart';;
ustym4kpro)
brand='uclan';;
vuduo4k|vuduo4kse|vusolo4k|vusolo4kse|vuultimo4k|vuuno4k|vuuno4kse|vuzero4k)
brand='vuplus';;
*) echo "> your device is not supported "
exit 1 ;;
esac

imgnm=$(curl -s "https://www.pur-e2.club/OU/images/index.php?dir=7.4/$brand/" | grep $device | tail -n 1 | tr -d ' ' | sed 's/\.zip.*/.zip/')
sleep 3

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

#download image to mounted storage
echo '> Downloading '$image'-'$version' image to '$ms'/images please wait...'
sleep 3s
url='https://www.pur-e2.club/OU/images/index.php?dir=7.4/'$brand'/&file='$imgnm
wget -O $ms/images/$imgnm "$url"

for dir in "/media/hdd/ImagesUpload/" "/media/hdd/open-multiboot-upload/" "/media/hdd/OPDBootUpload/" "/media/hdd/EgamiBootUpload/"
do
echo ""
if [ -d $dir ] ; then
cp $ms/images/$imgnm $dir >/dev/null 2>&1
fi
done

echo '> Download '$image'-'$version' image to '$ms'/images finished 
> Biko_73 upload... '
sleep 3s 
fi
