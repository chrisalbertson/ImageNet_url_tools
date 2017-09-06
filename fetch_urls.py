#!/usr/bin/env python

from nltk.corpus import wordnet as wn
import urllib
import urllib.request
import re
from pathlib import Path
import argparse
import urltools as ut

## TODO     dryrun, no download just count URLs
##          patern matching in shopping list
##          get hyponymes of some sysnsets
##          argument parcing
##          doc strings
##          unit testing
##          asserts
##          handel this: ConnectionResetError: [Errno 104] Connection reset by peer


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

synsets = {}

def _main(args):
    ## print(args.image_dir, args.url_file, args.shopping_file, args.dryrun)

    # First step is to read the "shopping list".  This is the list of synsets we
    # want to downlown images for.  By convetion if this list is empty we will
    # download all synsets.
    #
    # This file contins one sysset per line but the synsets can be in either
    # of two formats:
    #   1)  A "synset name" such as "benthos.n.02" or,
    #   2)  A "wordnet ID" or "offset" such as "n00004475"
    # These two formats are interchangable.  For every synset name there is an offset
    # and vice versa.
    #
    # The software below figures out which form is used inthe files (forms can be mixed
    # withion a file)
    #
    synsetdict = {}
    lines = 0
    shoppinglist_file = open(args.shopping_file, 'r',   encoding="utf-8")
    for line in shoppinglist_file:
        lines += 1
        line = line.strip()

        if line[0] == 'n' and line[1:2].isnumeric():
            # We have a wordnet ID
            wnid = line

            pos = line[0]
            offset = int(line[1:])
            ss = wn.synset_from_pos_and_offset(pos, offset)
            synsetdict[offset] = ss

        elif line[0:3].isalpha:
            # We have a synset name

            ss = wn.synset(line)
            offset = int(ss.offset())
            synsetdict[offset] = ss
        else:
            # We can't figute out what is in the file
            print('ERROR shoppinglist.txt, line', lines, 'unrecognised format', line)
            exit()

    print('Processing URLs from the following shopping list', synsetdict)

    # read the URL list file end to end and process only those lines that
    # match synsets in our shopping list
    lines_read       = 0
    files_downloaded = 0
    files_existing   = 0
    urldict = {}
    urllist_file = open(args.url_file, 'r',   encoding="latin-1")
    for line in urllist_file:
        lines_read += 1

        wnid, url = re.split('\s+', line, maxsplit=1)

        # Normalixe the URL
        url = url.strip()
        url = url.strip('\n')
        url = ut.normalize(url)

        pos_offset, serial = wnid.split('_')
        pos = pos_offset[0]
        offset = int(pos_offset[1:])

        ss = wn.synset_from_pos_and_offset(pos, offset)
        ssstr = str(ss)[8:-2]

        # If synset is not on our shopping list we don't want it
        if offset not in synsetdict:
            continue

        # Have we already downloaded this URL?  Don't waste time doing it again.
        if url not in urldict:
            urldict[url] = line
        else:
            dup_count += 1
            print('WARNING DUPLICATE URL this jpg file will NOT be downloaded again:')
            print('   ', urldict[url_norm])
            print('   ', line)
            continue

        # create the file name
        jpg_filename = args.image_dir + ssstr + '-' + serial + '.jpg'

        # If we already have this file, we don't need to get it
        if Path(jpg_filename).is_file():
            files_existing += 1
            continue

        try:
            response = urllib.request.urlopen(url)
            imagedata = response.read()
            newfile = open(jpg_filename, 'wb')
            newfile.write(imagedata)
            newfile.close()
            files_downloaded += 1

            # Crude progress bar
            print('.', end='')

        except urllib.error.URLError as e:
            print(e.reason, wnid, ssstr, ' at line', lines_read)

    print('downloaded', files_downloaded,
          'skipped', files_existing, 'existing files',
          'did not download', dup_count, 'duplicate URLs')
    exit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description = 'Download jpg images from a list of URLs',
            epilog ='''URL_FILE is read on line at a time.  If the synset on the line
                      is present in the list of synsets contained in SHOPPING_FILE and
                      the .jpg image file is not already downloaded then
                      an attempt is made to download the URL.  If the download is
                      successful the .jpg file is saved in IMAGE_DIR.''')

    parser.add_argument('-i', '--image_dir',
                        default = '.',
                        help='directory for downloaded images, default is current directory',
                        required=False)

    parser.add_argument('-u', '--url_file',
                        help='file containing synsets and associated URL for jpg file',
                        required=True)

    parser.add_argument('-s', '--shopping_file',
                        help='file containing a list of synsets to be processed',
                        required=True)

    parser.add_argument('-d', '--dryrun',
                        action='store_true',
                        help='if specified no attemptis made to download image files')

    args = parser.parse_args()

    # Validate arguments
    args_ok = True
    if not Path(args.url_file).is_file():
        args_ok = False
        print('ERROR URL_FILE', args.url_file, 'not found')

    if not Path(args.shopping_file).is_file():
        args_ok = False
        print('ERROR SHOPPING_FILE', args.shopping_file, 'not found')

    if args.image_dir[:-1] /= '/':
        args.image_dir.append('/')

    if not Path(args.image_dir).is_dir():
        args_ok = False
        print('ERROR IMAGE_DIR', args.image_dir, 'must exist')

    if args_ok:
        _main(args)
    else:
        print('Terminating')
        exit()
