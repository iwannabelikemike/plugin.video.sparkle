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

as_regex_str = [r'(.*)(acestream://[a-f0-9]{40})(.*)', r'(.*)([a-f0-9]{40})(.*)']

# order of link qualities
LQ_1080p60 = 0
LQ_720p60  = 1
LQ_1080p30 = 2
LQ_720p30  = 3
LQ_OTHER   = 4

class SubRedditEvents(object):
    def __init__(self, username=None, password=None, client=None):
        self.client = client or Reddit(client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET,
                              user_agent=USER_AGENT,
                              username=username,
                              password=password,
                            )
        self.as_regex = re.compile(as_regex_str[0], re.IGNORECASE)

    @staticmethod
    def get_as_links(body):
        """
        For each acestream link, return a tuple of acestream link,
        and link quality
        """
        links = []
        for entry in body.split('\n'):
            linkfound = False
            for regx_str in as_regex_str:
                res = re.findall(regx_str, entry)
                if res and not linkfound:
                    linkfound = True
                    pre, acelink, post = res[0]
                    if 'acestream://' not in acelink.strip():
                        acelink = 'acestream://' + acelink.strip()

                    title = ''
                    if len(pre.strip()) > len(post.strip()):
                        title = pre.strip().replace('\\','')
                    else:
                        title = post.strip().replace('\\','')

                    quality = LQ_OTHER
                    if '1080' in title or '[HD]' in title:
                        quality = LQ_1080p30
                        if '60' in title:
                            quality = LQ_1080p60
                    elif '720' in title or '[SD]' in title:
                        quality = LQ_720p30
                        if '60' in title:
                            quality = LQ_720p60

                    links.append((acelink, title, quality))
        return links

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
        links_title = {}
        links_quality = {}
        scores = {}
        # Add the extracted links and details tuple
        for c in submission.comments.list():
            templinks = []
            if hasattr(c, 'body'):
                templinks = self.get_as_links(c.body.encode('utf-8'))
            # Add entry to our scores table taking the largest score for a given
            # acestream link
            score = c.score if hasattr(c, 'score') else 0
            for link,title,quality in templinks:
                scores[link] = max(scores.get(link, 0), score)
                if link not in links_title.keys():
                    links_title[link] = title
                elif len(links_title[link]) < len(title):
                    # Duplicate link found, update title if longer
                    links_title[link] = title
                # Update link quality if specified in title
                links_quality[link] = min(links_quality.get(link, 4), quality)
        # Sort links by quality
        for i in range(LQ_1080p60, LQ_OTHER + 1):
            for link,quality in links_quality.items():
                if i == quality:
                    links.append((link, links_title[link]))
        if len(links) > 0:
            return [(s, q, a) for ((a, q), s) in
                zip(links, map(lambda x: scores[x[0]], links))]
        else:
            return links
