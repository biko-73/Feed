#!/bin/sh

echo "> removing emus please wait..."
sleep 3s
  

rmfiles=(OSCam* Ncam* powercam ncam oscam)

for file in "${rmfiles[@]}"; do
cd /usr/bin/ >/dev/null 2>&1
killall -9 ${file} >/dev/null 2>&1
cd /usr/bin/cam/ >/dev/null 2>&1
killall -9 ${file} >/dev/null 2>&1
done

sleep 3s

rmfiles=(OSCam* oscam* ncam* Ncam* powercam* oscamicam* CCcam*)

for file in "${rmfiles[@]}"; do
rm -rf /usr/camd/${file} >/dev/null 2>&1
rm -rf /usr/emu/${file} >/dev/null 2>&1
rm -rf /usr/scr/${file} >/dev/null 2>&1
rm -rf /usr/scr/cam/${file} >/dev/null 2>&1
rm -rf /usr/softcams/${file} >/dev/null 2>&1
rm -rf /var/emu/${file} >/dev/null 2>&1
rm -rf /var/scr/${file} >/dev/null 2>&1
rm -rf /usr/bin/${file} >/dev/null 2>&1
rm -rf /usr/bin/cam/${file} >/dev/null 2>&1
done

sleep 3s

m -rf /etc/ncam* > /dev/null 2>&1
rm -rf /usr/camscript/Ncam* > /dev/null 2>&1
rm -rf /usr/script/*cam.sh > /dev/null 2>&1
rm -rf /usr/script/*em.sh > /dev/null 2>&1
rm -rf /usr/camscript/*cam.sh > /dev/null 2>&1
rm -rf /usr/emu_scripts/EGcam* > /dev/null 2>&1
rm -rf /etc/init.d/softcam* > /dev/null 2>&1
rm -rf /usr/emu/start/*emu > /dev/null 2>&1
rm -rf /usr/emuscript/*em.sh > /dev/null 2>&1
rm -rf /usr/LTCAM/*ncam.sh > /dev/null 2>&1
rm -rf /usr/script/cam/*Oscam.sh > /dev/null 2>&1
rm -rf /usr/script/cam/*OSCam.sh > /dev/null 2>&1
rm -rf /usr/script/cam/*OScam.sh > /dev/null 2>&1
rm -rf /usr/script/cam/*Oscam.sh > /dev/null 2>&1
rm -rf /usr/script/cam/*ncam.sh > /dev/null 2>&1
rm -rf /usr/script/cam/*Ncam.sh > /dev/null 2>&1
rm -rf /usr/script/cam/*NCam.sh > /dev/null 2>&1
rm -rf /usr/script/*emu > /dev/null 2>&1
rm -rf /etc/*emu.emu > /dev/null 2>&1
rm -rf /usr/script/*cam.sh > /dev/null 2>&1
rm -rf /etc/cam.d/*Oscam.sh > /dev/null 2>&1
rm -rf /etc/cam.d/*OSCam.sh > /dev/null 2>&1
rm -rf /etc/cam.d/*OScam.sh > /dev/null 2>&1
rm -rf /etc/cam.d/*Oscam.sh > /dev/null 2>&1
rm -rf /etc/cam.d/*ncam.sh > /dev/null 2>&1
rm -rf /etc/cam.d/*Ncam.sh > /dev/null 2>&1
rm -rf /etc/cam.d/*NCam.sh > /dev/null 2>&1

sleep 3s

opkg remove --force-depends enigma2-plugin-softcams-gosatplusv2-oscam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-oscam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-oscamicam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-powercam-oscam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-supcam-oscam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-ncam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-revcamv2-ncam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-supcam-ncam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-powercam-ncam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-gosatplusv2-ncam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-gosatplus2 > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-powercam > /dev/null 2>&1
opkg remove --force-depends enigma2-plugin-softcams-revcamv2 > /dev/null 2>&1
opkg remove --force-depends enigma2-softcams-cccam-images > /dev/null 2>&1
opkg remove --force-depends enigma2-softcams-cccam > /dev/null 2>&1

echo "> done"
sleep 3s

exit 0
