#!python3

# DeviantArt album/favourites download script.
# Author: Nobody... >.>
# Date: 18/12/2011 (dd/mm/yyyy)

# Uses urllib for downloading, lxml for parsing and sys for command line 
# arguments.
import urllib, lxml, sys, re
from urllib.request import urlopen
from lxml import html
from lxml import etree

if __name__ == '__main__':
    printstuff = True
else:
    printstuff = False

nsmap = {'atom': 'http://www.w3.org/2005/Atom', 'media':'http://search.yahoo.com/mrss/'}

valimagere = re.compile(r'http://fc.*')

def getImageUrlFromPage(page):
    """Gets a deviantart image URL from a page returned by lxml."""
    try:
        # This is the element id used for images you can expand.
        imgel = page.get_element_by_id('gmi-ResViewSizer_fullimg')
    except KeyError:
        try:
            # Just in case you can't expand.
            imgel = page.get_element_by_id('gmi-ResViewSizer_img')
        except KeyError:
            return False
    try:
        return(imgel.attrib['src'])
    except:
        return False

def getDownloadUrlFromPage(page):
    """Gets a deviantart download URL from a page returned by lxml."""
    try:
        # This is the element id used for the download button.
        return page.get_element_by_id('download-button').attrib['href']
    except KeyError:
        return False

def getUrlsFromThumbsInGallery(inurl, increment=24, preferDownloads=False):
    """Uses the gallery page specified by 'inurl' to acquire image URLs. The 
    'increment' argument is used to go through each page of the gallery. If 
    preferDownloads is True, will use the download links provided by pages. 
    Returns a set of URLs."""

    # Use sets because they're good for bunches of unique stuff.
    lpurls = set() # List page URLs (gallery pages)
    fpurls = set() # File page URLs (pages for individual art pieces.)

    initpage = urlopen(inurl)

    # Uses lxml.html to parse the document at inurl
    inithtml = html.document_fromstring(initpage.read().decode('utf-8', 'ignore'))

    # Calculate the offset of the last page
    endoffset = (int(inithtml.find_class('number')[-1][0].text))*increment

    # Populate lpurls with the gallery page URLs
    for x in range(0, endoffset, 24):
        lpurls.add(inurl+'?offset='+str(x))
    if printstuff:
        print(str(len(lpurls))+' pages to search for URLs...')
    # Get page links from thumbnail hrefs
    pagenum = 1
    for url in lpurls:
        if printstuff:
            print('Parsing page number '+str(pagenum)+'...')
            pagenum += 1
        page = html.document_fromstring(urlopen(url).read().decode('utf-8', 'ignore'))
        thumbels = page.find_class('thumb')
        for thumbel in thumbels:
            try:
                fpurls.add(thumbel.attrib['href'])
            except KeyError:
                print('No href for: '+str(thumbel.attrib))
    # Return a list containing the results.
    if printstuff:
        print('There are '+str(len(fpurls))+' pages to parse for image urls...')
    return getUrlsFromPages(fpurls, preferDownloads)

def getLinkFromItemElement(element, preferDownloads=False):
    pageUrl = element.getparent().find('./link').text
    url = ''
    if preferDownloads:
        try:
            url = element.find('./media:content[@medium="document"]', namespaces=nsmap).attrib['url']
            return url
        except:
            try:
                url = element.find('./media:content[@medium="image"]', namespaces=nsmap).attrib['url']
                if valimagere.match(url):
                    return url
                else:
                    page = lxml.parse(urlopen(pageUrl))
                    url = getImageUrlFromPage(page)
                    return url
            except:
                page = lxml.parse(urlopen(pageUrl))
                url = getImageUrlFromPage(page)
                return url
    else:
        try:
            url = element.find('./media:content[@medium="image"]', namespaces=nsmap).attrib['url']
            if valimagere.match(url):
                return url
            else:
                page = lxml.parse(urlopen(pageUrl))
                url = getImageUrlFromPage(page)
                return url
        except:
            page = lxml.parse(urlopen(pageUrl))
            url = getImageUrlFromPage(page)
            return url

def getUrlsFromRss(inurl, preferDownloads=False):
    ifurls = set()
    nextUrl = inurl
    while nextUrl:
        rss = urlopen(nextUrl)
        tree = etree.parse(rss)
        root = tree.getroot()
        channel = root.getchildren()[0]
        items = channel.findall('./item', namespaces=nsmap)
        for item in items:
            ifurls.add(getLinkFromItemElement(item, preferDownloads))

def getUrlsFromPages(inurls, preferDownloads=False):
    """Gets image URLs from the given pages and returns the set of them. If 
    preferDownloads is True, will try and get DA's download link and use that 
    (Uses expanded image on failure)."""
    # I like sets.
    outurls = set()
    pagenum = 1
    pages = str(len(inurls))+'...'
    for url in inurls:
        if printstuff:
            print('Parsing page '+str(pagenum)+'/'+pages)
            pagenum += 1
        try:
            page = html.document_fromstring(urlopen(url).read().decode('utf-8', 'ignore'))
        except:
            print('Failed on '+url)
            continue

        if not preferDownloads:
            res = getImageUrlFromPage(page)
            if res:
                outurls.add(res)
        else:
            res = getDownloadUrlFromPage(page)
            if res:
                outurls.add(res)
            else:
                res = getImageUrlFromPage(page)
                if res:
                    outurls.add(res)
                else:
                    print('Nothing for '+url)
    return outurls


if __name__ == '__main__':
    if len(sys.argv) == 3:
        outname = sys.argv[-1]
        inurl = sys.argv[-2]

        ifurls = getUrlsFromThumbsInGallery(inurl)

        outfile = open(sys.argv[-1], 'w')
        
        for url in ifurls:
            outfile.write(url+'\n')
        outfile.close()

        print('Done.\n')

    else:
        print('Usage: python3 DAownloader.py <Full DA URL (with http)> \
        <where to store the image URL list>\n')