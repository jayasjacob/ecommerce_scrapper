# Product Scraper
    Product Scraper` using `scapy`

# Features
- Product Title
- Product Image
- Product Price
- Product Rating
- Product Description
- Product Reviews
- Product Brand
- Product Colour

By default it scrapes `Amazon URLs` of product from `JSON`.

# Execute Amazon Scraper
there are two ways to execute scraper
### First one
Directly execute `run.sh` file using shell
```sh
sh ./run.sh
```

### Second one
you can execute the following command
```bash
scrapy crawl amazon_scraper -o ./data/data.json
```

It will create `data.json` file inside the `data` folder containing all the scraped data in `JSON` format and all the images will be saved in `data/img/full` folder.


# Troubleshooting
If `data.json` file doesn't generate in proper format then just delete `data.json` file and `img` folder.  
Now you good to go ;)

# Preresuisites
- you have to install `scrapy` -  use `pip install scrapy`
- you have to install `scrapy_proxies` -  use `pip install scrapy_proxies`


# API Call for DB
- getProduct()
- getPotentialBuyer_Email_UserID(product_id)
- getStalkProductUser_Email_UserID(product_id)
- updateStorePrice(updated_product) 

# FCM Push
- addPriceAlertMessage(user_id, message,,old_price, new_price, product_id)


