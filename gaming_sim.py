import heapq
import random

# ---------- Configuration ----------
SIM_TIME = 10.0          # seconds
N_USERS = 2
REQ_RATE = 10.0          # req/s per user (will increase later)
FAST_CPU_MS = 7.0
SLOW_CPU_MS = 18.0

# RTTs in ms (round-trip)
RTT = {
    (0, 0): 15.0,  # user 0 -> server 0 (fast)
    (0, 1): 35.0,  # user 0 -> server 1 (slow)
    (1, 0): 20.0,  # user 1 -> server 0 (fast)
    (1, 1): 25.0,  # user 1 -> server 1 (slow)
}

# ---------- Event types ----------
EV_GEN = "generate"      # user generates new request
EV_ARRIVE = "arrive"     # request arrives at server
EV_DONE = "done"         # request finished processing, ready to send back
EV_RESP = "response"     # response received by user

# ---------- Data structures ----------
event_queue = []         # (time, counter, event_type, data)
event_counter = 0        # to break ties in heapq

tasks = {}               # task_id -> info dict
next_task_id = 0

# Server state
servers = {
    0: {"type": "fast", "busy_until": 0.0},
    1: {"type": "slow", "busy_until": 0.0},
}

latencies = []           # list of total latency per task


def schedule(time, ev_type, data):
    global event_counter
    heapq.heappush(event_queue, (time, event_counter, ev_type, data))
    event_counter += 1


def exp_rv(rate):
    return random.expovariate(rate)


def cpu_time_ms(server_id):
    if servers[server_id]["type"] == "fast":
        return FAST_CPU_MS
    else:
        return SLOW_CPU_MS


def select_server_round_robin(task_id):
    # For now, always send to fast server 0 (we'll change this later)
    return 0


# ---------- Initialization ----------
current_time = 0.0
random.seed(1)

# Schedule first request generation for each user
for user_id in range(N_USERS):
    schedule(0.0, EV_GEN, {"user_id": user_id})

# ---------- Main simulation loop ----------
while event_queue and current_time <= SIM_TIME:
    current_time, _, ev_type, data = heapq.heappop(event_queue)

    if ev_type == EV_GEN:
        user_id = data["user_id"]
        task_id = next_task_id
        next_task_id += 1

        # Create task
        tasks[task_id] = {
            "user_id": user_id,
            "t_created": current_time,
        }

        # Choose server
        server_id = select_server_round_robin(task_id)
        tasks[task_id]["server_id"] = server_id

        # Network delay: half RTT to go, half to come back later
        rtt_ms = RTT[(user_id, server_id)]
        one_way = rtt_ms / 2.0 / 1000.0  # seconds

        # Schedule arrival at server
        schedule(current_time + one_way, EV_ARRIVE, {"task_id": task_id})

        # Schedule next generation for this user
        gap = exp_rv(REQ_RATE)  # exponential inter-arrival
        if current_time + gap <= SIM_TIME:
            schedule(current_time + gap, EV_GEN, {"user_id": user_id})

    elif ev_type == EV_ARRIVE:
        task_id = data["task_id"]
        task = tasks[task_id]
        server_id = task["server_id"]

        start_time = max(current_time, servers[server_id]["busy_until"])
        service_time = cpu_time_ms(server_id) / 1000.0  # seconds

        servers[server_id]["busy_until"] = start_time + service_time

        # Schedule done processing event
        schedule(start_time + service_time, EV_DONE, {"task_id": task_id})

    elif ev_type == EV_DONE:
        task_id = data["task_id"]
        task = tasks[task_id]
        user_id = task["user_id"]
        server_id = task["server_id"]

        rtt_ms = RTT[(user_id, server_id)]
        one_way = rtt_ms / 2.0 / 1000.0

        # Schedule response arrival at user
        schedule(current_time + one_way, EV_RESP, {"task_id": task_id})

    elif ev_type == EV_RESP:
        task_id = data["task_id"]
        task = tasks[task_id]
        total_latency = current_time - task["t_created"]
        latencies.append(total_latency)


# ---------- Results ----------
if latencies:
    avg_lat = sum(latencies) / len(latencies)
    lat_sorted = sorted(latencies)
    p95_index = int(0.95 * len(lat_sorted)) - 1
    p95 = lat_sorted[max(0, p95_index)]

    print(f"Tasks processed: {len(latencies)}")
    print(f"Average latency: {avg_lat * 1000:.2f} ms")
    print(f"95th percentile latency: {p95 * 1000:.2f} ms")
else:
    print("No tasks processed")
