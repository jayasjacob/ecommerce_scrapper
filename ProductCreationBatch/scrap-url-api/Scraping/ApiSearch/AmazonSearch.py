from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.condition import Condition
from paapi5_python_sdk.models.get_items_request import GetItemsRequest
from paapi5_python_sdk.models.get_items_resource import GetItemsResource
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.rest import ApiException
from .config import *
from .process_data import processData

def parse_response(item_response_list):
    mapped_response = {}
    for item in item_response_list:
        mapped_response[item.asin] = item
    return mapped_response


def get_items(item_ids):
    """ API declaration """
    default_api = DefaultApi(
        access_key=access_key, secret_key=secret_key, host=host, region=region
    )

    # item_ids = "059035342X"

    """ Forming request """
    try:
        get_items_request = GetItemsRequest(
            partner_tag=partner_tag,
            partner_type=PartnerType.ASSOCIATES,
            marketplace="www.amazon.in",
            item_ids=[item_ids],
            resources=search_items_resource,
        )
    except ValueError as exception:
        print("Error in forming GetItemsRequest: ", exception)
        return

    try:
        """ Sending request """
        response = default_api.get_items(get_items_request)

        print("API called Successfully")
        # print("Complete Response:", response)

        """ Parse response """
        if response.items_result is not None:
            response_list = parse_response(response.items_result.items)
            if item_ids in response_list:
                item = response_list[item_ids]
                if item is not None:
                    data = processData(item)
                    return data

        if response.errors is not None:
            print("\nPrinting Errors:\nPrinting First Error Object from list of Errors")
            print("Error code", response.errors[0].code)
            print("Error message", response.errors[0].message)

    except ApiException as exception:
        print("Error calling PA-API 5.0!")
        print("Status code:", exception.status)
        print("Errors :", exception.body)
        print("Request ID:", exception.headers["x-amzn-RequestId"])

    except TypeError as exception:
        print("TypeError :", exception)

    except ValueError as exception:
        print("ValueError :", exception)

    except Exception as exception:
        print("Exception :", exception)


# get_items("059035342X")