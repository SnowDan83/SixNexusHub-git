#!/usr/bin/env python3
# Vers. 3.1.0
# ==============================================================================
# SixNexus Hub - Network Utilities (Linux)
# ==============================================================================

import os
import shutil
import subprocess
import threading
import config


def execute_cmd_async(cmd, log_callback, on_complete=None):
    """Esegue comandi di sistema in background con streaming di output."""
    def _worker():
        cmd_str = ' '.join(cmd) if isinstance(cmd, list) else str(cmd)
        log_callback(f"[ESECUZIONE] {cmd_str}\n")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                if line:
                    log_callback(line)

            process.stdout.close()
            return_code = process.wait()

            if return_code == 0:
                log_callback("[SUCCESS] Operazione completata con successo.\n\n")
            else:
                log_callback(f"[ERRORE] Processo terminato con codice {return_code}\n\n")

            if on_complete:
                on_complete(return_code == 0)

        except Exception as e:
            log_callback(f"[ECCEZIONE] Errore: {e}\n\n")
            if on_complete:
                on_complete(False)

    threading.Thread(target=_worker, daemon=True).start()


def start_vpn(log_callback):
    if os.path.exists(config.SCRIPT_VPN_START):
        execute_cmd_async(["bash", config.SCRIPT_VPN_START], log_callback)
    else:
        execute_cmd_async(["tailscale", "up"], log_callback)


def stop_vpn(log_callback):
    if os.path.exists(config.SCRIPT_VPN_STOP):
        execute_cmd_async(["bash", config.SCRIPT_VPN_STOP], log_callback)
    else:
        execute_cmd_async(["tailscale", "down"], log_callback)


def start_mount(log_callback):
    if os.path.exists(config.SCRIPT_MOUNT):
        execute_cmd_async(["bash", config.SCRIPT_MOUNT], log_callback)
    else:
        log_callback(f"[ERRORE] Script {config.SCRIPT_MOUNT} non trovato.\n\n")


def start_unmount(log_callback):
    if os.path.exists(config.SCRIPT_UNMOUNT):
        execute_cmd_async(["bash", config.SCRIPT_UNMOUNT], log_callback)
    else:
        log_callback(f"[ERRORE] Script {config.SCRIPT_UNMOUNT} non trovato.\n\n")


def is_sftp_mounted() -> bool:
    """Verifica se il percorso SFTP locale è attualmente montato."""
    path = os.path.realpath(config.LOCAL_MOUNT_POINT)
    if not os.path.exists(path):
        return False

    try:
        if os.path.ismount(path):
            return True
    except Exception:
        pass

    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and os.path.realpath(parts[1]) == path:
                    return True
    except Exception:
        pass

    return False


def start_sftp_mount(log_callback, on_complete=None):
    """Monta la Home remota del NAS via SSHFS/SFTP."""
    mount_point = config.LOCAL_MOUNT_POINT
    os.makedirs(mount_point, exist_ok=True)

    if is_sftp_mounted():
        log_callback(f"[INFO] Risorsa SFTP già montata in: {mount_point}\n\n")
        if on_complete:
            on_complete(True)
        return

    if not shutil.which("sshfs"):
        log_callback("[ERRORE] 'sshfs' non risulta installato sul sistema. Esegui: sudo apt install sshfs\n\n")
        if on_complete:
            on_complete(False)
        return

    remote_target = f"{config.NAS_USER}@{config.NAS_IP}:{config.NAS_REMOTE_HOME}"
    cmd = ["sshfs", remote_target, mount_point] + config.SSHFS_OPTIONS
    log_callback(f"[INFO] Avvio montaggio SFTP verso {remote_target} su {mount_point}...\n")
    execute_cmd_async(cmd, log_callback, on_complete)


def start_sftp_unmount(log_callback, on_complete=None):
    """Smonta la directory SFTP locale tramite fusermount."""
    mount_point = config.LOCAL_MOUNT_POINT

    if not is_sftp_mounted():
        log_callback(f"[INFO] Nessun mount attivo rilevato su: {mount_point}\n\n")
        if on_complete:
            on_complete(True)
        return

    fusermount_bin = "fusermount3" if shutil.which("fusermount3") else "fusermount"
    cmd = [fusermount_bin, "-u", mount_point]
    log_callback(f"[INFO] Smontaggio SFTP da {mount_point} in corso...\n")
    execute_cmd_async(cmd, log_callback, on_complete)