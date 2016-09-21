Evaluating Results of the 2016 State Duma Elections in Russia
=============================================================

I scraped the results from izbirkom.ru. They are free to use for any purpose.
The results are [here](https://github.com/mpenkov/gosduma7/blob/master/scrapyproject/results.json).
The format is one JSON object per line.

You can see an example of working with the dataset [here](https://github.com/mpenkov/gosduma7/blob/master/Elections%20to%20the%20State%20Duma%202016.ipynb).

If you find a bug, please let me know.

Repeating the Scrape
--------------------

Some of the results data was not final when I ran the scrape on Sep 21.

You can obtain the most recent data by repeating the scrape:

    cd scrapyproject
    scrapy runspider -t lines gosduma7/spiders/myspider.py -o results.json

You will need python3 and scrapy.

Be considerate and scrape responsibly.
