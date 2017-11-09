__author__ = 'Chris Bredernitz'
from requests_oauthlib import OAuth2Session
import json
import webbrowser
from eventbrite_data import client_id, client_secret
import csv

## CACHING SETUP
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CREDS_CACHE_FILE = "creds.json"
CACHE_FNAME = "cache_contents.json"

#--------------------------------------------------
# Load cache files: data and credentials
#--------------------------------------------------
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

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
def save_cache(cache_dict, identifier):
    identifier = identifier.upper()
    CACHE_DICTION[identifier] = {
        'values': cache_dict,
    }

    with open(CACHE_FNAME, 'w') as f:
        cache_json = json.dumps(CACHE_DICTION)
        f.write(cache_json)

#  Load data cache
def get_from_data_cache(identifier, dictionary):
    identifier = identifier.upper()
    if identifier in dictionary:
        data = dictionary[identifier]['values']
    else:
        data = None
    return data

def create_request_identifier(url, params_diction):
    sorted_params = sorted(params_diction.items(),key=lambda x:x[0])
    params_str = "_".join([str(e) for l in sorted_params for e in l]) # Make the list of tuples into a flat list using a complex list comprehension
    total_ident = url + "?" + params_str
    return total_ident.upper()

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


def Make_Eventbrite_request(url, params=None):
    global oauth2inst

    if not oauth2inst:
        start_eventbrite_session()

    if not params:
        params = {}

    ident = create_request_identifier(url, params)
    data = get_from_data_cache(ident,CACHE_DICTION)
    if data:
        print("Loading from data cache: {}... data".format(ident))
    else:
        print("Fetching data from {}".format(ident))
        resp = oauth2inst.get(url, params=params)
        data = json.loads(resp.text)
        save_cache(data, ident)
    return data

base_url = 'https://www.eventbriteapi.com/v3/events/search/'

#  Envoking the function to two separate locations
aa_params = {"location.address": "Ann Arbor, MI"}
aa_ident = create_request_identifier(base_url, aa_params)
aa_data = Make_Eventbrite_request(base_url, aa_params)

sf_params = {"location.address": "San Francisco, CA"}
sf_ident = create_request_identifier(base_url, sf_params)
sf_data = Make_Eventbrite_request(base_url, sf_params)

# Class to handle assignment for CSV files
class Assignment(object):
    """ Class to Assign the information in the JSON file to variables.  This makes creating the csv file easier."""
    def __init__(self, json_data):
        # for x in json_data['events']:
        self.Name = json_data['name']['text'].encode('utf-8')
        self.Start = json_data['start']['local']
        self.End = json_data['end']['local']
        if json_data['description']['text'] == None:
            self.Description = 'None'
        else:
            self.Description = json_data['description']['text']
        if json_data['is_free']:
            self.Price = "Free"
        if not json_data['is_free']:
            self.Price = "Paid"

#  Class instances of each event from the request
aa_assingment = []
for x in aa_data['events']:
    aa_assingment.append(Assignment(x))

sf_assingment = []
for x in sf_data['events']:
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
