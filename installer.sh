#!/bin/bash

is_installed=$(which wordle)
if [ -n "$is_installed" ]; then
	echo "Already appears to be installed! Aborting setup..."
	exit 0
fi
cd ~/
haspip=$(which pip3)
if [ -z "$haspip" ]; then
	echo "PyPi not installed! Installing..."
	sudo apt-get install -y python3-pip3
fi
hasgit=$(which git)
if [ -z "$hasgit" ]; then
	echo "GIT cli not installed! Installing..."
	sudo apt-get install -y git
fi
echo "Downloading from git repo..."
git clone "https://darthmonkey2004/wordle_helper.git"
cd wordle_helper
echo "Installing..."
pip3 install --user "dist/wordle_helper-1.0.tar.gz" -r requirements.txt
rcpatched=$(cat "$HOME/.bashrc" | grep "/.local/bin")
if [ -z "$rcpatched" ]; then
	echo "Patching bashrc to add .local/bin to path..."
	echo "export PATH=\"$PATH:$HOME/.local/bin\"" >> "$HOME/.bashrc"
	export PATH="$PATH:$HOME/.local/bin"
else
	echo "bashrc already contains .local/bin! Skipping patch.."
fi
echo "Done!"
