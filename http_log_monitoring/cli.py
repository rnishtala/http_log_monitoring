"""Console script for http_log_monitoring."""
import argparse
import sys
import asyncio
from http_log_monitoring.http_log_monitoring import HttpMonitoring, Log
from http_log_monitoring.utils import (print_traffic_stats, print_traffic_volume,
                   reset_stats, reset_counter, capture_traffic_counts)


async def main():
    """Console script for http_log_monitoring"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", help="Alert threshold (default: 10)", type=int)
    parser.add_argument("--logfile", help="Enter a log file (default: /tmp/access.log)")
    args = parser.parse_args()
    threshold = args.threshold
    log_file = args.logfile or "/tmp/access.log"
    print(f"Streaming logs from the file: {log_file}")
    logfile = open(log_file,"r")
    log_monitor = HttpMonitoring(logfile, threshold)
    await asyncio.gather(log_monitor.compute_stats(),
                         log_monitor.traffic_counter(),
                         capture_traffic_counts(log_monitor),
                         print_traffic_volume(log_monitor),
                         print_traffic_stats(log_monitor),
                         reset_stats(log_monitor))

if __name__ == "__main__":
    asyncio.run(main())
