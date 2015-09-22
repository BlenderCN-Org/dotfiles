#!/bin/bash

# Init git submodules
git submodule init
git submodule update
git submodule foreach git submodule init
git submodule foreach git submodule update

# Install Vudle plugins
vim +PluginInstall +qall
