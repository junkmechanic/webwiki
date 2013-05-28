import re


class WikiPage:

    LEAVE_OUT = "(#cite_note)|(Help:)|(Wikipedia:)|(Category:)"

    def __init__(self, spun, level=0):
        self.yarn = spun
        self.name = spun.body.find('h1', id='firstHeading').text
        self.weighed_links = {}
        self.links = []
        self.words = {}
        self.level = level
        self.get_links()

    def get_links(self):
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



#for i in b:
#    regex = re.compile('(.+),')
#    r = regex.search(i)
#    if r is not None:
#        print(r.groups()[0])
