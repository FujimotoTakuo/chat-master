#!/bin/sh

moto=`pwd`
cd $(dirname $0)
datas=`pwd`

rm $datas/*.txt

cat /dev/null > $datas/test_data_ids_out.txt
cat /dev/null > $datas/test_data_ids_in.txt
cat /dev/null > $datas/train_data_ids_out.txt
cat /dev/null > $datas/train_data_ids_in.txt
cat /dev/null > $datas/vocab_in.txt
cat /dev/null > $datas/vocab_out.txt

cd $moto
