#!python3

# DeviantArt album/favourites download script.
# Author: Nobody... >.>
# Date: 18/12/2011 (dd/mm/yyyy)

# Uses urllib for downloading, lxml for parsing and sys for command line arguments.
import urllib, lxml, sys
from urllib.request import urlopen
from lxml import html

def getUrlsFromThumbsInGallery(inurl, increment=24):
    """Uses the gallery page specified by 'inurl' to acquire image URLs. The 'increment' 
    argument is used to go through each page of the gallery. Returns a dictionary."""

    # Use sets because they're good for bunches of unique stuff.
    lpurls = set() # List page URLs (gallery pages)
    ifurls = set() # Image file URLs
    fpurls = set() # File page URLs (pages for individual art pieces. Usually flash or text)

    initpage = urlopen(inurl)

    # Uses lxml.html to parse the document at inurl
    inithtml = html.document_fromstring(initpage.read().decode('utf-8', 'ignore'))

    # Calculate the offset of the last page
    endoffset = (int(inithtml.find_class('number')[-1][0].text))*increment

    # Populate lpurls with the gallery page URLs
    for x in range(0, endoffset, 24):
        lpurls.add(inurl+'?offset='+str(x))
    
    # Rip images from each gallery page using the super_img attribute on the thumb elements.
    # If such a thing is not possible, get the thumb href and add it to the file page set.
    for url in lpurls:
        page = html.document_fromstring(urlopen(url).read().decode('utf-8', 'ignore'))
        thumbels = page.find_class('thumb')
        for thumbel in thumbels:
            try:
                ifurls.add(thumbel.attrib['super_img'])
            except KeyError:
                try:
                    fpurls.add(thumbel.attrib['href'])
                except KeyError:
                    print('No super_img or href for: '+str(thumbel.attrib))
    # Return a dictionary containing the results.    
    return {'ifurls':ifurls, 'fpurls':fpurls}

def getUrlsFromPages(inurls):
    """Gets image URLs from the given pages and returns the set of them."""
    # I like sets.
    outurls = set()
    for url in inurls:
        try:
            page = html.document_fromstring(urlopen(url).read().decode('utf-8', 'ignore'))
        except:
            print('Failed on '+url)
            continue
        try:
            # This is the element id used for images you can expand.
            imgel = page.get_element_by_id('gmi-ResViewSizer_fullimg')
        except KeyError:
            try:
                # Just in case you can't expand.
                imgel = page.get_element_by_id('gmi-ResViewSizer_img')
            except KeyError:
                print('No image found for '+url)
                continue
        try:
            outurls.add(imgel.attrib['src'])
        except:
            print('Image found, but no SRC for '+url)
            continue
    return outurls


if __name__ == '__main__':
    if len(sys.argv) == 3:
        outname = sys.argv[-1]
        inurl = sys.argv[-2]

        results = getUrlsFromThumbsInGallery(inurl)

        ifurls = results['ifurls']
        ifurls.union(getUrlsFromPages(results['fpurls']))

        outfile = open(sys.argv[-1], 'w')
        
        for url in ifurls:
            outfile.write(url+'\n')
        outfile.close()

        print('Done.\n')

    else:
        print('Usage: python3 DAownloader.py <Full DA URL (with http)> <where to store the image URL list>\n')