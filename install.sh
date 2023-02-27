#!/bin/bash

haspip=$(which pip3)
if [ -z "$haspip" ]; then
	sudo apt-get install -y python3-pip3
fi
python3 setup.py sdist
pip3 install --user "dist/wordle_solver-1.1.tar.gz" -r requirements.txt
