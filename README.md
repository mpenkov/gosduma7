Dataset: Results of the 2016 State Duma Elections in Russia
===========================================================

I scraped the results from izbirkom.ru. They are free to use for any purpose.
The results are [here](https://github.com/mpenkov/gosduma7/blob/master/scrapyproject/results.json).
The format is one JSON object per line.

You can see an example of working with the dataset [here](https://github.com/mpenkov/gosduma7/blob/master/Introduction.ipynb).
I used the dataset to recreate [graphs](https://github.com/mpenkov/gosduma7/blob/master/Introduction.ipynb) found elsewhere on the Internet, with varying levels of success.

If you find a bug, please let me know.

Repeating the Scrape
--------------------

If you want to fetch the data by yourself, you can repeat the scrape:

    cd scrapyproject
    scrapy runspider -t lines gosduma7/spiders/myspider.py -o results.json

You will need python3 and scrapy.

Be considerate and scrape responsibly.
