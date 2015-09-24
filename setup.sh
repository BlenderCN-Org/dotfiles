#!/bin/bash

# Init git submodules
git submodule init
git submodule update
git submodule foreach git submodule init
git submodule foreach git submodule update

# Install Vudle + plugins
git clone https://github.com/VundleVim/Vundle.vim.git vim/bundle/Vundle.vim
vim +PluginInstall +qall
