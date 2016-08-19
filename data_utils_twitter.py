#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gzip
import os
import re
import tarfile
import tweet_crawler as tc

from tensorflow.python.platform import gfile
from six.moves import urllib

import time
from datetime import datetime as dt, timedelta
import shutil


_PAD = "_PAD"
_GO = "_GO"
_EOS = "_EOS"
_UNK = "_UNK"
_START_VOCAB = [_PAD, _GO, _EOS, _UNK]

PAD_ID = 0
GO_ID = 1
EOS_ID = 2
UNK_ID = 3

_WORD_SPLIT = re.compile("([.,!?\"':;)(])")
_DIGIT_RE = re.compile(r"\d")


def basic_tokenizer(sentence):
    words = []
    for space_separated_fragment in sentence.strip().split():
        words.extend(re.split(_WORD_SPLIT, space_separated_fragment))
    # 配列wordsを展開したw("w for w in words")のうち、ブランクでなかったw(if w)を返却する配列に入れて返す
    return [w for w in words if w]


def create_vocabulary(vocabulary_path, data_path, max_vocabulary_size,
                      tokenizer=None, normalize_digits=True):
    if os.path.exists(vocabulary_path):
        print("Creating vocabulary %s from data %s" % (vocabulary_path, data_path))
        vocab = {}

        f = open(data_path,"r")
        counter = 0
        for line in f:
            counter = counter + 1
            if counter % 100 == 0:
                print("  processing line %d" % counter)
            tokens = tokenizer(line) if tokenizer else basic_tokenizer(line)
            for w in tokens:
                word = re.sub(_DIGIT_RE, "0", w) if normalize_digits else w
                if word in vocab:
                    vocab[word] += 1
                else:
                    vocab[word] = 1
        vocab_list = _START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
        if len(vocab_list) > max_vocabulary_size:
            vocab_list = vocab_list[:max_vocabulary_size]

        vocab_file = open(vocabulary_path,"w")
        for w in vocab_list:
            vocab_file.write(w + "\n")
        vocab_file.close()
        f.close()

def create_vocabularyByArray(vocabulary_path, data_path, text_Array, max_vocabulary_size,
                             tokenizer=None, normalize_digits=True):

    if not os.path.exists(vocabulary_path):
        return

    print("Creating vocabulary %s from Twitter_data " % (vocabulary_path))
    vocab = {}

    f = open(data_path,"w")
    counterA = 0
    p = re.compile("([A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)《》◇▼◎⇒💕✨☺♥≪😂💓①♪😀 😬 😁 😂 😃 😄 😅 😆 😇 😉 😊 🙂 🙃 ☺️ 😋 😌 😍 😘 😗 😙 😚 😜 😝 😛 🤑 🤓 😎 🤗 😏 😶 😐 😑 😒 🙄 🤔 😳 😞 😟 😠 😡 😔 😕 🙁 ☹️ 😣 😖 😫 😩 😤 😮 😱 😨 😰 😯 😦 😧 😢 😥 😪 😓 😭 😵 😲 🤐 😷 🤒 🤕 😴 💤 💩 😈 👿 👹 👺 💀 👻 👽 🤖 😺 😸 😹 😻 😼 😽 🙀 😿 😾 🙌 👏 👋 👍 👎 👊 ✊ ✌️ 👌 ✋ 👐 💪 🙏 ☝️ 👆 👇 👈 👉 🖕 🖐 🤘 🖖 ✍️ 💅 👄 👅 👂 👃 👁 👀 👤 👥 🗣 👶 👦 👧 👨 👩 👱 👴 👵 👲 👳 👮 👷 💂 🕵 🎅 👼 👸 👰 🚶 🏃 💃 👯 👫 👬 👭 🙇 💁 🙅 🙆 🙋 🙎 🙍 💇 💆 💑 👩‍❤️‍👩 👨‍❤️‍👨 💏 👩‍❤️‍💋‍👩 👨‍❤️‍💋‍👨 👪 👨‍👩‍👧 👨‍👩‍👧‍👦 👨‍👩‍👦‍👦 👨‍👩‍👧‍👧 👩‍👩‍👦 👩‍👩‍👧 👩‍👩‍👧‍👦 👩‍👩‍👦‍👦 👩‍👩‍👧‍👧 👨‍👨‍👦 👨‍👨‍👧 👨‍👨‍👧‍👦 👨‍👨‍👦‍👦 👨‍👨‍👧‍👧 👚 👕 👖 👔 👗 👙 👘 💄 💋 👣 👠 👡 👢 👞 👟 👒 🎩 ⛑ 🎓 👑 🎒 👝 👛 👜 💼 👓 🕶🍏 🍎 🍐 🐶 🐱 🐭 🐹 🐰 🐻 🐼 🐨 🐯 🦁 🐮 🐷 🐽 🐸 🐙 🐵 🙈 🙉 🙊 🐒 🐔 🐧 🐦 🐤 🐣 🐥 🐺 🐗 🐴 🦄 🐝 🐛 🐌 🐞 🐜 🕷 🦂 🦀 🐍 🐢 🐠 🐟 🐡 🐬 🐳 🐋 🐊 🐆 🐅 🐃 🐂 🐄 🐪 🐫 🐘 🐐 🐏 🐑 🐎 🐖 🐀 🐁 🐓 🦃 🕊 🐕 🐩 🐈 🐇 🐿 🐾 🐉 🐲 🌵 🎄 🌲 🌳 🌴 🌱 🌿 ☘ 🍀 🎍 🎋 🍃 🍂 🍁 🌾 🌺 🌻 🌹 🌷 🌼 🌸 💐 🍄 🌰 🎃 🐚 🕸 🌎 🌍 🌏 🌕 🌖 🌗 🌘 🌑 🌒 🌓 🌔 🌚 🌝 🌛 🌜 🌞 🌙 ⭐️ 🌟 💫 ✨ ☄️ ☀️ 🌤 ⛅️ 🌥 🌦 ☁️ 🌧 ⛈ 🌩 ⚡️ 🔥 💥 ❄️ 🌨 ☃️ ⛄️ 🌬 💨 🌪 🌫 ☂️ ☔️ 💧 💦 🌊 💍 🌂🍊 🍋 🍌 🍉 🍇 🍓 🍈 🍒 🍑 🍍 🍅 🍆 🌶 🌽 🍠 🍯 🍞 🧀 🍗 🍖 🍤 🍳 🍔 🍟 🌭 🍕 🍝 🌮 🌯 🍜 🍲 🍥 🍣 🍱 🍛 🍙 🍚 🍘 🍢 🍡 🍧 🍨 🍦 🍰 🎂 🍮 🍬 🍭 🍫 🍿 🍩 🍪 🍺 🍻 🍷 🍸 🍹 🍾 🍶 🍵 ☕️ 🍼 🍴 🍽 🏀 🏈 ⚾️ 🎾 🏐 🏉 🎱 ⛳️ 🏌 🏓 🏸 🏒 🏑 🏏 🎿 ⛷ 🏂 ⛸ 🏹 🎣 🚣 🏊 🏄 🛀 ⛹ 🏋 🚴 🚵 🏇 🕴 🏆 🎽 🏅 🎖 🎗 🏵 🎫 🎟 🎭 🎨 🎪 🎤 🎧 🎼 🎹 🎷 🎺 🎸 🎻 🎬 🎮 👾 🎯 🎲 🎰 🎳⚽️ 🚗 🚕 🚙 🚌 🚎 🏎 🚓 🚑 🚒 🚐 🚚 🚛 🚜 🏍 🚲 🚨 🚔 🚍 🚘 🚖 🚡 🚠 🚟 🚃 🚋 🚝 🚄 🚅 🚈 🚞 🚂 🚆 🚇 🚊 🚉 🚁 🛩 ✈️ 🛫 🛬 ⛵️ 🛥 🚤 ⛴ 🛳 🚀 🛰 💺 ⚓️ 🚧 ⛽️ 🚏 🚦 🚥 🏁 🚢 🎡 🎢 🎠 🏗 🌁 🗼 🏭 ⛲️ 🎑 ⛰ 🏔 🗻 🌋 🗾 🏕 ⛺️ 🏞 🛣 🛤 🌅 🌄 🏜 🏖 🏝 🌇 🌆 🏙 🌃 🌉 🌌 🌠 🎇 🎆 🌈 🏘 🏰 🏯 🏟 🗽 🏠 🏡 🏚 🏢 🏬 🏣 🏤 🏥 🏦 🏨 🏪 🏫 🏩 💒 🏛 ⛪️ 🕌 🕍 🕋 ⛩◆≫🙏😊😭★✩☆◆]+)")
    private_use = re.compile(ur'[\uE000-\uF8FF]')
    for line in text_Array:
        # print(type(line))
        counterA = counterA + 1
        if counterA % 100 == 0:
            print("  processing line %d" % counterA)
        tokens = tokenizer(line) if tokenizer else basic_tokenizer(line)
        f.write(line + "\n")
        for w in tokens:
            if p.match(w) or private_use.match(w):
                print('match : ' + w)
                continue

            word = re.sub(_DIGIT_RE, "0", w) if normalize_digits else w
            if word in vocab:
                vocab[word] += 1
            else:
                vocab[word] = 1
    vocab_list = _START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
    if len(vocab_list) > max_vocabulary_size:
        vocab_list = vocab_list[:max_vocabulary_size]

    vocab_file = open(vocabulary_path,"w")

    for w in vocab_list:
        print(w)
        # print(type(w))
        vocab_file.write(w + "\n")
    vocab_file.close()
    f.close()

def initialize_vocabulary(vocabulary_path):

    if not os.path.exists(vocabulary_path):
        # raise ValueError("Vocabulary file %s not found.", vocabulary_path)
        file = open(vocabulary_path,"w")
        file.close()

    rev_vocab = []

    f = open(vocabulary_path,"r")
    rev_vocab.extend(f.readlines())
    rev_vocab = [line.strip() for line in rev_vocab]
    vocab = dict([(x, y) for (y, x) in enumerate(rev_vocab)])
    f.close()
    return vocab, rev_vocab


def sentence_to_token_ids(sentence, vocabulary,
                          tokenizer=None, normalize_digits=True):

    if tokenizer:
        words = tokenizer(sentence)
    else:
        words = basic_tokenizer(sentence)
    if not normalize_digits:
        return [vocabulary.get(w, UNK_ID) for w in words]
    return [vocabulary.get(re.sub(_DIGIT_RE, "0", w), UNK_ID) for w in words]


def data_to_token_ids(data_path, target_path, vocabulary_path,
                      tokenizer=None, normalize_digits=True):

    print("Tokenizing data in %s" % data_path)
    vocab, _ = initialize_vocabulary(vocabulary_path)
    data_file = open(data_path,"r")
    tokens_file = open(target_path,"w")
    counter = 0
    for line in data_file:
        counter += 1
        if counter % 100 == 0:
            print("  tokenizing line %d" % counter)
        token_ids = sentence_to_token_ids(line, vocab, tokenizer,
                                          normalize_digits)
        tokens_file.write(" ".join([str(tok) for tok in token_ids]) + "\n")
    data_file.close()
    tokens_file.close()

def prepare_wmt_data(data_dir, in_vocabulary_size, out_vocabulary_size):



    train_path = os.path.join(data_dir, "train_data")
    dev_path = os.path.join(data_dir, "test_data")


    out_vocab_path = os.path.join(data_dir, "vocab_out.txt" )
    in_vocab_path = os.path.join(data_dir, "vocab_in.txt" )
    # create_vocabulary(out_vocab_path, train_path + "_out.txt", out_vocabulary_size)

    menu_file_path = os.path.join(data_dir, "searchTargets.txt")
    town_file_path = os.path.join(data_dir, "searchTowns.txt")

    # ファイルバックアップ
    shutil.copyfile(menu_file_path,os.path.join(data_dir, "searchTargetsBak.txt"))
    shutil.copyfile(town_file_path,os.path.join(data_dir, "searchTownsBak.txt"))

    menu_file = open(menu_file_path,"r+")
    town_file = open(town_file_path,"r+")
    tweetData = []
    towns = []
    targetMenu = []
    # ファイルから読み込み
    for line in menu_file:
        targetMenu.append(line)

    for line in town_file:
        towns.append(line)

    counter = 0
    # while True:
    isLimit = False
    # 処理終了時のファイル出力用の検索ターゲットリスト
    nextFileTarget = []

    # loop用リスト
    # 初期値はファイルから読み込んだメニュー。以降は、新しい名詞をひたすら追加→ループする
    loopTarget = []
    loopTarget.extend(targetMenu)

    # 次のloop用リスト
    # loopTargetのループで、新しい名詞が見つかった時に保持しておくリスト。そのままloopTargetに代入する
    nextLoopTarget = []

    # 次回以降検索除外用リスト
    # 検索結果が0件の単語
    excludeWords = []

    # タウンも増やしてもいいかも。語彙の勉強と考えれば近場でなくとも。
    today = dt.now()
    # endTime = today + timedelta(hours=-1) # ループしない
    # endTime = today + timedelta(hours=1)   # => 1時間後
    # endTime = today + timedelta(hours=6)   # => 6時間後
    # endTime = today + timedelta(hours=7)   # => 7時間後
    endTime = today + timedelta(minutes=1)   # => 1分後
    print(today)
    print(endTime)
    # 指定時間回るループ
    while today <= endTime:
        # 町ループ
        for town in towns:
            # キーワードループ
            for target in loopTarget:
                result, limit, reset, meishiList = tc.searchTweet(target + ' ' + town)
                # 検索結果なしなので次の検索へ
                if len(result) != 0:
                    # ファイル出力対象へ、未追加なら追加
                    if not target in nextFileTarget:
                        nextFileTarget.append(target)

                    tweetData.extend(result)
                    for meishi in meishiList:
                        # 処理終了時にファイルに出力する単語（名詞）の追加
                        if not meishi in nextFileTarget and not meishi in targetMenu:
                            nextFileTarget.append(meishi)
                        # 次のループで使用する名詞として追加
                        if not meishi in loopTarget:
                            nextLoopTarget.append(meishi)

                # print('limit : ', limit)
                # 検索リミットになった場合には、解除されるまで待機
                if limit == '0':
                    print('limit is zero.')
                    nowPre = dt.now()
                    if nowPre >= endTime:
                        break
                    epochPre = datetime_to_epoch(nowPre)
                    print('reset time is', epoch_to_datetime(float(reset)))
                    print('sleep time is', (float(reset) - epochPre + 1))
                    # isLimit = True
                    # 制限解除時間が来るまで待機
                    while True:
                        now = dt.now()
                        epoch = datetime_to_epoch(now)
                        if float(reset) <= epoch:
                            break
                        else:
                            time.sleep(float(reset) - epoch + 1)
                # キーワードループここまで

            # 時間がきたらループを抜ける
            nowPre = dt.now()
            if nowPre >= endTime:
                break
            # 町ループここまで


        # 次のループで使用する検索ワードをループ用リストに代入する
        loopTarget = nextLoopTarget
        today = dt.now()
                #   break
            #       counter+=1
            #       if counter == 10:
            #         print('counter is 10')
            #         isLimit = True
            #         break
            # if isLimit:
            #   break
    # print(epoch_to_datetime(float(reset)))

    menu_file.close()
    town_file.close()
    # 新しい名詞を含んだファイルを作成する。削除→新規で作るが、もっといい方法はないものか。。。
    os.remove(menu_file_path)
    menu_file = open(menu_file_path,"w")
    for line in nextFileTarget:
        menu_file.write(line + '\n')
    menu_file.close()

    create_vocabularyByArray(out_vocab_path, os.path.join(data_dir, "tweetDataFile_out.txt"), tweetData, out_vocabulary_size)
    # create_vocabulary(in_vocab_path, train_path + "_in.txt", in_vocabulary_size)
    create_vocabularyByArray(in_vocab_path, os.path.join(data_dir, "tweetDataFile_in.txt"), tweetData, in_vocabulary_size)

    out_train_ids_path = train_path + ("_ids_out.txt" )
    in_train_ids_path = train_path + ("_ids_in.txt" )
    data_to_token_ids(train_path + "_out.txt", out_train_ids_path, out_vocab_path)
    data_to_token_ids(train_path + "_in.txt", in_train_ids_path, in_vocab_path)


    out_dev_ids_path = dev_path + ("_ids_out.txt" )
    in_dev_ids_path = dev_path + ("_ids_in.txt" )
    data_to_token_ids(dev_path + "_out.txt", out_dev_ids_path, out_vocab_path)
    data_to_token_ids(dev_path + "_in.txt", in_dev_ids_path, in_vocab_path)

    return (in_train_ids_path, out_train_ids_path,
            in_dev_ids_path, out_dev_ids_path,
            in_vocab_path, out_vocab_path)

def epoch_to_datetime(epoch):
    return dt(*time.localtime(epoch)[:6])

def datetime_to_epoch(d):
    return int(time.mktime(d.timetuple()))
