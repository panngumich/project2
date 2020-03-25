#################################
##### Name: NENG PAN  ###########
##### Uniqname: panng ###########
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

CACHE_SITE = 'site.json'

CACHE_STATE_URL_DICT = {}
CACHE_SITE_DICT = {}
CACHE_SITE_URL_DICT = {}
CACHE_NEARBY_PLACE_DICT = {}

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        info_value = self.name + " (" + self.category + "): " + self.address + " " + self.zipcode
        return info_value

def load_cache_site(): # called only once, when running the program
    try:
        cache_file = open(CACHE_SITE, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache_site(cache_site): # called whenever the cache is changed
    cache_file = open(CACHE_SITE, 'w')
    contents_to_write = json.dumps(cache_site)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_state_url_request_using_cache(state_url):
    if (state_url in CACHE_STATE_URL_DICT.keys()): # the url is unique key
        print("Using cache")
        return CACHE_STATE_URL_DICT[state_url]
    else:
        print("Fetching")
        CACHE_STATE_URL_DICT[state_url] = get_sites_for_state(state_url) # add the TEXT of the web page to the cache
        return CACHE_STATE_URL_DICT[state_url]

def make_site_url_request_using_cache(site_url):
    if (site_url in CACHE_SITE_URL_DICT.keys()): # the url is unique key
        print("Using cache")
        return CACHE_SITE_URL_DICT[site_url]
    else:
        print("Fetching")
        CACHE_SITE_URL_DICT[site_url] = get_site_instance(site_url) # add the TEXT of the web page to the cache
        return CACHE_SITE_URL_DICT[site_url]

def make_site_request_using_cache(site, cache_site):
    if (site in cache_site.keys()): # the url is unique key
        print("Using cache")
        return cache_site[site]
    else:
        print("Fetching")
        cache_site[site] = build_state_url_dict() # add the TEXT of the web page to the cache
        save_cache_site(cache_site)          # write the cache to disk
        return cache_site[site]

def make_nearby_place_request_using_cache(site_object):
    if (site in CACHE_NEARBY_PLACE_DICT.keys()):
        print("Using cache")
        return CACHE_NEARBY_PLACE_DICT[site_object]
    else:
        print("Fetching")
        CACHE_NEARBY_PLACE_DICT[site_object] = get_nearby_places(site_object) # add the TEXT of the web page to the cache
        return CACHE_NEARBY_PLACE_DICT[site_object]


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    response = requests.get("https://www.nps.gov")
    soup_1 = BeautifulSoup(response.text, 'html.parser')
    ul_items = soup_1.find_all('ul', class_ = 'dropdown-menu SearchBar-keywordSearch')
    ul_string = str(ul_items[0])
    soup_2 = BeautifulSoup(ul_string, 'html.parser')
    a_items = soup_2.find_all('a')
    
    state_url_dict = {}
    for item in a_items:
        value = 'https://www.nps.gov' + item['href']
        key = item.string.lower()
        state_url_dict[key] = value
    return state_url_dict
    
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    
    response = requests.get(site_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    site_name = soup.find_all(class_ = 'Hero-title')[0].string.strip()
    site_category = soup.find_all(class_ = 'Hero-designation')[0].string.strip()
    site_locality = soup.find_all(itemprop = 'addressLocality')[0].string.strip()
    site_region = soup.find_all(itemprop = 'addressRegion')[0].string.strip()
    site_zipcode = soup.find_all(class_ = 'postal-code')[0].string.strip()
    site_phone = soup.find_all(class_ = 'tel')[0].string.strip()
    site_address = site_locality + ", " + site_region
    return NationalSite(site_category, site_name, site_address, site_zipcode, site_phone) 


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    park_list = soup.find_all(id = 'list_parks')[0]
    parks = park_list.find_all('h3')
    park_instance_list = []
    for park in parks:
        tag = park.find('a')
        link = tag.get('href')
        park_url = "https://www.nps.gov" + link + "index.htm"
        park_instance = make_site_url_request_using_cache(park_url)
        park_instance_list.append(park_instance)
    return park_instance_list
    


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
        (origin: Zip code of a national site (Use NationalSite instance attribute.)
    
    Returns
    -------
    dict
        a converted API return from MapQuest API

    '''
    url = "https://www.mapquestapi.com/search/v2/radius?origin=" + site_object.zipcode + "&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json&key=" + secrets.API_KEY
    results = requests.get(url).json()
    
    for result in results['searchResults']:
        if result['name'] == '':
            place_name = "No name"
        else:
            place_name = result['name']
        
        if result['fields']['group_sic_code_name'] == '':
            place_category = "No category"
        else:
            place_category = result['fields']['group_sic_code_name']

        if result['fields']['address'] == '':
            place_address = "No address"
        else:
            place_address = result['fields']['address']
        
        if result['fields']['city'] == '':
            place_city = "No city"
        else:
            place_city = result['fields']['city']

        print("- " + place_name + " (" + place_category + "): " + place_address + ", " + place_city)
    return results

 
    

if __name__ == "__main__":
    CACHE_SITE_DICT = load_cache_site()

    dash = ('-' * 35)
    
    while True:
        state_name = input("Enter a state name, (e.g. Michigan, michigan) or “exit”:").lower()
        tmp = make_site_request_using_cache(state_name, CACHE_SITE_DICT)
       
        if state_name == "exit":
            exit()
        elif state_name in tmp.keys():
            print(dash)
            print('List of national sites in ' + state_name)
            print(dash)
            
            url = tmp[state_name]
            sites = make_state_url_request_using_cache(url)
            i = 1
            site_data_list = []
            for site in sites:
                site_data = "[" + str(i) + "] " + site.name + "(" + site.category + "): " + site.address + ", " + site.zipcode
                print(site_data)
                i += 1
                site_data_list.append(site)

            while True:
                search_number = input("Choose the number for detail search or “exit” or “back”:").lower()
                if search_number == "exit":
                    exit()
                elif search_number == "back":
                    break
                elif int(search_number) <= i:
                    searching_site = site_data_list[int(search_number)-1]
                    print(dash)
                    print('Places near ' + searching_site.name)
                    print(dash)

                    make_nearby_place_request_using_cache(searching_site)
                    break
                else:
                    print('[Error] Invalid input\n')
        else:
            print('[Error] Enter proper state name\n')