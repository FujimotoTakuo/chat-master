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
    
    
    for line in in_file:
        result_node = m.parseToNode(line)
        before_text = ""
        before_hinshi = ""
        is_before_write = False
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
                # まだ書き込んでいないのでtrue
                is_before_write = True
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
                # まだ書き込んでいないのでtrue
                is_before_write = True
                continue
            
            # 今のテキストが、後ろにくっつける品詞かチェック
            if hinshi in kuttuke_list:
                # 前のテキスト + 今のテキスト　まだ単語の確定はしない before_hinshiは変えない。
                before_text = before_text + current_text
                result_node = result_node.next
                # まだ書き込んでいないのでtrue
                is_before_write = True
                continue
            
            if hinshi in hinshiMap:
                list = hinshiMap[hinshi]
                if not current_text in list:
                    list.append(current_text)
                if is_before_write:
                    list.append(before_text)
            else :
                list = [current_text]
                if is_before_write:
                    list.append(before_text)
                hinshiMap[hinshi] = list
            result_node = result_node.next
    
    all_file = open('all.txt', 'w')
    for  (hinshi, text_list) in hinshiMap.iteritems():
        print("write : " + hinshi + '.txt' + " / count : " + str(len(text_list)))
        write_file = open(hinshi + '.txt', 'w')
        for text in text_list:
            write_file.write(text + "\n")
            all_file.write(hinshi + ',' + text + "\n")
        write_file.close()
    
    all_file.close()




