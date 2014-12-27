import requests
from datetime import date, timedelta
from random import randint
from time import sleep

#Today is my birthday!
first_day = date(1992, 1, 1) #is leap year
single_day = timedelta(days=1)

#Wikipedia grabbing
for day_offset in xrange(366):
    current_day = first_day + timedelta(days=day_offset)
    print current_day
    current_day_formatted = current_day.strftime('%B_%d')
    wiki_url = 'http://en.wikipedia.org/wiki/' + current_day_formatted
    wiki_req = requests.get(wiki_url)
    wiki_resp = wiki_req.text
    filename = 'wiki/' + current_day_formatted + '.html'
    with open(filename, 'w') as f:
        f.write(wiki_resp)
    sleep(randint(1, 5))