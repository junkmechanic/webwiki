import requests
import threading
import Queue
import time
from bs4 import BeautifulSoup
from operator import itemgetter
import pprint

from wikipage import WikiPage

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


class Worker(threading.Thread):
    def __init__(self, url, que):
        self.url = url
        self.display_que = que
        threading.Thread.__init__(self)

    def run(self):
        page = WikiPage(spin_yarn(base_url + self.url))
        try:
            print("Inserting {} ...".format(self.url))
            self.display_que.put((self.url, page), block=True, timeout=2)
        except:
            print("Error in inserting {} in queue".format(self.url))


class RootProcessor(threading.Thread):
    def __init__(self, url, que, level=1, max_thrds=3):
        self.url = url
        self.level = level
        self.display_que = que
        self.workers = []
        self.max_threads = max_thrds
        threading.Thread.__init__(self)

    def run(self):
        """
        This thread will take care of each root
        remember to acquire lock when updating wikipage link dict
        """
        root_page = WikiPage(spin_yarn(self.url), self.level)
        try:
            print("Inserting {} ...".format(self.url))
            self.display_que.put((self.url, root_page), block=True, timeout=2)
        except:
            print("Error in inserting {} in queue".format(self.url))
        for i in range(10):
            added = False
            while not added:
                if len(self.workers) < self.max_threads:
                    print("RootProcessor spawning new worker")
                    new_worker = Worker(root_page.links[i], self.display_que)
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
        while 1:
            try:
                url, page = self.queue.get(block=True, timeout=4)
                i = 0
                for word in sorted(page.words.iteritems(), key=itemgetter(1),
                                   reverse=True):
                    if i < 4:
                        i += 1
                        pprint.pprint(url + ' -> ' + word[0] + ':' + str(word[1]))
                    else:
                        break
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
