#!/bin/bash

hgrcContent="
[patch]
eol = auto

[ui]
username = $USER@$HOSTNAME
editor = vim

[trusted]
users = $USER
groups = $USER

[extensions]
graphlog =
"

mv ~/.hgrc ~/.hgrc-old
echo "$hgrcContent" > ~/.hgrc

