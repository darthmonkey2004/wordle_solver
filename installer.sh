#!/bin/bash

echo "Installing..."
sudo apt-get install -y chromium-bsu chromium-chromedriver python3-selenium 
dir=$(pwd)
tarfile=$(find "$dir" -name "*wordle*" | grep "tar.gz")
echo "installing tarball: '$tarfile'..."
pip3 install --user "$tarfile" -r requirements.txt
echo "Checking bashrc.."
rcpatched=$(cat "$HOME/.bashrc" | grep "/.local/bin")
if [ -z "$rcpatched" ]; then
	echo "Patching bashrc to add .local/bin to path..."
	echo "export PATH=\"$PATH:$HOME/.local/bin\"" >> "$HOME/.bashrc"
	export PATH="$PATH:$HOME/.local/bin"
else
	echo "bashrc already contains .local/bin! Skipping patch.."
fi
echo "Done!"
