#!/bin/bash

#determine image name & url based on device name
hostname=$(cat /etc/hostname)
case $hostname in
pulse4k)
brand=AB-COM
brand1=PULSe%204K
brand2=mmc
device=$pulse4k;;
pulse4kmini)
brand=AB-COM
brand1=PULSe%204K%20Mini
brand2=mmc
device=pulse4kmini;;
axmultiboxse)
brand=axmultiboxse
brand1=axmultiboxse
brand2=multi
device=$hostname;;
zgemmah2h)
brand=AirDigital
brand1=Zgemma%20H.2H
brand2=usb
device=$hostname;;
zgemmah2s)
brand=AirDigital
brand1=Zgemma%20H.2S
brand2=usb
device=$hostname;;
zgemmahs) 
brand=AirDigital
brand1=Zgemma%20H.S
brand2=usb
device=$hostname;;
zgemmah11s)
brand=AirDigital
brand1=Zgemma%20H11S
brand2=multi
device=$hostname;;
zgemmah32tc)
brand=AirDigital
brand1=Zgemma%20H3.2TC
brand2=usb
device=$hostname;;
zgemmah4)
brand=AirDigital
brand1=Zgemma%20H4
brand2=usb
device=$hostname;;
zgemmah5)
brand=AirDigital
brand1=Zgemma%20H5
brand2=usb
device=$hostname;;
zgemmah7|h7)
brand=AirDigital
brand1=Zgemma%20H7S
brand2=multi
device=zgemmah7s;;
zgemmah82h)
brand=AirDigital
brand1=Zgemma%20H8.2H
brand2=nand
device=$hostname;;
zgemmah9combo)
brand=AirDigital
brand1=Zgemma%20H9%20Combo
brand2=multi
device=zgemmah9combo;;
zgemmah9twin)
brand=AirDigital
brand1=Zgemma%20H9%20Twin
brand2=multi
device=$hostname;;
zgemmah92h)
brand=AirDigital
brand1=Zgemma%20H9.2H
brand2=usb
device=$hostname;;
zgemmah92hse)
brand=AirDigital
brand1=Zgemma%20H9.2H%20SE
brand2=multi
device=$hostname;;
zgemmah92s)
brand=AirDigital
brand1=Zgemma%20H9.2S
brand2=usb
device=$hostname;;
zgemmah9s)
brand=AirDigital
brand1=Zgemma%20H9S
brand2=usb
device=$hostname;;
zgemmah9sse)
brand=AirDigital
brand1=Zgemma%20H9S%20SE
brand2=multi
device=$hostname;;
zgemmah9t)
brand=AirDigital
brand1=Zgemma%20H9T
brand2=usb
device=$hostname;;
zgemmai55plus)
brand=AirDigital
brand1=Zgemma%20i55%20Plus
brand2=usb
device=$hostname;;
vipercombo)
brand=Amiko
brand1=Viper%20Combo
brand2=usb
device=$hostname;;
dinobot4k)
brand=DINOBOT
brand1=Dinobot%204K
brand2=mmc
device=$hostname;;
dinobot4ktwin)
brand=DINOBOT
brand1=Dinobot%204K%20Twin
brand2=mmc
device=$hostname;;
dinobot4kplus)
brand=DINOBOT
brand1=Dinobot%204K+
brand2=mmc
device=$hostname;;
dinobot4kmini)
brand=DINOBOT
brand1=U5%20mini
brand2=mmc
device=$hostname;;
osmega)
brand=Edision
brand1=OS%20mega
brand2=usb
device=$hostname;;
osmini)
brand=Edision
brand1=OS%20mini
brand2=usb
device=$hostname;;
osmini4k)
brand=Edision
brand1=OS%20mini%204k
brand2=usb
device=$hostname;;
osminiplus)
brand=Edision
brand1=OS%20mini%20plus
brand2=usb
device=$hostname;;
osmio4k)
brand=Edision
brand1=OS%20mio%204k
brand2=usb
device=$hostname;;
osmio4kplus)
brand=Edision
brand1=OS%20mio%204k%20plus
brand2=usb
device=$hostname;;
osnino)
brand=Edision
brand1=OS%20nino
brand2=usb
device=$hostname;;
osninoplus)
brand=Edision
brand1=OS%20nino%20plus
brand2=usb
device=$hostname;;
osninopro)
brand=Edision
brand1=OS%20nino%20pro
brand2=usb
device=$hostname;;
arivacombo)
brand=Ferguson
brand1=ARIVA%20ATV%20Combo
brand2=mmc
device=$hostname;;
arivatwin)
brand=Ferguson
brand1=ARIVA%20ATV%20TT
brand2=mmc
device=$hostname;;
formuler1)
brand=Formuler
brand1=F1
brand2=usb
device=$hostname;;
formuler3)
brand=Formuler
brand1=F3
brand2=usb
device=$hostname;;
formuler4)
brand=Formuler
brand1=F4
brand2=usb
device=$hostname;;
formuler4turbo)
brand=Formuler
brand1=F4%20turbo
brand2=usb
device=$hostname;;
et7000mini)
brand=Galaxy%20Innovations
brand1=Galaxy%20Innovations
brand2=usb
device=$hostname;;
gbquadplus)
brand=GigaBlue
brand1=$hostname
brand2=usb
device=$hostname;;
gbquad4k)
brand=GigaBlue
brand1=$hostname
brand2=usb
device=$hostname;;
gbtrio4k)
brand=GigaBlue
brand1=$hostname
brand2=mmc
device=$hostname;;
gbtrio4kpro)
brand=GigaBlue
brand1=$hostname
brand2=mmc
device=$hostname;;
gbx34k) 
brand=GigaBlue
brand1=$hostname
brand2=usb
device=$hostname;;
gbue4k)
brand=GigaBlue
brand1=$hostname
brand2=usb
device=$hostname;;
hitube4k)
brand=HITUBE
brand1=HITUBE4K
brand2=usb
device=$hostname;;
hitube4kplus)
brand=HITUBE
brand1=HITUBE4K%20PLUS
brand2=mmc
device=$hostname;;
hitube4kpro)
brand=HITUBE
brand1=HITUBE4K%20PRO
brand2=mmc
device=$hostname;;
iziboxecohd)
brand=IZIBOX
brand1=IZIBOX%20ECO%20TWIN%20HD
brand2=usb
device=$hostname;;
iziboxelite4k)
brand=IZIBOX
brand1=IZIBOX%20ELITE%204K
brand2=mmc
device=$hostname;;
iziboxone4k)
brand=IZIBOX
brand1=IZIBOX%20ONE%204K
brand2=usb
device=$hostname;;
iziboxx3)
brand=IZIBOX
brand1=IZIBOX%20X3
brand2=usb
device=$hostname;;
maxytecmulti)
brand=Maxytec
brand1=Maxytec%20Multi%204K
brand2=multi
device=$hostname;;
mutant51)
brand=Mut@nt
brand1=HD51
brand2=multi
device=$hostname;;
mutant60)
brand=Mut@nt
brand1=HD60
brand2=multi
device=$hostname;;
sf4008)
brand=Octagon
brand1=SF4008
brand2=usb
device=$hostname;;
sf8008)
brand=Octagon
brand1=SF8008
brand2=mmc
device=$hostname;;
dual)
brand=Qviart
brand1=dual
brand2=mmc
device=$hostname;;
ustym4kpro)
brand=Uclan
brand1=Ustym%204K%20PRO
brand2=mmc
device=$hostname;;
vuduo2|vuduo4k|vusolo2|vusolo4kse|vusolo4k|vuultimo4k|vuuno4k|vuuno4kse|vuzero|vuzero4k)
brand=Vuplus
brand1=$hostname
brand2=usb
device=$hostname;;
*)
echo "> your device is not supported "
exit 1 ;;
esac

imgnm=$(curl -s "https://openspa.webhop.info/scan.php" |grep -Eo "openspa-[0-9]+\.[0-9]+\.[0-9]+-$device-[0-9]+_$brand2.zip" | grep 8.3 | tail -n 1)
url="https://openspa.webhop.info/Descarga%20de%20Im%C3%A1genes/$brand/$brand1/$imgnm"

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


