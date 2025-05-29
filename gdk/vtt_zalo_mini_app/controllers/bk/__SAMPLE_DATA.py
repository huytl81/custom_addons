# zalo payment callback api data
response_data = {
    "data": {
        "amount": 100000,
        "method": "VNPAY_SANDBOX",
        "orderId": "1247119728271001068310574_1718783821211",
        "transId": "240619_1457012111490300220139602768262",
        "appId": "1007171034541595268",
        "extradata": "%7B%22storeName%22%3A%22C%E1%BB%ADa%20h%C3%A0ng%20A%22%2C%22storeId%22%3A%22123%22%2C%22orderGroupId%22%3A%22345%22%2C%22myTransactionId%22%3A%2212345678%22%2C%22notes%22%3A%22%C4%90%C3%A2y%20l%C3%A0%20gi%C3%A1%20tr%E1%BB%8B%20g%E1%BB%ADi%20th%C3%AAm%22%7D",
        "resultCode": 1,
        "description": "Thanh%20to%C3%A1n%20h%C3%B3a%20%C4%91%C6%A1n%20%C4%91i%E1%BB%87n%20n%C6%B0%E1%BB%9Bc",
        "message": "Giao d\u1ecbch th\u00e0nh c\u00f4ng",
        "paymentChannel": "VNPAY_SANDBOX"
    },
    "overallMac": "eac4616e0fbd822b0aa8c61e96ecee9917e8645300c690ffc38aadc4a41f6293",
    "mac": "3b2e54b68391b0db3c63e7eafa4119b2c4ac071df6cb324666a83dab69d1e81b"
}

# create shipping order params
{
    'payment_type_id': 2,
    'note': '',
    'required_note': 'KHONGCHOXEMHANG',
    'return_phone': '0965725831',
    'return_address': 'Số 6, ngõ 53 phố Phạm Tuấn Tài, phường Cổ Nhuế 1, quận Bắc Từ Liêm, thành phố Hà Nội',
    'return_district_id': 1485,
    'return_ward_code': '1A0608',
    'client_order_code': '',
    'to_name': 'Trong Giap',
    'to_phone': '0965725830',
    'to_address': 'Hn',
    'to_ward_code': '1A0604',
    'to_district_id': 1485,
    'cod_amount': 386320,
    'content': 'S00004', 'weight': 1, 'height': 1, 'length': 1, 'width': 1,
    'pick_station_id': 0,
    'insurance_value': 385000,
    'service_id': 0,
    'service_type_id': 2
}

{
    "code": 200,
    "code_message_value": "",
    "data": {
        "order_code": "LNKC89",
        "sort_code": "0-000-0-00",
        "trans_type": "truck",
        "ward_encode": "",
        "district_encode": "",
        "fee": {
            "main_service": 13200,
            "insurance": 0,
            "cod_fee": 0,
            "station_do": 0,
            "station_pu": 0,
            "return": 0,
            "r2s": 0,
            "return_again": 0,
            "coupon": 0,
            "document_return": 0,
            "double_check": 0,
            "double_check_deliver": 0,
            "pick_remote_areas_fee": 0,
            "deliver_remote_areas_fee": 0,
            "pick_remote_areas_fee_return": 0,
            "deliver_remote_areas_fee_return": 0,
            "cod_failed_fee": 0
        },
        "total_fee": 13200,
        "expected_delivery_time": "2024-08-22T23:59:59Z",
        "operation_partner": ""
    },
    "message": "Success",
    "message_display": "Tạo đơn hàng thành công. Mã đơn hàng: LNKC89"
}
