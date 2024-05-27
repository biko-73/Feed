#!/bin/sh

#########################################################
PACKAGE_DIR='DDRSSReader/main'
MY_FILE="DD_RSS-$version.tar.gz"
version=0.4
#########################################################

MY_MAIN_URL="https://raw.githubusercontent.com/Belfagor2005/"
MY_URL=$MY_MAIN_URL$PACKAGE_DIR'/'$MY_FILE
MY_TMP_FILE="/tmp/"$MY_FILE

rm -f $MY_TMP_FILE > /dev/null 2>&1

MY_SEP='============================================================='
echo $MY_SEP
echo 'Downloading '$MY_FILE' ...'
echo $MY_SEP
echo ''
wget -T 2 $MY_URL -P "/tmp/"

if [ -f $MY_TMP_FILE ]; then

	echo ''
	echo $MY_SEP
	echo 'Extracting ...'
	echo $MY_SEP
	echo ''
	tar -xf $MY_TMP_FILE -C /
	MY_RESULT=$?

	rm -f $MY_TMP_FILE > /dev/null 2>&1

	echo ''
	echo ''
	if [ $MY_RESULT -eq 0 ]; then
        echo "#############################################################################"
        echo "#             DD RSS FEEDS $version INSTALLED SUCCESSFULLY                  #"
        echo "#             adapted for py3 & added fhd screens By Lululla                #"
        echo "#   https://www.linuxsat-support.com/thread/158275-plugin-dd-rss-feeds      #"
        echo "#############################################################################"
        echo "#                       your Device will RESTART Now                        #"
        echo "#############################################################################"		
		if which systemctl > /dev/null 2>&1; then
			sleep 2; systemctl restart enigma2
		else
			init 4; sleep 4; init 3;
		fi
	else
		echo "   >>>>   INSTALLATION FAILED !   <<<<"
	fi;
	echo ''
	echo '**************************************************'
	echo '**                   FINISHED                   **'
	echo '**************************************************'
	echo ''
	exit 0
else
	echo ''
	echo "Download failed !"
	exit 1
fi
# ------------------------------------------------------------------------------------------------------------
