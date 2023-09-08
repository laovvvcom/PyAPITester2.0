import requests
import json
from urllib.parse import urlparse, parse_qs
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
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()  # 剔除头部名称中的多余空格和冒号
                headers[key] = value.strip()

        if "?" in url:
            parsed_url = urlparse(url)
            base_url = url.split('?')[0]
            original_params_list = parse_qs(parsed_url.query)
            original_params_url = {k: v[0] for k, v in original_params_list.items()}

            # 提取并解析请求体
            request_body_start = file_content.index("{")
            request_body_end = file_content.index("\nHTTP/1.1 200")  # 假设响应始终以"HTTP/1.1 200"开始
            request_body = file_content[request_body_start:request_body_end].strip()
            original_params_body = json.loads(request_body)
            original_params = {**original_params_url, **original_params_body}

            # 测试每个参数被留空的场景
            for key in original_params.keys():
                params = original_params.copy()
                params[key] = None if isinstance(params[key], int) else ''
                print("测试场景：验证参数值必填项")
                send_request(request_method, base_url, params, headers)

            # 测试每个参数被删除的场景
            for key in original_params.keys():
                params = original_params.copy()
                params.pop(key, None)
                print("测试场景：验证参数必填项")
                send_request(request_method, base_url, params, headers)

            # 测试整数类型参数的边界值
            for key, value in original_params.items():
                if isinstance(value, int):
                    params = original_params.copy()
                    params[key] = 999999999
                    print("测试场景：验证业务规则")
                    send_request(request_method, base_url, params, headers)

            # 测试 Authorization 或 token 头部为空的场景
            if 'Authorization' in headers or 'token' in headers:
                headers_copy = headers.copy()
                if 'Authorization' in headers_copy:
                    headers_copy['Authorization'] = ''
                if 'token' in headers_copy:
                    headers_copy['token'] = ''
                print("测试场景：验证鉴权判定")
                send_request(request_method, base_url, original_params, headers_copy)

            # 测试时间盲注的场景
            params = original_params.copy()
            last_key = list(original_params.keys())[-1]  # 获取最后一个参数的键
            # 检查参数类型是否是字符串或整数，如果是列表则跳过测试
            if not isinstance(params[last_key], list):
                if isinstance(params[last_key], int):
                    params[last_key] = f"{original_params[last_key]} OR IF(1=1, SLEEP(5), 0)"  # 修改最后一个参数的值
                elif isinstance(params[last_key], str):
                    params[last_key] = original_params[last_key] + " OR IF(1=1, SLEEP(5), 0)"

                print("测试场景：验证SQL盲注(时间盲注)")
                send_request(request_method, base_url, params, headers)

        else:
            # 提取并解析请求体
            request_body_start = file_content.index("{")
            request_body_end = file_content.index("\nHTTP/1.1 200")  # 假设响应始终以"HTTP/1.1 200"开始
            request_body = file_content[request_body_start:request_body_end].strip()
            original_params = json.loads(request_body)

            # 测试每个参数被留空的场景
            for key in original_params.keys():
                params = original_params.copy()
                params[key] = None if isinstance(params[key], int) else ''
                print("测试场景：验证参数值必填项")
                send_request(request_method, url, params, headers)

            # 测试每个参数被删除的场景
            for key in original_params.keys():
                params = original_params.copy()
                params.pop(key, None)
                print("测试场景：验证参数必填项")
                send_request(request_method, url, params, headers)

            # 测试整数类型参数的边界值
            for key, value in original_params.items():
                if isinstance(value, int):
                    params = original_params.copy()
                    params[key] = 999999999
                    print("测试场景：验证业务规则")
                    send_request(request_method, url, params, headers)

            # 测试 Authorization 或 token 头部为空的场景
            if 'Authorization' in headers or 'token' in headers:
                headers_copy = headers.copy()
                if 'Authorization' in headers_copy:
                    headers_copy['Authorization'] = ''
                if 'token' in headers_copy:
                    headers_copy['token'] = ''
                print("测试场景：验证鉴权判定")
                send_request(request_method, url, original_params, headers_copy)

            # 测试时间盲注的场景
            params = original_params.copy()
            last_key = list(original_params.keys())[-1]  # 获取最后一个参数的键
            # 检查参数类型是否是字符串或整数，如果是列表则跳过测试
            if not isinstance(params[last_key], list):
                if isinstance(params[last_key], int):
                    params[last_key] = f"{original_params[last_key]} OR IF(1=1, SLEEP(5), 0)"  # 修改最后一个参数的值
                elif isinstance(params[last_key], str):
                    params[last_key] = original_params[last_key] + " OR IF(1=1, SLEEP(5), 0)"

                print("测试场景：验证SQL盲注(时间盲注)")
                send_request(request_method, url, params, headers)


def send_request(request_method, url, params, headers):
    # print(f"请求方法: {request_method}")
    # print(f"URL: {url}")
    print(f"参数: {params}")
    # print(f"头部: {headers}")
    request_body = json.dumps(params)
    response = requests.request(request_method, url, data=request_body, headers=headers)
    print(f"请求响应状态码: {response.status_code}")
    print(f"请求响应内容: {response.text}")
    print(f"请求响应耗时: {response.elapsed.total_seconds()} 秒")
    print("="*40)  # 分隔线


# 获取当前目录下所有 .txt 文件
file_paths = glob.glob('./apitext_post_json/*.txt')
for file_path in file_paths:
    extract_request_details_and_send(file_path)
