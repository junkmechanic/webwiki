class WikiPage:
    def __init__(self, spun, level=1):
        self.yarn = spun
        self.name = spun.body.find('h1', id='firstHeading').text
        self.links = {}
        self.words = {}
        self.level = level

    def get_links(self):
        content = self.yarn.find('div', id='mw-content-text')
        paras = content.find_all('p')
        for para in paras:
            para_links = para.find_all('a')
            for link in para_links:
                href = link.get('href')
                if href not in self.links:
                    self.links[href] = 0



#for i in b:
#    regex = re.compile('(.+),')
#    r = regex.search(i)
#    if r is not None:
#        print(r.groups()[0])
