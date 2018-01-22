import requests
from bs4 import BeautifulSoup as bss

SEARCH_URL = 'https://acestreamsearch.com/en/'
CHANNELS_URL = 'http://acestreamchannel.blogspot.co.uk/'

def acesearch(term):
    """
    Search URL for acestreams and return list of dictionaries containing
    the name and acestream URL
    """
    r = requests.post(SEARCH_URL, data = {'cn':term})
    soup = bss(r.text, "html.parser")
    items = []
    for i in soup.findAll('a', {'class': 'list-group-item'}):
        items.append({'url': i['href'], 'desc': i.contents[0]})
    return items

def acestream_channels():
    """
    Return a list of tvshows from acestream channels url
    """
    items = []
    r = requests.get(CHANNELS_URL)
    soup = bss(r.text, 'html.parser')
    for i in soup.find('table').findAll('tr'):
        try:
            stream_name = i.find('td').renderContents()
            if not stream_name:
                continue
        except:
            continue
        try:
            ace_link = i.find('a').get('href')
        except:
            continue
        try:
            style = i.find('a').get('style')
        except:
            pass
        if not style:
            color = 'grey'
        elif 'red' in style:
            color = 'red'
        elif 'green' in style:
            color = 'green'
        else:
            color = 'blue'
        items.append({'url': ace_link, 'color': color, 'desc': stream_name })
    return items
