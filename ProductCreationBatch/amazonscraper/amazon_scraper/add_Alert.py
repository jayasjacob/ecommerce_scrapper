# Code Written BY : Alwin Joseph
# Function : Send Alert Messages to Firebase Realtime Database (Notifications)

# Importing the required packages.
import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from .config import *
BASE_URL = Credentials.api_base_url
# Class : to add the alert to the firebase
class addAlert:
    # Variables
    prod_info = None
    old_price = None
    position = None

    # Credentials for the api authentication header
    api_auth_userID = Credentials.userid
    api_auth_password = Credentials.password

    # Firebase Authentication
    credential = {
        "type": "service_account",
        "project_id": "revitup-86a41",
        "private_key_id": "8f4e6def7a9f95bc67b26f49e711e615f374f140",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCuUvLM+6YPRm90\nzN4alGK2yKUToNU2YfWBCRPP1T/ADShfr+o7UGvjJInDDFgbWCCv17zxh7tfW420\nZxjovn9OLiP5v/Gs/nrj1Xy2g52WGxZ3Ybh1PpPhqGcuJtHDJeo2HQN4wjE6xYYG\nX6axW4XAkD+yUlOiFn6DcR36tsucs+3WEQCbBuVqTcKB3AmpFNNpx5QFUERkrzyU\npcz5Wj36jLxF5suQ08ANjuJC+3AeN09xqUmGyMzntpLOymFdTFSJSjIi8M71UGqA\nsR0bKY8z/W6S1jdA663FjnbN4ofWo3/tvgYvXPY1mJ7HJGJuchHbCpIJee1HZKnq\nQWicQ4HZAgMBAAECggEAAYK4ZZeyFCENLl5yK5LnLWJ6fT8ixD146cidFWsyOkGi\n7uBC644fsTeIdkx7i6AI7y51VoLOFnaCxxFaS5v6WPsrz5x8SO0jupCSCtOcIHHD\nz2ZGAjRcUpHFUZ1BNOZWiUV04Irh75K+BmTRNQ+Lu4aebSyZu3l/WJ+nezROQsyv\nDEqnC47UScnQK+7qvLq6EO6x0kEPHc8x2KOUMPBsPGpIxB5jbmLcRJAFOGswkH2Q\nD85cMtDttKaecS9M6qSLCCAcUtTKslY69jEE7ArHkRjpevcyq1rDjSYCLS0sPtp9\nj7aoAyWms+lgQ2bCRHwOQSte9/hS4Ofltai5C718pQKBgQDwIqY2M+lhaW62HfJI\n6ixsWtzgD83b88JE58Crv4fPhgO7yCgxwf1iUZhFZwUhxhAb8NYG6LLZ8+X48MWg\nT7dW3wWQPe0+pDq1fMOLmqkAZOMYweYcPllp+g70C7ls4cHRCDYjp3C0NsstjJN/\nLHC9BwBz+5UrSKRy06GDtMNa4wKBgQC51z+F/4s7PI750OLV2P1KfygIgd/LLqTt\nOWqSq9uTMuozcPrzauc/0TPImupTXJdgWlgWtDBxdGS3PlfegB0ZYm8q8TfMNgK8\n2pA4ZIfZVroMh7Fk2G4i19GJxxh31u7ff/YFOBf2+ZbYRl+ZPxTxDufbkIJQmj7G\nN/Hlf+mhEwKBgAXxdZel1ULZ7ymGuDZhxVOxNAI/oeKtt8Mo0TXu+ZeDQ5hkLcp9\neJ30UwZ0tEXPtxpZ7ZIiNDr8tFZi7yE2l90IjASz46lHO0S+n8BWxZQC6zPzqJRO\nXrwmujQEDkTJmZho0Z40SK/NI14vOn9NREUJZVN5iImXtKo63qZ51NPtAoGAL/5b\nxGJLdb/c+L0uZ6XDPCL8lr3bquBf7Xe/gyNo8Gncu+44kPaRxBRl+C+xxleKLHMI\nfsyIGjTB8eTi0m5plW2rYf6rt0xXhqg3SKkFwGY6ZBQDBxUx1EPCNH+7XO+f/w5P\n3ecvoTOx9iaud6gn411DGZwHW4OKJKy8BtXy4wsCgYBuEEgBe56hR6CNY3eu78pj\nRnmBN5vWqk4lNilzqtKnPFyqyLwavOk7Ga3txuQLR9FrSG3y5Bv/fawDg0XpWSam\nTl8hcg60j6CDi9qUSWCW4PVd0juuDV/v4CcdQMMu+xedQyun8xrFNoEKCF0S6x1P\nw9Vx5FMsgeQOvXot/fTM0Q==\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-u1n4g@revitup-86a41.iam.gserviceaccount.com",
        "client_id": "100438459783947905257",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-u1n4g%40revitup-86a41.iam.gserviceaccount.com"
    }

    # Authenticating and obtaining the firebase databse reference
    cred = credentials.Certificate(credential)
    firebase_admin.initialize_app(
        cred, {'databaseURL': 'https://revitup-86a41.firebaseio.com/'})
    ref = db.reference('notifications')

    # Obtaining Token for API
    url = BASE_URL +  "/user/login"
    response = requests.post(url, json={
        "userid": api_auth_userID,
        "password": api_auth_password
    })
    a = response.json()
    tok = a['token']

    # Constructor, to recieve the arguments
    # product info - the details of the product
    # old-price - the old price, the new price is in the product info
    # Position - the name od the store
    def __init__(self, prod_info, old_price, position):
        self.prod_info = prod_info
        self.old_price = old_price
        self.position = position
        self.position = position

        # Call for identifing the users and send the notifications
        self.push_data()

    # Identify the useres to whom the alert to be send and send alert
    def push_data(self):
        # The api will retun the array user ID's who have 'STALKED' a particulr product
        header = {'Authorization': 'Bearer ' + self.tok,
                  'content-type': "application/json"}
        request_url = BASE_URL +  '/stalked/' + self.prod_info["product_id"]
        l = requests.get(request_url, headers=header)
        user_info = l.json()
        user_count = user_info['result']

        # Iterate over the userID's and create message and send to the database
        for i in range(int(user_count)):
            # Obtain the user id from the API response
            user = user_info['stalkedProducts'][i]['user_id']
            # Store name from the product information
            store_name = self.prod_info["stores"][self.position]["storeName"]
            # Create Messgae payload for the user
            payload = {'message': 'The price of the product ' + self.prod_info[
                "product_name"] + " you were stalking has been reduced from " + self.old_price.__str__() + " to " +
                                  self.prod_info["stores"][self.position]["storePrice"].__str__(),
                       'user_id': user,
                       'timestamp': str(datetime.now()),
                       'notifier_user_id': self.api_auth_userID,
                       'type': 'Product_' + store_name,
                       'typeId': self.prod_info["product_id"],
                       'postid': None
                       }

            # Send the details to firebase, for the user
            posts_ref = self.ref.child(user)
            posts_ref.push(payload)

        # for comments for a product ID
        request_url = BASE_URL +  '/likencomment/comments/' + self.prod_info["product_id"]
        l = requests.get(request_url, headers=header)
        user_info = l.json()
        user_count = user_info['result']

        # Iterate over the userID's and create message and send to the database
        for i in range(int(user_count)):
            # Obtain the user id from the API response
            user = user_info['stalkedProducts'][i]['user_id']
            # Store name from the product information
            store_name = self.prod_info["stores"][self.position]["storeName"]
            # Create Messgae payload for the user
            payload = {'message': 'The price of the product ' + self.prod_info[
                "product_name"] + " you commented has been reduced from " + self.old_price.__str__() + " to " +
                                  self.prod_info["stores"][self.position]["storePrice"].__str__(),
                       'user_id': user,
                       'timestamp': str(datetime.now()),
                       'notifier_user_id': self.api_auth_userID,
                       'type': 'Product_' + store_name,
                       'typeId': self.prod_info["product_id"],
                       'postid': None
                       }

            # Send the details to firebase, for the user
            posts_ref = self.ref.child(user)
            posts_ref.push(payload)

            # for likes for a product ID
            request_url = BASE_URL + '/likencomment/likes/' + self.prod_info["product_id"]
            l = requests.get(request_url, headers=header)
            user_info = l.json()
            user_count = user_info['result']

            # Iterate over the userID's and create message and send to the database
            for i in range(int(user_count)):
                # Obtain the user id from the API response
                user = user_info['stalkedProducts'][i]['user_id']
                # Store name from the product information
                store_name = self.prod_info["stores"][self.position]["storeName"]
                # Create Messgae payload for the user
                payload = {'message': 'The price of the product ' + self.prod_info[
                    "product_name"] + " you liked has been reduced from " + self.old_price.__str__() + " to " +
                                      self.prod_info["stores"][self.position]["storePrice"].__str__(),
                           'user_id': user,
                           'timestamp': str(datetime.now()),
                           'notifier_user_id': self.api_auth_userID,
                           'type': 'Product_' + store_name,
                           'typeId': self.prod_info["product_id"],
                           'postid': None
                           }

                # Send the details to firebase, for the user
                posts_ref = self.ref.child(user)
                posts_ref.push(payload)


# calling the method
# Parameters : Product ID
# addAlert('VJSPJGIELAAFAKYXTT')

# New APIs
# api/v1/likencomment/comments/<productid>
# api/v1/likencomment/likes/<productid>
# api/v1/stalked/<stalkedId>