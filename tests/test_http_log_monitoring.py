#!/usr/bin/env python

"""Tests for `http_log_monitoring` package."""

import json
import pytest
import pkg_resources
from http_log_monitoring.http_log_monitoring import Log, HttpMonitoring

test_log = pkg_resources.resource_filename(__name__, "test.log")
data_path = pkg_resources.resource_filename(__name__, "data.json")
data_stats_path = pkg_resources.resource_filename(__name__, "data_stats.json")
section_stats_path = pkg_resources.resource_filename(__name__, "section_stats.json")

with open(data_path, encoding='utf-8', errors='ignore') as json_data:
    data = json.load(json_data, strict=False)

with open(data_stats_path, encoding='utf-8', errors='ignore') as json_data:
    data_stats = json.load(json_data, strict=False)

with open(section_stats_path, encoding='utf-8', errors='ignore') as json_data:
    section_stats = json.load(json_data, strict=False)

with open(test_log, encoding='utf-8', errors='ignore') as logs:
    test_logs = logs.readlines()

def mock_logs(*args):
    return test_logs

def test_build_dict():
    result = []
    logfile = open(test_log,"r")
    log_monitor = HttpMonitoring(logfile)
    for log_line in log_monitor.read_logs():
        log = Log(log_line)
        log_dict = log.build_dict()
        result.append(log_dict)
    assert result == data

@pytest.mark.asyncio
async def test_data_stats(mocker):
    logfile = open(test_log,"r")
    mocker.patch('http_log_monitoring.http_log_monitoring.HttpMonitoring.stream_logs',
                 mock_logs)
    log_monitor = HttpMonitoring(logfile)
    await log_monitor.compute_stats()
    assert log_monitor.stats == data_stats
    assert log_monitor.top_section_stats == section_stats

@pytest.mark.asyncio
async def test_traffic_counter(mocker):
    logfile = open(test_log,"r")
    mocker.patch('http_log_monitoring.http_log_monitoring.HttpMonitoring.stream_logs',
                 mock_logs)
    log_monitor = HttpMonitoring(logfile)
    await log_monitor.traffic_counter()
    assert log_monitor.counter == 3

@pytest.mark.asyncio
async def test_generate_alert(mocker):
    """Test alert generation"""
    logfile = open(test_log,"r")
    mocker.patch('http_log_monitoring.http_log_monitoring.HttpMonitoring.stream_logs',
                 mock_logs)
    log_monitor = HttpMonitoring(logfile, 2)
    await log_monitor.traffic_counter()
    log_monitor.traffic_counts.append((0, log_monitor.counter))
    log_monitor.generate_alert()
    assert log_monitor.active_alert == True

@pytest.mark.asyncio
async def test_clear_alert(mocker):
    """Test alert clearing/resolution"""
    logfile = open(test_log,"r")
    mocker.patch('http_log_monitoring.http_log_monitoring.HttpMonitoring.stream_logs',
                 mock_logs)
    log_monitor = HttpMonitoring(logfile, 2)
    await log_monitor.traffic_counter()
    log_monitor.traffic_counts.append((0, log_monitor.counter))
    log_monitor.generate_alert()
    assert log_monitor.active_alert == True
    log_monitor.counter = 1
    log_monitor.traffic_counts.append((0, log_monitor.counter))
    log_monitor.clear_alert()
    assert log_monitor.active_alert == False
