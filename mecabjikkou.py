# coding: utf-8

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
    
    m = MeCab.Tagger ("-Owakati")
    for line in in_file:
        result = tagger.parse(line)
        out_file.write(result)
    

