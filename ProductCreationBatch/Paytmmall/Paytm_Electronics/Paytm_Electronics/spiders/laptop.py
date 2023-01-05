import scrapy,random,string
from ..items import PaytmElectronicsItem

class PaytmSpider(scrapy.Spider):
    name = 'paytmlaptop'
    pageno=2
    start_urls=['https://paytmmall.com/laptops-glpid-6453?use_mw=1&src=store&from=storefront']

    def parse(self, response, **kwargs):

        page = response.css("._8vVO::attr('href')").getall()
        for p in page:
            url = 'https://paytmmall.com/' + p
            yield scrapy.Request(url, callback=self.parse_elec)

        page = 'https://paytmmall.com/laptops-glpid-6453?use_mw=1&src=store&from=storefront&page=' + str(PaytmSpider.pageno) + '&category=6453'
        if PaytmSpider.pageno <= 2:
            PaytmSpider.pageno += 1
            yield response.follow(page, callback=self.parse)



    def parse_elec(self, response):

                    items = PaytmElectronicsItem()

                    product_name = response.css('.NZJI::text').get()
                    storeprice = response.css('._1V3w::text').extract()
                    storeLink = response.url
                    photos = response.css('img._3v_O::attr(src)').extract()
                    l = storeLink.find("product_id")
                    k = storeLink.find("&")
                    product_id = ''.join(random.sample(string.ascii_lowercase + string.digits, 20))
                    spec_title = response.css(".w3LC::text").extract()
                    spec_detail = response.css("._2LOI::text").extract()
                    spec_detail.insert(0,response.css("._2LOI span::text").get())
                    spec_detail.insert(1,response.css("._2LOI a::text").get())
                    rating = response.css('._19rA::text').extract()
                    reviews = response.css('pre::text').extract()

                    stores = {
                        "rating" : "NA" if not rating else rating[0],
                        "reviews" : reviews,
                        "storeProductId": storeLink[l + 11:k],
                        "storeLink": storeLink,
                        "storeName": "Paytm",
                        "storePrice": storeprice[0]
                    }

                    items['product_name'] = product_name
                    items['product_id'] = product_id
                    items['stores'] = stores
                    items['category'] = 'electronics'
                    items['subcategory'] = 'laptops'
                    items['brand'] = product_name.split()[0]
                    items['description']={}

                    for i in range(len(spec_title)):

                                           items['description'][spec_title[i]] = spec_detail[i]


                    items["photos"] = photos[0]



                    yield items