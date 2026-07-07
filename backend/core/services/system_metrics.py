import logging
import subprocess

from core.constants import LoggerLabel

logger = logging.getLogger("django")

# Bits du bitmask retourné par `vcgencmd get_throttled`.
# Les bits 0-3 = état actuel, bits 16-19 = "déjà survenu depuis le boot".
THROTTLED_BITS = {
    0: "under-voltage (now)",
    1: "arm freq capped (now)",
    2: "throttled (now)",
    3: "soft temp limit (now)",
    16: "under-voltage (since boot)",
    17: "arm freq capped (since boot)",
    18: "throttled (since boot)",
    19: "soft temp limit (since boot)",
}


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, timeout=5).strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ) as e:
        logger.warning(f"{LoggerLabel.MONITORING} Command failed {cmd}: {e}")
        return ""


def _decode_throttled(raw: str) -> str:
    # raw ressemble à "throttled=0x50000"
    try:
        value = int(raw.split("=")[1], 16)
    except (IndexError, ValueError):
        return "unknown"
    if value == 0:
        return "ok"
    flags = [label for bit, label in THROTTLED_BITS.items() if value & (1 << bit)]
    return ",".join(flags) if flags else "ok"


def _get_usb_errors() -> str:
    dmesg_out = _run(["dmesg", "-T", "--since", "2 min ago"])
    if not dmesg_out:
        return ""
    usb_lines = [line for line in dmesg_out.splitlines() if "usb" in line.lower()]
    return " | ".join(usb_lines[-5:])  # les 5 dernières pour ne pas noyer le log


def log_system_metrics() -> None:
    temp = _run(["vcgencmd", "measure_temp"])
    throttled_raw = _run(["vcgencmd", "get_throttled"])
    throttled = _decode_throttled(throttled_raw)

    mem_line = _run(["free", "-m"]).splitlines()
    mem = mem_line[1].split() if len(mem_line) > 1 else []
    ram_used = mem[2] if len(mem) > 2 else "?"
    ram_total = mem[1] if len(mem) > 1 else "?"

    disk = _run(["df", "-h", "/"]).splitlines()
    disk_usage = disk[1].split()[4] if len(disk) > 1 else "?"

    loadavg = _run(["cat", "/proc/loadavg"]).split()
    load = " ".join(loadavg[:3]) if len(loadavg) >= 3 else "?"

    uptime_since = _run(["uptime", "-s"])

    usb_errors = _get_usb_errors()

    message = (
        f"{LoggerLabel.MONITORING} {temp} throttled={throttled} "
        f"ram={ram_used}/{ram_total}M disk_used={disk_usage} "
        f"load={load} up_since={uptime_since}"
    )
    if usb_errors:
        message += f" usb_errors=[{usb_errors}]"

    # Le throttling/under-voltage et les erreurs USB sont le signal qu'on
    # cherche pour l'hypothèse JMicron : on log en warning pour qu'ils
    # ressortent facilement, sinon info.
    if throttled != "ok" or usb_errors:
        logger.warning(message)
    else:
        logger.info(message)
