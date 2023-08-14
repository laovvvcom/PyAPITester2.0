import requests
from urllib.parse import parse_qsl
import glob


def extract_request_details_and_send(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
        request_line = file_content.split('\n')[0].strip()
        request_method, url = request_line.split(' ')[0], request_line.split(' ')[1]

        # 提取头部
        headers = {}
        for line in file_content.split('\n')[1:]:
            line = line.strip()
            if not line:
                break
            key, value = line.split(': ', 1)
            headers[key] = value

        # 提取请求体
        request_body_start = file_content.find("\n\n")
        request_body_end = file_content.find("HTTP/1.1 200", request_body_start)
        request_body = file_content[request_body_start + 2:request_body_end].strip()

        # 解析请求体
        original_params = dict(parse_qsl(request_body))

        # 测试每个参数被留空的场景
        for key in original_params.keys():
            params = original_params.copy()
            params[key] = ''
            send_request(request_method, url, params, headers)

        # 测试每个参数被删除的场景
        for key in original_params.keys():
            params = original_params.copy()
            params.pop(key, None)
            send_request(request_method, url, params, headers)

        # 测试整数类型参数的边界值
        for key, value in original_params.items():
            if str(value).isdigit():
                params = original_params.copy()
                params[key] = '999999999'
                send_request(request_method, url, params, headers)

        # 测试 Authorization 或 token 头部为空的场景
        if 'Authorization' in headers or 'token' in headers:
            headers_copy = headers.copy()
            if 'Authorization' in headers_copy:
                headers_copy['Authorization'] = ''
            if 'token' in headers_copy:
                headers_copy['token'] = ''
            send_request(request_method, url, original_params, headers_copy)

        # 测试时间盲注的场景
        params = original_params.copy()
        last_key = list(original_params.keys())[-1]  # 获取最后一个参数的键
        params[last_key] = original_params[last_key] + " OR IF(1=1, SLEEP(5), 0)"  # 修改最后一个参数的值
        send_request(request_method, url, params, headers)


def send_request(request_method, url, params, headers):
    # print(f"头部: {headers}")
    print(f"参数: {params}")
    request_data = '&'.join([f"{key}={value}" for key, value in params.items()])
    response = requests.request(request_method, url, data=request_data, headers=headers)
    print(f"请求响应状态码: {response.status_code}")
    print(f"请求响应内容: {response.text}")
    print(f"请求响应耗时: {response.elapsed.total_seconds()} 秒")
    print("=" * 40)  # 分隔线


# 获取当前目录下所有 .txt 文件
file_paths = glob.glob('./apitext_post_urlencoded/*.txt')
for file_path in file_paths:
    extract_request_details_and_send(file_path)
