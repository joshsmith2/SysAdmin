#!/bin/bash
#The parent script from which all other font clearing scripts are called. 
#SYNTAX: fontFinder.sh delOption(STRING - Default: "-list") verboseOption(STRING - Default: "-verbose") selfdestructOption(STRING - Default: "-noselfdestruct")

fileName=`basename $0`
versionNumber=`echo $fileName | tail -c 7 | head -c 3`

delOption=$4				#Whether to delete files after tarring them. 	DEFAULT - on
verboseOption=$5			#Python script is verbose.						DEFAULT - on
selfdestructOption=$6		#fontFinder removes itself after running		DEFAULT - off

echo ""

#Generate a date string to use for unique file names
dateTimeNow=`date +"%d%m-%H%M"`

#The location of the log file - not in the fontFinder dir as this is removed once the script has run. 
logFile="/var/fontDeletionLog-$dateTimeNow.txt"

#cd to the directory containing this script:
#a=$(dirname $0)
#cd $a

#cd to the directory containing fontFinder:
cd /Users/joshsmith/Desktop/Git/Tower/Fonts/fontFinder_v$versionNumber

#Use expect to run the standalone FW_Client:
#./scripts/expectFontwise.sh && echo "" && echo "---------------------------" && echo "   End of Fontwise report  " && echo "---------------------------" && echo ""

#Run a python script to tar up any fonts found. 
#SYNTAX: fontFinder.py  deleteOrList(STRING - '-d', '-delete' or '-l, -list') logPath(STRING) archiveFile(STRING) isVerbose(STRING - 'verbose', 'v' or empty) timeStamp(STRING - the time.)
python ./scripts/toothlessFonter.py ${delOption:-"-list"} $logFile /var/hogarth-del-fonts ${verboseOption:-"-verbose"} $dateTimeNow


function sendFile(){

	doRm=$1

	#Create a unique folder containing the generated log files
	logDir=$dateTimeNow
	
	mkdir $HOSTNAME
	mkdir $HOSTNAME/$logDir 
	mv -n ./fontwise/*.tab ./$HOSTNAME/$logDir/
	mv -n ./fontwise/*.mci ./$HOSTNAME/$logDir/
	mv -n ./fontwise/Temp ./$HOSTNAME/$logDir/
	
	cp $logFile ./$HOSTNAME/$logDir/
	
	#Send these files to the cenralised server on ixllvmva49 via ssh. If successful, remove the logs from the local machine.
	mkdir /Volumes/FWShare
	mount -t smbfs -o nobrowse '//mrFontwiseReports:1AbsoluteBinBag@ixllvmva49/Fontwise/' /Volumes/FWShare
	scp -r $HOSTNAME /Volumes/FWShare && rm -r $HOSTNAME
	umount /Volumes/FWShare
	
	#Once it's all done, get rid of fontFinder
	if [[ $doRm == "-selfdestruct" ]]; then
		rm -r ../fontFinder_v$versionNumber
	fi
}

#sendFile ${selfdestructOption:-"-noselfdestruct"}
