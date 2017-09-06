ImageNet URL Tools
==================

This is a set of simle tools for dealing with the list in image URLs you can 
down loadload from ImageNet at http://image-net.org/download 

Presently there are three Python scripts:

- fetch_urls.py  Reads a file containing the synsets you want to download 
images for.  If all you want are dogs then place one line of text in this file that 
reads "dog.n.01".  If you need images for 1000 clases then place 1000 lines
in this file, one for each class.  Note that you can use the synset "dog.n.01" 
or the WordNetID "n00003456" in the file.  This script treats them 
interchanably. 

- unique_synsets.py  Reads a URL file that you downloaded from ImageNet.  This file
might have 14 million lines of text so in practice it could never be read by
a normal human.  This script can read the file.  Convert the WordNetIDs to 
more human readable Synsets and then print the unique set of synsets in sorted
order.  You can then read this to see just what is in the URL file.  Optionally
the script can check if any of the synsets in the list are hypernyms or 
hyponyms of each other.  The output of this script can be used as input to 
fetch_urls.py

- scan_urs.py  Reads the URL File and looks for duplicate URLs.  The URLs are
first normalized before they are compared.  As it turns out many duplicates
are present.  There are two cases (1) simple, where the same jpg file is used
twice in the same sysnset.  and (2) cross-class where to same jpg file is
used in two different classes.


Background
----------

I went to ImageNet some time ago expecting to be able to download hundreds of
thousands of jpg format image files and lables that I could use directly. 
BUt I foubd they offer not the files themselves but a list of URLs where 
you cn download each of the image file.  You likely already know this or
you would not be here.

The URL list is a plain text file with two colums.  The colums are white
space separated.  The two colums are:

- WordNetID_Serial.  THis has two parts.  A WordnetID and then a serial 
number with an underbar between
the parts.  A WordNetID also has two parts.  The first is what Wordnet
calls an "offset".  It is an integer.  
Prepened to the integer is a single characer poart of speech tag tha is
alwaus equal to 'n'.   An example WordNetID is "n00003456".  These IDs are
exactly equalent to and have a one to one relationship to WordNet Synsets.
An example of whjat you find in this colum is "n00005432_345" and is taken
to mean the 345th jpg image file of the synset at offset 5432.


- URL.  This is a standard file URL that should always points to a .jpg file.  
If all goes right you can cut and past this url into a web browes and see
the image.

fetch_urls.py
-------------

Use this when you are ready to download the images.  Place the list of 
synsets you want
in a file and only those will be downloaded.   The JPG files are placed
in a directory you speciy on the command line.   If fetch_urls.py is 
interrupted and restarted it will NOT re-download any JPG images it finds 
in the image directory. So you can run this perhaps every night and stop 
and restart it if you need to use free up bandwidth.

For faster downloading you may implement a simple form of parallelism by 
running multiple instances fetch_urls.py  Give each instance a different
set if synsets.  Each parallel instance will work on a different subset
of the data so there is no need for the instance to communicate.  The
speedup is close to linear, up to the limit of available bandwidth.

Note that the scrip unique_synset.py can create a file a file that is
suitable format for fetch_urs.py  There is no need to type in 1,000
synsets, edit this file.

unique_synsets.py
----------------

This scrip is a good place to start.  Redirect it's output to a file then 
explore the file using an editor.  It will print the unique list of
synsets in sorted order and privide a cross referance between synsets
and WordNetIDs.

Optionally this script can seach the unique list and determine if any of
the synsets are hyper or hyponyms of each other.  So for example if to
need images of dogs to train you cat vs. dog clasifier, you may be disappointed
to find only 900 images of "dog.n.01" but then you notice that unique_synsets.py
points out that there are many hyponymes of "dog" such as "working dog" and "puppy" 
and "poddle" and so on and you might concider downloadin there as well, there
by multiplying the number of images available for trainning.

scan_urls.py
------------

Scans the list of URLs to find duplicates.  Prints a list of all duplactes.  
This is really just to give a "heads up" to the user.  This scrip uses the
same logic as fetch_urs.py.  You can use the script to perform a basic
quality control check on the input file.   URLs are normailzed before they
are compared so that those pointing to the same .jpg file can be detected
even if the URLs look visulay different.

Author
------

All, comments, suggestions and bug fixed welcome

    Chris Albertson
    albertson.chris@gmail.com
