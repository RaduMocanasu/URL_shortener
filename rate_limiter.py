import time

capacity = 5            # max tokens one can have
refill_rate = 1 / 10    # 1 token every 10 seconds
inactive_timeout = 60   # 5 * 10 = 50, so 60 seconds of inactivity should be enough to remove an IP from the dictionary
cleanup_interval = 60

clients = {}

last_cleanup = time.monotonic()

def cleanup_clients(now):
    stale_clients = []

    # loop for checking users
    for ip, client in clients.items():
        if now - client['last_request'] >= inactive_timeout:
            stale_clients.append(ip)

    # second loop for deleting users(like in c++, modifying a map while iterating through it can cause an error)
    for ip in stale_clients:
        del clients[ip]

def is_allowed(client_ip : str):

    global last_cleanup # references the global variable we defined

    now = time.monotonic()

    if now - last_cleanup >= cleanup_interval:
        cleanup_clients(now)
        last_cleanup = now

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
    