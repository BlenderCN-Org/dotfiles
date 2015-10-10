set nocompatible
filetype off

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" ----- Making vim look good
Plugin 'blueshirts/darcula'
Plugin 'bling/vim-airline'

" ----- Working with git
Plugin 'tpope/vim-fugitive'
Plugin 'airblade/vim-gitgutter'

" ----- Dev tools
Plugin 'Raimondi/delimitMate'
Plugin 'scrooloose/nerdtree'
Plugin 'jistr/vim-nerdtree-tabs'
Plugin 'kien/ctrlp.vim'
Plugin 'vim-scripts/a.vim'
Plugin 'scrooloose/syntastic'
Plugin 'klen/python-mode'


call vundle#end()
filetype plugin indent on	"enable loading indent file for filetype

set foldmethod=indent
set foldlevel=99
set number
set ruler
set mouse=nicrv
set ttymouse=xterm2

syntax enable	"syntax highlighting

colorscheme darcula
autocmd colorscheme * hi Normal ctermbg=none
autocmd colorscheme * hi NonText ctermbg=none

autocmd FileType python set omnifunc=pythoncomplete#Complete

" set smartindent
" set tabstop=4
" set shiftwidth=4
" set autoindent
" set expandtab

" set backspace=indent,eol,start


imap <C-Space> <C-x><C-o>
imap <C-@> <C-Space>

"This unsets the "last search pattern" register by hitting return
nnoremap <CR> :noh<CR><CR>

vnoremap < <gv
vnoremap > >gv

" Reload .vimrc when saved
au BufWritePost .vimrc so ~/.vimrc

set scrolloff=8

" PyDiction settings
let g:pydiction_location = '~/.vim/bundle/pydiction/complete-dict'

" Autostart NERDTree
"autocmd VimEnter * NERDTree
"autocmd VimEnter * wincmd p
"map <F3> :NERDTree<CR>
map <F3> <plug>NERDTreeTabsToggle<CR>
let g:NERDTreeWinPos = "right"


" Tagbar
nnoremap <silent> <F9> :TagbarToggle<CR>
let g:tagbar_left = 1
let g:tagbar_sort = 0

" Run python file
"map <F5> :!python

" Powerline
"set rtp+=~/.vim/bundle/powerline/powerline/bindings/vim
"set laststatus=2
"let g:ambiwidth="single"
"let g:Powerline_symbols = "fancy"

" Airline
let g:airline#extensions#tagbar#enabled=1
let g:airline_powerline_fonts=1
set laststatus=2
set ttimeoutlen=50
set t_Co=256

" Flake8
autocmd BufWritePost *.py call Flake8()

" Autoclose pairs
let g:autoclose_on = 0

" Smart <Home> key
noremap <expr> <silent> <Home> col('.') == match(getline('.'),'\S')+1 ? '0' : '^'
imap <silent> <Home> <C-O><Home>

" Snipmate
ino <c-j> <c-r>=snipMate#TriggerSnippet()<cr>
snor <c-j> <esc>i<right><c-r>=snipMate#TriggerSnippet()<cr>
