#!/bin/bash

gituser="makerdrone"
gitemail="makerdrone@gmail.com"

if [ $USER != "drd" ] && [ $USER != "pi" ]; then
	gituser=$USER
	gitemail=$HOSTNAME
fi

if [ $USER = "Clouway" ]; then
	gituser="stefan.dimitrov"
	gitemail="stefan.dimitrov.009@gmail.com"
fi

gitContent="
[alias]
st = status
glog = log --graph --decorate --oneline --all
glogm = log --graph --decorate --all

[user]
	name = $gituser
	email = $gitemail
[core]
	editor = vim
	autocrlf = input

[color]
	ui = true
"

mv gitconfig gitconfig-old

echo "$gitContent" > gitconfig

