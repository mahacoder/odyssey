import codecs
import logging
import string #added because of tf-idf
import math #added because of tf-idf
import pickle
import sys
sys.path.append('../')

from datamodel.search.AsbapatApushpenKbaijalKyuseony_datamodel import AsbapatApushpenKbaijalKyuseonyLink, OneAsbapatApushpenKbaijalKyuseonyUnProcessedLink, add_server_copy, get_downloaded_content
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter, ServerTriggers
from lxml import html,etree
from io import StringIO, BytesIO
from lxml.html.clean import clean_html
from bs4 import BeautifulSoup
from lxml.html.clean import Cleaner
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
invalid_count = 0
max_link_count = 0
max_link_page = ''
visited_count = 0
redirect_count = 0
document_counter = 0

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
        with open("run_stats.txt", "w") as file:
            file.write('Invalid Count='+str(invalid_count)+'\n')
            file.write('Visited Count='+str(visited_count)+'\n')
            file.write('Redirect Count='+str(redirect_count)+'\n')
            file.write('Page with maximum links:'+max_link_page+'\n')
            file.write('Number of links found in above page='+str(max_link_count)+'\n')
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")

def create_url(current_url, relative_url):
    global counter
    url = ''
    counter = 0
    while relative_url[0:3]=='../':
        counter+=1
        relative_url = relative_url[3:]
    while counter!=0:
        index = current_url.rfind('/')
        current_url = current_url[:index]
        counter-=1
    url = current_url+'/'+relative_url
    return url

def links_from_link(content, current_url, http_code):
    global max_link_count
    global max_link_page
    root_url = "http://www.ics.uci.edu"
    links = []
    if http_code==200 and len(content)==0:
        pass
        # with codecs.open('empty_html.txt', mode='a', encoding='utf-8') as html_file:
        #     html_file.write(current_url+'\n')
    elif len(content)==0:
        pass
        # with codecs.open('non_200.txt', mode='a', encoding='utf-8') as non_200:
        #     non_200.write(current_url+'|'+str(http_code)+'\n')
    else:
        doc = html.document_fromstring(content)
        xpath = doc.xpath("//a")
        separator = '/'
        for i in xpath:
            target = i.get("href")
            if target is None or len(target)==0:
                continue
            if target[0:4] != "http":
                if target[0]=='/':
                    target = root_url+target
                    links.append(target)
                else:
                    target = create_url(current_url, target)
                    # with codecs.open('relative_url.txt', mode='a', encoding='utf-8') as file:
                    #     file.write(target+'\n')
            else:
                links.append(target)
    if len(links)>max_link_count:
        max_link_page = current_url
        max_link_count = len(links)
    # with open('stats.txt', 'a') as f:
    #     f.write(current_url+','+str(len(links))+'\n')
    return links

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
    global visited_count, redirect_count
    visited_count += 1
    if rawDataObj.is_redirected == True:
        redirect_count += 1
        outputLinks = links_from_link(rawDataObj.content, rawDataObj.final_url
            , rawDataObj.http_code)
        createDocumentWithContent(rawDataObj)
    else:
        outputLinks = links_from_link(rawDataObj.content, rawDataObj.url
            , rawDataObj.http_code)
        createDocumentWithContent(rawDataObj)
    return outputLinks

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''

    global invalid_count
    parsed = urlparse(url)
    is_valid_flag = False
    if parsed.scheme not in set(["http", "https"]):
        is_valid_flag = False
    try:
        is_valid_flag = ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) \
            and not re.search("calendar", url.lower()) \
            and not re.search("mailto", url.lower()) \
            and not len(parsed.query)!=0
    except TypeError:
        print ("TypeError for ", parsed)
        is_valid_flag = False

    if not is_valid_flag:
        invalid_count += 1
    return is_valid_flag

def createDocumentWithContent(dataObject):
    counterURL = {}
    global document_counter
    doc_name = r'C:\Users\anant\repos\projects\odyssey\HTMLdocs\doc_' + str(document_counter)

    with open(doc_name+ ".txt",'wb') as f:
    
        doc = "doc_" + str(document_counter)
        print (dataObject.url)
        counterURL[doc] = dataObject.url
        print (counterURL)
        document_counter = document_counter + 1
        f.write(dataObject.content)

    mapper_file_name = "doc_url_map"
    fileObject = open(mapper_file_name,'wb') 
    pickle.dump(counterURL,fileObject)   
    fileObject.close()
    
    getCleanText(doc_name)


def getCleanText(textData):
    array = []
    fh = open(textData+ ".txt", "r") 
    if fh.read(1):
        cleaner = Cleaner()
        parser = etree.HTMLParser()
        tree   = etree.parse(BytesIO(fh.read()), parser)
        result = etree.tostring(tree.getroot(), method="html")
        mresult = re.sub(r' {[^}]*}','',result)


        soup = BeautifulSoup(mresult)
        for tag in soup.find_all():
        #print (tag.name)
            array.append(tag.name)
        cleaner.remove_tags = array

        with open(textData+ ".txt",'wb') as f:
            f.write(cleaner.clean_html(mresult))   