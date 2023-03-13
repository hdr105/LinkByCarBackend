from fastapi import FastAPI, File, UploadFile
import requests
from requests.auth import HTTPBasicAuth
import csv

app = FastAPI()

@app.post("/check_eligibility")
async def check_eligibility(file: UploadFile):
    apiResponse = []
    byPassUrl = 'https://api-prelive.autopass.pro/vehicule'
    bearerTokenUrl = 'https://api.linkbycar.com/v1/token'
    eligibilityUrl = "https://api.linkbycar.com/v1/eligibility/vin/"
    userName = "shopdev"
    password = "tymJqFRF4tLD34"
    chunk_size = 5

    csv_text = await file.read()
    csv_string = csv_text.decode("utf-8")
    csv_rows = csv_string.splitlines()
    csv_reader = csv.reader(csv_rows)
    headers = next(csv_reader, None)
    vin_list = []
    response = requests.post(bearerTokenUrl, data={
        "username": userName,
        "password": password,
        "scope": 'read'
    })

    access_token = response.json()["access_token"]
    for i, row in enumerate(csv_reader):
        vin = row[0]
        if vin:
            vin_list.append(vin)
        if len(vin_list) == chunk_size or (i == len(csv_rows) - 1 and vin_list):
            for data in vin_list:
                params = {'reg_or_vin': data, 'reg_country': 'fr', 'access_token': 'm84x5u6eg5f4m2767cvt0muagu86tifklvln52zi'}
                response = requests.get(byPassUrl, params=params)
                if response.status_code != 200:
                    print('Error:', response.status_code, response.text)
                vin_data_list = response.json()
                vin = ''
                if vin_data_list['car_identification']['vin'] == None:
                    vin = vin_data_list['reg_or_vin']
                else:
                    vin = vin_data_list['car_identification']['vin']    
                response = requests.get(eligibilityUrl+vin, headers={"Authorization": f"Bearer {access_token}","Accept": "application/json"})
                apiResponse.append(response.json())
            vin_list = []
    return apiResponse
