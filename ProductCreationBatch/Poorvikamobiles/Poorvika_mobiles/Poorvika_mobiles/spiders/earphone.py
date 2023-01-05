import scrapy,random,string
from ..items import PoorvikaMobilesItem

class PoorvikaSpider(scrapy.Spider):

    name = 'poorvikaearphone'
    url=[]

    start_urls=['https://www.poorvikamobile.com/index.php?route=product/search/searchautocomplete']

    def parse(self, response, **kwargs):


        PoorvikaSpider.url =[]
        page = str(response.body)
        k = page.find("keyword")
        k2 = page.find("}",k)

        for i in range(1000):

                if 'headset' in page[k+10:k2-1].split('-'):
                                PoorvikaSpider.url.append('https://www.poorvikamobile.com/' + page[k+10:k2-1])
                k=page.find("keyword",k2)
                k2 = page.find("}",k)


        for p in PoorvikaSpider.url:

                yield scrapy.Request(p, callback=self.parse_elec)



    def parse_elec(self, response):

                items = PoorvikaMobilesItem()

                product_name = response.css('#content h1::text').get()

                storeprice = response.css('#price-old::text').get()

                storeLink = response.url

                photos = response.css(".mw-auto .small_img::attr(src)").get()

                spec_title = response.css(".attr_name::text").extract()

                spec_detail = response.css(".attr_text::text").extract()

                product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))

                stores = {

                    "rating": '',
                    "reviews":[],
                    'storeproductid': '',
                    "storeLink": storeLink,
                    "storeName": "Poorvika",
                    "storePrice": storeprice[3:],

                }

                items['product_name'] = product_name.strip()
                items['product_id'] = product_id
                items['stores'] = stores
                items['category'] = 'electronics'
                items['subcategory'] = 'earphone'
                items['brand'] = product_name.split()[0]
                items['description'] = {}

                for i in range(len(spec_title)):
                    items['description'][spec_title[i]] = spec_detail[i]

                items['photos'] = photos

                yield items
