# coding:utf-8

import MeCab
import sys

### Execute
if __name__ == "__main__":
    print(u'Main run')
    param = sys.argv
    path = param[1]
    out_path = path + '_mecabed.txt'
    in_file = open(path, 'r')
    out_file = open(out_path, 'w')
    
    m = MeCab.Tagger ("-Ochasen")
    
    hinshiMap = {}
    
    kuttuke_list = ["名詞-and-接尾-and-一般-and-*",
                    "助詞-and-終助詞-and-*-and-*",
                    "名詞-and-接尾-and-助数詞-and-*",
                    "名詞-and-非自立-and-一般",
                    "動詞-and-接尾-and-*-and-*",
                    "名詞-and-接尾-and-助数詞-and-*",
                    "形容詞-and-非自立-and-*-and-*",
                    "助詞-and-格助詞-and-一般-and-*",
                    "助詞-and-係助詞-and-*-and-*",
                    "助詞-and-接続助詞-and-*-and-*",
                    "助詞-and-副助詞-and-*-and-*",
                    "助動詞-and-*-and-*-and-*",
                    "動詞-and-非自立-and-*-and-*",
                    "名詞-and-接尾-and-サ変接続-and-*",
                    "名詞-and-接尾-and-一般-and-*",
                    "名詞-and-接尾-and-形容動詞語幹-and-*",
                    "名詞-and-接尾-and-助数詞-and-*",
                    "名詞-and-接尾-and-助動詞語幹-and-*",
                    "名詞-and-接尾-and-副詞可能-and-*"]
    
    atama_list = ["接頭詞-and-名詞接続-and-*-and-*"]
    
    hajikknai_kigou_list = ["記号-and-句点-and-*-and-*", "記号-and-読点-and-*-and-*"]
    
    
    # 頭にくっつけたり、後ろにくっつけたりする必要がある
    # そのまま出力はしない。くっつけの判定を終えて確定した前テキストから出力をする
    # まず、1行目は、前テキストに保持して終わり
    # 2行目以降は、
    #   1.前テキストが、頭にくっつける場合 : 前テキスト + 今テキスト　品詞は、今テキスト(今テキスト品詞を前テキスト品詞にする)
    #   2.今テキストが、後ろにくっつける場合 : 前テキスト + 今テキスト 品詞は、前テキスト
    #   ⇒  1 2は同時に出ないはず
    #   1, 2 にも該当しない場合 : 前テキストは、確定した。出力する。出力後、前テキスト情報に今テキスト情報を入れる
    # ループ終了 : 最終行が前テキストに入っているので、出力
    # 
    
    for line in in_file:
        result_node = m.parseToNode(line)
        before_text = ""
        before_hinshi = ""
        while result_node:
            split_array = result_node.feature.split(",")
            if ('/' in split_array[0]) :
                result_node = result_node.next
                continue
            current_text = result_node.surface
            hinshi = split_array[0] + "-and-" + split_array[1] + "-and-" + split_array[2] + "-and-" + split_array[3]
            # 初回はブランク 保持して次へ
            if not before_text:
                before_text = current_text
                before_hinshi = hinshi
                result_node = result_node.next
                continue
            
            # 記号は基本はじくが、句読点ははじかない。
            # はじかないListに含まれない、記号はcontinue
            if '記号' in split_array[0] and not hinshi in hajikknai_kigou_list:
                result_node = result_node.next
                continue
            
            # 前のテキストが、頭に付けるかチェック
            if before_hinshi in atama_list:
                # 前のテキスト + 今のテキスト
                before_text = before_text + current_text
                # before_hinshiを変える
                before_hinshi = hinshi
                result_node = result_node.next
                continue
            
            # 今のテキストが、後ろにくっつける品詞かチェック
            if hinshi in kuttuke_list:
                # 前のテキスト + 今のテキスト　まだ単語の確定はしない before_hinshiは変えない。
                before_text = before_text + current_text
                result_node = result_node.next
                continue
            
            # before を書き込む
            
            if before_hinshi in hinshiMap:
                list = hinshiMap[before_hinshi]
                if not before_text in list:
                    list.append(before_text)
            else :
                list = [before_text]
                hinshiMap[before_hinshi] = list
            # 今のテキストは保持して次へ
            before_text = current_text
            before_hinshi = hinshi
            
            result_node = result_node.next
    
        if before_hinshi in hinshiMap:
            list = hinshiMap[before_hinshi]
            if not before_text in list:
                list.append(before_text)
        else :
            list = [before_text]
            hinshiMap[before_hinshi] = list
    
    all_file = open(out_path, 'w')
    for  (hinshi, text_list) in hinshiMap.iteritems():
        print("write : " + hinshi + '.txt' + " / count : " + str(len(text_list)))
        # write_file = open(hinshi + '.txt', 'w')
        for text in text_list:
            # write_file.write(text + "\n")
            all_file.write(hinshi + ',' + text + "\n")
        # write_file.close()
    
    all_file.close()




