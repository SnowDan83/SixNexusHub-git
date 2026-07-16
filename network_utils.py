#Vers. 2.0.0
import subprocess
import threading
import os
import config

def run_script_async(script_path, log_callback, success_message="Operazione completata."):
    """
    Esegue uno script .sh in un thread separato per non bloccare la GUI di CustomTkinter,
    reindirizzando l'output (stdout/stderr) in tempo reale alla textbox dei log.
    """
    def target():
        if not os.path.exists(script_path):
            log_callback(f"❌ ERRORE: Lo script '{os.path.basename(script_path)}' non esiste in BASE_DIR.")
            return

        log_callback(f"⏳ Avvio script: {os.path.basename(script_path)}...")
        try:
            # Popen esegue il processo in background e unisce stdout/stderr
            process = subprocess.Popen(
                [script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Leggiamo l'output riga per riga e lo inviamo alla GUI
            for line in process.stdout:
                log_callback(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                log_callback(f"✅ SUCCESS: {success_message}")
            else:
                log_callback(f"❌ ERRORE: Lo script è terminato con codice di uscita {process.returncode}.")
        except Exception as e:
            log_callback(f"💥 ERRORE CRITICO: {str(e)}")

    # Avviamo il thread demone per non tenere appeso il processo principale alla chiusura dell'app
    threading.Thread(target=target, daemon=True).start()

# --- FUNZIONI DI INTERFACCIA CON IL MAIN ---

def start_mount(log_callback):
    """Monta i volumi di rete NFS usando mount.sh"""
    run_script_async(config.SCRIPT_MOUNT, log_callback, "Volumi NFS montati correttamente.")

def start_unmount(log_callback):
    """Smonta i volumi di rete NFS usando unmount.sh"""
    run_script_async(config.SCRIPT_UNMOUNT, log_callback, "Volumi NFS smontati correttamente.")

def start_vpn_connect(log_callback):
    """Avvia la VPN usando vpn_start.sh"""
    run_script_async(config.SCRIPT_VPN_START, log_callback, "Connessione VPN avviata.")

def start_vpn_disconnect(log_callback):
    """Scollega la VPN usando vpn_stop.sh"""
    run_script_async(config.SCRIPT_VPN_STOP, log_callback, "Connessione VPN interrotta.")
