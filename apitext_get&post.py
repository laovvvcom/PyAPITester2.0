import requests
from urllib.parse import urlparse, parse_qs
import glob


def extract_request_details_and_send(file_path):
    with open(file_path, 'r') as file:
        line = file.readline().strip()
        request_method, url = line.split(' ')[0], line.split(' ')[1]
        parsed_url = urlparse(url)
        base_url = url.split('?')[0]
        original_params = parse_qs(parsed_url.query)

        original_headers = {}
        for line in file:
            line = line.strip()
            if not line:
                break
            key, value = line.split(': ', 1)
            original_headers[key] = value

        if original_params:
            scenarios(request_method, base_url, original_params, original_headers)

        # 测试 Authorization 或 token 头部为空的场景
        if 'Authorization' in original_headers or 'token' in original_headers:
            print("测试场景：验证鉴权判定")
            headers = original_headers.copy()
            if 'Authorization' in headers:
                headers['Authorization'] = ''
            if 'token' in headers:
                headers['token'] = ''
            send_request(request_method, base_url, original_params, headers)


def scenarios(request_method, base_url, original_params, original_headers):
    # 测试每个参数被留空、被删除、整数类型边界值的场景
    for key in original_params.keys():
        params = original_params.copy()
        params[key] = ['']
        print("测试场景：验证参数值必填项")
        send_request(request_method, base_url, params, original_headers)
        params = original_params.copy()
        params.pop(key, None)
        print("测试场景：验证参数必填项")
        send_request(request_method, base_url, params, original_headers)
        if original_params[key][0].isdigit():
            params = original_params.copy()
            params[key] = [999999999]
            print("测试场景：验证业务规则")
            send_request(request_method, base_url, params, original_headers)

    # 测试时间盲注的场景
    print("测试场景：验证SQL盲注(时间盲注)")
    params = original_params.copy()
    last_key = list(original_params.keys())[-1]  # 获取最后一个参数的键
    params[last_key] = [f"{original_params[last_key][0]} OR IF(1=1, SLEEP(5), 0)"] # 修改最后一个参数的值
    send_request(request_method, base_url, params, original_headers)


def send_request(request_method, base_url, params, headers):
    params = {k: v[0] for k, v in params.items()}
    print(f"参数: {params}")
    response = requests.request(request_method, base_url, params=params, headers=headers)
    print(f"请求响应状态码: {response.status_code}")
    print(f"请求响应内容: {response.text}")
    print(f"请求响应耗时: {response.elapsed.total_seconds()} 秒")
    print("="*40)  # 分隔线


# 获取当前目录下所有 .txt 文件
file_paths = glob.glob('apitext_get&post/*.txt')
for file_path in file_paths:
    extract_request_details_and_send(file_path)
