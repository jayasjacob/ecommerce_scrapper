from flask import Flask, request, jsonify
from config import Credentials
import requests

app = Flask(__name__)


@app.route('/',methods=['post'])
def chatApi():
    # request API for getting the credentials
    url = Credentials.BASE_URL + "/user/login"
    response = requests.post(url, json={
        "userid": Credentials.userid,
        "password": Credentials.password
    })

    auth_response = response.json()
    if auth_response['status'] == 'fail':
        # If api authentication is fail
        error_m = {'error': 'Error in Connecting to DB : ' + str(auth_response)}
        return jsonify(error_m)
    else:
        # If api authentication is success
        header = {'Authorization': 'Bearer ' + auth_response['token'], 'content-type': "application/json"}
        # request API for getting the product details
        url_by_prod_id = Credentials.BASE_URL + ''
        res_prod_id = requests.get(url_by_prod_id, headers=header)
        data = res_prod_id.json()
        # IF else conditions

        # return the json response
        return jsonify(data)


if __name__ == '__main__':
    app.run()
