#!/bin/sh
# ==============================================================================
# Jarvis OS: Shell Aliases & Smart Terminal Integration
# ==============================================================================

# ?? <prompt> triggers the smart shell assistant
alias \?\?='/usr/bin/python3 /opt/jarvis-core/tools/shell_assistant.py'

# jarvis CLI & Package Manager shortcuts
alias jarvis='/usr/bin/python3 /opt/jarvis-core/tools/jarvis_cli.py'
alias jarvis-pkg='/usr/bin/python3 /opt/jarvis-core/tools/pkg_manager.py'
alias jarvis-commit='/usr/bin/python3 /opt/jarvis-core/tools/shell_assistant.py commit'
alias zen='jarvis mode zen'
alias desktop='jarvis mode desktop'
alias ambient='jarvis mode jarvis'
alias jarvis-mode='jarvis mode'
alias jarvis-theme='jarvis theme'

# Linux Power Tools Quality-of-Life Aliases
alias bat='batcat 2>/dev/null || bat'
alias fd='fdfind 2>/dev/null || fd'
alias top='btop 2>/dev/null || htop 2>/dev/null || top'
alias fetch='fastfetch 2>/dev/null || neofetch 2>/dev/null'
alias ll='ls -lah --color=auto'
alias grep='grep --color=auto'
