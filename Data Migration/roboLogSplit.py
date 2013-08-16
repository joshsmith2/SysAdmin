import sys 
import os 
import os.path

#Syntax: roboLogSplit logFile[STRING] outDir[STRING]

f = os.path.abspath(sys.argv[1])
outDir = os.path.abspath(sys.argv[2])

inFile = open(f, 'r')

#Stores the name of the current folder in clients
folderName = ""
outFile = ""
outList = []


for l in inFile:
	if l.strip() != "":	
		#Get position of first "/" after the folder name
		i = 56
		j = ""
		while j != "/":
			i += 1 
			j = l[i]
		
		currentDir = l[55:i]

		#If the current directory is different to the previous one, and we're not on the 0th run, wrte outList to file
		if folderName == "":
			folderName = currentDir
		else:
			if folderName == currentDir:
				outList.append(l)	
			else:
				o = outDir + "/" + folderName + ".txt"
				outFile = open(o, 'w')
				outFile.write( '\n'.join(outList) )
				folderName = currentDir

				outList = [l]

