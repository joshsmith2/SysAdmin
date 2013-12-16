#!/usr/bin/python
#This script will check through all subfolders and files inside dir and remove all occurences of problematic characters

#----PROGRESS NOTE: Must update 'passDir' to point to Panzura after it's been mounted on a machine.

import sys
import os
import os.path
import re
import getopt
import time
import datetime
import atexit
from xattr import xattr
from struct import unpack

#Define functions:

def sanitise(inString):
#This function removes any occurences of characters found in blackList from theString, except ':' which, for legibility, are changed to '-'

		outString = inString.translate(None, blackList)

		#Remove all whitespace from filenames except spaces (from http://stackoverflow.com/questions/1898656/remove-whitespace-in-python-using-string-whitespace)
		noWhitespaceString = ' '.join(outString.split())

		#Prevent multiple runs of whitespace from being stripped
		noMultSpaceString = ' '.join(re.split(' +', outString))
	
		if noMultSpaceString != noWhitespaceString:
			
			outString = noWhitespaceString

		#Substitute hyphens for colons, to help legibility
		outString = re.sub(':','-',outString)

		return str(outString)

def appendIndex(filename, ext, path):
#Given a file 'filename' at location 'path' with extension 'ext', this will return the path of filename(n)ext, where n is the lowest integer for which filename(n-1)ext already exitsts.

	index = 1

	appendedFile = filename + "(" + str(index) + ")" + ext

	appendedPath = os.path.join(path, appendedFile)

	while os.path.exists(appendedPath) or appendedPath in sanitisedList:
		
		index += 1
		appendedFile = filename + "(" + str(index) + ")" + ext
		appendedPath = os.path.join(path, appendedFile)

	return appendedPath

def immediateSubdirs(theDir):
	
	return [name for name in os.listdir(theDir)
		if os.path.isdir(os.path.join(theDir,name))]

def timeStamp(form='long'):
#A timestamp which will tell you when the last renaming occurred. Will prefix all output from the program. 
		
	ts = time.time()
	return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') + " : "

	if form == 'short':
		return datetime.datetime.fromtimestamp(ts).strftime('%m$d-%H%M')

def printAndLog(toPrint, ts=0,):
#Prints toPrint to stdOut and also to logFile. If ts is passed, will print the tim eof the log. 

	if ts != 0:
		ts = timeStamp()
	
	if not quiet:
		print ts + toPrint
	if logFileName is not None:
		logFile.write( ts + toPrint )

def renameFile(prevPath, newPath, rename):
#Either renames a file, or logs it. 
	
	#We're here if and only if an error has been found
	global errorsFound
	errorsFound = True

	if rename:
		try:
			os.rename(prevPath, newPath)

			printAndLog("Changed from: " + prevPath, 1)
			printAndLog("Changed to:   " + newPath + "\n", 1)

		except OSError:
			printAndLog("Error: unable to rename " + prevPath + "\n", 1)
			if errorFileName is not None:
				errorFile.write( timeStamp() + "Error: unable to rename " + prevPath + "\n")

	else:
		#Add the clean path to a list of changed files, so that logging without changing works correctly
		sanitisedList.append(newPath)

		printAndLog("Illegal character found in file : " + prevPath, 1)
		printAndLog("Suggested change                : " + newPath + "\n", 1)

def renameToClean(path, obj, objType):
		#Takes an object (a string - either a file or a directory, as defined in 'type' which must be one of 'file' or 'dir') and, if the string has any forbidden characters, sanitises it and renames it.

		fullPath = os.path.join(path, obj)		
	
		cleanObj = sanitise(obj)
		
		cleanPath = fullPath #This is a little dishonest here, since the path hasn't been cleaned yet, but it will change as soon as any sanitisation goes on

		#If sanitise has made any difference, record the file in a list of changed files, then rename the file.
		if cleanObj != obj:
			
				#Check for strings prefixed with '.', and remove these for replacement after file renaming.
				prefix = ""	
		
				if cleanObj[:1] == '.':
					prefix = '.'
					cleanObj = cleanObj[1:]

				#Separate filename from extension:
				cleanSplit = cleanObj.split('.')

				#For files and directories which were only composed of illegal characters, rename these 'Renamed file' or 'Renamed Folder'
				if cleanSplit[0].strip() == '':
						if objType == 'file':
								cleanObj = 'Renamed File' + cleanObj[len(cleanSplit[0]):]
						elif objType == 'dir':
								cleanObj = 'Renamed Folder'

				#Replace any previously removed periods
				cleanObj = prefix + cleanObj

				cleanPath = os.path.join(path, cleanObj)

				#If the clean path already exists, append '(n)' to the filename
				if os.path.exists(cleanPath) or cleanPath in sanitisedList:

						cleanPath = appendIndex(cleanSplit[0], cleanObj[len(cleanSplit[0]):], path)
	
				renameFile(fullPath, cleanPath, rename)
	
		#If the cleaned and original versions are the same, check that there's no case clash with a previously seen file
		else:
	
			if caseSens:		
				
				extension = ""

				if fullPath.lower() in lCaseList:
					
					filename = fullPath.split('/')[-1]
					
					#This could be spun off into a function, save some coding - bound to be reusable too.
					if "." in filename:
						extension = "." + filename.split(".")[-1]
						filename = filename[:-len(extension)]
				
					cleanPath = appendIndex(filename, extension, path)
	
					renameFile(fullPath, cleanPath, rename)



	 	#Append the clean (i.e final) path to the array which will allow us to check for case sensitive clashes, if the case sensitive option is set. 
	 	if caseSens:
			lCaseList.append(cleanPath.lower())

		if oversizeLogFileName is not None:
			if len(fullPath) > 254:
				if not quiet:
					print timeStamp() + "--WARNING-- Overlong directory found: " + cleanPath + " is " + str(len(cleanPath)) + " characters long.\n"
				if oversizeLogFileName is not None:
					oversizeFile.write( timeStamp() + "Oversize directory: " + cleanPath + "\n")
					oversizeFile.write(str(len(cleanPath)) + " characters long.\n\n")

def usage():
		print ("\nSanitisePath - this version for use in 'hot folders' on SANs. Please contact josh.smith@hogarthww.com or giles.barford@hogarthww.com for further versions.")
		print ("\nUsage:")
	
		print ("   -c, --casesensitive: For use on case sensitive filesystems. Default - off.")
		print ("   -d, --dorename:      Actually rename the files - otherwise just log and output to standard output.")
		print ("   -e, --errorlog:      Error log (contains files which have thrown errors on rename.")
		print ("   -h, --help:          Print this help and exit.")
		print ("   -l, --location:      Location/name of the share (E.g HGSL_SAN)")
		print ("   -o, --oversizelog:   Log to write files with overlong path names in - otherwise don't log.")
		print ("   -p, --passdir:       Directory to which clean files should be moved.")
		print ("   -q, --quiet:         Don't output to standard out.")
		print ("   -r, --root:          Directory to sanitise (otherwise use working directory).")
		print ("   -t, --target:        The location of the hot folder\n")

def closeFile(theFile):
#Used to close pid files on unexpected exit
	os.unlink(theFile)

def prepend(pre, post):
#If 'pre' is defined, append it to post, concatenate and return
	if pre != None:
	
		return pre + post
	
	else:
		return post

def unescape(fromStr):
#Removes backslashes used to escape characters
	return fromStr.replace('\\','')

#Write PID file (prevents process from running multiple times syncronously.
pidFile = "/tmp/SanitisePaths.pid"

if os.path.isfile(pidFile):
	print "PIDfile already exists - exiting"
	sys.exit()
else:
	pf = open(pidFile, 'w')
	file(pidFile, 'w').write(str(os.getpid()))

atexit.register(closeFile, theFile=pidFile)

try:
		opts, args = getopt.getopt(sys.argv[1:], "o:r:e:t:l:dhqc", ["oversizelog=","root=", "errorlog=","target=","location=","dorename","help","quiet","debug","casesensitive"])

except getopt.GetoptError as err:
		# print help information and exit:
		usage()
		print str(err) # will print something like "option -a not recognized"
		
		sys.exit(2)	

sanitisedList=[]
errorList=[]
lCaseList=[]

#These can be reconfigured depending on the folder structure
toArchiveDir = "./To_Archive"
passDir =  "./Passed_For_Archive"
illegalLogDir = "./Illegal_File_Logs"

#Argument variables
rename=False
theRoot = toArchiveDir
oversizeLogFileName = None
errorLogFileName = None
quiet = False
debug = False #NB - this variable used only during development, so not in the --help. 
oldPath = ""
caseSens = False
target = None
location = None

for o, a in opts:
		
		if o in ("-r","--root"):
				theRoot = unescape(a)
		elif o in ("-d","--dorename"):
				rename = True
		elif o in ("-h","--help"):
				usage()
				sys.exit(2)	
		elif o in ("-q","--quiet"):
				quiet = True
		elif o in ("-o","--oversizelog"):
				oversizeLogFileName = a
				oversizeOut = os.path.abspath(oversizeLogFileName)
				oversizeFile = open (oversizeOut, 'w')
		elif o in ("--debug"):
				debug = True
		elif o in ("-c", "--casesensitive"):
				caseSens = True
		elif o in ("-e", "--errorlog"):
				errorLogFileName = a
				errorOut = os.path.abspath(errorLogFileName)
				errorFile = open (logOut, 'w')
		elif o in ("-l", "--log"):
				illegalLogDir = a
		elif o in ("-p", "--passdir"):
				passDir = a
		elif o in ("-t", "--target"):
				target = a
				theRoot = unescape(prepend(target, theRoot))
				illegalLogDir = unescape(prepend(target, illegalLogDir))
				passDir = unescape(prepend(target, passDir))
		elif o in ("-l", "--location"):
				location = a

#These are the characters we want to remove
blackList = '`\/?"<>|*'

#MAIN FUNCTION:
#Save the first argument to a normalised logRoot variable
for folder in immediateSubdirs(theRoot):

	logFileName = folder + ' illegal files log.txt'
	logPath = illegalLogDir + '/' + logFileName
	
	targetPath = theRoot + '/' + folder

	#Limit filenames to shorter than 260 chars
	logPath = logPath[:259]

	logOut = os.path.abspath(logPath)
	
	logFile = open (logOut, 'w')

	errorsFound = False

	#Sanitise the directory itself:
	renameToClean(theRoot, folder, 'dir')

	for thePath, theDirs, theFiles in os.walk(targetPath, topdown=False):

			#Sanitise file names
			for f in theFiles:
				renameToClean(thePath, f, 'file')
					
			#Sanitise directory names
			for d in theDirs:
					renameToClean(thePath, d, 'dir')

	if not errorsFound:
		os.rename(targetPath, passDir + '/' + folder)


#		#Colour the directory red. Might be worth exploring these functions - I found it at http://stackoverflow.com/questions/8328493/getting-and-setting-mac-file-and-folder-finder-labels-from-python
#		attrs = xattr(theRoot + '/' + folder)
#
#		try:
#			plistKey = u'com.apple'
#			finderAttrs = attrs[u'com.apple.FinderInfo']
#			flags = unpack(32*'B', finder_attrs)
#			color = flags[9]

sys.exit(0)


