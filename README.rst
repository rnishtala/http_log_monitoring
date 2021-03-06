===================
http_log_monitoring
===================


.. image:: https://img.shields.io/pypi/v/http_log_monitoring.svg
        :target: https://pypi.python.org/pypi/http_log_monitoring

.. image:: https://img.shields.io/travis/rnishtala/http_log_monitoring.svg
        :target: https://travis-ci.com/rnishtala/http_log_monitoring

.. image:: https://readthedocs.org/projects/http-log-monitoring/badge/?version=latest
        :target: https://http-log-monitoring.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Consume an actively written-to w3c-formatted HTTP access log and computes statistics.

* Free software: Apache Software License 2.0


Features
--------
* Streams HTTP access logs
* Computes various traffic statistics
* Generates an alert if the traffic count is > 10 per second (average over 2 mins)
* Clears an active alert if the traffic count is < 10 per second (default)
* Tested with: https://github.com/xuwenyihust/lunaticlog

Future improvements
-------------------
* The current service stores up to 2 minutes of data in memory, this could be increased to be a day
* More relevant statistics could be displayed at the top
* A data store could be introduced to store long term statistics
* This service could be deployed in a cluster (Kubernetes/docker-compose) with a load balancer in front
* The unit-test coverage could be improved

Development
------------
To run tests (including alert generation tests)

.. code-block:: console

    $ make clean
    $ make test


Installation
-------------
.. code-block:: console

    $ git clone git://github.com/rnishtala/http_log_monitoring

.. code-block:: console

    $ make install

Alternative Installation
------------------------
.. code-block:: console

    $ git clone git://github.com/rnishtala/http_log_monitoring
    $ make dist
    $ pip install dist/http_log_monitoring-0.0.1-py2.py3-none-any.whl

Usage
-------

To use http_log_monitoring in a project, run the cli script below:
Its also in http_log_monitoring/cli.py

.. code-block:: console

    $ python cli.py --threshold 5 --logfile /tmp/access.log

.. code-block:: python

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
