#!/usr/bin/env python3
import sys
import subprocess
import glob
import time
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

def get_gpu_util():
    try:
        # Run nvidia-smi
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            encoding="utf-8"
        )
        return get_color(out.strip(), "%", 30, 80)
    except:
        return f"{GREY}  0%{RESET}"

def get_gpu_temp():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            encoding="utf-8"
        )
        return get_color(out.strip(), "°C", 60, 80)
    except:
        return f"{GREY}N/A{RESET}"

def get_cpu_temp():
    # Scan for Tctl or Package temp
    paths = glob.glob("/sys/class/hwmon/hwmon*/temp*_label")
    target_input = None

    for path in paths:
        try:
            with open(path, "r") as f:
                label = f.read().strip()
            if label in ["Tctl", "Package", "CPU Package"]:
                target_input = path.replace("_label", "_input")
                break
        except:
            continue

    if target_input and os.path.exists(target_input):
        try:
            with open(target_input, "r") as f:
                raw = int(f.read().strip())
            return get_color(raw / 1000, "°C", 65, 85)
        except:
            pass
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
    paths = glob.glob("/sys/class/hwmon/hwmon*/fan*_input")
    for path in paths:
        try:
            with open(path, "r") as f:
                speed = int(f.read().strip())
            if speed > 0:
                return get_color(speed, "RPM", 1400, 2200)
        except:
            continue
    return f"{GREY}  0RPM{RESET}"

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
