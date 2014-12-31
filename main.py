import datetime
from random import choice
import re

from bs4 import BeautifulSoup
import requests
import tweepy

# Add suffix to a number, e.g. 123 -> 123rd
def add_suffix(num):
    num_str = str(num)
    digit = int(num_str[-1])
    suffix = 'th'
    # if digit == 0 or digit >= 4:
    #     suffix = 'th'
    if digit == 1:
        suffix = 'st'
    elif digit == 2:
        suffix = 'nd'
    elif digit == 3:
        suffix = 'rd'

    return num_str + suffix


#Today is my birthday!
# today = datetime.date.today()
today = datetime.datetime.now()
today_formatted = today.strftime('%B_%d')

# WIKIPEDIA
# # Sending a request
# wiki_endpoint = 'http://en.wikipedia.org/' + today_formatted
# wiki_req = requests.get(wiki_url)
# wiki_resp = wiki_req.text

# Local files (good for testing)
wiki_resp = ''
with open('wiki/' + today_formatted + '.html', 'r') as f:
   wiki_resp = f.read()

# Getting names and ages of people via BeautifulSoup
wiki_soup = BeautifulSoup(wiki_resp)
uls = wiki_soup.select('#content > #bodyContent > #mw-content-text > ul')
births = uls[1].select('li')
# print births
# re_yob = re.compile('\d+')
# re_name = re.compile('[\w+.* ]*,')
re_yob = re.compile('(?<=a href="/wiki/)\d+')
re_name = re.compile('(?<=">)\D.*?(?=</a>,)')
people = []
for i in xrange(len(births)):
    # birthtext = births[i].get_text()
    birthtext = str(births[i])
    years = re.findall(re_yob, birthtext)
    names = re.findall(re_name, birthtext)
    if len(years) > 0 and len(names) > 0:
        person = {'age': today.year - int(years[0]), 'name': names[0]}
        people.append(person)

# Choose subset of people based on time of day and how often posts are made
# Because we use integer division for indices the last batch may have a couple entries lopped off
# e.g. if len(people)=214 and POSTS_PER_DAY=8, unit=26, but 26*8=208!=214
POSTS_PER_DAY = 24
unit = len(people)/(POSTS_PER_DAY) #use integer division
batch_count = int(POSTS_PER_DAY * (today.hour/24.))
start = batch_count * unit
end = start + unit #no need for - 1 here
# # Testing ranges
# for i in xrange(POSTS_PER_DAY):
#     start = i * unit
#     end = start + unit - 1
#     print '{}-{}'.format(str(start), str(end))

# Construct the greeting!

people = people[start:end]
greeting = 'This string is less than 140 characters long. It is still less than one hundred and forty characters long. But now this string\'s length > 140'

# Make sure it's < 140 chars...
while len(greeting) > 140:
    person = choice(people)

    age_first = True
    age_then_name = [
        'A happy dapper {} birthday to {}!',
        'Celebrating the {} birthday of {}!',
        'Lucky number {}: here\'s to you, {}!',
        'Happy {}, {}!',
        'Happy {} birthday, {}!'
        ]

    name_then_age = [
        'Today is {}\'s birthday! Happy {} birthday!',
        'Happy birthday dear {}, happy {} birthday to you!',
        '{}\'s {} birthday is today. YAY!',
        'HEY! It\'s {}\'s {} birthday today! ',
        'Time flies when it\'s {}\'s {} birthday!'
        ]
    last_resort = 'Happy bday {}'

    greetings = choice([age_then_name, name_then_age])
    if greetings == name_then_age:
        age_first = False
    greeting = ''

    if age_first:
        greeting = choice(greetings).format(add_suffix(str(person['age'])), person['name'])
    else:
        greeting = choice(greetings).format(person['name'], add_suffix(str(person['age'])))

    print greeting


# TWITTER
# Authorize and post
keys = [line.rstrip('\n') for line in open('keys.txt')]
consumer_key = keys[0]
consumer_secret = keys[1]
access_key = keys[2]
access_secret = keys[3]

tweet_endpoint = 'https://api.twitter.com/1.1/statuses/update.json'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# redirect_url = auth.get_authorization_url()
# verifier = requests.get('oauth_verifier')
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)
resp = api.update_status(greeting)
print resp.id