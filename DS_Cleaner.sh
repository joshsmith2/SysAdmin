#!/bin/bash

for dir in ./; do 
	
	if [[ -d "$dir" ]];

		then for subdir in "$dir/"*; do
			sudo find -x "$subdir" -name '.DS_Store' -type f -print0 | xargs -0 sudo rm -vf;
		done;
		
		rm -vf $dir/.DS_Store;

	fi;

done
