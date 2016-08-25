#!/bin/sh

cp nohup.out bak_nohup.out
cat /dev/null > nohup.out

nohup python x_translate.py &

