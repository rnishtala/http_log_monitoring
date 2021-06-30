
import time
import datetime
import asyncio
import json
from collections import defaultdict, deque

class Log(object):
    def __init__(self, log_line):
        self._log = log_line.replace('[', '')
        self._log.replace(']', '')
        self._headers = ["ip", "user", "timestamp", "section", "status"]

    def build_dict(self):
        values = self._log.split(' ')
        indexes = [1, 4, 5, 7, 9]
        for index in sorted(indexes, reverse=True):
            del values[index]
        log_dict = dict(zip(self._headers, values))
        resource = log_dict["section"].split('/')[2:]
        log_dict["resource"] = '/'.join(resource)
        log_dict["section"] = log_dict["section"].split('/')[1]
        return log_dict

class HttpMonitoring(object):
    """Monitor http logs to compute traffic statistics"""
    def __init__(self, location, threshold=None):
        self._location = location
        self._http_logs = dict()
        self.stats = defaultdict(int)
        self.traffic_counts = deque(maxlen=120) # Store traffic count for 2 minutes
        self.counter = 0
        self.active_alert = False
        self._threshold = threshold or 10

    def stream_logs(self):
        """Stream logs from a file"""
        self._location.seek(0,2)
        while True:
            line = self._location.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

    def read_logs(self):
        """Read logs from a file"""
        lines = self._location.readlines()
        for line in lines:
            time.sleep(0.1)
            yield line

    @property
    def display_stats(self):
        """Display stats in json format"""
        print(json.dumps(self.stats, indent=2, default=str)+"\n")

    async def compute_stats(self):
        """Compute various traffic stats"""
        for log_line in self.stream_logs():
            log = Log(log_line)
            log_dict = log.build_dict()
            self.stats[log_dict['section']] += 1
            self.stats[log_dict['user']] += 1
            self.stats[log_dict['ip']] += 1
            self.stats[log_dict['status']] += 1
            await asyncio.sleep(0.00001)

    async def traffic_counter(self):
        for log_line in self.stream_logs():
            self.counter += 1
            await asyncio.sleep(0.00001)

    def generate_alert(self):
        """Generate an alert if traffic rate is beyond a threshold value"""
        if len(self.traffic_counts) > 0:
            avg_count = int(self.traffic_counts[-1][1]/len(self.traffic_counts))
            if avg_count >= self._threshold:
                self.active_alert = True
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"High traffic generated an alert - hits = {avg_count}, triggered at {timestamp}")

    def clear_alert(self):
        """Clear an alert"""
        if len(self.traffic_counts) > 0:
            avg_count = int(self.traffic_counts[-1][1]/len(self.traffic_counts))
            if self.active_alert and avg_count < self._threshold:
                self.active_alert = False
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"High traffic alert cleared - hits {avg_count}, triggered at {timestamp}")
