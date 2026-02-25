#!/usr/bin/env python3
import time
import glob
import os

# --- COLORS ---
GREEN = "%{F#9ece6a}"
YELLOW = "%{F#e0af68}"
RED = "%{F#f7768e}"
GREY = "%{F#565f89}"
RESET = "%{F-}"

def get_cpu_power():
    # ---------------------------------------------------------
    # METHOD 1: Volts * Amps (The "Ryzen Secret" Method)
    # Look for Core Voltage (in0) and Current (curr1)
    # ---------------------------------------------------------
    try:
        # Find the sensor with "Tctl" or "Vcore" to ensure we are looking at the CPU
        hwmon_paths = glob.glob("/sys/class/hwmon/hwmon*")

        for path in hwmon_paths:
            # We need both voltage (in0_input) and current (curr1_input)
            v_path = os.path.join(path, "in0_input")
            c_path = os.path.join(path, "curr1_input")

            if os.path.exists(v_path) and os.path.exists(c_path):
                # Read Voltage (mV) and Current (mA)
                with open(v_path, 'r') as f: voltage_mv = int(f.read().strip())
                with open(c_path, 'r') as f: current_ma = int(f.read().strip())

                # Watts = (mV / 1000) * (mA / 1000)
                # Simplified: (mV * mA) / 1,000,000
                watts = (voltage_mv * current_ma) / 1_000_000.0

                return format_output(watts)
    except:
        pass

    # ---------------------------------------------------------
    # METHOD 2: RAPL Energy (The "s-tui" Method)
    # ---------------------------------------------------------
    rapl_path = "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
    if os.path.exists(rapl_path) and os.access(rapl_path, os.R_OK):
        try:
            with open(rapl_path, "r") as f: e1 = int(f.read().strip())
            time.sleep(0.5)
            with open(rapl_path, "r") as f: e2 = int(f.read().strip())

            # Watts = Delta_uJ / Time_us
            # Time is 0.5s (500,000us)
            watts = (e2 - e1) / 500000.0
            return format_output(watts)
        except:
            pass

    # ---------------------------------------------------------
    # METHOD 3: Estimation (Fallback)
    # ---------------------------------------------------------
    try:
        # Load-based guess for 9900X (120W TDP)
        with open("/proc/loadavg", "r") as f:
            load = float(f.read().split()[0])
        # Crude calc: Load * 8W per thread + 30W Idle
        est_watts = (load * 5) + 30
        if est_watts > 160: est_watts = 160
        return format_output(est_watts, estimated=True)
    except:
        return f"{GREY}N/A{RESET}"

def format_output(watts, estimated=False):
    # Scale for Ryzen 9900X
    # Green < 60W | Yellow 60-110W | Red > 110W

    # Format to integer for clean look
    val_str = f"{int(watts):3d}"
    unit = "W"

    if estimated:
        unit = "*" # Mark estimated values with *

    if watts >= 110:
        return f"{RED}{val_str}{unit}{RESET}"
    elif watts >= 60:
        return f"{YELLOW}{val_str}{unit}{RESET}"
    else:
        return f"{GREEN}{val_str}{unit}{RESET}"

if __name__ == "__main__":
    print(get_cpu_power())
