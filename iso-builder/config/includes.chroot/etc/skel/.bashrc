# ~/.bashrc for Jarvis OS (Debian Edition)

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# Source global definitions & Jarvis aliases
if [ -f /etc/bash.bashrc ]; then
    . /etc/bash.bashrc
fi

if [ -f /etc/profile.d/jarvis-aliases.sh ]; then
    . /etc/profile.d/jarvis-aliases.sh
fi

# Enable color support
if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
    color_prompt=yes
else
    color_prompt=
fi

# Custom Minimalist Prompt
if [ "$color_prompt" = yes ]; then
    PS1='\[\033[01;36m\]jarvis\[\033[00m\]@\[\033[01;34m\]jarvis-os\[\033[00m\]:\[\033[01;32m\]\w\[\033[00m\]\$ '
else
    PS1='jarvis@jarvis-os:\w\$ '
fi
unset color_prompt

# Quality of Life history settings
HISTCONTROL=ignoreboth
HISTSIZE=5000
HISTFILESIZE=10000
shopt -s histappend
shopt -s checkwinsize

# Terminal Greeting
if [ -n "$PS1" ] && [ -x /usr/bin/fastfetch ]; then
    fastfetch 2>/dev/null
elif [ -n "$PS1" ] && [ -x /usr/bin/neofetch ]; then
    neofetch 2>/dev/null
fi
