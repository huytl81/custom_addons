import chardet

file_path = 'default_res_ward.csv'

# Tự động phát hiện mã hóa của tệp
with open(file_path, 'rb') as file:
    raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']

# Đọc tệp với mã hóa đã phát hiện
with open(file_path, 'r', encoding=encoding) as file:
    lines = file.readlines()

# Sử dụng một tập hợp để tìm các dòng trùng lặp
unique_lines = set()
duplicate_lines = set()

for line in lines:
    if line in unique_lines:
        duplicate_lines.add(line)
    else:
        unique_lines.add(line)

if duplicate_lines:
    print("Các dòng trùng lặp:")
    for line in duplicate_lines:
        print(line.strip())
else:
    print("Không có dòng nào bị trùng lặp.")