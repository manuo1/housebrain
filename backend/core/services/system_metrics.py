import logging
import subprocess

from core.constants import LoggerLabel

logger = logging.getLogger("django")

# Bits du bitmask retourné par `vcgencmd get_throttled`, séparés par sens :
# bits 0-3 = état actuel, bits 16-19 = "déjà survenu depuis le boot".
# Gardés séparés (plutôt qu'un seul dict fusionné) pour ne jamais confondre
# un souci actif avec un souci seulement historique dans les logs.
THROTTLED_BITS_NOW = {
    0: "under-voltage",
    1: "arm freq capped",
    2: "throttled",
    3: "soft temp limit",
}
THROTTLED_BITS_SINCE_BOOT = {
    16: "under-voltage",
    17: "arm freq capped",
    18: "throttled",
    19: "soft temp limit",
}

# housebrain-periodic.timer déclenche cette commande toutes les minutes ;
# on interroge dmesg sur une fenêtre légèrement plus large (90s) pour
# absorber la gigue de l'ordonnanceur sans dupliquer une même ligne sur
# deux exécutions consécutives (ce qui arrivait avec une fenêtre de 2min).
USB_DMESG_WINDOW = "90 seconds ago"


def _run(cmd: list[str]) -> str:
    """Run a shell command and return its stripped stdout, or "" on failure.

    Failures (missing binary, permission error, non-zero exit, timeout) are
    logged as a warning and swallowed so one failing metric doesn't prevent
    the others from being collected.
    """
    try:
        return subprocess.check_output(cmd, text=True, timeout=5).strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        OSError,
    ) as e:
        logger.warning(f"{LoggerLabel.MONITORING} Command failed {cmd}: {e}")
        return ""


def _decode_throttled(raw: str) -> tuple[str, str]:
    """Decode `vcgencmd get_throttled` output (e.g. "throttled=0x50000").

    Returns a (now, since_boot) pair of strings, each either "ok", "unknown"
    (if raw couldn't be parsed), or a comma-separated list of active flags.
    Kept as two separate values so callers can react to an active problem
    without being distracted by a flag that only fired once since boot.
    """
    try:
        value = int(raw.split("=")[1], 16)
    except (IndexError, ValueError):
        return "unknown", "unknown"

    now_flags = [label for bit, label in THROTTLED_BITS_NOW.items() if value & (1 << bit)]
    since_boot_flags = [
        label for bit, label in THROTTLED_BITS_SINCE_BOOT.items() if value & (1 << bit)
    ]
    now = ",".join(now_flags) if now_flags else "ok"
    since_boot = ",".join(since_boot_flags) if since_boot_flags else "ok"
    return now, since_boot


def _get_usb_errors() -> str:
    """Return the last 5 dmesg lines mentioning "usb" in the recent window, or "" if none."""
    dmesg_out = _run(["dmesg", "-T", "--since", USB_DMESG_WINDOW])
    if not dmesg_out:
        return ""
    usb_lines = [line for line in dmesg_out.splitlines() if "usb" in line.lower()]
    return " | ".join(usb_lines[-5:])  # les 5 dernières pour ne pas noyer le log


def log_system_metrics() -> None:
    """Collect and log a snapshot of Pi health metrics (temp, throttling, RAM,
    disk, load, uptime, recent USB errors).

    Logged at warning level when there's an active throttling condition or
    recent USB errors (the signal this is meant to help correlate for the
    JMicron hypothesis), info level otherwise.
    """
    temp = _run(["vcgencmd", "measure_temp"])
    throttled_raw = _run(["vcgencmd", "get_throttled"])
    throttled_now, throttled_since_boot = _decode_throttled(throttled_raw)

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
        f"{LoggerLabel.MONITORING} {temp} throttled_now={throttled_now} "
        f"throttled_since_boot={throttled_since_boot} "
        f"ram={ram_used}/{ram_total}M disk_used={disk_usage} "
        f"load={load} up_since={uptime_since}"
    )
    if usb_errors:
        message += f" usb_errors=[{usb_errors}]"

    # Seul un throttling ACTIF (throttled_now) ou des erreurs USB récentes
    # sont le signal qu'on cherche pour l'hypothèse JMicron : un flag qui n'a
    # fait que passer depuis le boot ne justifie pas une alerte à chaque run.
    if throttled_now != "ok" or usb_errors:
        logger.warning(message)
    else:
        logger.info(message)
