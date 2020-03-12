import json
import os
import time

import requests


CLOUDFLARE_API="https://api.cloudflare.com/client/v4"


def print_errors(res):
    for message in res["errors"]:
        print(message["message"])
        for chain in message["error_chain"]:
            print("  " + chain["message"])


def check_token_is_valid(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    res = requests.get(f"{CLOUDFLARE_API}/user/tokens/verify", headers=headers).json()

    if not res["success"]:
        print_errors(res)
    
    return res["success"]


def check_global_ipaddress():
    res = requests.get("https://api.ipify.org?format=json")
    if res.status_code != 200:
        return None
    return res.json()["ip"]


def get_dns_record_id(name, token, zone_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = {
        "type": "A",
        "name": name
    }

    res = requests.get(f"{CLOUDFLARE_API}/zones/{zone_id}/dns_records", headers=headers, params=params).json()

    if not res["success"]:
        print_errors(res)
        return None

    if not len(res["result"]):
        return None
    return res["result"][0]["id"]


def create_dns_record(name, addr, token, zone_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {
        "type": "A",
        "name": name,
        "content": addr,
        "ttl": 120
    }

    res = requests.post(f"{CLOUDFLARE_API}/zones/{zone_id}/dns_records", headers=headers, data=json.dumps(data)).json()

    if not res["success"]:
        print_errors(res)
        return None

    return res["result"]["id"]


def update_dns_record(name, addr, token, zone_id, record_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {
        "type": "A",
        "name": name,
        "content": addr,
    }

    res = requests.put(f"{CLOUDFLARE_API}/zones/{zone_id}/dns_records/{record_id}", headers=headers, data=json.dumps(data)).json()

    if not res["success"]:
        print_errors(res)
        return None

    return res["result"]["id"]


def main():
    token = os.environ["CLOUDFLARE_TOKEN"]
    name = os.environ["CLOUDFLARE_NAME"]
    zone_id = os.environ["CLOUDFLARE_ZONE_ID"]
    
    if not check_token_is_valid(token=token):
        return

    record_id = get_dns_record_id(name, token=token, zone_id=zone_id)

    prev_ipaddress = "127.0.0.1"
    while True:
        ipaddress = check_global_ipaddress()

        if ipaddress and prev_ipaddress != ipaddress:
            if not record_id:
                record_id = create_dns_record(name, ipaddress, token=token, zone_id=zone_id)
            else:
                record_id = update_dns_record(name, ipaddress, token=token, zone_id=zone_id, record_id=record_id)
            prev_ipaddress = ipaddress

        time.sleep(1)


if __name__ == "__main__":
    main()
