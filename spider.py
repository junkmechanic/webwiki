import requests
import threading
import Queue
import time
import math
from bs4 import BeautifulSoup
from operator import itemgetter

from wikipage import WikiPage

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              '*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) '
                  'Gecko/20100101 Firefox/21.0'
}

url_d = '/wiki/Batman'
base_url = 'http://en.wikipedia.org'

ROOT_IDS = 0

root_nodes = {}

lock = threading.Lock()


def spin_yarn(url):
    response = requests.get(url, headers=req_headers)
    yarn = BeautifulSoup(response.text, 'html.parser')
    return(yarn)


def compare_pages(root_page, page):
    similarity = 0
    for rword in root_page.word_dict.keys():
        for word in page.word_dict.keys():
            if word == rword:
                print(word)
                similarity += (1 - similarity) * (root_page.word_dict[rword] *
                                                  page.word_dict[word])
    print('{} <- {} -> {}'.format(root_page.url, str(similarity), page.url))
    if similarity > 0:
        lock.acquire()
        root_page.weighed_links[page.url] = math.exp(similarity * 50)
        lock.release()
        page.weighed_links[root_page.url] = math.exp(similarity * 50)


class Worker(threading.Thread):
    def __init__(self, url, que, parent_id):
        self.parent_id = parent_id
        self.url = url
        self.display_que = que
        threading.Thread.__init__(self)

    def run(self):
        page = WikiPage(spin_yarn(base_url + self.url), self.url)
        try:
            print("Inserting {} ...".format(self.url))
            self.display_que.put((page, self.parent_id, None), block=True,
                                 timeout=2)
        except:
            print("Error in inserting {} in queue".format(self.url))


class RootProcessor(threading.Thread):
    def __init__(self, url, que, level=1, max_thrds=3, parent_id=0):
        self.parent_id = parent_id
        self.url = url
        self.level = level
        self.display_que = que
        self.workers = []
        self.max_threads = max_thrds
        threading.Thread.__init__(self)
        self.get_id()

    def get_id(self):
        global ROOT_IDS
        lock.acquire()
        ROOT_IDS += 1
        self.id = ROOT_IDS
        lock.release()

    def run(self):
        root_page = WikiPage(spin_yarn(base_url + self.url), self.url)
        try:
            print("Inserting {} ...".format(self.url))
            self.display_que.put((root_page, self.parent_id, self.id),
                                 block=True, timeout=2)
        except:
            print("Error in inserting {} in queue".format(self.url))
        for i in range(10):
            added = False
            while not added:
                if len(self.workers) < self.max_threads:
                    print("RootProcessor spawning new worker")
                    new_worker = Worker(root_page.links[i], self.display_que,
                                        self.id)
                    self.workers.append(new_worker)
                    new_worker.start()
                    added = True
                else:
                    print("Cant insert presently!!")
                    print(self.workers)
                    time.sleep(1)
                    self.clear_workers()

    def clear_workers(self):
        for thrd in self.workers:
            if not thrd.isAlive():
                self.workers.remove(thrd)


class Displayer(threading.Thread):
    def __init__(self, que):
        self.queue = que
        threading.Thread.__init__(self)

    def run(self):
        global root_nodes
        while 1:
            try:
                page, parent_id, id = self.queue.get(block=True, timeout=4)
                i = 0
                sum = 0.0
                for word in sorted(page.words.iteritems(), key=itemgetter(1),
                                   reverse=True):
                    if i < 4:
                        i += 1
                        page.word_dict[word[0]] = word[1]
                        sum += word[1]
                    else:
                        break
                for word in page.word_dict.keys():
                    page.word_dict[word] = page.word_dict[word] / sum
                if id is not None:
                    lock.acquire()
                    root_nodes[id] = page
                    lock.release()
                if parent_id is not 0:
                    lock.acquire()
                    root_page = root_nodes[parent_id]
                    lock.release()
                    compare_pages(root_page, page)
                    print(root_page.weighed_links)
                self.queue.task_done()
            except:
                print("Queue is empty now")
                break


def weave():
    display_queue = Queue.Queue()
    root = RootProcessor(url_d, display_queue, 1)
    root.start()
    display = Displayer(display_queue)
    time.sleep(2)
    display.start()
    display_queue.join()


if __name__ == '__main__':
    weave()
