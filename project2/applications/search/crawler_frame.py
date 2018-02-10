import logging
from datamodel.search.AsbapatApushpenKbaijalKyuseony_datamodel import AsbapatApushpenKbaijalKyuseonyLink, OneAsbapatApushpenKbaijalKyuseonyUnProcessedLink, add_server_copy, get_downloaded_content
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter, ServerTriggers
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"

@Producer(AsbapatApushpenKbaijalKyuseonyLink)
@GetterSetter(OneAsbapatApushpenKbaijalKyuseonyUnProcessedLink)
@ServerTriggers(add_server_copy, get_downloaded_content)
class CrawlerFrame(IApplication):

    def __init__(self, frame):
        self.starttime = time()
        self.app_id = "AsbapatApushpenKbaijalKyuseony"
        self.frame = frame


    def initialize(self):
        self.count = 0
        l = AsbapatApushpenKbaijalKyuseonyLink("http://www.ics.uci.edu/")
        print l.full_url
        self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get(OneAsbapatApushpenKbaijalKyuseonyUnProcessedLink)
        if unprocessed_links:
            link = unprocessed_links[0]
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(AsbapatApushpenKbaijalKyuseonyLink(l))

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")

def links_from_link(url):
    page = requests.get(url).text
    doc = html.document_fromstring(page)
    x = doc.xpath("//a")
    l = []
    s = '/'
    for i in x:
        t = i.get("href")
        if len(t)<2:
            continue
        elif t[0:4] != "http" and t[0]!= s:
             t = url+t
             l.append(t)
        elif(t[0:4] != "http"):
             t = url+t[1:]
             l.append(t)
        else:
            l.append(t)
    return l

def extract_next_links(rawDataObj):
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded.
    The frontier takes care of that.

    Suggested library: lxml
    '''
    if rawDataObj.is_redirected == True:
        outputLinks = links_from_link(final_url)
    else:
        outputLinks = links_from_link(url)
    return outputLinks

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False
