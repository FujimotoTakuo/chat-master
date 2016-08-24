# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys
import time

import tensorflow.python.platform

import numpy as np
from six.moves import xrange
import tensorflow as tf

import data_utils_twitter as data_utils
from tensorflow.models.rnn.translate import seq2seq_model
from tensorflow.python.platform import gfile

def read_data(source_path, target_path, max_size=None):
  data_set = [[] for _ in _buckets]
  source_file = open(source_path,"r")
  target_file = open(target_path,"r")

  source, target = source_file.readline(), target_file.readline()
  counter = 0
  while source and target and (not max_size or counter < max_size):
    counter += 1
    if counter % 50 == 0:
      print("  reading data line %d" % counter)
      sys.stdout.flush()

    source_ids = [int(x) for x in source.split()]
    target_ids = [int(x) for x in target.split()]
    src_len = len(source_ids)
    tgt_len = len(target_ids)
    big_len = 0
    if src_len > tgt_len:
        big_len = src_len
    else :
        big_len = tgt_len
    # 知恵袋ALLを散布図で表したい。
    # 視覚的に、単語数がどんなもんになるのかを確認して、バケツのサイズ感の参考にしたい
    target_ids.append(data_utils.EOS_ID)
    for bucket_id, (source_size, target_size) in enumerate(_buckets):
      if len(source_ids) < source_size and len(target_ids) < target_size:
        data_set[bucket_id].append([source_ids, target_ids])
        break
    source, target = source_file.readline(), target_file.readline()
  return data_set

### Execute
if __name__ == "__main__":
    in_train = os.path.join('datas', 'train_data_ids_in.txt')
    out_train = os.path.join('datas', 'train_data_ids_out.txt')
    in_dev = os.path.join('datas', 'test_data_ids_in.txt')
    out_dev = os.path.join('datas', 'test_data_ids_out.txt')
