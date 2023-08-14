import requests
import json
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

        # 提取并解析请求体
        request_body_start = file_content.index("{", file_content.index("Accept-Language: zh-CN,zh;q=0.9"))
        request_body_end = file_content.index("}\nHTTP/1.1 200") + 1
        request_body = file_content[request_body_start:request_body_end]
        original_params = json.loads(request_body)

        # 测试每个参数被留空的场景
        for key in original_params.keys():
            params = original_params.copy()
            params[key] = None if isinstance(params[key], int) else ''
            send_request(request_method, url, params, headers)

        # 测试每个参数被删除的场景
        for key in original_params.keys():
            params = original_params.copy()
            params.pop(key, None)
            send_request(request_method, url, params, headers)

        # 测试整数类型参数的边界值
        for key, value in original_params.items():
            if isinstance(value, int):
                params = original_params.copy()
                params[key] = 999999999
                send_request(request_method, url, params, headers)

        # 测试 Authorization 或 token 头部为空的场景
        if 'Authorization' in headers or 'token' in headers:
            headers_copy = headers.copy()
            if 'Authorization' in headers_copy:
                headers_copy['Authorization'] = ''
            if 'token' in headers_copy:
                headers_copy['token'] = ''
            send_request(request_method, url, original_params, headers_copy)


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

