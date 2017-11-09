__author__ = 'Chris Bredernitz'

from requests_oauthlib import OAuth2Session
import json
import webbrowser
from eventbrite_data import client_id, client_secret
import csv

## CACHING SETUP
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CREDS_CACHE_FILE = "creds.json"

#--------------------------------------------------
# Load cache files: data and credentials
#--------------------------------------------------

#  Load token cache
def get_saved_token():
    with open(CREDS_CACHE_FILE, 'r') as f:
        token_json = f.read()
        token_dict = json.loads(token_json)
        return token_dict

#  Save token cache
def save_token(token_dict):
    with open(CREDS_CACHE_FILE, 'w') as f:
        token_json = json.dumps(token_dict)
        f.write(token_json)

#  Save data cache
def save_cache(cache_dict, cache_fname):
    with open(cache_fname, 'w') as f:
        cache_json = json.dumps(cache_dict)
        f.write(cache_json)

#  Load data cache
def get_data_cache(cache_fname):
    with open(cache_fname, 'r') as f:
        cache_json = f.read()
        cache_dict = json.loads(cache_json)
        return cache_dict

## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.

#  Client ID and Client Secret obtained by setting up an application through
#  your eventbrite profile.
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CLIENT_ID = client_id
CLIENT_SECRET = client_secret

#  Below are the urls and redirect URI specified in your application profile.
#  The two URL's SHOULD NOT CHANGE sicne these are provided by eventbrite

REDIRECT_URI = 'https://www.programsinformationpeople.org/runestone/oauth'
AUTHORIZATION_URL = 'https://www.eventbrite.com/oauth/authorize'
TOKEN_URL = 'https://www.eventbrite.com/oauth/token'
scope = []  # Define your scope if you change the requests
oauth2inst = False

def start_eventbrite_session():
    #  we use 'global' to tell python that we will be modifying this global variable.
    #  the 'global' makes it so that we can modify the global variable and assign the oauth instance to something we can keep calling to.
    global oauth2inst

    try:
        token = get_saved_token()

    except FileNotFoundError:
        token = None

    #  if there is a token availible then we will use that
    if token:
        oauth2inst = OAuth2Session(CLIENT_ID, token = token)

    else:
        #  Session
        print("-- Getting authorization from Eventbrite -- ")
        oauth2inst = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope = scope)

        #  Authorization
        authorization_url, state = oauth2inst.authorization_url(AUTHORIZATION_URL)
        webbrowser.open(authorization_url)

        #  Creates a token variable
        authorization_response = input('Authenticate and then enter the full callback URL: ').strip()
        token = oauth2inst.fetch_token(TOKEN_URL, authorization_response=authorization_response, client_secret=CLIENT_SECRET)

        #  saves the token for future requests
        save_token(token)

#  Main function to make the request.
def Make_Eventbrite_request(url, params=None):
    global oauth2inst

    if not oauth2inst:
        start_eventbrite_session()

    if not params:
        params = {}

    return oauth2inst.get(url, params=params)

# Making a request to events in the Ann Arbor area
try:
    aa_response_dict = get_data_cache('AA_cache_content.json')
    print("We are using the cache file!\n")

except:
    print("Fetching data from the Eventbrite API for events in Ann Arbor, MI")
    event_url = 'https://www.eventbriteapi.com/v3/events/search/'
    aa_event_info = Make_Eventbrite_request(event_url, params = {"location.address": "Ann Arbor, MI"})
    aa_response_dict = json.loads(aa_event_info.text)
    save_cache(aa_response_dict, "AA_cache_content.json")

#  Making a request to get events in the San Francisco area
try:
    sf_response_dict = get_data_cache('SF_cache_content.json')
    print("We are using the cache file!\n")

except:
    print("Fetching data from the Eventbrite API for events in San Francisco, CA")
    event_url = 'https://www.eventbriteapi.com/v3/events/search/'
    sf_event_info = Make_Eventbrite_request(event_url, params = {"location.address": "San Francisco, CA"})
    sf_response_dict = json.loads(sf_event_info.text)
    save_cache(sf_response_dict, "SF_cache_content.json")


# Class to handle assignment for CSV files
class Assignment(object):
    """ Class to Assign the information in the JSON file to variables.  This makes creating the csv file easier."""
    def __init__(self, json_data):
        # for x in json_data['events']:
        self.Name = json_data['name']['text'].encode('utf-8')
        self.Start = json_data['start']['local']
        self.End = json_data['end']['local']
        self.Description = json_data['description']['text']
        if json_data['is_free']:
            self.Price = "Free"
        if not json_data['is_free']:
            self.Price = "Paid"

#  Class instances of each event from the request
aa_assingment = []
for x in aa_response_dict['events']:
    aa_assingment.append(Assignment(x))

sf_assingment = []
for x in sf_response_dict['events']:
    sf_assingment.append(Assignment(x))

##############################################################################
# The below handles writing CSV files of the data collected above

with open('Ann_Arbor_Events.csv', 'w', newline = '') as AA_Events_csv:
    AA_writter = csv.writer(AA_Events_csv, delimiter=',')
    AA_writter.writerow(["Name",
                        "Start Time",
                        "End Time",
                        "Description",
                        "Price"])
    for info in aa_assingment:
        AA_writter.writerow([info.Name,
                                info.Start,
                                info.End,
                                info.Description,
                                info.Price])
AA_Events_csv.close()

with open('San_Francisco_Events.csv', 'w', newline = '') as SF_Events_csv:
    SF_writter = csv.writer(SF_Events_csv, delimiter=',')
    SF_writter.writerow(["Name",
                        "Start Time",
                        "End Time",
                        "Description",
                        "Price"])
    for info in sf_assingment:
        SF_writter.writerow([info.Name,
                            info.Start,
                            info.End,
                            info.Description,
                            info.Price])
SF_Events_csv.close()
