# ExPutt Client

Python client that connects to an ExPutt camera over Wi‑Fi (same session as the phone app) and prints **ball / club putt data** each time a putt is measured.

The camera allows **one peer at a time**. Close the phone ExPutt app before running this client.

## Requirements

- Python 3.10+ recommended
- Camera and PC on the same Wi‑Fi network
- Dependency:

```bash
pip install -r requirements.txt
```

(`pyzmq` is required.)

## Quick start

```bash
python exputt_client.py
```

Typical flow:

1. Client discovers the camera via UDP broadcast on port `9999`
2. Connects over NetMQ (TCP port `8889`)
3. Syncs the mat (`resyncToMat` → wait for `MatOK`)
4. Arms practice mode
5. Prints putt data when you putt
6. Logs everything (timestamped) to the console and a logfile

Stop with `Ctrl+C`.

## Command-line options

| Option | Default | Description |
|--------|---------|-------------|
| `--ip IP` | *(discover)* | Skip UDP discovery and connect directly to this camera IP |
| `--port PORT` | `8889` | NetMQ dealer port |
| `--discover-timeout SEC` | `30` | How long to wait for a camera UDP broadcast |
| `--duration SEC` | `0` | Listen for this many seconds, then exit (`0` = until Ctrl+C) |
| `--log PATH` | `exputt_YYYYMMDD_HHMMSS.log` | Logfile path (same messages as the console, with timestamps) |
| `--left-handed` | off | Send `setDexterityLeft` instead of `setDexterityRight` |
| `--no-alive` | off | Disable periodic `N_ALIVE` keepalives |
| `--verbose` | off | Show full protocol traffic (sends, receives, preview noise) |
| `--demo-parse` | off | Print a sample putt block and exit (no network) |
| `-h` / `--help` | | Show help |

### Examples

```bash
# Auto-discover camera, log to a dated file
python exputt_client.py

# Known camera IP, custom logfile
python exputt_client.py --ip 192.168.5.171 --log session1.log

# Left-handed setup
python exputt_client.py --left-handed

# Debug protocol / mat sync
python exputt_client.py --verbose --log debug.log

# Run for 2 minutes then exit
python exputt_client.py --duration 120

# Offline sample output
python exputt_client.py --demo-parse
```

## What you’ll see

**Setup (quiet mode)** — short status lines, for example:

```text
[2026-07-31 21:36:06.333] Looking for camera on UDP :9999 ...
[2026-07-31 21:36:06.400] Found camera 192.168.5.171 (v1.21.2176)
[2026-07-31 21:36:07.100] Syncing mat... place/aim the camera until MatOK
[2026-07-31 21:36:12.500] MatOK - arming practice
[2026-07-31 21:36:12.800] Armed - putt when ready (ball/club data prints each putt)
[2026-07-31 21:36:20.100] [ready] ball in launch area (#1)
```

**Each measured putt** — ball/shot and club/putter fields, plus the raw CSV:

```text
PUTT #1
============================================================
ball / shot
  angle : ...
  speed : ...
club / putter
  time             : ...
  speed            : ...
  putter_direction : ...
  impact_angle     : ...
  putter_x         : [...]
  putter_y         : [...]
  putter_angle     : [...]
  putter_pos       : ...
------------------------------------------------------------
raw: PuttResult,...
```

### Reading the numbers

- **Shot `angle` / `speed`** — ball launch direction and speed from the camera.
- **Club fields at `-9999.0`** — not an error in this client. That value is the camera/app sentinel for “no valid putter measurement.” The ball was tracked; the putter was not.
- If club data is missing, check camera aim/height, lighting, putter visibility through the stroke, and `--left-handed` if needed. Use the same physical setup that works with the phone app.

## Logging

Every message is prefixed with a timestamp:

```text
[YYYY-MM-DD HH:MM:SS.mmm] message
```

The same line is written to:

- the console
- the logfile (`--log`, or `exputt_YYYYMMDD_HHMMSS.log` by default)

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| `Camera busy` / `N_BUSY` | Phone app (or another client) still connected — close it |
| No discovery | PC and camera not on same Wi‑Fi; firewall blocking UDP `9999` |
| Stuck on “Looking for mat” | Aim/height/lighting; mat not in view |
| `[ready]` never appears | Ball not in launch zone, or practice not armed yet |
| Shot data OK, club all `-9999` | Putter not tracked (aim, light, contrast, handedness) |

Use `--verbose --log debug.log` when diagnosing sync or protocol issues.
