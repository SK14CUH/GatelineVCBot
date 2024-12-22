#!/bin/bash

cd ~/GatelineVCBotNew
. bot-env/bin/activate
python3 backup.py >> log$1.txt
