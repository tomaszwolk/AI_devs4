from helper import filter_logs, find_unique_log_levels, filter_unique_logs, create_payload, send_payload, save_data, get_logs
from pathlib import Path

log_path = Path(__file__).parent / "data" / "failure.log.txt"
filtered_path = Path(__file__).parent / "data" / "filtered.log.txt"
filtered_unique_path = Path(__file__).parent / "data" / "filtered_unique.log.txt"

# Download and save logs from the hub
logs = get_logs()
save_data(logs, log_path)

# Function to find unique log levels
# print(find_unique_log_levels(log_path))
# Unique log levels: {'[CRIT]', '[INFO]', '[WARN]', '[ERRO]'}

# Function to filter logs
levels = ["CRIT"]
filter_logs(log_path, filtered_path, levels)

# Function to filter unique logs
filter_unique_logs(filtered_path, filtered_unique_path)

filtered_logs = ""
with open(filtered_unique_path, "r") as file:
    for line in file:
        filtered_logs += line

# filtered_slogs = "[2026-03-18 06:04:13] [CRIT] ECCS8 reported runaway outlet temperature. Protection interlock initiated reactor trip.\n[2026-03-18 06:16:56] [CRIT] WSTPOOL2 absorption path reached emergency boundary. Heat rejection is no longer sufficient.\n[2026-03-18 08:00:26] [CRIT] ECCS8 core cooling cannot maintain safe gradient. Immediate protective actions are required.\n[2026-03-18 10:15:56] [CRIT] WTANK07 coolant level is below critical threshold. Shutdown logic is moving to hard trip stage.\n[2026-03-18 11:01:33] [CRIT] WTRPMP lost stable prime under peak thermal demand. Core loop continuity is compromised.\n[2026-03-18 12:51:11] [CRIT] FIRMWARE entered emergency guard branch after repeated safety faults. Manual override is locked.\n[2026-03-18 12:56:27] [CRIT] STMTURB12 decoupling sequence forced by thermal risk. Energy conversion is terminated.\n[2026-03-18 13:37:40] [CRIT] PWR01 can no longer sustain stable feed for cooling auxiliaries. Critical loads are shedding.\n[2026-03-18 14:52:40] [CRIT] Safety bootstrap read missing environment marker SAFETY_CHECK=pass. FIRMWARE continues in restricted validation mode.\n[2026-03-18 16:06:47] [CRIT] WSTPOOL2 entered critical protection state during startup. Immediate shutdown safeguards remain active.\n[2026-03-18 19:54:49] [CRIT] ECCS8 cannot remove heat with the current WTANK07 volume. Reactor protection initiates critical stop.\n[2026-03-18 20:05:21] [CRIT] Critical boundary exceeded on ECCS8. Emergency interlock keeps the reactor in protected mode."
filtered_logs = """
[2026-02-26 06:04] [CRIT] ECCS8 runaway outlet temp. Protection interlock initiated reactor trip.\\n[2026-02-26 06:11] [WARN] PWR01 input ripple crossed warning limits.\\n[2026-02-26 10:15] [CRIT] WTANK07 coolant below critical threshold. Hard trip initiated.
"""


payload = create_payload(filtered_logs)
status_code, response = send_payload(payload)
print(f"Status code: {status_code}")
print(f"Response: {response}")
