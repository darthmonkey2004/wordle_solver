#!/bin/bash

haspip=$(which pip3)
if [ -z "$haspip" ]; then
	sudo apt-get install -y python3-pip3
fi
pip3 install --user "dist/wordle_helper-1.0.tar.gz" -r requirements.txt
