import random
from lib.pikabu import get_posts_pikabu
from lib.reddit import get_posts_reddit

def GetMem(message):
    posts = []
    if not {'red', 'reddit','реда', 'реддита', 'реддит', 'ред'}.isdisjoint(message.lower().split(' ')):
        posts = get_posts_reddit()
    else:
        posts = get_posts_pikabu()
    return random.choice(posts)
