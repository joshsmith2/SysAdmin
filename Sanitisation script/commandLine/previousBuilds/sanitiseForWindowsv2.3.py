#!/usr/bin/python
#This script will check through all subfolders and files inside dir and remove all occurences of problematic characters

import sys
import os
import os.path
import re
import getopt

#Define functions:

def sanitise(inString):
#This function removes any occurences of characters found in blackList from theString, except ':' which, for legibility, are changed to '-'

		outString = inString.translate(None, blackList)

		#Remove all whitespace from filenames except spaces (from http://stackoverflow.com/questions/1898656/remove-whitespace-in-python-using-string-whitespace)
		#outString = ' '.join(outString.split())

		#Substitute hyphens for colons, to help legibility
		outString = re.sub(':','-',outString)

		return str(outString)


#Given a file 'filename' at location 'path' with extension '.ext', this will return the path of filename(n).ext, where n is the lowest integer for which filename(n-1).ext already exitsts.
def appendIndex(filename, ext, path):
	
	index = 1

	appendedFile = filename + "(" + str(i) + ")." + ext

	appendedPath = os.path.join(path, appendedFile)

	while os.path.exists(appendedPath) or appendedPath in sanitisedList
		
		i += 1
		appendedFile = filename + "(" + str(i) + ")." + ext
		appendedPath = os.path.join(path, appendedFile)

	return appendedPath

def renameToClean(path, obj, objType):
		#Takes an object (a string - either a file or a directory, as defined in 'type' which must be one of 'file' or 'dir') and, if the string has any forbidden characters, sanitises it and renames it.

		cleanObj = sanitise(obj)
		cleanPath = os.path.join(path,obj) #NB - this variable will be changed if any sanitisation takes place. It's here so that it can be used when flagging up long filenames. 

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

				fullPath = os.path.join(path, obj)
				cleanPath = os.path.join(path, cleanObj)

				#If the clean path already exists, append '(n)' to the filename
				if os.path.exists(cleanPath) or cleanPath in sanitisedList:

						appendIndex(cleanSplit[0], cleanObj[len(cleanSplit[0])-1:], path)
		
#						i=1
#
#						cleanAppended = cleanSplit[0] + "(" + str(i) + ")" + cleanObj[len(cleanSplit[0]):]
#
#						#Check for existing files appended with (1), (2) etc
#					
#						appendedPath = os.path.join(path, cleanAppended)
#
#						while os.path.exists(appendedPath) or appendedPath in sanitisedList:
#								i += 1
#								cleanAppended = cleanSplit[0] + "(" + str(i) + ")" + cleanObj[len(cleanSplit[0]):]
#								appendedPath = os.path.join(path, cleanAppended)
#
#						cleanPath = os.path.join(path, cleanAppended)

				if rename:
					try:
								os.rename(fullPath, cleanPath)
								if not quiet:
									print "Changed from: " + fullPath
									print "Changed to:   " + cleanPath + "\n"
								if logFileName is not None:
									logFile.write( "Changed from: " + fullPath + "\n")
									logFile.write( "Changed to:	" + cleanPath + "\n")
					except OSError:
								print "Error: unable to rename " + fullPath
								if logFileName is not None:
									logFile.write("Error: unable to rename " + fullPath)

				else:
					#Add the clean path to a list of changed files, so that logging without changing works correctly
					sanitisedList.append(cleanPath)


					if not quiet:
						print "Would change:    " + fullPath
						print "Would change to: " + cleanPath + "\n"
				
					if logFileName is not None:
						logFile.write( "Would change:	 " + fullPath + "\n")
						logFile.write( "Would change to: " + cleanPath + "\n")
	
		if oversizeLogFileName is not None:
			if len(cleanPath) > 254:
				if not quiet:
					print "--WARNING-- Overlong directory found: " + cleanPath + " is " + str(len(cleanPath)) + " characters long.\n"
				if oversizeLogFileName is not None:
					oversizeFile.write("Oversize directory: " + cleanPath + "\n")
					oversizeFile.write(str(len(cleanPath)) + " characters long.\n\n")

def usage():
		print ("Usage " + sys.argv[1] + ":")
		print ("   -d, --dorename:	   Actually rename the files otherwise just log and output to standard output")
		print ("   -h, --help:		   Print this help and exit")
		print ("   -l, --log:		   Log filename; otherwise don't log ")
		print ("   -o, --oversizelog:  Log to write files with overlong path names in - otherwise don't log.")
		print ("   -q, --quiet:		   Don't output to standard out")
		print ("   -r, --root:		   Root directory otherwise use working directory")

try:
		opts, args = getopt.getopt(sys.argv[1:], "o:l:r:dhqb", ["oversizelog=","log=", "root=", "dorename","help","quiet"])
except getopt.GetoptError as err:
		# print help information and exit:
		usage()
		print str(err) # will print something like "option -a not recognized"
		sys.exit(2)

sanitisedList=[]
errorList=[]
rename=False
theRoot = "."
logFileName = None
oversizeLogFileName = None
quiet = False

for o, a in opts:
		if o in ("-r","--root"):
				theRoot = a
		elif o in ("-l","--log"):
				logFileName = a
				logOut = os.path.abspath(logFileName)
				logFile = open (logOut, 'w')
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


#These are the characters we want to remove
blackList = '`\/?"<>|*\n\t'


#MAIN FUNCTION:
#Save the first argument to a normalised logRoot variable


for thePath, theDirs, theFiles in os.walk(theRoot, topdown=False):

		#Sanitise file names
		for f in theFiles:
				renameToClean(thePath, f, 'file')

		#Sanitise directory names
		for d in theDirs:
				renameToClean(thePath, d, 'dir')


