#!/bin/sh

cur=`pwd`
shDir=`dirname $0`
cd $shDir
homeDir=`pwd`

for file in `ls text`
do
  nohup python ../anlzMaCab/MeCabFuji.py $homeDir/text/$file &
done

cd $cur

