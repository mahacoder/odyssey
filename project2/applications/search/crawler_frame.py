import codecs
import logging
import string #added because of tf-idf
import math #added because of tf-idf
import sys
sys.path.append('../')

from tokenizer import tokenize 
from datamodel.search.AsbapatApushpenKbaijalKyuseony_datamodel import AsbapatApushpenKbaijalKyuseonyLink, OneAsbapatApushpenKbaijalKyuseonyUnProcessedLink, add_server_copy, get_downloaded_content
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter, ServerTriggers
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4
from __future__ import division #added because of tf-idf

from urlparse import urlparse, parse_qs
from uuid import uuid4

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
invalid_count = 0
max_link_count = 0
max_link_page = ''
visited_count = 0
redirect_count = 0
inverted_index_list = {} #dictionary type
PATH_T0_FILES = os.path.join(os.getcwd, 'files')

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

#tokenization function in the website
tokenize = lambda doc: doc.lower().split(" ")

#creating inverted index per term
def create_inverted_index(term, document, position):

    #if term is new, then make a new document list
    if term in inverted_index_list == False:
        document_list = {}

        document_list[document] = position
        inverted_index_list[term] = document_list

    #if term is existed, then append to a document list
    else:
        inverted_index_list[term][document] = position

#this function is converting all terms in the document into inverted index
def create_document_inverted_list(tokens, document):
    for term in tokens:
        # position_list = []
        position_list = [tokens.index(i) for i in tokens if term == tokens.index(i)]
        create_inverted_index(term,document,position_list)

#custructing part (whole)
def construct_index(directory_path):
    tokens_from_file = []
    for file_path in os.listdir(directory_path): 
         tokens_from_file = tokenize(os.path.join(directory_path. file_path))
         create_document_inverted_list(tokens_from_file, file_path)

#tf = count the number of positions> DONE
def term_frequency(term, document_name):
    return len(inverted_index_list[term][document_name])

#in the website, they use this function and so as lecture
def sublinear_term_frequency(term, document_name):
    return 1 + math.log(term_frequency(term, document_name))

#function for calculating idf
def inverse_document_frequencies(term):
    # pass directory name or make it global
    file_list = os.listdir("directory name")#calcuate N
    return math.log(len(file_list)/len(inverted_index_list[term]))

#calculate the tfidf
def tfidf(term):
    idf = inverse_document_frequencies(term)
    tf = sublinear_term_frequency(term, document)
    return tf * idf

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
    else:
        outputLinks = links_from_link(rawDataObj.content, rawDataObj.url
            , rawDataObj.http_code)
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
