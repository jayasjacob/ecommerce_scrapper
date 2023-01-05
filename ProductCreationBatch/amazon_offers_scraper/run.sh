#!/bin/bash
cd /home/ubuntu/ProductCreationBatch/amazonscraper
PATH=$PATH:/usr/local/bin
export PATH
curl -o ./http_proxies.txt -k "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all"
scrapy crawl amazon_scraper -o ./data/data_update_amazon.json
