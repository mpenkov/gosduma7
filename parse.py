"""Parse result table HTML into JSON."""
import io
import argparse
import logging
import collections
import json

import lxml.etree


def join(list_of_strings):
    return " ".join(list_of_strings).strip()


def parse_value(value):
    try:
        value, percentage = value.split("\n", 1)
        assert percentage[-1] == "%"
        return float(value.strip()), float(percentage[:-1].strip())
    except ValueError:
        return float(value.strip()), None


def parse_totals(rows):
    """Parse the totals across all polling stations."""
    summary = []
    for row in rows:
        try:
            subtitle = join(row[1].xpath(".//text()"))
            value = join(row[2].xpath(".//text()"))
            value, percentage = parse_value(value)

            obj = {"subtitle": subtitle, "value": value}
            if percentage:
                obj["percentage"] = percentage

            summary.append(obj)
        except IndexError:
            pass
    return summary


def parse_stations(table, totals):
    station_names = [join(td.xpath(".//text()")) for td in table[0]]

    result = collections.defaultdict(list)

    #
    # Skip the table header that contains the station names, we already
    # have this.
    #
    rows = list(table)[1:]

    row_counter = 0
    for row in rows:
        subtitle = totals[row_counter]["subtitle"]

        if len(row) != len(station_names):
            continue

        assert len(row) == len(station_names)
        for station, column in zip(station_names, row):
            value = join(column.xpath(".//text()"))
            value, percentage = parse_value(value)
            obj = {"subtitle": subtitle, "value": value}
            if percentage:
                obj["percentage"] = percentage
            result[station].append(obj)
            logging.info("station: %r obj: %r", station, obj)

        row_counter += 1

    return dict(result)


def parse(html):
    parser = lxml.etree.HTMLParser()
    tree = lxml.etree.parse(io.StringIO(html), parser)

    electorate = tree.xpath(
        "/html/body/table[2]/tr[4]/td/table[3]/tr[2]/td[2]"
    )[0].text
    logging.debug("parse: electorate: %r", electorate)

    totals = parse_totals(
        tree.xpath(
            "/html/body/table[2]/tr[4]/td/table[5]/tr/td[1]/table/tr"
        )
    )

    station_breakdown = parse_stations(
        tree.xpath(
            "/html/body/table[2]/tr[4]/td/table[5]/tr/td[2]/div/table"
        )[0], totals
    )

    return totals, station_breakdown


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("html_file")
    args = parser.parse_args()

    with open(args.html_file) as fin:
        totals, by_station = parse(fin.read())

    print(
        json.dumps(
            {
                "totals": totals, "stations": by_station
            }, ensure_ascii=False, indent=2
        )
    )

if __name__ == "__main__":
    main()
