#!/usr/bin/expect
send "Interacting with Fontwise...\n"

spawn ./fontwise/FW_Client

expect "Starting Path : " { send "\r" }
expect "<y/n>" { send "y\r" }

#Set expect to never timout, allow the script to complete, then exit successfully if eof is encountered.
set timeout -1
expect "Total Font File" { 
	expect "Finish" {
		exit 0
	}	
}
