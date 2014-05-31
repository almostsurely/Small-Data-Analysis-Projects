import json
import http.client
import string
import matplotlib.pyplot as plt

#Establish Reddit Connection and read response.
conn = http.client.HTTPConnection('www.reddit.com')
hdr = {'User-Agent' : 'Lexical Diversity Test'}
conn.request('GET', '/r/WritingPrompts/.json?limit=100', headers=hdr)
response = conn.getresponse().readall().decode('utf-8')

#Load response into dictionary
front_page = json.loads(response)

#Creates a list of tuples of post ids and popularity.
#Removes Moderator Posts, Prompt Me's, and Prompt Inspired.
#These post types do not have stories as the first tier of comments.
posts = [
    (x['data']['id'], x['data']['ups'] - x['data']['downs'])
    for x in front_page['data']['children']
    if x['data']['num_comments'] > 0 and
    x['data']['link_flair_text'] not in ['Moderator Post',
                                         'Prompt Me',
                                         'Prompt Inspired']
    ]

#Initialize our list of stories
stories = []

#Iterates through all posts
for post in posts:
    post_id, popularity = post

    #Requests and loads responses to prompt into a dictionary.
    conn.request('GET', '/r/WritingPrompts/comments/%s/.json' % post_id,
                 headers=hdr)
    response = conn.getresponse().readall().decode('utf-8')

    data = json.loads(response)

    #Grabs the list of top tier comments from post.
    #These are the individual story responses to the prompt.
    comments = data[1]['data']['children']

    #Iterate through each story.
    for story in comments:
        text = story['data']['body']

        #Removes all punctuation from text.
        #Gives us clean text to work with.
        for ch in string.punctuation:
            text = text.replace(ch, '')

        #List of all words in text
        words = [word for word in text.split()]

        #By casting to a set, we now have a group of unique words
        unique_words = set(words)

        #The lexical diversity of the story is derived by dividing
        #the total number of unique words by the word total.
        diversity = len(unique_words)/len(words)

        #Establishes the popularity of the story within the prompt.
        story_popularity = story['data']['ups'] - story['data']['downs']

        try:
            #Here we attempt to normalize the popularity by dividing
            #the story popularity by the total popularity of the prompt.
            #This is an attempt to compare the popularity of stories
            #between prompts with different popularities
            norm_popularity = story_popularity/popularity
        except ZeroDivisionError:
            norm_popularity = 0

        #Add our findings to the stories list.
        stories.append((diversity, norm_popularity))

stories.sort()

#Group items by 0.1 level of lexical diversity, and find the average
#popularity amongst them.

x = []

for i in range(1, 10):
    i *= 0.1

    pop_group = [a[1] for a in stories if i <= a[0] < (i + .10)]
    try:
        avg = sum(pop_group)/len(pop_group)
    except ZeroDivisionError:
        avg = 0

    x.append(avg)

#Plot the results
plt.bar([i * .10 for i in range(1,10)], x, 0.1)
plt.xlabel('Lexical Diversity')
plt.ylabel('Average Popularity')
plt.show()
