export ZSH="/home/nsilverman/.oh-my-zsh"

ZSH_THEME="risto"

plugins=(
  git
  ruby
  bundler
  python
  archlinux
  virtualenvwrapper
  zsh-autosuggestions
  zsh-completions
)

source $ZSH/oh-my-zsh.sh
autoload -U compinit && compinit

alias vim='nvim'
