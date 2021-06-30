import asyncio
from constants import MAX_STATS_TIME, MAX_COUNTER_TIME
from collections import defaultdict, deque

async def print_traffic_stats(sensor):
    """Display traffic stats"""
    while True:
        print("======Traffic Stats=====")
        sensor.display_stats
        await asyncio.sleep(MAX_STATS_TIME)

async def print_traffic_volume(sensor):
    """Display traffic volume"""
    while True:
        print(f"Traffic volume: {sensor.traffic_counts}\n")
        await asyncio.sleep(MAX_STATS_TIME)

async def reset_stats(sensor):
    """Reset traffic stats"""
    while True:
        sensor.stats = defaultdict(int)
        await asyncio.sleep(MAX_STATS_TIME)

async def reset_counter(sensor):
    """Reset traffic counter"""
    while True:
        sensor.counter = 0
        await asyncio.sleep(MAX_COUNTER_TIME)

async def capture_traffic_counts(sensor):
    """Capture traffic counts in 1 second intervals/buckets"""
    bucket = 0
    while True:
        if bucket == MAX_COUNTER_TIME:
            sensor.generate_alert()
            sensor.clear_alert()
            sensor.counter = 0
            bucket = 0
            sensor.traffic_counts = deque(maxlen=120)
        bucket += 1
        sensor.traffic_counts.append((bucket, sensor.counter))
        await asyncio.sleep(1)
