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

valimageres = [re.compile(r'https?://fc.*'), re.compile(r'https?://img\.ponibooru\.org.*')]
dare = re.compile(r'.*deviantart\.com.*')
urldomre = re.compile(r'[a-zA-Z]+://([a-zA-Z-\.])/')

def validImageUrl(url):
    for imgre in valimageres:
        if imgre.match(url):
            return True
    return False

def relToAbsUrl(inurl, relurl):
    parsedin = list(urllib.parse.urlparse(inurl))
    parsedin[2] = relurl
    return parse.urlunparse(parsedin)

def getRssFromPageUrl(url):
    x = html.document_fromstring(urlopen(url).read().decode('utf-8', 'ignore'))
    return x.find('.//link[@rel="alternate"][@type="application/rss+xml"]').attrib['href']

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

def getUrlFromItemElement(element, preferDownloads=False, daRss=False):
    nsmap = element.getroottree().getroot().nsmap
    pageUrl = element.find('./link').text
    url = ''
    if daRss:
        if preferDownloads:
            try:
                url = element.find('./media:content[@medium="document"]', namespaces=nsmap).attrib['url']
                return url
            except:
                try:
                    url = element.find('./media:content[@medium="image"]', namespaces=nsmap).attrib['url']
                    if validImageUrl(url):
                        return url
                    else:
                        page = html.document_fromstring(urlopen(pageUrl).read().decode('utf-8', 'ignore'))
                        url = getImageUrlFromPage(page)
                        return url
                except:
                    page = html.document_fromstring(urlopen(pageUrl).read().decode('utf-8', 'ignore'))
                    url = getImageUrlFromPage(page)
                    return url
        else:
            try:
                url = element.find('./media:content[@medium="image"]', namespaces=nsmap).attrib['url']
                if validImageUrl(url):
                    return url
                else:
                    page = html.document_fromstring(urlopen(pageUrl).read().decode('utf-8', 'ignore'))
                    url = getImageUrlFromPage(page)
                    return url
            except:
                page = html.document_fromstring(urlopen(pageUrl).read().decode('utf-8', 'ignore'))
                url = getImageUrlFromPage(page)
                return url
    else:
        try:
            return element.find('./media:content', namespaces=nsmap).attrib['url']
        except:
            return False

def getUrlsFromRss(inurl, preferDownloads=False):
    ifurls = set()
    nextUrl = inurl
    pagenum = 0
    daRss = bool(dare.match(inurl))
    while nextUrl:
        try:
            rss = urlopen(nextUrl)
        except:
            print('Failed on '+nextUrl)
            break
        tree = etree.parse(rss)
        root = tree.getroot()
        channel = root.getchildren()[0]
        nsmap = root.nsmap
        items = channel.findall('./item', namespaces=nsmap)
        for item in items:
            url = getUrlFromItemElement(item, preferDownloads, daRss)
            if url:
                ifurls.add(url)
            else:
                print('No URL found for '+item.find('title').text)
        try:
            nextUrl = urllib.parse.urljoin(inurl, channel.find('atom:link[@rel="next"]', namespaces=nsmap).attrib['href'])
        except:
            nextUrl = ''
        pagenum = pagenum + 1
        print ('Page {0} done.'.format(pagenum))
    return ifurls

if __name__ == '__main__':
    if len(sys.argv) == 4:
        outname = sys.argv[-1]
        inurl = sys.argv[-2]
        rssornot = bool(sys.argv[-3])
        if not rssornot:
            rssUrl = getRssFromPageUrl(inurl)
        else:
            rssUrl = inurl
        ifurls = getUrlsFromRss(rssUrl)
        #ifurls = getUrlsFromThumbsInGallery(inurl)

        outfile = open(sys.argv[-1], 'w')
        
        for url in ifurls:
            outfile.write(url+'\n')
        outfile.close()

        print('Done.\n')

    else:
        print('Usage: python3 DAownloader.py <Full DA URL (with http)> \
        <where to store the image URL list>\n')