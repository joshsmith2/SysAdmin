$i=0
$sourceDir = @()
$destDir = @()
$notCopied = @()
$copied=0
$sourceRoot="\\svr005.hogarthww.prv\Clients\"
$destRoot="F:\Shares\Clients\"
$sourceFile="E:\BatchScripts\ClientsTree.txt"
$destFile="E:\BatchScripts\TargetTree.txt"

#Read source and destination directories into a file. NOTE: This will overwrite any existing log. 
dir $sourceRoot -name | Out-file $sourceFile
#dir $destRoot -name | Out-file $destFile

#Read contents of txt files contining the origin and target directories into an array
Get-Content $sourceFile | ForEach-Object {
	
	$sourceDir = $sourceDir += $_

}

<#
Get-Content $destFile | ForEach-Object {

	$destDir = $destDir += $_	

}#>

#Output any non-copied files into notCopied
foreach ($f in $sourceDir) { 

	# copied checks to see if this file has already been robocopied - set this to 'no'
	$copied = 0
	
	<#foreach ($e in $destDir) {
		
		#If there's a match between a dir in F and one in E, flip 'copied' to 1 if it's not already. Could improve this by exiting the loop once a match is found. 
		if ($f -eq $e -and $copied -eq 0){
			$copied=1
		}
	}#>

	#copy any files which have not already been transferred
	if ($copied -eq 0){
		$fullSource= "$sourceRoot$f"
		$fullDest = "$destRoot$f"
		robocopy $(echo $fullSource) $(echo $fullDest) /MIR /MT /V /W:1 /R:0 /LOG:E:\scriptLogs\run06\robocopy-$f.log
	}
}