""" Following are your credentials """
""" Please add your access key here """
access_key = "AKIAIV4M6IGPAVS7TC2Q"

""" Please add your secret key here """
secret_key = "nChgbG54oyjDx+RriIriJWrZ0CMJkVZibt0yFvd6"

""" Please add your partner tag (store/tracking id) here """
partner_tag = "revmeup-21"

""" PAAPI host and region to which you want to send request """
""" For more details refer: https://webservices.amazon.com/paapi5/documentation/common-request-parameters.html#host-and-region"""
host = "webservices.amazon.in"
region = "eu-west-1"

""" Choose resources you want from SearchItemsResource enum """
""" For more details, refer: https://webservices.amazon.com/paapi5/documentation/search-items.html#resources-parameter """
from paapi5_python_sdk.models.search_items_resource import SearchItemsResource
search_items_resource = [
    "BrowseNodeInfo.BrowseNodes",
    "BrowseNodeInfo.BrowseNodes.Ancestor",
    "BrowseNodeInfo.BrowseNodes.SalesRank",
    "BrowseNodeInfo.WebsiteSalesRank",
    "CustomerReviews.Count",
    "CustomerReviews.StarRating",
    "Images.Primary.Large",
    "Images.Variants.Large",
    "ItemInfo.ByLineInfo",
    "ItemInfo.ContentInfo",
    "ItemInfo.ContentRating",
    "ItemInfo.Classifications",
    "ItemInfo.ExternalIds",
    "ItemInfo.Features",
    "ItemInfo.ManufactureInfo",
    "ItemInfo.ProductInfo",
    "ItemInfo.TechnicalInfo",
    "ItemInfo.Title",
    "ItemInfo.TradeInInfo",
    "Offers.Listings.Availability.MaxOrderQuantity",
    "Offers.Listings.Availability.Message",
    "Offers.Listings.Availability.MinOrderQuantity",
    "Offers.Listings.Availability.Type",
    "Offers.Listings.Condition",
    "Offers.Listings.Condition.ConditionNote",
    "Offers.Listings.Condition.SubCondition",
    "Offers.Listings.DeliveryInfo.IsAmazonFulfilled",
    "Offers.Listings.DeliveryInfo.IsFreeShippingEligible",
    "Offers.Listings.DeliveryInfo.IsPrimeEligible",
    "Offers.Listings.DeliveryInfo.ShippingCharges",
    "Offers.Listings.IsBuyBoxWinner",
    "Offers.Listings.LoyaltyPoints.Points",
    "Offers.Listings.MerchantInfo",
    "Offers.Listings.Price",
    "Offers.Listings.ProgramEligibility.IsPrimeExclusive",
    "Offers.Listings.ProgramEligibility.IsPrimePantry",
    "Offers.Listings.Promotions",
    "Offers.Listings.SavingBasis",
    "Offers.Summaries.HighestPrice",
    "Offers.Summaries.LowestPrice",
    "Offers.Summaries.OfferCount",
    "ParentASIN",
    "RentalOffers.Listings.Availability.MaxOrderQuantity",
    "RentalOffers.Listings.Availability.Message",
    "RentalOffers.Listings.Availability.MinOrderQuantity",
    "RentalOffers.Listings.Availability.Type",
    "RentalOffers.Listings.BasePrice",
    "RentalOffers.Listings.Condition",
    "RentalOffers.Listings.Condition.ConditionNote",
    "RentalOffers.Listings.Condition.SubCondition",
    "RentalOffers.Listings.DeliveryInfo.IsAmazonFulfilled",
    "RentalOffers.Listings.DeliveryInfo.IsFreeShippingEligible",
    "RentalOffers.Listings.DeliveryInfo.IsPrimeEligible",
    "RentalOffers.Listings.DeliveryInfo.ShippingCharges",
    "RentalOffers.Listings.MerchantInfo",
    "SearchRefinements"
]


userid =  "ZKh5adE6Lvb2lQGrru9LEKWQUXq2"
password = "ZKh5adE6Lvb2lQGrru9LEKWQUXq2"
# api_base_url = "https://apistaging.revmeup.in/api/v1"
api_base_url = 'https://api.revmeup.in/api/v1'


