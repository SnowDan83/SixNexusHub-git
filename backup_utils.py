# Vers. 2.0.0
import os
import subprocess
import threading
from datetime import datetime
import config

class BackupManager:
    def __init__(self):
        self.current_process = None
        self.stop_requested = False

    def stop_process(self, log_callback):
        """Interrompe il processo rsync corrente se esiste."""
        if self.current_process:
            self.stop_requested = True
            log_callback("\n!!! RICHIESTA DI INTERRUZIONE INVIATA... !!!\n")
            try:
                self.current_process.terminate()
            except Exception as e:
                log_callback(f"Errore durante l'interruzione: {e}\n")

    def start_sync(self, mode, job, log_callback, on_complete_callback):
        """Avvia il processo di sync in un thread separato."""
        self.stop_requested = False
        threading.Thread(target=self._run_sync_thread, args=(mode, job, log_callback, on_complete_callback)).start()

    def _run_sync_thread(self, mode, job, log_callback, on_complete_callback):
        log_callback(f"\n{'='*15} INIZIO {mode.upper()}: {job['name']} {'='*15}\n")

        local_path = job['local']
        remote_path = job['remote']
        use_ssh = "@" in remote_path

        if mode == "backup":
            src = local_path
            dest = remote_path
        else: # restore
            src = remote_path
            if "NB" in job['name']:
                folder_name = os.path.basename(local_path.rstrip('/'))
                src = f"{remote_path}/{folder_name}/"
            else:
                if not src.endswith("/"):
                    src += "/"
            dest = local_path

        cmd = ["rsync", "-avrh", "--progress", "--delete"]

        # Gestione Esclusioni (Dinamica)
        exclude_file = job.get('exclude_file')
        if exclude_file and os.path.exists(exclude_file):
            log_callback(f"File esclusioni trovato e applicato: {exclude_file}\n")
            cmd.append(f"--exclude-from={exclude_file}")
        elif exclude_file:
            log_callback(f"ATTENZIONE: File esclusioni definito ma NON TROVATO nel percorso: {exclude_file}\n")
        else:
            log_callback("Nessun file di esclusione configurato per questo job.\n")

        if use_ssh:
            cmd.extend(["-e", "ssh"])

        # FIX Sintassi applicato qui!
        cmd.extend([src, dest])
        log_callback(f"Comando: {' '.join(cmd)}\n\n")

        try:
            self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            for line in self.current_process.stdout:
                log_callback(line)

            self.current_process.wait()
            return_code = self.current_process.returncode
            self.current_process = None

            if self.stop_requested:
                 log_callback("\n--- OPERAZIONE ANNULLATA DALL'UTENTE ---\n")
                 on_complete_callback(False, "Annullato")
            elif return_code == 0:
                log_callback(f"\n--- OPERAZIONE COMPLETATA SU {job['name']} ---\n")
                self._write_to_log_file(mode, job['name'])
                on_complete_callback(True, "Successo")
            else:
                log_callback(f"\n--- ERRORE (Codice: {return_code}) ---\n")
                on_complete_callback(False, f"Errore {return_code}")

        except Exception as e:
            log_callback(f"\nERRORE CRITICO: {str(e)}\n")
            self.current_process = None
            on_complete_callback(False, "Exception")

    def _write_to_log_file(self, mode, job_name):
        try:
            os.makedirs(os.path.dirname(config.BACKUP_LOG_FILE), exist_ok=True)
            with open(config.BACKUP_LOG_FILE, "a") as f:
                f.write(f"{datetime.now()} - {mode.upper()} [{job_name}] completato.\n")
        except Exception as e:
             print(f"Impossibile scrivere log su file: {e}")
