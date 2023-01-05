#!/bin/bash
#cd /home/ubuntu/ProductCreationBatch/scraper
#PATH=$PATH:/usr/local/bin
#export PATH
#curl -o ./http_proxies.txt -k "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all"
scrapy crawl flipkart_scraper -o ./data/data_update_flipkart.json
