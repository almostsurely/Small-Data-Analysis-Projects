import json
import http.client
import matplotlib.pyplot as plt
from collections import Counter

#Gets Reddit page, including count and after parameters
def get_bestof_page(count, after):

    #Establish Reddit Connection and read response.
    conn = http.client.HTTPConnection('www.reddit.com')
    hdr = {'User-Agent' : 'Bestof Top Subreddits'}
    conn.request('GET',
                 '/r/bestof/top/.json?sort=top&t=all&limit=100&count=%s&after=%s' % (count, after),
                 headers=hdr)
    response = conn.getresponse().readall().decode('utf-8')
    return json.loads(response)

#Initialize after and sub_list variables
after = None
sub_list = []

#For the first 1000 posts
for i in range(0, 1000, 100):

    #Gets the page
    page = get_bestof_page(i, after)

    #For next page's after parameter
    after = page['data']['after']

    #If there is not after, then we reach the end
    if not after:
        break

    #Generates a list of subs linked, which are stored as link_flair_text
    page_subs = [x['data']['link_flair_text'] for x in page['data']['children']]

    #Appends sub list from page to master list
    sub_list += page_subs

#Counts subs listed
counted = Counter(sub_list)

#Prints the most common 100 Subreddits
for sub in counted.most_common(100):
    print(sub)
