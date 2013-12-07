filetype off
call pathogen#infect()
"call pathogen#runtime_append_all_bundles()
call pathogen#helptags()

set foldmethod=indent
set foldlevel=99
set number
set ruler
set mouse=nicrv
set ttymouse=xterm2
set background=dark

syntax on	"syntax highlighting
filetype plugin indent on	"enable loading indent file for filetype
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
map <F3> :NERDTree<CR>
let g:NERDTreeWinPos = "right"


" Tagbar
nnoremap <silent> <F9> :TagbarToggle<CR>
let g:tagbar_left = 1
let g:tagbar_sort = 0

" Run python file
"map <F5> :!python

" Powerline
set rtp+=~/.vim/bundle/powerline/powerline/bindings/vim
set laststatus=2
let g:ambiwidth="single"
let g:Powerline_symbols = "fancy"

" Flake8
autocmd BufWritePost *.py call Flake8()

" Autoclose pairs
let g:autoclose_on = 0

" Smart <Home> key
noremap <expr> <silent> <Home> col('.') == match(getline('.'),'\S')+1 ? '0' : '^'
imap <silent> <Home> <C-O><Home>
