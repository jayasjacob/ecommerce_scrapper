import scrapy,random,string
from ..items import SnapdealElectronicsItem

class SnapdealSpider(scrapy.Spider):

    name = 'snapcamera'


    start_urls=['https://www.snapdeal.com/products/cameras-digital-slrs?sort=plrty#bcrumbLabelId:290']

    def parse(self, response):


        page = response.css("a.dp-widget-link::attr('href')").getall()



        for p in page[4:]:

             yield scrapy.Request(p, callback=self.parse_elec)



    def parse_elec(self, response):

        items = SnapdealElectronicsItem()

        product_name = response.css('.pdp-e-i-head::text').get()

        storeprice = response.css('.payBlkBig::text').get()

        storeLink = response.url

        id = ''
        k = storeLink.find('#')
        while storeLink[k] != '/':
            id = id + storeLink[k]
            k -= 1

        photos = response.xpath('//*[@id="bx-slider-left-image-panel"]/li[1]/img').xpath("@src").get()

        spec_title = response.css(".product-spec td:nth-child(1)::text").extract()

        spec_detail = response.css("td+ td::text").extract()

        product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))

        rating = response.css('span.avrg-rating::text').get()
        reviews = response.css('#defaultReviewsCard p::text').extract()

        stores = {

            "rating": "0" if rating == None else rating[1:4],
            "reviews":reviews,
            'storeproductid': id[::-1],
            "storeLink": storeLink,
            "storeName": "Snapdeal",
            "storePrice": storeprice,

        }

        items['product_name'] = product_name.strip()
        items['product_id'] = product_id
        items['stores'] = stores
        items['category'] = 'electronics'
        items['subcategory'] = 'camera'
        items['brand'] = product_name.split()[0]
        items['description'] = {}

        for i in range(len(spec_title)):
            items['description'][spec_title[i]] = spec_detail[i]

        items['photos'] = photos

        yield items