# -*- coding: utf-8 -*-
import re
import unittest
import logging
import os.path as P

import scrapy

LOGGER = logging.getLogger(__name__)

TOP_URL = "http://www.vybory.izbirkom.ru/region/\
izbirkom?action=show&global=1&vrn=100100067795849&region=0&prver=0&pronetvd=0"

RESULTS_REGEX = re.compile(
    "Сводная таблица (предварительных )?итогов голосования \
по федеральному избирательному округу",
    re.IGNORECASE | re.UNICODE
)

TEST = False


class MyspiderSpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["vybory.izbirkom.ru"]
    start_urls = (TOP_URL,)

    def parse(self, response):
        self.logger.debug("handling reponse from url: %r", response.url)

        for value in response.xpath("//option/@value").extract():
            self.logger.debug("extracted value: %r", value)
            yield scrapy.Request(value, callback=self.parse_level1)
            if TEST:
                break

    def parse_level1(self, response):
        self.logger.debug("handling reponse from url: %r", response.url)

        for value in response.xpath("//option/@value").extract():
            self.logger.debug("extracted value: %r", value)
            yield scrapy.Request(value, callback=self.parse_level2)
            if TEST:
                break

    def parse_level2(self, response):
        self.logger.debug("handling reponse from url: %r", response.url)

        for hyperlink in response.xpath("//a"):
            text = join(hyperlink.xpath("./text()").extract())
            self.logger.debug("text: %r", text)
            if RESULTS_REGEX.search(text):
                href = hyperlink.xpath("./@href").extract_first()
                self.logger.debug("extracted href: %r", href)
                yield scrapy.Request(href, callback=self.parse_table)

                if TEST:
                    break

    def parse_table(self, response):
        self.logger.debug("parse_table: called")
        yield parse(response.selector)


def join(list_of_strings):
    return " ".join(list_of_strings).strip()


def parse(root):
    electorate = join(
        root.xpath(
            "/html/body/table[2]/tr[4]/td/table[3]/tr[2]/td[2]/text()"
        ).extract()
    )
    logging.debug("parse: electorate: %r", electorate)

    station_names = [
        join(td.xpath(".//text()").extract())
        for td in root.xpath(
            "/html/body/table[2]/tr[4]/td/table[5]/tr/td[2]\
/div/table/tr[1]/td"
        )
    ]
    logging.debug("parse: station_names: %r", station_names)

    #
    # The 1st row is the header.  The 20th row is blank.  Ignore them.
    #
    stats_rows = list(range(1, 19))
    votes_rows = list(range(21, 35))

    stats = []
    votes = []
    for row in stats_rows + votes_rows:
        subtitle = join(
            root.xpath(
                "/html/body/table[2]/tr[4]/td/table[5]/tr/td[1]/table/\
tr[%d]/td[2]/nobr/text()" % row
            ).extract()
        )
        total_value = join(
            root.xpath(
                "/html/body/table[2]/tr[4]/td/table[5]/tr/td[1]/table/\
tr[%d]/td[3]/nobr/b/text()" % row
            ).extract()
        )
        LOGGER.debug("subtitle: %r total_value: %r", subtitle, total_value)

        if not subtitle:
            continue

        obj = {
            "subtitle": subtitle, "total_value": float(total_value),
            "stations": []
        }
        for st_number, st_name in enumerate(station_names, 1):
            value = join(
                root.xpath(
                    "/html/body/table[2]/tr[4]/td/table[5]/tr/td[2]/\
div/table/tr[%d]/td[%d]/nobr/b/text()" % (row, st_number)
                ).extract()
            )
            LOGGER.debug("name: %r value: %r", st_name, value)
            obj["stations"].append({"name": st_name, "value": float(value)})

        (stats if row in stats_rows else votes).append(obj)

    return {
        "electorate": electorate, "stats": stats, "votes": votes
    }


class TestParse(unittest.TestCase):

    def setUp(self):
        curr_dir = P.dirname(P.abspath(__file__))
        with open(P.join(curr_dir, "test_parse.html"), "rb") as fin:
            self.selector = scrapy.Selector(text=fin.read())

    def test(self):
        result = parse(self.selector)

        self.assertEquals(
            result["electorate"], "Республика Адыгея (Адыгея) - Адыгейский"
        )
        self.assertEquals(len(result["stats"]), 17)
        self.assertEquals(len(result["votes"]), 14)

        self.assertEquals(result["stats"][0]["total_value"], 339685)
        self.assertEquals(len(result["stats"][0]["stations"]), 9)
        self.assertEquals(result["stats"][0]["stations"][0]["value"], 11932)
        self.assertEquals(
            result["stats"][0]["stations"][0]["name"], "Адыгейская"
        )


class TestRegex(unittest.TestCase):

    def test_final(self):
        text = "Сводная таблица итогов голосования по федеральному \
избирательному округу"
        self.assertIsNotNone(RESULTS_REGEX.search(text))

    def test_preliminary(self):
        text = "Сводная таблица предварительных итогов голосования \
по федеральному избирательному округу"
        self.assertIsNotNone(RESULTS_REGEX.search(text))
