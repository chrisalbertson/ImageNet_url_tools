#!/usr/bin/env python

from nltk.corpus import wordnet as wn
from urllib.parse import urlparse
import urllib.request
import re
from pathlib import Path
import os.path
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



def check_magic(buffer):

    extension = '' # return a zero length string on wrong file type

    # Macic numbers at offset=0 for the short list of files we accept.
    # for more robut checking of more file type we could use "libmagic"
    #
    # LIst of ( filename extension, magic bytes at offset zero)
    filesigs = [('jpg', b'\xFF\xD8\xFF'),
                ('png', b'\x89\x50\x4E\x47'),
                ('gif', b'\x47\x49\x46\x38\x37\x61'),  # gif87a
                ('gif', b'\x47\x49\x46\x38\x39\x61')]  # gif89a

    for (ex, sig) in filesigs:
        if buffer.startswith(sig):
            extension = ex
            break
    return extension



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

    # Dictionary of acceptable image file extensions and what we will use as
    # the extension when we save the file locally
    file_ext_whitelist = {'jpg': 'jpg', 'png': 'png', 'jpeg': 'jpg',
                          'JPG': 'jpg', 'PNG': 'png', 'JPEG': 'jpg'}
    file_ext_gif       = {'gif': 'gif', 'GIF': 'gif'}


    synsetdict = {}
    lines = 0
    shoppinglist_file = open(args.shopping_file, 'r',   encoding="utf-8")
    for line in shoppinglist_file:
        lines += 1
        line = line.strip()
        line = line.strip('\n')

        if line[0] == 'n' and line[1:2].isnumeric():
            # We have a wordnet ID
            wnid = line

            pos = line[0]
            offset = int(line[1:])
            ss = wn.synset_from_pos_and_offset(pos, offset)
            synsetdict[offset] = ss

        elif line[0:2].isalpha:
            # We have a synset name

            ss = wn.synset(line)
            offset = int(ss.offset())
            synsetdict[offset] = ss
        else:
            # We can't figute out what is in the file
            print('ERROR shoppinglist.txt, line', lines, 'unrecognised format', line)
            exit()

    if args.verbose:
        print('INFO: Processing URLs from the following shopping list', synsetdict)

    # Make sure we have a directory for every synset, these may alreadys exist or not
    for offset in synsetdict:
        ssstr = str(synsetdict[offset])[8:-2]
        path = args.image_dir + ssstr
        if not os.path.exists(path):
            os.makedirs(path)

    # if we are going to allow GIF files, append to the whitelist
    if args.gif_ok:
        file_ext_whitelist.update(file_ext_gif)
        if args.verbose:
            print('INFO: allowing gif files')

    # read the URL list file end to end and process only those lines that
    # match synsets in our shopping list
    lines_read       = 0
    files_downloaded = 0
    files_existing   = 0
    dup_count        = 0
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

        # Attempt to find the file extension.  If we can't find it skip the URL
        # if we do find it, normalise the extension to lower case and three characters
        urlparts = urlparse(url)
        urlpath  = urlparts.path

        try:
            _f, urlextension = urlpath.rsplit(sep='.', maxsplit=1)
        except (ValueError):
            print('WARNING No file extension, URL skiped:', line)
            continue

        if urlextension not in file_ext_whitelist:

            # did not find filename extension in path, perhaps it is a parameter
            for ext in file_ext_whitelist:
                dotext = '.' + ext
                if (dotext in urlparts.params) or (dotext in urlparts.query):
                    file_extension = file_ext_whitelist[ext]
                    break
                else:
                    file_extension = ''
                    print('WARNING No file extension found, URL skiped:', line)
                    break
            if '' == file_extension:
                continue

        else:
            file_extension = file_ext_whitelist[urlextension]


        # Have we already downloaded this URL?  Don't waste time doing it again.
        if url not in urldict:
            urldict[url] = line
        else:
            dup_count += 1
            print('WARNING DUPLICATE URL this jpg file will NOT be downloaded again:')
            print('   ', urldict[url])
            print('   ', line)
            continue

        # create the file name
        image_filename = args.image_dir + ssstr + '/' + ssstr + '-' + serial + '.' + file_extension

        # If we already have this file, we don't need to get it
        if Path(image_filename).is_file():
            files_existing += 1
            if args.verbose:
                print('INFO: File exists, not downloaing again', image_filename)
            continue

        try:
            response = urllib.request.urlopen(url)
            imagedata = response.read()

        except urllib.error.URLError as e:
            print(e.reason, wnid, ssstr, ' at line', lines_read, url)
            continue
        except:
            print('WARNING unknown error while downloading data at line', lines_read, url)
            continue

        ext_by_magic = check_magic(imagedata)
        if ext_by_magic not in file_ext_whitelist:
            print('WARNING Downloaded file signature is wrong, not saved', line)
            continue
        if ext_by_magic != file_extension:
            print("WARNING Downloaded file signature", ext_by_magic, "does not match URL", line)
            continue

        newfile = open(image_filename, 'wb')
        newfile.write(imagedata)
        newfile.close()
        files_downloaded += 1

        # Crude progress bar
        print('.', end='')

    # after loop end, print a summary of what was done then exit
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

    parser.add_argument('-g', '--gif_ok',
                        action='store_true',
                        help='if specified .gif files are allowed')

    parser.add_argument('-d', '--dryrun',
                        action='store_true',
                        help='if specified no attemptis made to download image files')

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='print lots of information about each URL in requested synsets')

    args = parser.parse_args()

    args = parser.parse_args()

    # Validate arguments
    args_ok = True
    if not Path(args.url_file).is_file():
        args_ok = False
        print('ERROR URL_FILE', args.url_file, 'not found')

    if not Path(args.shopping_file).is_file():
        args_ok = False
        print('ERROR SHOPPING_FILE', args.shopping_file, 'not found')

    if args.image_dir[:-1] != '/':
        args.image_dir += '/'

    if not Path(args.image_dir).is_dir():
        args_ok = False
        print('ERROR IMAGE_DIR', args.image_dir, 'must exist')

    if args_ok:
        _main(args)
    else:
        print('Terminating')
        exit()
