import argparse
import gdown
import os



if __name__ == "__main__":
    # do không thể nào lấy được tên folder nên phải nhập thủ công

    test_name = input('Input the test name correspond to url bellow:.. ')
    url = input('Input the url of test_name:... ')

    parent_dir = 'Solomon_25'
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    # Tạo thư mục con cho test_name
    test_dir = f'{parent_dir}/{test_name}'
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    gdown.download_folder(url, output= test_dir)
