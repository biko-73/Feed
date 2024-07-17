#!/bin/bash

# ********************************************************************************************************
# wget -q "--no-check-certificate" https://github.com/biko-73/Feed/raw/main/openpli-9.0.sh -O - | /bin/sh
# ********************************************************************************************************

#Check device name
device=$(head -n 1 /etc/hostname)

#Determine urls for devicea
case $device in

pulse4k)
url1="https://openpli.org/download/ab-com/PULSe+4K"
url2="pulse4k" ;;

pulse4kmini)
url1="https://openpli.org/download/ab-com/PULSe+4K+mini"
url2="pulse4kmini" ;;

zgemmahs)
url1="https://openpli.org/download/zgemma/H.S"
url2="h3" ;;

zgemmah2s)
url1="https://openpli.org/download/zgemma/H.2S"
url2="h3" ;;

zgemmah32tc)
url1="https://openpli.org/download/zgemma/H3.2TC"
url2="h3" ;;

zgemmah4)
url1="https://openpli.org/download/zgemma/H4"
url2="h4" ;;

zgemmah5)
url1="https://openpli.org/download/zgemma/H5"
url2="h5" ;;

zgemmah6)
url1="https://openpli.org/download/zgemma/H6"
url2="h6" ;;

zgemmah7|h7)
url1="https://openpli.org/download/zgemma/H7.S" 
url2=h7 ;;

zgemmah82h)
url1="https://openpli.org/download/zgemma/H8.2H"
url2="h8" ;;

zgemmah9combo)
url1="https://openpli.org/download/zgemma/H9+Combo"
url2="h9combo" ;;

zgemmah9combose)
url1="https://openpli.org/download/zgemma/H9+Combose"
url2="h9combose" ;;

zgemmah9sse)
url1="https://openpli.org/download/zgemma/H9+Combo+SE"
url2="h9se" ;;

zgemmah9twin)
url1="https://openpli.org/download/zgemma/H9+Twin"
url2="h9combo" ;;

zgemmah9twinse)
url1="https://openpli.org/download/zgemma/H9+Twin+SE"
url2="h9combose" ;;

zgemmah92h)
url1="https://openpli.org/download/zgemma/H9.2H"
url2="h9" ;;

zgemmah92hse)
url1="https://openpli.org/download/zgemma/H9.2S+SE"
url2="h9se" ;;

zgemmah9s)
url1="https://openpli.org/download/zgemma/H9.S"
url2="h9" ;;

zgemmah9sse)
url1="https://openpli.org/download/zgemma/H9.S+SE"
url2="h9se" ;;

zgemmah10)
url1="https://openpli.org/download/zgemma/H10"
url2="h10" ;;

zgemmah11s)
url1="https://openpli.org/download/zgemma/H11"
url2="h11" ;;

zgemmai55)
url1="https://openpli.org/download/zgemma/I55"
url2="i55" ;;

zgemmai55plus)
url1="https://openpli.org/download/zgemma/I55+Plus"
url2="i55plus" ;;

e4hdcombo)
url1="https://openpli.org/download/axas/E4HD+4K+Ultra"
url2="e4hd" ;;

dm500)
url1="https://openpli.org/download/dreambox/DM500"
url2="dm500" ;;

dm500hd)
url1="https://openpli.org/download/dreambox/DM500+HD"
url2="dm500hd" ;;

dm500plus)
url1="https://openpli.org/download/dreambox/DM500+PLUS"
url2="dm500plus" ;;

dm7000)
url1="https://openpli.org/download/dreambox/DM7000"
url2="dm7000" ;;

dm7020)
url1="https://openpli.org/download/dreambox/DM7020"
url2="dm7020" ;;

dm7020hd)
url1="https://openpli.org/download/dreambox/DM7020+HD"
url2="dm7020hd" ;;

dm7025hd)
url1="https://openpli.org/download/dreambox/DM7025+HD"
url2="dm7025" ;;

dm800)
url1="https://openpli.org/download/dreambox/DM800"
url2="dm800" ;;

dm800sehd)
url1="https://openpli.org/download/dreambox/DM800+SE+HD"
url2="dm800se" ;;

osmini4k)
url1="https://openpli.org/download/edision/OS+mini+4K"
url2="osmini4k" ;;

osmio4k)
url1="https://openpli.org/download/edision/OS+mio+4K"
url2="osmio4k" ;;

osmio4kplus)
url1="https://openpli.org/download/edision/OS+mio+4K+%2B"
url2="osmio4kplus" ;;

osninoplus)
url1="https://openpli.org/download/edision/OS+nino+%2B"
url2="osninoplus" ;;

osninopro)
url1="https://openpli.org/download/edision/OS+nino+pro"
url2="osninopro" ;;

gbtrio4k)
url1="https://openpli.org/download/gigablue/UHD+Trio+4K"
url2="gbtrio4k" ;;

gbquad4k)
url1="https://openpli.org/download/gigablue/UHD+Quad+4K"
url2="gbquad4k" ;;

gbue4k)
url1="https://openpli.org/download/gigablue/UHD+UE+4K"
url2="gbue4k" ;;

mutant51)
url1="https://openpli.org/download/mutant/HD51"
url2="hd51" ;;

mutant60)
url1="https://openpli.org/download/mutant/HD60"
url2="hd60" ;;

mutant1500)
url1="https://openpli.org/download/mutant/HD1500"
url2="hd1500" ;;

sf8008)
url1="https://openpli.org/download/octagon/SF8008"
url2="sf8008" ;;


sfx6008)
url1="https://openpli.org/download/octagon/SFX6008"
url2="sfx6008" ;;

dual)
url1="https://openpli.org/download/qviart/Dual+4K"
url2="dual" ;;

ustym4kpro)
url1="https://openpli.org/download/uclan/Ustym+4K+pro"
url2="ustym4kpro" ;;

duo)
url="https://openpli.org/download/vuplus/Duo"
url2="duo" ;;

vuduo2)
url1="https://openpli.org/download/vuplus/Duo2"
url2="vuduo2" ;;

vuduo4k)
url1="https://openpli.org/download/vuplus/Duo+4K"
url2="vuduo4k" ;;

vuduo4kse)
url1="https://openpli.org/download/vuplus/Duo+4K+SE"
url2="vuduo4kse" ;;

solo)
url="https://openpli.org/download/vuplus/Solo"
url2="solo" ;;

vusolo2)
url1="https://openpli.org/download/vuplus/Solo2"
url2="vusolo2" ;;

vusolose)
url1="https://openpli.org/download/vuplus/Solo+SE"
url2="vusolose" ;;

vusolo4k)
url1="https://openpli.org/download/vuplus/Solo+4K"
url2="vusolo4k" ;;

vuultimo)
url1="https://openpli.org/download/vuplus/Ultimo"
url2="pulse4kmini" ;;

vuultimo4k)
url1="https://openpli.org/download/vuplus/Ultimo+4K"
url2="vuultimo4k" ;;

uno)
url="https://openpli.org/download/vuplus/Uno"
url2="uno" ;;

vuuno4k)
url1="https://openpli.org/download/vuplus/Uno+4K"
url2="vuuno4k" ;;

vuuno4kse)
url1="https://openpli.org/download/vuplus/Uno+4K+SE"
url2="vuuno4kse" ;;

vuzero)
url1="https://openpli.org/download/vuplus/Zero"
url2="vuzero" ;;

vuzero4k)
url1="https://openpli.org/download/vuplus/Zero+4K"
url2="vuzero4k" ;;

et10000)
url1="https://openpli.org/download/gi_es/ET-11000"
url2="et10000" ;;

et7000mini)
url1="https://openpli.org/download/gi_es/ET7000+mini"
url2="et7000mini" ;;

*)
echo "> your device is not supported "
exit 1 ;;
esac

#Check image name 
imgnm=$(curl -s $url1 | grep -o 'href="[^"]*\.zip"' | grep "9.0" | awk -F'"' '{print $2; exit}' | sed 's/^.*openpli-/openpli-/')
url="https://downloads.openpli.org/builds/$url2/$imgnm"

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

#download images
echo '> Downloading '$image'-'$version' image to '$ms'/images please wait...'
sleep 3s
echo $url
wget -O $ms/images/$imgnm $url

#Check an copy images to upload folders
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
