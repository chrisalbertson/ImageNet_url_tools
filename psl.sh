# The Python scripts import "urltools".  Urltols will look for
# an environment variable called PUBLIC_SUFFIX_LIST and if found
# will read the local file it points to.   If NOT found, urltools
# will download the 200K byte file on Import.  This slows down
# every invocation of the script.  Having a local copy can speed
# things up for you.
#
# to use this, uncompress the file public_suffix_list.dat.bz2 and
# place it anyplace you wish.  Then edit the line below to point
# to the file.  Then source this simple one oline script.
#
export PUBLIC_SUFFIX_LIST=./public_suffix_list.dat

