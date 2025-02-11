This tool will backdoor all bashrc files on a system. The tool also will manage connections initiated using the shells spawned through the bashrc backdoor

Usage:
	Start the control server using 'python3 server.py
	Modify install.sh to use the IP of your server's system
	Run install.sh on the target system to append a bashrc backdoor onto all user's bashrc file
	When a user opens a new shell, you will get a connection
	Type help in the server to see a list of commands (or look below)

Server commands:
	help		-	print command options
	shells		-	print available shells
	[number]	-	connect to specified shell
	leave		-	leave connected shell without closing
	exit		-	close connected shell
	exit/quit	-	close server

Shortened commands:
	help   ->  h
	shells ->  s
        leave  ->  l
