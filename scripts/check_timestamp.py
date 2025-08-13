#!/usr/bin/env python3
import datetime

timestamp = 1754684932.973565
dt = datetime.datetime.fromtimestamp(timestamp)
print(f"Timestamp {timestamp} = {dt}")
print(f"Formatted: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
