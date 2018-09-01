import os, sys, re, json
from praw2 import Reddit
reload(sys)

try:
    from xbmc import log
except:
    def log(msg):
        print(msg)

sys.setdefaultencoding("utf-8")

CLIENT_ID = 'J_0zNv7dXM1n3Q'
CLIENT_SECRET = 'sfiPkzKDd8LZl3Ie1WLAvpCICH4'
USER_AGENT = 'sparkle streams 1.0'

class SubRedditEvents(object):
    as_regex_str = r'(acestream://[^$\s]+)'

    def __init__(self, username=None, password=None, client=None):
        self.client = client or Reddit(client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET,
                              user_agent=USER_AGENT,
                              username=username,
                              password=password,
                            )
        self.as_regex = re.compile(self.as_regex_str, re.IGNORECASE)

    @staticmethod
    def get_as_links(body):
        """
        For each acestream link, return a tuple of acestream link,
        and link quality
        """
        return re.findall('(acestream://[a-z0-9]+)\s*(.*)', body)

    @staticmethod
    def priority(entry):
        """
        For cases where we have multiple entries for the same acestream link,
        prioritize based on the quality text to get the best text possible
        """
        if not entry[0]:
            return (entry, 3)
        elif re.search('.*\[.*\].*', entry[0]):
            return (entry, 1)
        else:
            return (entry, 2)

    @staticmethod
    def collapse(entries):
        """
        Collapse oure list of acestream entries to pick only one with the best
        quality text
        """
        results = []
        prev = None
        # Sort the entries by our priority logic, then iterate
        for entry in sorted(entries, key=lambda entry: priority(entry), reverse=True):
            if prev != entry[0]:
                results.append(entry)
            prev = entry[0]
        return results

    def get_events(self, subreddit, filtering=False):
        subs = []
        path = '/r/{}'.format(subreddit)
        for submission in self.client.get(path):
            sub_id = submission.id
            score = submission.score
            title = submission.title
            title = title.encode('utf-8')
            subs.append({'submission_id': sub_id, 'title': title, 'score': score })
        return sorted(subs, key=lambda d: d['score'], reverse=True)

    def get_event_links(self, submission_id):
        submission = self.client.submission(id=submission_id)
        links = []
        scores = {}
        # Add the extracted links and details tuple
        for c in submission.comments.list():
            if hasattr(c, 'body'):
                links.extend(self.get_as_links(c.body.encode('utf-8')))
            # Add entry to our scores table taking the largest score for a given
            # acestream link
            score = c.score if hasattr(c, 'score') else 0
            for entry in links:
                scores[entry[0]] = max(scores.get(entry[0], 0), score)
        if len(links) > 0:
            return [(s, q, a) for ((a, q), s) in
                zip(links, map(lambda x: scores[x[0]], links))]
        else:
            return links
