a = '["&", ("zalo_id_by_oa", "!=", False), ("district_id", "in", [1])]'

# Chuyển chuỗi a thành list
a_list = eval(a)

# Kiểm tra xem đã có key zalo_id_by_oa chưa
key_exists = any(item[0] == 'zalo_id_by_oa' for item in a_list if isinstance(item, tuple))

# Nếu chưa có thì thêm vào
if not key_exists:
    a_list.append(('zalo_id_by_oa', '!=', False))

# Loại bỏ điều kiện có key district_id nếu tồn tại
a_list = [item for item in a_list if not (isinstance(item, tuple) and (item[0] == 'district_id') or item[0] == 'zalo_id_by_oa')]

a_list.append(('zalo_id_by_oa', '!=', False))

print(key_exists)
print(a_list)
