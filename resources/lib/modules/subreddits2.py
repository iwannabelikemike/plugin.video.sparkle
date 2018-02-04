import os
import log_utils
import re
import urlparse
import praw2

CLIENT_ID = 'J_0zNv7dXM1n3Q'
CLIENT_SECRET = 'sfiPkzKDd8LZl3Ie1WLAvpCICH4'
USER_AGENT = 'sparkle streams 1.0'

class subreddits(object):
    as_regex_str = r'(acestream://[^$\s]+)'
    newregex = r'(.*acestream://.*")'
    comment_url = 'https://www.reddit.com/r/MMAStreams/comments/{}'

    def __init__(self, username=None, password=None):
        self.client = praw2.Reddit(client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET,
                              user_agent=USER_AGENT,
                              username=username,
                              password=password,
                            )
        self.as_regex = re.compile(self.as_regex_str, re.IGNORECASE)

    def events(self, subreddit, filtering=False):
        subs = []
        path = '/r/{}'.format(subreddit)
        for submission in self.client.get(path):
            sub_id = submission.id
            score = submission.score
            title = submission.title
            title = title.encode('utf-8')
            subs.append({'submission_id': sub_id, 'title': title, 'score': score })
        return sorted(subs, key=lambda d: d['score'], reverse=True)

    def event_links(self, submission_id):
        submission = self.client.submission(id=submission_id)
        links = []
        for c in submission.comments.list():
            if hasattr(c, 'body'):
                linkline = re.findall(self.newregex, c.body.encode('utf-8'))
                if linkline:
                    findstr = linkline.split('acestream://')
                if as_links:
                    links.append({'quality': findstr[0]
                                  'comment_id': c.id,
                                  'score': c.score,
                                  'ace_links': findstr[1]})
        # Return the list sorted by score
        return sorted(links, key=lambda d: d['score'], reverse=True)
