#!/usr/bin/env python3
import sys
import subprocess
import glob
import os

# --- COLORS ---
GREEN = "%{F#9ece6a}"
YELLOW = "%{F#e0af68}"
RED = "%{F#f7768e}"
GREY = "%{F#ffffff}"
RESET = "%{F-}"

def get_color(val, unit, warn, crit):
    """Returns the Polybar formatted string."""
    try:
        val_num = float(val)
    except (ValueError, TypeError):
        return f"{GREY}N/A{RESET}"

    # Format width: 3 chars for number (e.g. " 55")
    val_str = f"{int(val_num):3d}"

    if val_num >= crit:
        return f"{RED}{val_str}{unit}{RESET}"
    elif val_num >= warn:
        return f"{YELLOW}{val_str}{unit}{RESET}"
    else:
        return f"{GREY}{val_str}{unit}{RESET}"

def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except (OSError, ValueError):
        return ""

def get_nvidia_value(field):
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                f"--query-gpu={field}",
                "--format=csv,noheader,nounits",
            ],
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
        # The bar represents the primary GPU when more than one is installed.
        return out.splitlines()[0].strip()
    except (IndexError, OSError, subprocess.SubprocessError):
        return None

def get_gpu_util():
    value = get_nvidia_value("utilization.gpu")
    return get_color(value, "%", 30, 80)

def get_gpu_temp():
    value = get_nvidia_value("temperature.gpu")
    return get_color(value, "°C", 60, 80)

def get_cpu_temp():
    # Prefer the CPU's own hwmon device instead of similarly named board probes.
    preferred_labels = ("Tctl", "Tdie", "CPU Package", "Package id 0", "Package")
    for hwmon in glob.glob("/sys/class/hwmon/hwmon*"):
        if read_text(os.path.join(hwmon, "name")) not in ("k10temp", "zenpower", "coretemp"):
            continue
        labels = {}
        for label_path in glob.glob(os.path.join(hwmon, "temp*_label")):
            labels[read_text(label_path)] = label_path.replace("_label", "_input")
        for label in preferred_labels:
            raw = read_text(labels.get(label, ""))
            if raw:
                try:
                    return get_color(int(raw) / 1000, "°C", 65, 85)
                except ValueError:
                    continue
    return f"{GREY}N/A{RESET}"

def get_cpu_power():
    try:
        # Run turbostat with sudo (allowed via visudo)
        # --interval 0.1 makes it fast so the bar doesn't freeze
        out = subprocess.check_output(
            ["sudo", "turbostat", "--quiet", "--show", "PkgWatt", "--interval", "0.1", "--num_iterations", "1"],
            encoding="utf-8"
        )

        # Output looks like:
        # PkgWatt
        # 27.70

        # Split into lines, take the second line (the value)
        lines = out.strip().split("\n")
        if len(lines) >= 2:
            watts = float(lines[1])
            return get_color(watts, "W", 65, 100)

    except Exception as e:
        return f"{GREY}ERR{RESET}"

    return f"{GREY}N/A{RESET}"

def get_fan_speed():
    candidates = []
    board_drivers = ("nct6687", "nct6686", "nct6683", "nct6775", "it87")

    for hwmon in glob.glob("/sys/class/hwmon/hwmon*"):
        driver = read_text(os.path.join(hwmon, "name"))
        for path in glob.glob(os.path.join(hwmon, "fan*_input")):
            try:
                speed = int(read_text(path))
            except ValueError:
                continue
            if speed <= 0:
                continue

            label = read_text(path.replace("_input", "_label")).lower()
            basename = os.path.basename(path)
            if "cpu" in label:
                priority = 0
            elif driver in board_drivers and basename == "fan1_input":
                priority = 1
            elif driver in board_drivers:
                priority = 2
            else:
                priority = 3
            candidates.append((priority, basename, speed))

    if not candidates:
        return f"{GREY}N/A{RESET}"

    _, _, speed = min(candidates)
    return get_color(speed, "RPM", 1400, 2200)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: monitor.py <mode>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "gpu-util":
        print(get_gpu_util())
    elif mode == "gpu-temp":
        print(get_gpu_temp())
    elif mode == "cpu-temp":
        print(get_cpu_temp())
    elif mode == "cpu-power":
        print(get_cpu_power())
    elif mode == "cpu-fan":
        print(get_fan_speed())
