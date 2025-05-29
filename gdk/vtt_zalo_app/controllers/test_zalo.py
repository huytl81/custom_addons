import json

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



event_mac = "f6a1b03a794c997145028810db38121108305e0f4d67b977e22e8f0f19ee33ec"
event_mac = "f6a1b03a794c997145028810db38121108305e0f4d67b977e22e8f0f19ee33ec"
timestamp = "1725608725618"
app_id = "3349222483842580322"
oa_key = "SdqcwULlfSWKAJrAmMh4"

follow_data = {"oa_id": "4024926008133882615", "follower": {"id": "8958041078911298472"}, "event_name": "follow", "source": "oa_profile", "app_id": "3349222483842580322", "timestamp": "1725608725618"}

f_json = json.dumps(follow_data)
f_replace = f_json.replace(': ', ':').replace(', ', ',')

s_1 = app_id + f_replace + timestamp + oa_key
mm = hashlib.sha256(s_1.encode('utf-8')).hexdigest()

print(mm)