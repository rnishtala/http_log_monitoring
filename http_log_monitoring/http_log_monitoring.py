import time
import datetime
import asyncio
import json
from collections import defaultdict, deque, Counter

class Log(object):
    """Parses the logs into a data structure"""
    def __init__(self, log_line):
        self._log = log_line.replace('[', '')
        self._log.replace(']', '')
        self._headers = ["ip", "user", "timestamp", "section", "status"]

    def build_dict(self):
        """Builds a dictionary after parsing a log line"""
        values = self._log.split(' ')
        indexes = [1, 4, 5, 7, 9]
        for index in sorted(indexes, reverse=True):
            del values[index]
        log_dict = dict(zip(self._headers, values))
        resource = log_dict["section"].split('/')[2:]
        log_dict["resource"] = '/'.join(resource)
        log_dict["section"] = f"{log_dict['section'].split('/')[1]} (section)"
        log_dict["user (IP)"] = f"{log_dict['user']} ({log_dict['ip']})"
        log_dict["state_code"] = f"State code ({log_dict['status']})"
        return log_dict

class HttpMonitoring(object):
    """Monitor http logs to compute traffic statistics"""
    def __init__(self, location, threshold=None):
        self._location = location
        self._http_logs = dict()
        self.stats = defaultdict(int)
        self.section_stats = defaultdict(int)
        self.top_section_stats = defaultdict(int)
        self.traffic_counts = deque(maxlen=120) # Store traffic count for 2 minutes
        self.counter = 0
        self.active_alert = False
        self._threshold = threshold or 10
        self.log_dict = dict()

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
        print("\n=====Section Stats (top 5 hits)=====")
        for item, value in self.top_section_stats.items():
            print(f"{item} - {value} hit/s!")
        print("\n=====Other stats======")
        for item, value in self.stats.items():
            print(f"{item} - {value} hit/s!")

    def top_section_hits(self):
        return dict(Counter(self.section_stats).most_common(5))

    async def compute_stats(self):
        """Compute various traffic stats"""
        for log_line in self.stream_logs():
            log = Log(log_line)
            self.log_dict = log.build_dict()
            self.section_stats[self.log_dict['section']] += 1
            self.top_section_stats = self.top_section_hits()
            self.stats[self.log_dict['user (IP)']] += 1
            self.stats[self.log_dict['state_code']] += 1
            await asyncio.sleep(0.00001)

    async def traffic_counter(self):
        for log_line in self.stream_logs():
            self.counter += 1
            await asyncio.sleep(0.00001)

    def generate_alert(self):
        """Generate an alert if traffic rate is beyond (or equal to) a threshold value"""
        if len(self.traffic_counts) > 0:
            avg_count = int(self.traffic_counts[-1][1]/len(self.traffic_counts))
            if avg_count >= self._threshold:
                self.active_alert = True
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"High traffic generated an alert - {avg_count} hits per second (avg), triggered at {timestamp}")

    def clear_alert(self):
        """Clear an alert"""
        if len(self.traffic_counts) > 0:
            avg_count = int(self.traffic_counts[-1][1]/len(self.traffic_counts))
            if self.active_alert and avg_count < self._threshold:
                self.active_alert = False
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"High traffic alert cleared - {avg_count} hits per second (avg), triggered at {timestamp}")
