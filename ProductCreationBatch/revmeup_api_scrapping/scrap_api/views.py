import json

import requests
from API_Scraping import APIScraping
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
@api_view(['GET', 'POST'])
def ScrapDriver(request):

    if request.method == 'POST':
        # url_input = request.data['url']
        BASE_URL = "https://apistaging.revmeup.in/api/v1"

        url = BASE_URL + "/user/login"
        response = requests.post(url, json={
            "userid": request.data['username'],
            "password": request.data['password']
        })

        auth_response = response.json()
        if auth_response['status'] == 'fail':
            error_m = {'error': 'Error in Connecting to DB : ' + str(auth_response)}
            return Response(json.dumps(error_m))
        else:
            # Scraping the website URL
            api_response = APIScraping.scrap_url(request.data['url'],request.data['username'],request.data['password'])

        # # Response to user
        return Response(api_response)


# https://www.amazon.in/Test-Exclusive-435/dp/B0756ZFXWP/ref=sr_1_1?dchild=1&pf_rd_i=21439725031&pf_rd_m=A1K21FY43GMZF8&pf_rd_p=previewPlacement_center-1&pf_rd_r=NPEEYN74XP9R83ET74EF&pf_rd_s=merchandised-search-3&pf_rd_t=101&qid=1600787217&sr=8-1

# https://www.amazon.in/Kall-K210-Smartphone-16GB-Rose/dp/B08HYY4KF5/

# https://www.flipkart.com/vivo-y91i-fusion-black-32-gb/p/itmff6vsadyrbauf?pid=MOBFEFCPX6AJ7C6K&lid=LSTMOBFEFCPX6AJ7C6KGKPZED&marketplace=FLIPKART&srno=b_1_1&otracker=clp_banner_1_20.bannerX3.BANNER_mobile-phones-store_OP3C5KFEYKJA&fm=neo%2Fmerchandising&iid=d3119407-69fc-4cb1-9c68-edc53cff6497.MOBFEFCPX6AJ7C6K.SEARCH&ppt=browse&ppn=browse&ssid=zhgvk7tl9gnp0etc1600861255745
