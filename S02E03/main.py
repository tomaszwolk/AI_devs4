from helper import filter_logs, find_unique_log_levels, filter_unique_logs, create_payload, send_payload
from pathlib import Path

log_path = Path(__file__).parent / "data" / "failure.log.txt"
filtered_path = Path(__file__).parent / "data" / "filtered.log.txt"
filtered_unique_path = Path(__file__).parent / "data" / "filtered_unique.log.txt"

# Function to find unique log levels
# print(find_unique_log_levels(log_path))
# Unique log levels: {'[CRIT]', '[INFO]', '[WARN]', '[ERRO]'}

# Function to filter logs
levels = ["INFO"]
filter_logs(log_path, filtered_path, levels)

# Function to filter unique logs
filter_unique_logs(filtered_path, filtered_unique_path)

filtered_logs = ""
with open(filtered_unique_path, "r") as file:
    for line in file:
        filtered_logs += line


payload = create_payload(filtered_logs)
status_code, response = send_payload(payload)
print(f"Status code: {status_code}")
print(f"Response: {response}")
