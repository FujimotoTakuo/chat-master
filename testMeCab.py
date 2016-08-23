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
    
    for line in in_file:
        result_node = m.parseToNode(line)
        while result_node:
            split_array = result_node.feature.split(",")
            hinshi = split_array[0] + "-and-" + split_array[1] + "-and-" + split_array[2] + "-and-" + split_array[3]
            if hinshi in hinshiMap:
              hinshiMap[hinshi].append(result_node.surface)
            else :
              list = [result_node.surface]
              hinshiMap[hinshi] = list
            result_node = result_node.next
    
    all_file = open('all.txt')
    for  (hinshi, text_list) in hinshiMap.iteritems():
        write_file = open(hinshi + '.txt', w)
        for text in text_list:
            write_file.write(text + "\n")
            all_file.write(hinshi + ',' + text + "\n")
            




