from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.models.search_items_request import SearchItemsRequest
from paapi5_python_sdk.rest import ApiException
from config import *
from process_data import processData
import json
import time
import requests
from send_to_db import sendToDb


def requestApi(tok, default_api, search_items_request):
    try:
        """ Sending request """
        response = default_api.search_items(search_items_request)

        print("API called Successfully")

        """ Parse response """
        if response.search_result is not None:
            for item in response.search_result.items:
                data = processData(item)
                print("Processing....")
                sendToDb(tok, data)
                # with open("response.txt", "a") as file:
                #      json.dump(data, file)
                #      file.write('\n')
                print("Response Added to file")

        if response.errors is not None:
            print("\nPrinting Errors:\nPrinting First Error Object from list of Errors")
            print("Error code", response.errors[0].code)
            print("Error message", response.errors[0].message)
            return False

        return True

    except ApiException as exception:
        print("Error calling PA-API 5.0!")
        print("Status code:", exception.status)
        print("Errors :", exception.body)
        print("Request ID:", exception.headers["x-amzn-RequestId"])
        return False


    except TypeError as exception:
        print("TypeError :", exception)
        print("Handle request again")
        return False

    except ValueError as exception:
        print("ValueError :", exception)
        print("Handle request again")
        return False

    except Exception as exception:
        print("Exception :", exception)
        print("Handle request again")
        return False


def search_items():
    """ API declaration """
    default_api = DefaultApi(
        access_key=access_key, secret_key=secret_key, host=host, region=region
    )

    url = api_base_url + "/user/login"
    response = requests.post(url, json={
        "userid": userid,
        "password": password
    })
    a = response.json()
    tok = a['token']

    """ Forming request """
    try:
        search_index = "Electronics"
        with open("keywords.txt", "r") as myfile:
            keyword = myfile.readlines()
        content = [x.strip().replace(" ", "+") for x in keyword]
        for item in content:
            error_skip = 5
            for i in range(1, 11, 1):
                try:
                    search_items_request = SearchItemsRequest(
                        partner_tag=partner_tag,
                        partner_type=PartnerType.ASSOCIATES,
                        keywords=item,
                        search_index=search_index,
                        resources=search_items_resource,
                        item_page=i,
                        item_count=10,
                    )
                except ValueError as exception:
                    print("Error in forming SearchItemsRequest: ", exception)
                    return
                val = requestApi(tok, default_api, search_items_request)
                while val != True and error_skip != 0:
                    error_skip -= 1
                    val = requestApi(tok,default_api, search_items_request)
    except:
        return


search_items()

# print("Product Name: ", item.item_info.title.display_value)
# print("product ID: ", ''.join(random.sample(string.ascii_lowercase + string.digits, 15)))
# print("Time Stamp: ",datetime.now())
# print("Brand Name: ", item.item_info.by_line_info.brand.display_value)
# print("Stores")
# print('ASIN : ',item.asin)
# print('Store Link :', item.detail_page_url)
# print('StoreName: amazon')
# print('Store Price :',item.offers.listings[0].price.amount)
# print('Store mrp :',item.offers.listings[0].saving_basis.amount)
# print('Store Logo :',store_logo)
# print('Store Description :', description)
# print('Instock :', item.offers.listings[0].availability.message)
# print('storeTechnicalDetails :')
# print('Model: ',item.item_info.manufacture_info.model.display_value)
# print('Warranty: ',item.item_info.manufacture_info.warranty.display_value)
# print('Color: ',item.item_info.product_info.color.display_value)
# print('Height: ',item.item_info.product_info.item_dimensions.height.display_value)
# print('Length: ',item.item_info.product_info.item_dimensions.length.display_value)
# print('Width: ',item.item_info.product_info.item_dimensions.width.display_value)
# print('Weight: ',item.item_info.product_info.item_dimensions.weight.display_value)
# print('Size: ',item.item_info.product_info.size.display_value)
# print("Category : ",item.item_info.classifications.binding.display_value)
# print("Subcategory :",item.item_info.classifications.product_group.display_value)
# print("Description : ", description)
# print('Images : ', images)
