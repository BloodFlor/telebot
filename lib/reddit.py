import praw

def get_posts_reddit():
    posts = []
    reddit = praw.Reddit(client_id='Q0hjzGx07bNTuQ',
                    client_secret='SXz0GmmCYggfs6PXwF3NteM4PxY',
                    user_agent='my user agent')
    for submission in reddit.subreddit('Memes').hot(limit = 20):
        if (submission.link_flair_css_class == 'image') or ((submission.is_self != True) and ((".jpg" in submission.url) or (".png" in submission.url))):
            posts.append([ submission.title, submission.url])
    return posts
