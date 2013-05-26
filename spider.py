import requests
import threading
from bs4 import BeautifulSoup

import wikipage

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              '*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) '
                  'Gecko/20100101 Firefox/21.0'
}


url_d = 'http://en.wikipedia.org/wiki/Batman'
base_url = 'http://en.wikipedia.org'


def spin_yarn(url):
    response = requests.get(url, headers=req_headers)
    yarn = BeautifulSoup(response.text, 'html.parser')
    return(yarn)


class RootProcessor(threading.Thread):
    def __init__(self, url, que, level):
        self.url = url
        self.level = level
        self.display_que = que
        threading.Thread.__init__(self)

    def run(self):
        """
        This thread will take care of each root
        remember to acquire lock when updating wikipage link dict
        """
        root_page = WikiPage(spin_yarn(self.url), self.level)


def weave():
    page = spin_yarn(url_d)
    #infobox = page.find_all('table', class_='infobox')
    content = page.find('div', id='mw-content-text')
    paras = content.find_all('p')
    links = []
    for para in paras:
        links.extend(para.find_all('a'))
        #for text in para.stripped_strings:
        #    print(repr(text))
    #pprint.pprint(links)
    for l in links:
        print(l)
    #print(type(links[0]))


if __name__ == '__main__':
    weave()
