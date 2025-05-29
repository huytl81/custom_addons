import requests
import hmac
import hashlib

ZALO_APP_SECRET_KEY = "4j7N7G784MLbPUqX76YT"
accessToken = "GVrYAyQkHpv5yMSamgv3F4pwO2R9iYHF4BDUDjIa159Jf6CjqeKUDmgFFNNVg5bqF9TsETcMC2qrX4aiyPfcCIMl14xIZ6eMKQCsO9E1JJKNY69Iyfv52oYrAdJhd6yHByuQM_sSTWS3bIuVXxv2LcIy5Xcal4HS9ROb2EM6PajgjnyYcPHaFaMtCMAbg7WbIVWgUPtkT15Jrn1yqVjIOZJDBnlspKi61E5k78J97GDuzpvRjlGTMaQaF1_4YsTiGvuT5BcNRrSvk30svuvYIcAD9G-dZqTEPA1ZBg6N5tLdYKOGe8iUK7cROJEYYZ5nOgDV3URpC4mbm14vtjPVB2B2UMJJYI81DO5INDIXCn8kjNLvjcOMBCErHZS"

def calculate_hmac_sha256(data, secret_key):
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

options = {
    "url": "https://graph.zalo.me/v2.0/me",
    "method": "GET",
    "headers": {
        "access_token": accessToken,
        "appsecret_proof": calculate_hmac_sha256(accessToken, ZALO_APP_SECRET_KEY)
    },
    "params": {
        "fields": "id,name,birthday,picture,phone"
    }
}

response = requests.request(**options)

if response.status_code == 200:
    print("Response Code:", response.status_code)
    print("Response Body:", response.json())
else:
    print("Error:", response.text)
