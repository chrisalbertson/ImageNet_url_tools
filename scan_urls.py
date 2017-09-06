#!/usr/bin/env python

from nltk.corpus import wordnet as wn
import urllib
import urllib.request
import re
import argparse
from pathlib import Path
import urltools as ut


# Find a word given an offset
#ss = wn.synset_from_pos_and_offset('n',4543158)
#offset = str(ss.offset()).zfill(8) + '-' + ss.pos()
#print(offset, ss)

task = 'find_unique_synsets'


# Open and read the URL list.  It looks like this
'''
n00005787_86	http://img.99118.com/Big2/1024768/20101211/1700013.jpg
n00005787_97	http://farm1.static.flickr.com/45/139488995_bd06578562.jpg
n00005787_105	http://farm3.static.flickr.com/2285/2658605078_f409b25597.jpg
n00005787_119   http://farm4.static.flickr.com/3202/2960028736_74d31b947d.jpg
'''
# The first line above has four fields as follows:
#   pos = 'n'
#   offset = 00005787
#   serial = 86
#   url = 'http://img.99118.com/Big2/1024768/20101211/1700013.jpg'


def _main(args):
    synsets = {}
    lines_read = 0

    urldict = {}
    dup_count = 0


    #urllist_file = codecs.open('../fall11_urls.txt',
    #                           errors='ignore',
    #                            encoding='utf-8')
    urllist_file = open(args.url_file, 'r',   encoding="latin-1")
    for line in urllist_file:
        #line = repr(line)
        lines_read += 1

        wnid, url = re.split('\s+', line, maxsplit=1)

        url = url.strip()
        url = url.strip('\n')
        url_norm = ut.normalize(url)

        if args.normalized and (url != url_norm):
            print('NORMALIZED URL:')
            print('   original:  ', url)
            print('   normalized:', url_norm)

        if url_norm not in urldict:
            urldict[url_norm] = line
        else:
            dup_count += 1
            print('DUPLICATE URL:')
            print('   ', urldict[url_norm])
            print('   ', line)

    print(dup_count, 'duplicate URLs found')
    exit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description = 'print the unique list of sysnsets in a URL file')

    parser.add_argument('url_file',
                        help='file containing synsets and associated URL')

    parser.add_argument('-n', '--normalized',
                        action='store_true',
                        help='print show URLs that were changed by normalization')
    args = parser.parse_args()

    # Validate arguments
    args_ok = True
    if not Path(args.url_file).is_file():
        args_ok = False
        print('ERROR url_file', args.url_file, 'not found')

    if args_ok:
        _main(args)
    else:
        print('Terminating')
        exit()
