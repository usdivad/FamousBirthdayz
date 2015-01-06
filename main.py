import datetime
from random import choice
import re
import urllib

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
# Sending a request
wiki_endpoint = 'http://en.wikipedia.org/wiki/' + today_formatted
wiki_req = requests.get(wiki_endpoint)
wiki_resp = wiki_req.text

# # Local files (good for testing)
# wiki_resp = ''
# with open('wiki/' + today_formatted + '.html', 'r') as f:
#    wiki_resp = f.read()

# Getting names and ages of people via BeautifulSoup
wiki_soup = BeautifulSoup(wiki_resp)
uls = wiki_soup.select('#content > #bodyContent > #mw-content-text > ul')
births = uls[1].select('li')
# print births
# re_yob = re.compile('\d+')
# re_name = re.compile('[\w+.* ]*,')
re_yob = re.compile('(?<=>)\d+')
re_name = re.compile('(?<=">)\D.*?(?=</a>,)')
re_link = re.compile('(?<= <a href="/wiki/).+?(?=")')
prepositions = ['and', 'of', 'in', 'for']

people = []
for i in xrange(len(births)):
    birthtext_text = births[i].get_text()
    birthtext = str(births[i])
    years = re.findall(re_yob, birthtext)
    names = re.findall(re_name, birthtext)
    links = re.findall(re_link, birthtext)

    # Getting descs, some rudimentary NLP
    # Example: Charles Xavier, British psychic and philanthropist, founder of X-Men
    # 1934 - Phil Ramone, South African-American record producer and DJ, co-founded A & R Recording (d. 2013)
    phrases = birthtext_text.split(',')[1:] #first element is year+name
    descs = []
    for phrase in phrases:
        descs.extend(phrase.split(' and '))
    for i in xrange(len(descs)):
        desc = []
        words = descs[i].split(' ')
        for word in words:
            if word.title() != word:
                desc.append(word)
        # descs[i] = ' '.join(desc)
        descs[i] = ''.join(desc) #already formatted
        print '#' + desc

    # Automatically include first link
    if len(links) > 1:
        # desc = links[1].replace('_', ' ')
        desc = links[1].replace('_', '') #already formatted
        descs.insert(0, desc) #prepend
        print '#' + desc

    if len(years) > 0 and len(names) > 0:
        person = {'age': today.year - int(years[0]), 'name': names[0]}
        if len(links) > 0:
            person['link'] = links[0]
            # if len(links) > 1:
            #     person['link'] = links[1]
            # else:
            #     person['link'] = links[0]
            # print person['link'] + ' for ' + person['name']
        person['descs'] = descs
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

# TWITTER authorize
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


# Construct the greeting!

# print len(people)
people = people[start:end]
# print people

greeting = 'This string is less than 140 characters long. It is still less than one hundred and forty characters long. But now this string\'s length > 140'
greeting = 'HAPPY BIRTHDAY YA\'LL HAPPY BIRTHDAY YA\'LL HAPPY BIRTHDAY YA\'LL HAPPY BIRTHDAY YA\'LL HAPPY BIRTHDAY YA\'LL HAPPY BIRTHDAY YA\'LL HAPPY BIRTHDAY YA\'LL'
person = {}

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

# Get person's picture if available
has_picture = False
picture_filename = 'person.jpg'

# ... using Wikipedia
if 'link' in person:
    person_endpoint = 'http://en.wikipedia.org/wiki/' + person['link']
    person_req = requests.get(person_endpoint)
    person_resp = person_req.text
    person_soup = BeautifulSoup(person_resp)
    person_infobox = person_soup.select('.infobox') #infobox biography vcard
    # print person_infobox
    if len(person_infobox) > 0:
        re_picture = re.compile('(?<=src=")(.+?\.jpg|.+?\.png)(?=")', re.IGNORECASE)
        picture_arr = re.findall(re_picture, str(person_infobox[0]))
        if len(picture_arr) > 0:
            print picture_arr
            picture_url = 'http:' + picture_arr[0]
            if 'png' in picture_url.lower():
                picture_filename = 'person.png'
            print picture_url
            urllib.urlretrieve(picture_url, picture_filename)
            print picture_url
            has_picture = True

# # ... using Bing
# bing_endpoint = 'http://www.bing.com/' + person['name']
# bing_req = requests.get(bing_endpoint)
# bing_resp = bing_req.text
# print bing_resp
# re_picture = re.compile('http://.+?\.jpg')
# picture_arr = re.findall(re_picture, bing_resp)
# if len(picture_arr) > 0:
#     print picture_arr
#     picture_url = picture_arr[0]
#     urllib.urlretrieve(picture_url, picture_filename)
#     print picture_url
#     has_picture = True

# TWITTER post
resp = {'id': 'FAILED'}
if has_picture:
    resp = api.update_with_media(picture_filename, status=greeting)
else:
    resp = api.update_status(greeting)
print resp.id