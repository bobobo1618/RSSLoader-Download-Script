#!python3

# DeviantArt album/favourites download script.
# Author: Nobody... >.>
# Date: 18/12/2011 (dd/mm/yyyy)

# Uses urllib for downloading, lxml for parsing and sys for command line 
# arguments.
import urllib, lxml, sys, re
from xmlrpc import client
from urllib.request import urlopen

from lxml import html
from lxml import etree

import feedparser

if __name__ == '__main__':
    printstuff = True
else:
    printstuff = False

valimageres = [re.compile(r'https?://fc.*'), re.compile(r'https?://img\.ponibooru\.org.*')]
dare = re.compile(r'.*deviantart\.com.*')

def getUrlsFromFeed(feedurl, da=False, preferDownloads=False, imageType=None, fallbackToDownload=True):
    nextUrl = feedurl
    urls = set()
    while nextUrl:
        t = feedparser.parse(nextUrl)
        if not da:
            if printstuff:
                print('Not using DeviantArt stuff...')
            if imageType:
                print('derp')
            else:
                for x in t.entries:
                    questionable = 0
                    try:
                        questionable = x.media_thumbnail[0]['url'] == "/questionable.png"
                    except:
                        print("Could not determine questionability.")
                    try:
                        for y in x.media_content:
                            urls.add((y['url'], x.link, questionable))
                    except:
                        print ("URL Not found for item.")
        else:
            if printstuff:
                print('Assuming DeviantArt...')
            for x in t.entries:
                url, imageurl, pageurl, downloadurl = False, False, False, False
                for y in x.media_content:
                    if y['medium']=='document':
                        downloadurl = y['url']
                    else:
                        if y['medium']=='image':
                            imageurl = y['url']
                pageurl = [link['href'] for link in x.links if link['rel'] == 'alternate'][0]
                if preferDownloads and downloadurl:
                    url = downloadurl
                elif imageurl:
                    if validImageUrl(imageurl):
                        url = imageurl
                    else:
                        url = getImageUrlFromPageUrl(pageurl)
                        if downloadurl and fallbackToDownload and not url:
                            url = downloadurl
                else:
                    url = getImageUrlFromPageUrl(pageurl)
                
                if url:
                    urls.add((url, pageurl, 0))
                else:
                    if printstuff:
                        print('No URL for '+x.title)
                    print(url)
                    print
        try:
            nextUrl = [link['href'] for link in t.channel.links if link['rel'] == 'next'][0]
        except:
            nextUrl = False
    return list(urls)

def ariaUrlsFromFeed(feedurl, da=False, preferDownloads=False, imageType=None, fallbackToDownload=True):
    nextUrl = feedurl
    s = client.ServerProxy('http://localhost:6800/rpc').aria2
    while nextUrl:
        t = feedparser.parse(nextUrl)
        if not da:
            if printstuff:
                print('Not using DeviantArt stuff...')
            if imageType:
                print('derp')
            else:
                [[s.addUri([y['url']]) for y in x.media_content] for x in t.entries]
        else:
            if printstuff:
                print('Assuming DeviantArt...')
            for x in t.entries:
                url, imageurl, pageurl, downloadurl = False, False, False, False
                for y in x.media_content:
                    if y['medium']=='document':
                        downloadurl = y['url']
                    else:
                        if y['medium']=='image':
                            imageurl = y['url']
                pageurl = [link['href'] for link in x.links if link['rel'] == 'alternate'][0]
                if preferDownloads and downloadurl:
                    url = downloadurl
                elif imageurl:
                    if validImageUrl(imageurl):
                        url = imageurl
                    else:
                        url = getImageUrlFromPageUrl(pageurl)
                        if downloadurl and fallbackToDownload and not url:
                            url = downloadurl
                else:
                    url = getImageUrlFromPageUrl(pageurl)
                
                if url:
                    s.addUri([url])
                else:
                    if printstuff:
                        print('No URL for '+x.title)
                    print(url)
                    print
        try:
            nextUrl = [link['href'] for link in t.channel.links if link['rel'] == 'next'][0]
        except:
            nextUrl = False
    return list(urls)

def validImageUrl(url):
    for imgre in valimageres:
        if imgre.match(url):
            return True
    return False

def getRssFromPageUrl(url):
    x = html.document_fromstring(urlopen(url).read().decode('utf-8', 'ignore'))
    try:
        result = x.find('.//link[@rel="alternate"][@type="application/rss+xml"]').attrib['href']
    except:
        result = False
    return result

def getImageUrlFromPageUrl(pageurl):
    """Gets a deviantart image URL from a page returned by lxml."""
    page = html.document_fromstring(urlopen(pageurl).read().decode('utf-8', 'ignore'))
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

if __name__ == '__main__':
    if len(sys.argv) == 4:
        inurl = sys.argv[-1]
        rssornot = bool(int(sys.argv[-2]))
        preferDownloads = bool(int(sys.argv[-3]))
        isDA = dare.match(inurl)
        if not rssornot:
            rssUrl = getRssFromPageUrl(inurl)
        else:
            rssUrl = inurl
        ifurls = getUrlsFromFeed(feedurl=rssUrl, da=isDA, preferDownloads=preferDownloads)
        #ifurls = getUrlsFromRss(rssUrl)
        #ifurls = getUrlsFromThumbsInGallery(inurl)

        outfile = open('urls.txt', 'w')
        
        for url in ifurls:
            outfile.write(url[0]+'\n')
        outfile.close()

        outfile = open('meta.txt', 'w')
        
        for url in ifurls:
            outfile.write("{0}|{1}|{2}".format(urls[0], urls[1], urls[2])+'\n')
        outfile.close()

        if printstuff:
            print('Done.\n')

    else:
        print("""Usage: python3 DAownloader.py <preferDownloads> <URL is RSS?> <Full URL (with http)> <where to store the image URL list>\n""")