import time

capacity = 5            # max tokens one can have
refill_rate = 1 / 10    # 1 token every 10 seconds

clients = {}

def is_allowed(client_ip : str):

    now = time.time()

    if client_ip not in clients:
        clients[client_ip] = {
            "tokens" : capacity,
            "last_request" : now
        }

    client = clients[client_ip]

    elapsed = now - client["last_request"]

    client["tokens"] = min(
        capacity, 
        client["tokens"] + elapsed * refill_rate
    )

    client["last_request"] = now

    if client["tokens"] >= 1:
        client["tokens"] -= 1
        return True

    return False
    