# coding:utf-8

from requests_oauthlib import OAuth1Session
import json
import sys
import MeCab
import base64
import socket
import urllib, urllib2
import re
import time
from datetime import datetime as dt, timedelta
import gzip
import os
import tarfile
import shutil
import log_utils

### Constants
oath_key_dict = {
    "consumer_key": "mHZBHgpkdtAS0tGxlh0bqNWmt",
    "consumer_secret": "AeKNuy2lrZXwZyLMxghWweCG0cMP3nUbhtT6IL5grJxqAKJB62",
    "access_token": "762901895346200577-AGr4TQVMeQBndDywpa38jlC6WTKWqc4",
    "access_token_secret": "vNhZqGU5lCFPMu2MxHw6xFiDluecLxiXuuAA8YB38apj3"
}

oauth_consumer_key1 = "mHZBHgpkdtAS0tGxlh0bqNWmt"     # your consumer key
oauth_consumer_secret1 = "AeKNuy2lrZXwZyLMxghWweCG0cMP3nUbhtT6IL5grJxqAKJB62"  # your consumer secret

oauth_consumer_key2 = "ifCxeCJNHybM4SoKZq4kIYgzm"     # your consumer key
oauth_consumer_secret2 = "PONr9LdvQBlxtOG8Ly1BxoQxODG6DgZQszGaF0V32a2FupU2I1"  # your consumer secret

### Functions

def authenticate(oauth_consumer_key, oauth_consumer_secret):
    print("authenticate execute.")
    url = 'https://api.twitter.com/oauth2/token'

    token_credential = urllib.quote(oauth_consumer_key) + ':' + urllib.quote(oauth_consumer_secret)
    credential = 'Basic ' + base64.b64encode(token_credential)

    value = {'grant_type': 'client_credentials'}
    data = urllib.urlencode(value)

    req = urllib2.Request(url)
    req.add_header('Authorization', credential)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')

    response = urllib2.urlopen(req, data)
    json_response = json.loads(response.read())
    access_token = json_response['access_token']
    return access_token

def main():
    # 引数チェック
    param = sys.argv
    exec_time = param[1]
    if not exec_time:
        print 'input exectime as args[0]'
        return

    # 認証
    access_token1 = authenticate(oauth_consumer_key1, oauth_consumer_secret1)
    access_token2 = authenticate(oauth_consumer_key2, oauth_consumer_secret2)

    # ファイルパス作り
    data_dir = 'datas'
    menu_file_path = os.path.join(data_dir, "searchTargets.txt")
    base_menu_file_path = os.path.join(data_dir, "searchTargetsBaseMenu.txt")
    town_file_path = os.path.join(data_dir, "searchTowns.txt")

    # ファイルバックアップ
    shutil.copyfile(menu_file_path,os.path.join(data_dir, "searchTargetsBak_main.txt"))
    shutil.copyfile(town_file_path,os.path.join(data_dir, "searchTownsBak_main.txt"))

    # ファイルオープン
    menu_file = open(menu_file_path, 'r')
    base_menu_file = open(base_menu_file_path, 'r')
    town_file = open(town_file_path, 'r')
    tweet_data_file = open(os.path.join('datas', 'tweetDataFile.txt'), 'r+')

    # ファイルのデータ展開
    tweet_data = get_array_from_file(tweet_data_file)
    towns = get_array_from_file(town_file)
    target_menu = get_array_from_file(base_menu_file)

    for line in menu_file:
        if not line in target_menu and line:
            target_menu.append(line)

    # 処理終了時のファイル出力用の検索ターゲットリスト
    next_file_target = []

    # loop用リスト
    # 初期値はファイルから読み込んだメニュー。以降は、新しい名詞をひたすら追加→ループする
    loop_target = []
    loop_target.extend(target_menu)

    # 次のloop用リスト
    # loop_targetのループで、新しい名詞が見つかった時に保持しておくリスト。そのままloop_targetに代入する
    next_loop_target = []

    # タウンも増やしてもいいかも。語彙の勉強と考えれば近場でなくとも。
    now_time = dt.now()
    # end_time = today + timedelta(hours=-1) # ループしない
    # end_time = today + timedelta(hours=1)   # => 1時間後
    # end_time = today + timedelta(hours=6)   # => 6時間後
    # end_time = today + timedelta(hours=7)   # => 7時間後
    end_time = now_time + timedelta(minutes=float(exec_time))   # => 指定分後

    # API制限リセット時間　アカウント１と２の２つ分
    # 初期値は現在時刻(リセット済の扱い)
    reset_time1 = datetime_to_epoch(now_time)
    reset_time2 = datetime_to_epoch(now_time)

    # 最初はアカウント1を使用する
    isOne = True
    access_token = access_token1

    print(now_time)
    print(end_time)
    # 指定時間回るループ
    try:
        while now_time <= end_time:
            # 町ループ
            for town in towns:
                # キーワードループ
                for target in loop_target:
                    # ブランク除外
                    if not target:
                        continue
                    result, limit, reset, meishiList = searchTweet(target + ' ' + town, access_token)
                    # 検索結果なしなので次の検索へ
                    if len(result) != 0:
                        # ファイル出力対象へ、50件以上Hitした単語を追加
                        if not target in next_file_target and 50 <= len(result):
                            next_file_target.append(target)

                        # ツイートデータ書き込み
                        for line in result:
                            if not line in tweet_data:
                                tweet_data.append(line)
                                tweet_data_file.write(line)

                        for meishi in meishiList:
                            # 次のループで使用する名詞として追加
                            if not meishi in loop_target and meishi:
                                next_loop_target.append(meishi)

                    # print('limit : ', limit)
                    # 検索リミットになった場合には、解除されるまで待機
                    if limit != '0':
                        continue

                    print('limit is zero. ' + str(epoch_to_datetime(float(reset))))
                    # 実行時間チェック。終わってたら終了
                    now_time = dt.now()
                    if now_time >= end_time:
                        break

                    # 1と2を切り替える
                    # どちらもリミット0なら、待機
                    if isOne:
                        # 1のリセット時間をセットしておく
                        reset_time1 = float(reset)
                        # 1→2に切り替え
                        # 現時刻で2がリミットになっていたら、2の制限解除まで待ってから切り替え
                        if datetime_to_epoch(now_time) <= reset_time2:
                            # 制限解除時間が来るまで待機
                            sleep(reset_time2)

                        # フラグ切り替え
                        isOne = False
                        # トークン切り替え
                        access_token = access_token2
                    else:
                        # 2のリセット時間をセットしておく
                        reset_time2 = float(reset)
                        # 2→1に切り替え
                        # 現時刻で1がリミットになっていたら、1の制限解除まで待ってから切り替え
                        if datetime_to_epoch(now_time) <= reset_time1:
                            # 制限解除時間が来るまで待機
                            sleep(reset_time1)

                        # フラグ切り替え
                        isOne = True
                        # トークン切り替え
                        access_token = access_token1
                    # キーワードループここまで

                # 時間がきたらループを抜ける
                now_time = dt.now()
                if now_time >= end_time:
                    break
                # 町ループここまで


            # 次のループで使用する検索ワードをループ用リストに代入する
            loop_target = next_loop_target
            # どんどん溜まるので、初期化してまた貯めなおす
            next_loop_target = []
            now_time = dt.now()
    finally :
        menu_file.close()
        base_menu_file.close()
        town_file.close()
        tweet_data_file.close()

        # 新しい名詞を含んだファイルを作成する。削除→新規で作るが、もっといい方法はないものか。。。
        os.remove(menu_file_path)
        menu_file = open(menu_file_path,"w")
        for line in next_file_target:
            menu_file.write(line)
        menu_file.close()

def sleep(to_time):

    print('reset time is ' + str(epoch_to_datetime(to_time)))
    print('sleep time is ', (to_time - datetime_to_epoch(dt.now()) + 1))
    while True:
        now_time = datetime_to_epoch(dt.now())
        if to_time <= now_time:
            break
        else:
            time.sleep(to_time - now_time + 1)

def get_array_from_file(file):
    data = file.read()  # ファイル終端まで全て読んだデータを返す
    return data1.split('n')

def searchTweet(target, access_token):
    # print(access_token)
    target = target + ' exclude:retweets'
    mcb = MeCab.Tagger("-Owakati")
    mcbAll = MeCab.Tagger("mecabrc")

    # timeout in seconds
    timeout = 30
    socket.setdefaulttimeout(timeout)
    decodeTarget = ''
    try:
        decodeTarget = target.decode('utf-8')
    except UnicodeDecodeError as e:
        log_utils.log(str(e) + ' : : : ' + target + ' is could not decode.')
        # 検索はしていないので、次も検索できるようにリミットは1で返す
        return [], "1", "12345", []

    tweets, limit, reset = tweet_search(decodeTarget, oath_key_dict, access_token)

    print(target.strip() + ' count : ' + str(len(tweets["statuses"])))
    if len(tweets["statuses"]) == 0:
        return [], limit, reset, []

    # print(limit)
    # print(reset)
    result = []
    meishiList = []
    p = re.compile("([A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)《》◇▼◎⇒💕✨☺♥≪😂💓①♪😀 😬 😁 😂 😃 😄 😅 😆 😇 😉 😊 🙂 🙃 ☺️ 😋 😌 😍 😘 😗 😙 😚 😜 😝 😛 🤑 🤓 😎 🤗 😏 😶 😐 😑 😒 🙄 🤔 😳 😞 😟 😠 😡 😔 😕 🙁 ☹️ 😣 😖 😫 😩 😤 😮 😱 😨 😰 😯 😦 😧 😢 😥 😪 😓 😭 😵 😲 🤐 😷 🤒 🤕 😴 💤 💩 😈 👿 👹 👺 💀 👻 👽 🤖 😺 😸 😹 😻 😼 😽 🙀 😿 😾 🙌 👏 👋 👍 👎 👊 ✊ ✌️ 👌 ✋ 👐 💪 🙏 ☝️ 👆 👇 👈 👉 🖕 🖐 🤘 🖖 ✍️ 💅 👄 👅 👂 👃 👁 👀 👤 👥 🗣 👶 👦 👧 👨 👩 👱 👴 👵 👲 👳 👮 👷 💂 🕵 🎅 👼 👸 👰 🚶 🏃 💃 👯 👫 👬 👭 🙇 💁 🙅 🙆 🙋 🙎 🙍 💇 💆 💑 👩‍❤️‍👩 👨‍❤️‍👨 💏 👩‍❤️‍💋‍👩 👨‍❤️‍💋‍👨 👪 👨‍👩‍👧 👨‍👩‍👧‍👦 👨‍👩‍👦‍👦 👨‍👩‍👧‍👧 👩‍👩‍👦 👩‍👩‍👧 👩‍👩‍👧‍👦 👩‍👩‍👦‍👦 👩‍👩‍👧‍👧 👨‍👨‍👦 👨‍👨‍👧 👨‍👨‍👧‍👦 👨‍👨‍👦‍👦 👨‍👨‍👧‍👧 👚 👕 👖 👔 👗 👙 👘 💄 💋 👣 👠 👡 👢 👞 👟 👒 🎩 ⛑ 🎓 👑 🎒 👝 👛 👜 💼 👓 🕶🍏 🍎 🍐 🐶 🐱 🐭 🐹 🐰 🐻 🐼 🐨 🐯 🦁 🐮 🐷 🐽 🐸 🐙 🐵 🙈 🙉 🙊 🐒 🐔 🐧 🐦 🐤 🐣 🐥 🐺 🐗 🐴 🦄 🐝 🐛 🐌 🐞 🐜 🕷 🦂 🦀 🐍 🐢 🐠 🐟 🐡 🐬 🐳 🐋 🐊 🐆 🐅 🐃 🐂 🐄 🐪 🐫 🐘 🐐 🐏 🐑 🐎 🐖 🐀 🐁 🐓 🦃 🕊 🐕 🐩 🐈 🐇 🐿 🐾 🐉 🐲 🌵 🎄 🌲 🌳 🌴 🌱 🌿 ☘ 🍀 🎍 🎋 🍃 🍂 🍁 🌾 🌺 🌻 🌹 🌷 🌼 🌸 💐 🍄 🌰 🎃 🐚 🕸 🌎 🌍 🌏 🌕 🌖 🌗 🌘 🌑 🌒 🌓 🌔 🌚 🌝 🌛 🌜 🌞 🌙 ⭐️ 🌟 💫 ✨ ☄️ ☀️ 🌤 ⛅️ 🌥 🌦 ☁️ 🌧 ⛈ 🌩 ⚡️ 🔥 💥 ❄️ 🌨 ☃️ ⛄️ 🌬 💨 🌪 🌫 ☂️ ☔️ 💧 💦 🌊 💍 🌂🍊 🍋 🍌 🍉 🍇 🍓 🍈 🍒 🍑 🍍 🍅 🍆 🌶 🌽 🍠 🍯 🍞 🧀 🍗 🍖 🍤 🍳 🍔 🍟 🌭 🍕 🍝 🌮 🌯 🍜 🍲 🍥 🍣 🍱 🍛 🍙 🍚 🍘 🍢 🍡 🍧 🍨 🍦 🍰 🎂 🍮 🍬 🍭 🍫 🍿 🍩 🍪 🍺 🍻 🍷 🍸 🍹 🍾 🍶 🍵 ☕️ 🍼 🍴 🍽 🏀 🏈 ⚾️ 🎾 🏐 🏉 🎱 ⛳️ 🏌 🏓 🏸 🏒 🏑 🏏 🎿 ⛷ 🏂 ⛸ 🏹 🎣 🚣 🏊 🏄 🛀 ⛹ 🏋 🚴 🚵 🏇 🕴 🏆 🎽 🏅 🎖 🎗 🏵 🎫 🎟 🎭 🎨 🎪 🎤 🎧 🎼 🎹 🎷 🎺 🎸 🎻 🎬 🎮 👾 🎯 🎲 🎰 🎳⚽️ 🚗 🚕 🚙 🚌 🚎 🏎 🚓 🚑 🚒 🚐 🚚 🚛 🚜 🏍 🚲 🚨 🚔 🚍 🚘 🚖 🚡 🚠 🚟 🚃 🚋 🚝 🚄 🚅 🚈 🚞 🚂 🚆 🚇 🚊 🚉 🚁 🛩 ✈️ 🛫 🛬 ⛵️ 🛥 🚤 ⛴ 🛳 🚀 🛰 💺 ⚓️ 🚧 ⛽️ 🚏 🚦 🚥 🏁 🚢 🎡 🎢 🎠 🏗 🌁 🗼 🏭 ⛲️ 🎑 ⛰ 🏔 🗻 🌋 🗾 🏕 ⛺️ 🏞 🛣 🛤 🌅 🌄 🏜 🏖 🏝 🌇 🌆 🏙 🌃 🌉 🌌 🌠 🎇 🎆 🌈 🏘 🏰 🏯 🏟 🗽 🏠 🏡 🏚 🏢 🏬 🏣 🏤 🏥 🏦 🏨 🏪 🏫 🏩 💒 🏛 ⛪️ 🕌 🕍 🕋 ⛩◆≫🙏😊😭★✩☆◆]+)")
    private_use = re.compile(ur'[\uE000-\uF8FF]')
    for tweet in tweets["statuses"]:
        content = tweet[u'text']
        # URL除去
        content = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', content)
        text = mcb.parse(content.encode('utf-8'))
        node = mcbAll.parseToNode(content.encode('utf-8'))
        while node:
            word = node.feature.split(',')[0]
            if '名詞' == node.feature.split(',')[0]:
                # 追加済みでなくかつ、英数記号でない(英数記号は検索しない)
                if not node.surface in meishiList and not p.match(node.surface) and not private_use.match(node.surface):
                    meishiList.append(node.surface)
            node = node.next
        text2 = text.decode('utf-8')

        # print "tweet_id:", tweet_id
        # print "textType:", type(text)
        # print "text2Type : ", type(text2)
        # print "text:", text
        # print "text2:", text2
        result.append(text)

        # tweet_id = tweet[u'id_str']
        # created_at = tweet[u'created_at']
        # user_id = tweet[u'user'][u'id_str']
        # user_description = tweet[u'user'][u'description']
        # screen_name = tweet[u'user'][u'screen_name']
        # user_name = tweet[u'user'][u'name']
        # print "created_at:", created_at
        # print "user_id:", user_id
        # print "user_desc:", user_description
        # print "screen_name:", screen_name
        # print "user_name:", user_name
        # print ""
    return result, limit, reset, meishiList

def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
        oath_key_dict["consumer_key"],
        oath_key_dict["consumer_secret"],
        oath_key_dict["access_token"],
        oath_key_dict["access_token_secret"]
    )
    return oath

def tweet_search(search_word, oath_key_dict, access_token):
    # add and edit
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {
        "q": search_word.encode('utf-8'),
        "lang": "ja",
        "result_type": "recent",
        "count": "100"
    }
    # print(url+'?'+urllib.urlencode(params))
    req = urllib2.Request(url+'?'+urllib.urlencode(params))
    # print access_token
    req.add_header('Authorization', 'Bearer ' + access_token)

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        print '=== エラー内容 ==='
        print 'type:' + str(type(e))
        print 'args:' + str(e.args)
        print 'message:' + e.message
        print 'e自身:' + str(e)
        log_utils.log(str(e))
        obj = {"statuses":[]}
        now_time = dt.now()
        wait_minutes = 15
        if str(e).count('503') or str(e).count('504'):
            wait_minutes = 5
        elif not str(e).count('429'):
            # 503(サーバーがオーバーロードなう)でも504(サーバー起動中だけどなんか障害)でも429(Too Many Requests)でもないなら、続行不可
            raise

        end_time = now_time + timedelta(minutes=wait_minutes)
        # リミット：0で返して、とりあえずWaitをかけさせる。
        # アカウントが切り替わったらまたずに実行されてしまうが、現状2つしかアカウントがないので、すぐ待つことになるから目を瞑る
        return obj, "0", str(datetime_to_epoch(end_time))

    json_response = json.loads(response.read())
    json_str = json.dumps(json_response)

    # add and edit to

    # oath = create_oath_session(oath_key_dict)
    # responce = oath.get(url, params = params)
    if response.code != 200:
        print "Error code: %d" %(response.code)
        return None

    # API残り
    limit = response.info().getheader('x-rate-limit-remaining')
    # API制限の更新時刻 (UNIX time)
    reset = response.info().getheader('x-rate-limit-reset')

    # tweets = json.loads(response.text)
    return json_response, limit, reset

def epoch_to_datetime(epoch):
    return dt(*time.localtime(epoch)[:6])

def datetime_to_epoch(d):
    return int(time.mktime(d.timetuple()))

### Execute
if __name__ == "__main__":
    print(u'あ')
    main()
