from flask import Flask, request, jsonify, Response, abort
from Scraping import APIScraping
import requests
import json

app = Flask(__name__)
# "https://apistaging.revmeup.in/api/v1",

@app.route('/', methods=['POST'])
def scrap():
    data = request.get_json(force=True)

    url = data['baseurl'] + "/user/login"
    response = requests.post(url, json={
        "userid": data['username'],
        "password": data['password']
    })
    auth_response = response.json()

    if auth_response['status'] == 'fail':
        return Response("Could not establish a successful connection with DB, please check the username / password",
                        status=400,mimetype='application/json')
    else:
        # Scraping the website URL
        api_response = APIScraping.scrap_url(data['baseurl'], data['url'], data['username'], data['password'])

        if api_response == None or api_response == "" or api_response == 'null':
            api_response = -4
        # print("api-response",api_response)

        header = {'Authorization': 'Bearer ' + auth_response['token'], 'content-type': "application/json"}

        if api_response == -1:
            payload = json.dumps(
                {'url': data['url'], 'userid': data['username'], 'status': 'Failure', 'reason': 'User Auth Failure'})
            res = requests.post(data['baseurl'] + '/urlSearch/', data=payload, headers=header)

            return Response("The URL used cannot be processed now, Sorry for the inconveniences caused", status=400,mimetype='application/json')
        elif api_response == -2:
            payload = json.dumps([{'url': data['url'], 'userid': data['username'], 'status': 'Failure',
                                  'reason': 'Error in processing the requested URL'}])
            res = requests.post(data['baseurl'] + '/urlSearch/', data=payload, headers=header)
            return Response("Please verify the URL you have requested", status=400,mimetype='application/json')
        elif api_response == -3:
            payload = json.dumps([{'url': data['url'], 'userid': data['username'], 'status': 'Failure',
                                  'reason': 'Server side error in processing Files'}])
            res = requests.post(data['baseurl'] + '/urlSearch/', data=payload, headers=header)
            return Response("Could not establish a successful connection with DB, please check the username / password",
                            status=400,mimetype='application/json')
        elif api_response == -4:
            payload = json.dumps([{'url': data['url'], 'userid': data['username'], 'status': 'Failure',
                                  'reason': 'The requested URL is having error or not supported'}])
            res = requests.post(data['baseurl'] + '/urlSearch/', data=payload, headers=header)
            return Response("The URL used is not proper / Could not be processed now, Sorry for the inconveniences, we are working and will take care of your requested product", status=400,mimetype='application/json')
        elif api_response == -5:
            payload = json.dumps({'url': data['url'], 'userid': data['username'], 'status': 'Failure',
                                  'reason': 'Fail to retrive the data from scraper'})
            res = requests.post(data['baseurl'] + '/urlSearch/', data=payload, headers=header)
            return Response(
                "We could not track your product, we are working closely to fix your issues, Sorry for the inconveniences",
                status=400,mimetype='application/json')
        else:
            payload = json.dumps({'url': data['url'], 'userid': data['username'], 'status': 'Success'})
            res = requests.post(data['baseurl'] + '/urlSearch/', data=payload, headers=header)
            # Response to user - everything fine
            return jsonify(api_response)


if __name__ == '__main__':
    from waitress import serve

    serve(app, host="127.0.0.1", port=8000)
    # app.run()
