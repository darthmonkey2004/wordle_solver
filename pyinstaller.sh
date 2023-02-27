#!/bin/bash

is_installed=$(which wordle)
if [ -n "$is_installed" ]; then
	echo "Already appears to be installed! Aborting setup..."
	exit 0
fi
cd ~/
haswget=$(which wget)
if [ -z "$haswget" ]; then
	sudo apt-get install -y wget
fi
hasunzip=$(which unzip)
if [ -z "$hasunzip" ]; then
	sudo apt-get install -y unzip
fi
url = 'https://drive.google.com/file/d/1POSJIqyRjLGsKuMiB2mJdkQpR0WywZy7/view?usp=sharing'
zipfile="$HOME/Downloads/wordle_helper.zip"
wget -o "$zipfile" "$url"
unzip "$zipfile" -d "$HOME/.local/etc"
sudo ln -s "$HOME/.local/etc/wordle_helper/wordle_helper" "$HOME/.local/bin/wordlehelper"
rcpatched=$(cat "$HOME/.bashrc" | grep "/.local/bin")
if [ -z "$rcpatched" ]; then
	echo "export PATH=\"$PATH:$HOME/.local/bin\"" >> "$HOME/.bashrc"
	export PATH="$PATH:$HOME/.local/bin"
fi
