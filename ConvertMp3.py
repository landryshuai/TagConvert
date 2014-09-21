#!/usr/bin/env python
# Author: mmpower; Oct 2007
# based on pytagger and tagEncoder

from TagConvert import *
from tagger import *



import sys, os, fnmatch, pickle

DEFAULT_ENC = ['gb2312', 'big5', 'big5hkscs','utf_8', 'iso8859_1','gbk','gb18030','hz']

def print_debug(filename, msg):
    print os.path.basename(filename), ':',  msg
    
def o_string(s, toenc, fromenc='latin_1'):
        """
        Converts a String or Unicode String to a byte string of specified encoding.

        @param toenc: Encoding which we wish to convert to. This can be either ID3V2_FIELD_ENC_* or the actual python encoding type
        @param fromenc: converting from encoding specified
        """

        # sanitise input - convert to string repr
        #try:
        #    if type(encodings[toenc]) == types.StringType:
        #        toenc = encodings[toenc]
        #except KeyError:
        #    toenc = 'latin_1'

        outstring = ''

        # make sure string is of a type we understand
        if type(s) not in [types.StringType, types.UnicodeType]:
            s = unicode(s)

        if type(s) == types.StringType:
            if  toenc == fromenc:
                # don't need any conversion here
                outstring = s
            else:
                try:
                    outstring = s.decode(fromenc).encode(toenc)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    warn("o_string: frame conversion failed. leaving as is.")
                    outstring = s

        elif type(s) == types.UnicodeType:
            try:
                outstring = s.encode(toenc)
            except UnicodeEncodeError, err:
                warn("o_string: frame conversion failed - leaving empty. %s" %\
                     err)
                outstring = ''

        return outstring



def o_text(strings, encoding):
        """
        Output text bytestring
        """
        newstrings = []
        
        for s in strings:

            if encoding == 'latin_1':
               newstrings.append(o_string(s, "utf_8","big5"))
            else:
               newstrings.append(s)

        output = chr(encodings[encoding])
        for s in newstrings:
            output += null_terminate(encoding, s)

        """
        # strip the last null terminator
        if is_double_byte(self.encoding) and len(output) > 1:
            output = output[:-2]
        elif not is_double_byte(self.encoding) and len(output) > 0:
            output = output[:-1]
        """

        return output

def combine(strings):
        """
        Output text bytestring
        """
        newstrings = ''

        for s in strings:
               newstrings+= s

        return newstrings

def do_convert(filename, verbose=1):

    try:

        ftag = EncodedID3(filename, DEFAULT_ENC)
        """
        tempfd, tempname = tempfile.mkstemp(suffix = ".mp3")

                os.close(tempfd)
                ftag.commit_to_file(tempname)
                self.tempfiles.append(tempname)
                print f.encode('utf_8')
        """
        #print filename

        if verbose:
                for key in ftag.converted:
                    try:
                        print_debug( key,"%s" % ftag.converted[key].encode('gb18030') )
                    except:
                        print_debug(filename, "%s - unprintable" % key)
        ftag.commit()
    except ID3Exception, e:
        print_debug(filename, "ID3v2 exception: %s" % str(e))


def do_id3(filename, verbose=1):
    try:
        id3 = ID3v2(filename)
        if not id3.tag_exists():
            print_debug(filename, "Unable to find ID3v2 tag")
        else:
            print_debug(filename, "Found ID3v2 tag ver: %.1f frames: %d" % \
                (id3.version, len(id3.frames)))

            if verbose:
                for frame in id3.frames:
                    try:
                        print_debug(filename, "%s (%s) %s" % \
                            (frame.fid, frame.encoding, o_text(frame.strings,'latin_1')))
                    except:
                        print_debug(filename, "%s - unprintable" % frame.fid)
    
            # commit changes to mp3 file (pretend mode)
            id3.commit(pretend=1)
        
    except ID3Exception, e:
        print_debug(filename, "ID3v2 exception: %s" % str(e))

    try:
        id3 = ID3v1(filename)
        if not id3.tag_exists():
            print_debug(filename, "Unable to find ID3v1 tag")
        else:
            print_debug(filename, "ID3v1 tag found")
            if verbose:
                print_debug(filename, "song: %s" % id3.songname)
                print_debug(filename, "artist: %s" % id3.artist)
    except ID3Exception, e:
        print_debug(filename, "ID3v1 exception: %s" % str(e))

def do_recurse(filename):
    if os.path.isdir(filename):
        #print "traversing dir:", filename
        for f in fnmatch.filter(os.listdir(filename), '*.mp3'):
            do_recurse(os.path.join(filename, f))
	for f in fnmatch.filter(os.listdir(filename), '*.MP3'):
            do_recurse(os.path.join(filename, f))    
	for f in fnmatch.filter(os.listdir(filename), '*.mp2'):
            do_recurse(os.path.join(filename, f))    
	for f in fnmatch.filter(os.listdir(filename), '*.MP2'):
            do_recurse(os.path.join(filename, f))    
        for f in os.listdir(filename):
            if os.path.isdir(os.path.join(filename, f)):
                do_recurse(os.path.join(filename, f))
    else:
        #print "checking file:", filename
        do_convert(filename)

try:
    do_recurse(sys.argv[1])
finally:
    pass
