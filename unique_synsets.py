#!/usr/bin/env python

from nltk.corpus import wordnet as wn
import urllib
import urllib.request
import re
import argparse
from pathlib import Path


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

    print_hyponyms  = True

    #urllist_file = codecs.open('../fall11_urls.txt',
    #                           errors='ignore',
    #                            encoding='utf-8')
    urllist_file = open(args.url_file, 'r',   encoding="latin-1")
    for line in urllist_file:
        #line = repr(line)
        lines_read += 1

        wnid, url = re.split('\s+', line, maxsplit=1)

        pos_offset, serial = wnid.split('_')
        pos = pos_offset[0]
        offset = int(pos_offset[1:])

        ss    = wn.synset_from_pos_and_offset(pos, offset)
        ssstr = str(ss)[8:-2]

        if ssstr not in synsets:
            synsets[ssstr] = (pos_offset, 1)
        else:
            _p, count = synsets[ssstr]
            synsets[ssstr] = (_p, count + 1)

    # Print a sorted list of all synsets
    sortedss = sorted(synsets)
#    for ssstr in sortedss:
#        poff, count = synsets[ssstr]
#        print(ssstr, '\t', poff, '\t', count)

    # Create a sorted list with hypernymes and hyponyms
    for ssstr in sortedss:
        poff, count = synsets[ssstr]
        print(ssstr, '\t', poff, '\t', count)

        if args.hyper:
            ss = wn.synset(ssstr)
            hyperlist  = ss.hypernyms()
            hyperlist2 = hyperlist
            for hyper in hyperlist:
                hyperstr = str(hyper)[8:-2]
                if hyperstr not in synsets:
                    hyperlist2.remove(hyper)

            if len(hyperlist2) > 0:
                print('    hypernyms:', end='')
                for s in sorted(hyperlist2):
                    print(' ', str(s)[8:-2], end='')
                print('')

        if args.hypo:
            ss = wn.synset(ssstr)
            hypolist  = ss.hyponyms()
            hypolist2 = hypolist
            for hypo in hypolist:
                hypostr = str(hypo)[8:-2]
                if hypostr not in synsets:
                    hypolist2.remove(hypo)

            if len(hypolist2) > 0:
                print('    hyponymes:', end='')
                for s in sorted(hypolist2):
                    print(' ', str(s)[8:-2], end='')
                print('')

    exit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description = 'print the unique list of sysnsets in a URL file')

    parser.add_argument('url_file',
                        help='file containing synsets and associated URL')

    parser.add_argument('-r ', '--hyper',
                        action='store_true',
                        help='print hypernyms that are included in URL_FILE')

    parser.add_argument('-o ', '--hypo',
                        action='store_true',
                        help='print hyponyms that are included in URL_FILE')

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
