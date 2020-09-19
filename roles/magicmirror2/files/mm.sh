#!/bin/bash

# Needed to display correct times when HW clock is UTC
export TZ=America/Denver

cd ~/MagicMirror
DISPLAY=:0 npm start