from datetime import datetime
import string
import random
import json

def processData(item):
    if item.asin is not None:
        images = []
        for image in item.images.variants:
            images.insert(1, image.large.url)
        store_logo = "https://i.pinimg.com/564x/42/a7/86/42a7861bb1a403af534b18986ab4e198.jpg"

        description = " "
        for desc in item.item_info.features.display_values:
            description = description + " " + desc

        try:
            model = item.item_info.manufacture_info.model.display_value
        except:
            model = None

        try:
            warranty = item.item_info.manufacture_info.warranty.display_value
        except:
            warranty = None

        try:
            color = item.item_info.product_info.color.display_value
        except:
            color = None

        try:
            height = item.item_info.product_info.item_dimensions.height.display_value
        except:
            height = None

        try:
            length = item.item_info.product_info.item_dimensions.length.display_value
        except:
            length = None

        try:
            width = item.item_info.product_info.item_dimensions.width.display_value
        except:
            width = None

        try:
            weight = item.item_info.product_info.item_dimensions.weight.display_value
        except:
            weight = None

        try:
            size = item.item_info.product_info.size.display_value
        except:
            size = None

        technical_details = {
            "model": None,
            "warranty": None,
            "color": color,
            "height": height,
            "length": length,
            "width": width,
            "weight": weight,
            "size": size,
        }

        try:
            store_prize = item.offers.listings[0].price.amount
        except:
            store_prize = None

        try:
            store_mrp = item.offers.listings[0].saving_basis.amount
        except:
            store_mrp = None

        try:
            instock = item.offers.listings[0].availability.message
        except:
            instock = None

        stores = [{
            "storeProductId": item.asin,
            "storeLink": str(item.detail_page_url)+"&tag=revmeup-21",
            "storeName": "amazon",
            "storePrice": store_prize,
            "store_mrp": store_mrp,
            "store_logo": store_logo,
            "storeDescription": description,
            "instock": instock,
            "storeTechnicalDetails": technical_details,
        }]

        try:
            subcategory = item.item_info.classifications.product_group.display_value
        except:
            subcategory = None

        try:
            category = item.item_info.classifications.binding.display_value
        except:
            category = None

        try:
            brand_name = item.item_info.by_line_info.brand.display_value
        except:
            brand_name = None

        try:
            product_name = item.item_info.title.display_value
        except:
            product_name = None

        # Item
        item = {
            "product_name": product_name,
            "product_id": ''.join(random.sample(string.ascii_lowercase + string.digits, 15)),
            "timestamp": str(datetime.now()),
            "brand_name": brand_name,
            "stores": stores,
            "category": category,
            "subcategory": subcategory,
            "description": description,
            "photos": images,
        }

        return json.dumps(item)
