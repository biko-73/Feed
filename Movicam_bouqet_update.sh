#!/bin/sh
#DESCRIPTION = This script to Download or update Movicam Bouquet

echo "164.132.206.27 87dcf324b3c2" >> /etc/hosts 
echo "31.200.241.16  88dcf324b3c4" >> /etc/hosts 
echo "185.135.157.72 89dcf324b3c6" >> /etc/hosts  

rm -rf /etc/enigma2/userbouquet.SkyDE_ICAM.tv
rm -rf /etc/enigma2/userbouquet.SkyItalia.tv
rm -rf /etc/enigma2/userbouquet.MovistarEsp.tv
rm -rf /etc/enigma2/userbouquet.SausditaSsc.tv
rm -rf /etc/enigma2/userbouquet.CanalFrancia.tv
rm -rf /etc/enigma2/userbouquet.SkyUk.tv
sleep 2

wget -O /etc/enigma2/userbouquet.SkyDE_ICAM.tv http://movicam-iks.com/enigma2/icam/userbouquet.SkyDE_ICAM.tv && chmod 775 /etc/enigma2/userbouquet.SkyDE_ICAM.tv
sleep 1
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyDE_ICAM.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv

wget -O /etc/enigma2/userbouquet.SkyItalia.tv http://movicam-iks.com/enigma2/drm/skyitalia/userbouquet.SkyItalia.tv && chmod 775 /etc/enigma2/userbouquet.SkyItalia.tv
sleep 1
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyItalia.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv 

wget -O /etc/enigma2/userbouquet.MovistarEsp.tv http://movicam-iks.com/enigma2/drm/movistar/userbouquet.MovistarEsp.tv && chmod 775 userbouquet.MovistarEsp.tv
sleep 1
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.MovistarEsp.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv

wget -O /etc/enigma2/userbouquet.SausditaSsc.tv http://movicam-iks.com/enigma2/drm/saudi/userbouquet.SausditaSsc.tv && chmod 775 /etc/enigma2/userbouquet.SausditaSsc.tv
sleep 1
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SausditaSsc.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv

wget -O /etc/enigma2/userbouquet.CanalFrancia.tv http://movicam-iks.com/enigma2/drm/french/userbouquet.CanalFrancia.tv && chmod 775 /etc/enigma2/userbouquet.CanalFrancia.tv
sleep 1
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.CanalFrancia.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv

wget -O /etc/enigma2/userbouquet.SkyUk.tv http://movicam-iks.com/enigma2/drm/skyuk/userbouquet.SkyUk.tv && chmod 775 /etc/enigma2/userbouquet.SkyUk.tv
sleep 1
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyUk.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv

sleep 1
wget -qO - http://127.0.0.1/web/servicelistreload?mode=2

wget -O /dev/null -q "http://127.0.0.1/api/message?text= مرحباً بكم في العالم الجديد للإينجما ! &type=2&timeout=10&_=1425677186730"

MY_RESULT=$?

echo ''
echo ''
if [ $MY_RESULT -eq 0 ]; then
	echo "   >>>>   Your Bouqet are updated   <<<<"
	echo ''
	echo "   >>>>         RESTARING         <<<<"
	if which systemctl > /dev/null 2>&1; then
		sleep 2; systemctl restart enigma2
	else
		init 4; sleep 4; init 3;
	fi
else
	echo "   >>>>   Update Bouqet Failed !   <<<<"
fi;
echo ''
echo '**************************************************'
echo '**                   FINISHED                   **'
echo '**************************************************'
echo ''
exit 0
