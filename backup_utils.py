#!/usr/bin/env python3
# Vers. 3.1.0
# ==============================================================================
# SixNexus Hub - Backup Engine (Rsync Multi-Thread via SSH/NFS)
# ==============================================================================

import os
import subprocess
import threading
import time


class BackupManager:
    def __init__(self):
        self.process = None
        self._stop_requested = False

    def start_sync(self, mode, job, log_callback, on_complete):
        self._stop_requested = False
        thread = threading.Thread(
            target=self._run_sync_thread,
            args=(mode, job, log_callback, on_complete),
            daemon=True
        )
        thread.start()

    def _run_sync_thread(self, mode, job, log_callback, on_complete):
        src = job.get("source", "")
        dst = job.get("dest", "")

        if mode == "restore":
            src, dst = dst, src

        src_cmd = src if src.endswith("/") else src + "/"

        if ":" not in dst:
            os.makedirs(dst, exist_ok=True)

        cmd = [
            "rsync",
            "-avrh",
            "--delete",
            "--stats",
            "-e",
            "ssh -o BatchMode=yes -o ConnectTimeout=10"
        ]

        exclude_file = job.get("exclude")
        if exclude_file and os.path.exists(exclude_file):
            cmd.append(f"--exclude-from={exclude_file}")
        elif exclude_file:
            log_callback(f"[WARNING] File esclusioni non trovato: {exclude_file} (proseguo senza)\n")

        cmd.extend([src_cmd, dst])

        log_callback(f"[INFO] Avvio operazione {mode.upper()}...\n")
        log_callback(f"[SORGENTE] {src}\n")
        log_callback(f"[DESTINAZIONE] {dst}\n")
        log_callback(f"[COMANDO] {' '.join(cmd)}\n\n")

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            buffer = []
            while True:
                if self._stop_requested:
                    break
                char = self.process.stdout.read(1)
                if not char:
                    break

                if char in ('\r', '\n'):
                    line = "".join(buffer).strip()
                    if line:
                        log_callback(line + "\n")
                    buffer = []
                else:
                    buffer.append(char)

            if buffer:
                line = "".join(buffer).strip()
                if line:
                    log_callback(line + "\n")

            self.process.stdout.close()
            return_code = self.process.wait()

            if self._stop_requested:
                log_callback("\n[ANNULLATO] Processo interrotto dall'utente.\n")
                on_complete(False, "Annullato")
            elif return_code == 0:
                log_callback("\n[SUCCESS] Operazione rsync completata con successo.\n")
                on_complete(True, "Completato")
            elif return_code == 255:
                log_callback("\n[ERRORE SSH] Impossibile autenticarsi. Verifica le chiavi SSH sul NAS.\n")
                on_complete(False, "Errore SSH")
            else:
                log_callback(f"\n[ERRORE] Rsync terminato con codice {return_code}.\n")
                on_complete(False, f"Errore Rsync ({return_code})")

        except Exception as e:
            log_callback(f"\n[ECCEZIONE] Errore esecuzione: {e}\n")
            on_complete(False, str(e))
        finally:
            self.process = None

    def stop(self):
        """Interrompe il processo rsync."""
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                time.sleep(0.4)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception:
                pass