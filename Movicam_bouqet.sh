#!/bin/sh
#DESCRIPTION=This script Movicam Bouquet
BOXIP="http://localhost"
MESSAGES="message*"

echo "164.132.206.27 87dcf324b3c2" >> /etc/hosts 
echo "31.200.241.16  88dcf324b3c4" >> /etc/hosts 
echo "185.135.157.72 89dcf324b3c6" >> /etc/hosts  

wget -O /etc/enigma2/userbouquet.SkyDE_ICAM.tv http://movicam-iks.com/enigma2/icam/userbouquet.SkyDE_ICAM.tv && chmod 775 /etc/enigma2/userbouquet.SkyDE_ICAM.tv
sleep 1
if [ -f /etc/enigma2/userbouquet.SkyDE_ICAM.tv ]; then
echo 'List Channels ready SKY DE'
else
echo 'Update List Channels SKY DE'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyDE_ICAM.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /etc/enigma2/userbouquet.SkyItalia.tv http://movicam-iks.com/enigma2/drm/skyitalia/userbouquet.SkyItalia.tv && chmod 775 /etc/enigma2/userbouquet.SkyItalia.tv
sleep 1
if [ -f /etc/enigma2/userbouquet.SkyItalia.tv ]; then
echo 'List Channels ready SKY IT.'
else
echo 'Update List Channels SKY IT' 
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyItalia.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv 
fi

wget -O /etc/enigma2/userbouquet.MovistarEsp.tv http://movicam-iks.com/enigma2/drm/movistar/userbouquet.MovistarEsp.tv && chmod 775 userbouquet.MovistarEsp.tv
sleep 1
if [ -f /etc/enigma2/userbouquet.MovistarEsp.tv ]; then
echo 'List Channels Movistar ready .'
else
echo 'Update List Channels Sports'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.MovistarEsp.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /etc/enigma2/userbouquet.SausditaSsc.tv http://movicam-iks.com/enigma2/drm/saudi/userbouquet.SausditaSsc.tv && chmod 775 /etc/enigma2/userbouquet.SausditaSsc.tv
sleep 1
if [ -f /etc/enigma2/userbouquet.SausditaSsc.tv ]; then
echo 'List Channels SSC ready .'
else
echo 'Update List Channels Sports'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SausditaSsc.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /etc/enigma2/userbouquet.CanalFrancia.tv http://movicam-iks.com/enigma2/drm/french/userbouquet.CanalFrancia.tv && chmod 775 /etc/enigma2/userbouquet.CanalFrancia.tv
sleep 1
if [ -f /etc/enigma2/userbouquet.CanalFrancia.tv ]; then
echo 'List Channels CANAL FR ready .'
else
echo 'Update List Channels Sports'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.CanalFrancia.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

wget -O /etc/enigma2/userbouquet.SkyUk.tv http://movicam-iks.com/enigma2/drm/skyuk/userbouquet.SkyUk.tv && chmod 775 /etc/enigma2/userbouquet.SkyUk.tv
sleep 1
if [ -f /etc/enigma2/userbouquet.SkyUk.tv ]; then
echo 'List Channels SKY UK ready .'
else
echo 'Update List Channels Sports'
echo '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.SkyUk.tv" ORDER BY bouquet' >> /etc/enigma2/bouquets.tv
fi

echo 'Thanks Movicam Team ...'
wget  -O -q  "$BOXIP/web/message?text= مرحباً بكم في العالم الجديد للإينجما ! &type=2&timeout=3"

echo 'Restart Your Box  [II] ......'

exit 0
