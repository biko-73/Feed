#!/bin/sh
#DESCRIPTION=This script Movicam Bouquet

echo "164.132.206.27 87dcf324b3c2" >> /etc/hosts 
echo "31.200.241.16  88dcf324b3c4" >> /etc/hosts 

wget -O /etc/enigma2/userbouquet.SkyDE_ICAM.tv http://movicam-iks.com/enigma2/icam/userbouquet.SkyDE_ICAM.tv && chmod 775 /etc/enigma2/userbouquet.SkyDE_ICAM.tv

if [ -f /etc/enigma2/userbouquet.SkyDE_ICAM.tv ]; then
echo 'List Channels ready SKY DE'
else
echo 'Update List Channels SKY DE'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyDE_ICAM.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /etc/enigma2/userbouquet.SkyItalia.tv http://movicam-iks.com/enigma2/drm/skyitalia/userbouquet.SkyItalia.tv && chmod 775 /etc/enigma2/userbouquet.SkyItalia.tv

if [ -f /etc/enigma2/userbouquet.SkyItalia.tv ]; then
echo 'List Channels ready SKY IT.'
else
echo 'Update List Channels SKY IT' 
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyItalia.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv 
fi

wget -O /etc/enigma2/userbouquet.MovistarEsp.tv http://movicam-iks.com/enigma2/drm/movistar/userbouquet.MovistarEsp.tv && chmod 775 userbouquet.MovistarEsp.tv

if [ -f /etc/enigma2/userbouquet.MovistarEsp.tv ]; then
echo 'List Channels Movistar ready .'
else
echo 'Update List Channels Sports'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.MovistarEsp.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /etc/enigma2/userbouquet.SausditaSsc.tv http://movicam-iks.com/enigma2/drm/saudi/userbouquet.SausditaSsc.tv && chmod 775 /etc/enigma2/userbouquet.SausditaSsc.tv

if [ -f /etc/enigma2/userbouquet.SausditaSsc.tv ]; then
echo 'List Channels SSC ready .'
else
echo 'Update List Channels Sports'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SausditaSsc.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /etc/enigma2/userbouquet.CanalFrancia.tv http://movicam-iks.com/enigma2/drm/french/userbouquet.CanalFrancia.tv && chmod 775 /etc/enigma2/userbouquet.CanalFrancia.tv

if [ -f /etc/enigma2/userbouquet.CanalFrancia.tv ]; then
echo 'List Channels CANAL FR ready .'
else
echo 'Update List Channels Sports'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.CanalFrancia.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /dev/null -q "http://127.0.0.1/api/message?text= مرحباً بكم في العالم الجديد للإينجما ! &type=2&timeout=5&_=1425677186730"

echo " Thanks Movicam Team "
echo 'Restart Box  [II] ......'
sleep 2; systemctl restart enigma2
exit 0
