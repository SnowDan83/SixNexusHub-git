# Vers. 3.0.1
#!/usr/bin/env python3
# ==============================================================================
# SixNexus Hub - Network Utilities
# Asynchronous CLI Execution for Tailscale VPN & NFS Mounts
# ==============================================================================

import os
import subprocess
import threading
import config


def execute_cmd_async(cmd, log_callback, on_complete=None):
    """
    Esegue comandi di sistema in un thread separato fornendo lo streaming
    dei log riga per riga alla callback specificata.
    """
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
            log_callback(f"[ECCEZIONE] Errore di esecuzione: {e}\n\n")
            if on_complete:
                on_complete(False)

    threading.Thread(target=_worker, daemon=True).start()


def start_vpn(log_callback):
    """Avvia la VPN Mesh Tailscale tramite script locale o binario nativo."""
    if os.path.exists(config.SCRIPT_VPN_START):
        execute_cmd_async(["bash", config.SCRIPT_VPN_START], log_callback)
    else:
        execute_cmd_async(["tailscale", "up"], log_callback)


def stop_vpn(log_callback):
    """Disconnette la VPN Mesh Tailscale."""
    if os.path.exists(config.SCRIPT_VPN_STOP):
        execute_cmd_async(["bash", config.SCRIPT_VPN_STOP], log_callback)
    else:
        execute_cmd_async(["tailscale", "down"], log_callback)


def start_mount(log_callback):
    """Monta le share NFS tramite script bash dedicato."""
    if os.path.exists(config.SCRIPT_MOUNT):
        execute_cmd_async(["bash", config.SCRIPT_MOUNT], log_callback)
    else:
        log_callback(f"[ERRORE] Script di montaggio non trovato: {config.SCRIPT_MOUNT}\n")


def start_unmount(log_callback):
    """Smonta le share NFS tramite script bash dedicato."""
    if os.path.exists(config.SCRIPT_UNMOUNT):
        execute_cmd_async(["bash", config.SCRIPT_UNMOUNT], log_callback)
    else:
        log_callback(f"[ERRORE] Script di smontaggio non trovato: {config.SCRIPT_UNMOUNT}\n")
