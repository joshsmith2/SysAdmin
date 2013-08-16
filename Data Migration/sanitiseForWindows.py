#sanitiseForWindows dir[String], log[String], readonlyFlag[String, on="-readonly", default off]
#This script will check through all subfolders and files inside dir and remove all occurences of problematic characters 

import sys
import os
import os.path
import re

sanitisedList=[]
errorList=[]


#These are the characters we want to remove
blackList = '\/?"<>|*'


def sanitise(inString):
#This function removes any occurences of characters found in blackList from theString, except ':' which, for legibility, are changed to '-'
	
	outString = inString.translate(None, blackList)
	
	#Remove all whitespace from filenames except spaces (from http://stackoverflow.com/questions/1898656/remove-whitespace-in-python-using-string-whitespace)
	outString = ' '.join(outString.split())
	
	#Substitute hyphens for colons, to help legibility
	outString = re.sub(':','-',outString)
	
	return str(outString)
	
def renameToClean(path, obj, objType):
	#Takes an object (a string - either a file or a directory, as defined in 'type' which must be one of 'file' or 'dir') and, if the string has any forbidden characters, sanitises it and renames it.

	cleanObj = sanitise(obj)
		
	#If sanitise has made any difference, record the file in a list of changed files, then rename the file. 
	if cleanObj != obj:

		#Separate filename from extension:
		cleanSplit = cleanObj.split('.')
		
		#For files and directories which were only composed of illegal characters, rename these 'Renamed file' or 'Renamed Folder' 
		if cleanSplit[0].strip() == '':
			if objType == 'file':
				cleanObj = 'Renamed File' + cleanObj[len(cleanSplit[0]):]
			elif objType == 'dir':
				cleanObj = 'Renamed Folder'
		
		fullPath = os.path.join(path, obj)
		cleanPath = os.path.join(path, cleanObj)		
	
		#Change the ouput if in readonly mode
		if readonlyFlag == "-readonly":
			notification = "Will change: "
		else:
			notification = "Changed: "

		sanitisedList.append(notification + fullPath)
		sanitisedList.append("To:      " + cleanPath + "\n")

		print notification + fullPath
		print "To:      " + cleanPath + "\n"
	
		
		#If the clean path already exists, append '(n)' to the filename
		if os.path.exists(cleanPath):
			
			i=1	
			
			cleanAppended = cleanSplit[0] + "(" + str(i) + ")" + cleanObj[len(cleanSplit[0]):]	
		
			#Check for existing files appended with (1), (2) etc
			while os.path.exists(os.path.join(path, cleanAppended)):
				i += 1
				cleanAppended = cleanSplit[0] + "(" + str(i) + ")" + cleanObj[len(cleanSplit[0]):]
			
			cleanPath = os.path.join(path, cleanAppended)
		
		#Rename the files
		if readonlyFlag != "-readonly":
			
			try:
				os.rename(fullPath, cleanPath)
			except OSError:
				errorList.append(fullPath)

			
			
#MAIN FUNCTION: 
#Save the first argument to a normalised theRoot variable
try:
	theRoot = os.path.abspath(sys.argv[1])
except:
	print "Error: no directory given. Syntax: sanitiseForWindows.py dir logs -readonly" 
	quit()


#Check for the 'readonly' flag - if not there, set to off
try:
	readonlyFlag = sys.argv[3]
except:
	readonlyFlag = "-noreadonly"	

if readonlyFlag != "-readonly":

	renamePrompt = raw_input("This will rename any files with illegal characters in " +	theRoot +": Is this ok? <y/n>").lower()

	if renamePrompt != "y":
		quit()


for thePath, theDirs, theFiles in os.walk(theRoot, topdown=False):
	
	#Sanitise file names
	for f in theFiles:
		renameToClean(thePath, f, 'file')
	
	#Sanitise directory names
	for d in theDirs:
		renameToClean(thePath, d, 'dir')

#Open log file if given
try:
	logOut = os.path.abspath(sys.argv[2])

	logFile = open (logOut, 'w')

	logFile.write( '---------------------------------------------------------------------------------------------\n \t Changed Files and Directories: \n---------------------------------------------------------------------------------------------\n' ) 
	logFile.write( '\n'.join(sanitisedList) + '\n')
	logFile.write( '\n---------------------------------------------------------------------------------------------\n \t Errors: (Likely to be duplicately named files)\n---------------------------------------------------------------------------------------------\n' ) 
	logFile.write( '\n'.join(errorList))
	
except:
	print "Log root unspecified or onopenable. SYNTAX: sanitiseForWindows.py dir logs -readonly"
	quit()
