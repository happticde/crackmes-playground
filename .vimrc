colorscheme molokai

syntax on                       " Enable syntax highlighting.
filetype plugin indent on       " Enable file type based indentation.

set number	                    " Show line numbers
set linebreak	                " Break lines at word (requires Wrap lines)
set showbreak=+++	            " Wrap-broken line prefix
set textwidth=100	            " Line wrap (number of cols)
set showmatch	                " Highlight matching brace
set visualbell	                " Use visual bell (no beeping)
 
set hlsearch	                " Highlight all search results
set smartcase	                " Enable smart-case search
set incsearch	                " Searches for strings incrementally
 
set autoindent	                " Auto-indent new lines
set expandtab	                " Use spaces instead of tabs
set shiftwidth=2	            " Number of auto-indent spaces
set smartindent	                " Enable smart-indent
set smarttab	                " Enable smart-tabs
set softtabstop=2	            " Number of spaces per Tab
 
set ruler	                    " Show row and column ruler information
 
set undolevels=1000	            " Number of undo levels
set backspace=indent,eol,start	" Backspace behaviour

set backspace=2                 " Fix backspace behavior on most terminals.