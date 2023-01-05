#!/bin/bash
cd /home/ubuntu/ProductCreationBatch/amazonscraper
#PATH=$PATH:/usr/local/bin:/home/ubuntu/.local/bin
#export PATH
curl -o /home/ubuntu/ProductCreationBatch/amazonscraper/http_proxies.txt -k "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all"
/home/ubuntu/.local/bin/scrapy crawl amazon_scraper -o /home/ubuntu/ProductCreationBatch/amazonscraper/data/data_update_amazon.json
