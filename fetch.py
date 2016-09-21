"""Fetch detailed election results from the RosIzbirKom website."""
import os
import os.path as P
import http.client
import unittest
import io
import logging
import time
# import codecs

import lxml.etree
import requests

"""The URL from which to start fetching from."""
TOP_URL = "http://www.vybory.izbirkom.ru/region/\
izbirkom?action=show&global=1&vrn=100100067795849&region=0&prver=0&pronetvd=0"

"""The anchor text for the tables we're interested in.  Currently, there are
both preliminary results, and final results."""
RESULTS_TABLE = [
    "Сводная таблица итогов голосования по федеральному избирательному округу",
    "Сводная таблица предварительных итогов голосования по федеральному \
избирательному округу"
]


def write(filename, content):
    """Save a HTML file to our temporary directory (mostly for debugging)."""
    curr_dir = P.dirname(P.abspath(__file__))
    tmp_dir = P.join(curr_dir, "gitignore")
    if not P.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    path = P.join(curr_dir, "gitignore", filename)
    with open(path, "w") as fout:
        fout.write(content)


def read(filename):
    """Read a HTML file from our temporary subdirectory."""
    curr_dir = P.dirname(P.abspath(__file__))
    path = P.join(curr_dir, "gitignore", filename)
    with open(path, "r") as fin:
        return fin.read()


def persistent_fetch(url):
    """Fetch from the specified URL. Don't give up until we have something."""
    while True:
        r = requests.get(url)
        assert r.status_code == http.client.OK
        if r.text:
            return r.text
        else:
            #
            # This happens from time to time. Not sure why.
            #
            logging.error("received empty reply, retrying")
            time.sleep(5)


def parse_links(html):
    """Parse links to polling stations from a HTML string."""
    logging.debug("parse_links")
    logging.debug("%r", html)
    parser = lxml.etree.HTMLParser()
    tree = lxml.etree.parse(io.StringIO(html), parser)
    return [
        (e.get("value"), e.text.strip()) for e in tree.xpath("//option")
        if e.get("value")
    ]


def parse_table_link(html):
    """Parse the link to the result table from a HTML string."""
    logging.debug("parse_table_link")
    logging.debug("%r", html)
    parser = lxml.etree.HTMLParser()
    tree = lxml.etree.parse(io.StringIO(html), parser)
    links = [
        e for e in tree.xpath("//a")
        if e.text.strip() in RESULTS_TABLE
    ]
    assert len(links) == 1
    return links[0].get("href"), links[0].text


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.ERROR)

    top = persistent_fetch(TOP_URL)
    write("top.html", top)

    for url, name in parse_links(top):
        for url2, name2 in parse_links(persistent_fetch(url)):
            logging.info("processing: %r %r", name, name2)
            html = persistent_fetch(url2)
            write("_".join(["tmp", name2]) + ".html", html)

            results_url, anchor = parse_table_link(html)
            results = persistent_fetch(results_url)
            write("_".join(["results", name2, anchor]) + ".html", results)

            time.sleep(5)


if __name__ == "__main__":
    main()


class TestParseLinks(unittest.TestCase):

    def test(self):
        html = read("top.html")
        primary = parse_links(html)
        urls, names = zip(*primary)

        self.assertEqual(len(primary), 85)
        self.assertTrue("Республика Алтай" in names)


class TestParseTableLink(unittest.TestCase):

    def test(self):
        html = read("Республика Адыгея (Адыгея)_1 Республика Адыгея \
(Адыгея) - Адыгейский.html")
        link = parse_table_link(html)
        print("link: %r" % link)
        self.assertIsNotNone(link)
