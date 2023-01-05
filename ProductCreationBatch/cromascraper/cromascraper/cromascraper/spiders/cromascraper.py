import re

import scrapy,random,string
from ..items import CromascraperItem

class CromaSpider(scrapy.Spider):

    name = 'croma'

    pageno = 0

    with open("./data/keywords.txt", "r") as myfile:
        keyword = myfile.readlines()
    content = [x.strip().replace(" ", "+") for x in keyword]
    items = content

    def start_requests(self):

        # urls to scrap
        urls = [ 'https://www.croma.com/phones-wearables/mobile-phones/c/10?q=%3Arelevance%3AskuStockFlag%3Atrue&page=1',
                'https://www.croma.com/computers-tablets/laptops/c/20?q=%3Arelevance%3AskuStockFlag%3Atrue&page=1',
                'https://www.croma.com/cameras/professional-cameras/c/548?q=%3Arelevance%3AskuStockFlag%3Atrue&page=1',
                'https://www.croma.com/audio-video/headphones-earphones/c/1012?q=%3Arelevance%3AskuStockFlag%3Atrue&page=1',
                'https://www.croma.com/audio-video/speakers/c/1006?q=%3Arelevance%3AskuStockFlag%3Atrue&page=1',
                'https://www.croma.com/computers-tablets/tablets-e-readers/c/22?q=%3Arelevance%3AskuStockFlag%3Atrue&page=1']

        for u in urls:

            CromaSpider.pagno = 2
            yield scrapy.Request(u, callback=self.parse)

    def parse(self, response, **kwargs):

                #scraping anchor tags
                page = response.css("a.product__list--thumb::attr(href)").getall()

                for p in page:

                     url = 'https://www.croma.com' + p
                     # scraping from each product urls
                     yield scrapy.Request(url, callback=self.parse_elec)

                # going to next page till 10 pages
                page = response.url[:-1] + str(CromaSpider.pageno)
                if CromaSpider.pageno <= 10:
                    CromaSpider.pageno += 1
                    yield response.follow(page, callback=self.parse)


    def parse_elec(self, response):

                    items = CromascraperItem()

                    # getting product name
                    product_name = response.css('h1::text').get()

                    # getting store price
                    storeprice = response.css('.pdpPrice::text').get()
                    trim = re.compile(r'[^\d.,]+')
                    storeprice = str(storeprice)
                    storeprice = trim.sub('',storeprice)
                    storeprice.replace(".00", "").replace(",", "")

                    # getting store link
                    storeLink = response.url

                    # getting photo url
                    photos = response.css('img._pdp_im::attr(src)').extract()


                    # generating random product id
                    product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))

                    # getting rating
                    rating = response.css('#finalReviewRating::text').get()

                    #finding index of '/' in storelink[::-1] for getting store product id
                    id = storeLink[::-1].find('/')

                    # storing specification as a map
                    storeAdditionalDetails = {}
                    for i in response.css(".products"):

                        storeAdditionalDetails[i.css(".attrib::text").get().strip()] = i.css(".attribvalue::text").get().strip()


                    # trim  = re.compile(r"[-()\"#/@;:<>{}`+=~|.!?,*]")
                    # storeAdditionalDetails = trim.sub("",storeAdditionalDetails)
                    # storeAdditionalDetails = list(map(lambda s: s.strip(), storeAdditionalDetails))
                    # storeAdditionalDetails = dict(zip(storeAdditionalDetails[::2], storeAdditionalDetails[1::2]))

                    stores = {

                        "rating": "NA" if not rating else rating,
                        "reviews": [],
                        'storeproductid': storeLink[-id:],
                        "storeLink": storeLink,
                        "storeName": "Croma",
                        "storePrice": storeprice,
                        "storeAdditionalDetails": storeAdditionalDetails

                    }

                    items['product_name'] = product_name.strip()
                    items['product_id'] = product_id
                    items['stores'] = stores
                    items['category'] = 'electronics'

                    #checking if earphone,earbud,airpod or headphone in storelink for subcategory to be earphone
                    if 'earphone' in storeLink or 'earbud' in storeLink or 'airpod' in storeLink or 'headphone' in storeLink:
                        sub='earphone'

                    #checking if speaker in storelink for subcategory to be speaker
                    elif 'speaker' in storeLink:
                        sub='speaker'

                    #checking if tablet in storelink for subcategory to be tablet
                    elif 'tablet' in storeLink:
                        sub='tablet'

                    #checking if laptop in storelink for subcategory to be laptop
                    elif 'laptop' in storeLink:
                        sub='laptop'

                    #checking if camera in storelink for subcategory to be camera
                    elif 'camera' in storeLink:
                        sub='camera'

                    #else subcategory is mobile
                    else:
                        sub='mobile'

                    items['subcategory'] = sub
                    items['brand'] = product_name.split()[0]
                    items['description'] = product_name
                    items['photos'] = photos

                    yield items