## import statements
__author__ = 'Chris Bredernitz'

from requests_oauthlib import OAuth2Session
import json
import webbrowser
import eventbrite_data
import csv
## CACHING SETUP
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = "cache_contents.json"
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
def save_cache(cache_dict):
    with open(CACHE_FNAME, 'w') as f:
        cache_json = json.dumps(cache_dict)
        f.write(cache_json)

#  Load data cache
def get_data_cache():
    with open(CACHE_FNAME, 'r') as f:
        cache_json = f.read()
        cache_dict = json.loads(cache_json)
        return cache_dict



## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.

#  Client ID and Client Secret obtained by setting up an application through
#  your eventbrite profile.
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CLIENT_ID = eventbrite_data.client_id
CLIENT_SECRET = eventbrite_data.client_secret

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
    response_dict = get_data_cache()
    print("We are using the cache file!\n")

except:
    print("Fetching data from the Eventbrite API for events in Ann Arbor, MI")
    event_url = 'https://www.eventbriteapi.com/v3/events/search/'
    event_info = Make_Eventbrite_request(event_url, params = {"location.address": "Ann Arbor"})
    response_dict = json.loads(event_info.text)
    save_cache(response_dict)

# print(json.dumps(response_dict, indent=2))

# prints out each of the event names
for x in response_dict['events']:
    print("\n")
    print(x['name']['text'])
    print('-'*20)

# Class to handle assignment
# class Assignment(object):
#     """ Class to Assign the information in the JSON file to
#         variables.  This makes creating the csv file easier."""
#     def __init__(self, json_data):
#         # for x in json_data['events']:
#         self.Name = json_data['name']['text']
#         self.Start =
#


# The below handles writing CSV files of the data collected above

# with open('Ann_Arbor_Events.csv', 'w', newline = '') as AA_events:
#     AA_writter = csv.writer(california_csv, delimiter=',')
#     AA_writter.writerow(["Name",
#                             "Start Time",
#                             "End Time",
#                             "Address",
#                             "Description"])
#     for info in california_natl_sites:
#         movie_writter.writerow([info.name, info.location, info.type, info.get_mailing_address(), info.description])
# california_csv.close()

##############################################################################
#Example request to retrieve personal info on my profile

# p_url = 'https://www.eventbriteapi.com/v3/users/me/?token=ZQFUUDM33JTWKSOGO4Z'
# personal_info = Make_Eventbrite_request(p_url)
# response_diction = json.loads(personal_info.text)
# print(json.dumps(response_diction, indent=2))


    ## Make sure to run your code and write CSV files by the end of the program.
