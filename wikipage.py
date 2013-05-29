import re
from stopwords import stopwords


class WikiPage:

    LEAVE_OUT = "(#cite_note)|(Help:)|(Wikipedia:)|(Category:)"
    WEED_OUT = "(.+)(,|\.|'s)"

    def __init__(self, spun):
        self.yarn = spun
        self.name = spun.body.find('h1', id='firstHeading').text
        self.weighed_links = {}
        self.links = []
        self.words = {}
        self.knit_yarn()

    def knit_yarn(self):
        content = self.yarn.find('div', id='mw-content-text')
        paras = content.find_all('p')
        for para in paras:
            para_links = para.find_all('a')
            for link in para_links:
                href = link.get('href')
                regex = re.compile(WikiPage.LEAVE_OUT)
                r = regex.search(href)
                if (href not in self.weighed_links) and (r is None):
                    self.weighed_links[href] = 0
                    self.links.append(href)
            word_list = para.text.split()
            for word in word_list:
                regex = re.compile(WikiPage.WEED_OUT)
                r = regex.search(word)
                if r is not None:
                    self.insert_word(r.groups()[0].lower())
                else:
                    self.insert_word(word.lower())

    def insert_word(self, word):
        if word not in stopwords:
            if word in self.words:
                self.words[word] += 1
            else:
                self.words[word] = 0
