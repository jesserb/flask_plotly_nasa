import json
import requests
import sys
from datetime import datetime
import os.path as path
from bs4 import BeautifulSoup

# get the absolute path to THIS file, the go 'back' to cache directory
dir_path = path.abspath(path.join(__file__ ,"../.."))
EXT = ('{}/cache/').format(dir_path)

# set up time stuff
now = datetime.now()
sec_since_epoch = now.timestamp()
MAX_STALENESS = 86400 # seconds


def load_cache(filename):
    try:
        cache_file = open(EXT + filename, 'r')
        cache_contents = cache_file.read()
        cache = json.loads(cache_contents)
        cache_file.close()
    # if there was no file, no worries. There will be soon!
    except:
        cache = {}

    return cache



# Scrapes the wikipidea page @ link and returns text from
# the first paragraph of page. CME specific
def get_scrape_one(link):
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')

    all_ps = soup.find_all('p')

    for p in (all_ps[1] for p in all_ps):
        return p.text.split('[')[0]



# Scrapes the wikipidea page @ link and returns text from
# the first paragraph of page. SOlar Flare specific
def get_scrape_two(link):
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')

    return soup.p.get_text().split('[')[0]
    


# A helper function that accepts 2 parameters
# and returns a string that uniquely represents the request
# that could be made with this info (url + params)
def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_" + "_".join(res)



# Based on cache_entry input, checks the staleness of the current cached
# value of the chache_entry. Returns true if cache is good to accept, false
# if its too old / needs to be replaced
def is_fresh(cache_entry): 
    now = datetime.now().timestamp() 
    staleness = now - cache_entry['cache_timestamp']
    return staleness < MAX_STALENESS



# The main cache function: it will always return the result for this
# url+params combo. However, it will first look to see if we have already
# cached the result and, if so, return the result from cache.
# If we haven't cached the result, it will get a new one (and cache it)
def make_request_using_cache(baseurl, params, filename, cache, scrape):
    unique_ident = params_unique_combination(baseurl, params)

    # first, look in the cache to see if we already have this data
    if unique_ident in cache:
        if is_fresh(cache): 
            print("Getting cached data...")
            return cache[unique_ident]
    else:
        pass

    if scrape:
        text = ''
        if params['type'] == 'cme' or params['type'] == 'neo':
            text = get_scrape_one(baseurl)
        else:
            text = get_scrape_two(baseurl)

        cache[unique_ident] = text
        return saveCache(cache, unique_ident, filename)

    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params)
        cache[unique_ident] = json.loads(resp.text)
        return saveCache(cache, unique_ident, filename)



# function takes in the cahce dictionary, the item identifier,
# and a chached filename, and saves the data in the cache to the
# given file. Returns the data in the cache
def saveCache(cache, identifier, filename):
        cache['cache_timestamp']= datetime.now().timestamp()
        dumped_json_cache = json.dumps(cache) 
        fw = open(EXT+filename,"w") 
        fw.write(dumped_json_cache) 
        fw.close()
        return cache[identifier]


# main function on cache_handler / starting point. Function
# calls all above functions in an attempt to load data, set data,
# and check data in the cache.
def getData(url, params, filename, scrape=False):
    cache = load_cache(filename)
    return make_request_using_cache(url, params, filename, cache, scrape)
