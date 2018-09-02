# test_capitalize.py
import pytest, os
from mock import Mock, MagicMock

from praw2 import Reddit
from subreddits import SubRedditEvents

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

class comment():
    def __init__(self, id, score):
        self.id = id
        self.score = score
        self.body = self.load_body()

    def load_body(self):
        with open(os.path.join(FIXTURES_PATH, "{}.txt".format(self.id)), 'r') as f:
            return f.read()

@pytest.fixture
def mock_reddit():
    reddit = Mock(spec=Reddit)
    reddit.submission.return_value.comments.list.return_value = [comment('nflstreams_comment_1', 1)]
    return reddit

def test_subreddits_event_links_nflstreams_1():
    reddit = Mock(spec=Reddit)
    reddit.submission.return_value.comments.list.return_value = [comment('nflstreams_comment_1', 1)]
    sr = SubRedditEvents(client=reddit)
    results = sr.get_event_links(submission_id="nflstreams_comment_1")
    assert isinstance(results, list)
    assert results == [(1, '[HD] [NBC] [EN]', 'acestream://1f427d0e2c1b9d365369f8fa88a32e09583a9c03')]

def test_subreddits_event_links_soccerstreams_1():
    reddit = Mock(spec=Reddit)
    reddit.submission.return_value.comments.list.return_value = [comment('e4x7mg6_9aq6d8_output', 1)]
    sr = SubRedditEvents(client=reddit)
    results = sr.get_event_links(submission_id="e4x7mg6_9aq6d8_output")
    assert isinstance(results, list)
    assert len(results) == 0

def test_subreddits_event_links_soccerstreams_2():
    reddit = Mock(spec=Reddit)
    reddit.submission.return_value.comments.list.return_value = [comment('e4x7xf9_9aq6d8_output', 1)]
    sr = SubRedditEvents(client=reddit)
    results = sr.get_event_links(submission_id="e4x7xf9_9aq6d8_output")
    assert isinstance(results, list)
    assert results == [
        (1, '[HD] [MATCH! FUTBOL 1] [RU]', 'acestream://e1d935d46c9d40d19700273c9ea3ff94b37c7cfd'),
        (1, '[520P] [MATCH! FUTBOL 1] [RU]', 'acestream://0e9535e1fb8bf175f823596326688c9da1020f80'),
        (1, '[HD] [MATCH! TV] [RU]', 'acestream://a6321e085ea80432007c05989263822bc3e4a10d'),
        (1, '[520P] [MATCH! TV] [RU]', 'acestream://e395ed3864f9e1678f9b1ef2c6d1b0ae64648177'),
    ]

def test_subreddits_event_links_motorsportsstreams_1():
    reddit = Mock(spec=Reddit)
    reddit.submission.return_value.comments.list.return_value = [comment('motorsportsstreams_comment_1', 1)]
    sr = SubRedditEvents(client=reddit)
    results = sr.get_event_links(submission_id="motorsportsstreams_comment_1")
    assert isinstance(results, list)
    assert results == [
        (1, '[Bein Sports USA] [720p] [EN]', 'acestream://7a59ee311d1e9e908e7526b081159fe29ca4e360')
    ]
