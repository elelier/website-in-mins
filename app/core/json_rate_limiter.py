import json
import time
from fastapi import Request, HTTPException

RATE_LIMIT = 100  # requests per hour
RATE_LIMIT_FILE = "rate_limit.json"
BLOCK_DURATION = 3600  # 1 hour in seconds


def load_rate_limit_data():
    try:
        with open(RATE_LIMIT_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_rate_limit_data(data):
    with open(RATE_LIMIT_FILE, 'w') as file:
        json.dump(data, file)


def check_rate_limit(ip: str):
    data = load_rate_limit_data()
    current_time = time.time()
    if ip in data and 'blocked_until' in data[ip]:
        if current_time < data[ip]['blocked_until']:
            raise HTTPException(status_code=403, detail="IP blocked due to excessive requests.")
        else:
            del data[ip]['blocked_until']
    
    if ip not in data:
        data[ip] = {'count': 1, 'last_request': current_time}
    else:
        elapsed_time = current_time - data[ip]['last_request']
        if elapsed_time < 3600:
            if data[ip]['count'] >= RATE_LIMIT:
                data[ip]['blocked_until'] = current_time + BLOCK_DURATION
                save_rate_limit_data(data)
                raise HTTPException(status_code=429, detail="Rate limit exceeded. IP blocked.")
            data[ip]['count'] += 1
        else:
            data[ip] = {'count': 1, 'last_request': current_time}
    data[ip]['last_request'] = current_time
    save_rate_limit_data(data)


async def rate_limiter_dependency(request: Request):
    client_ip = request.client.host
    check_rate_limit(client_ip)
