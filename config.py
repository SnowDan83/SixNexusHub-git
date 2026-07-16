# Vers. 2.0.0
import os
import socket

# --- FIX PER IL MOUSE GIGANTE (Bug XWayland/GNOME Scaling) ---
os.environ["XCURSOR_SIZE"] = "24"
os.environ["XCURSOR_THEME"] = "Adwaita"

# Identifica la cartella esatta del software
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOSTNAME = socket.gethostname()

# Percorsi relativi per i file di esclusione
EXCLUDE_DESK = os.path.join(BASE_DIR, "list_desk.txt")
EXCLUDE_NB = os.path.join(BASE_DIR, "list_nb.txt")
EXCLUDE_OTHER = os.path.join(BASE_DIR, "list_other.txt")

# Percorsi VPN (Relativi)
SCRIPT_VPN_START = os.path.join(BASE_DIR, "vpn_start.sh")
SCRIPT_VPN_STOP = os.path.join(BASE_DIR, "vpn_stop.sh")

# --- GESTIONE MULTI-REPOSITORY GIT ---
GIT_REPOS = {
    "SixNexus Hub": "PATH/SixNexusHub-git",
    "Git-2": "PATH/Git-2"
}

# --- CONFIGURAZIONE SERVER UNSLOTH ---
# Configurazione bare-metal con percorso assoluto e CWD dinamico
UNSLOTH_START_CMD = ["/home/YOUR_USER/.local/bin/unsloth", "studio", "-p", "8888"]
UNSLOTH_CWD = "/home/YOUR_USER/Unsloth_Project"
UNSLOTH_HF_CACHE = "/home/YOUR_USER/.cache/huggingface"
UNSLOTH_URL = "http://localhost:8888"

# Configurazione dinamica basata sull'host
if "PC1" in HOSTNAME.lower():
    AMB_NAME = "OS"
    UI_SCALE = 2  # <--- Ridimensionamento perfetto per lo schermo del notebook
    
    SCRIPT_MOUNT = os.path.join(BASE_DIR, "mount.sh")
    SCRIPT_UNMOUNT = os.path.join(BASE_DIR, "unmount.sh")
    
    # --- JOB BACKUP NOTEBOOK (1 Solo Job) ---
    BACKUP_JOBS = [
        {
            "id": 0,
            "name": "Backup 3rd",
            "local": "/home/YOUR_USER",
            "remote": "YOUR_USER@IP:PATH",
            "exclude_file": EXCLUDE_NB
        }
    ]
else:
    AMB_NAME = "OS"
    UI_SCALE = 1.0  # <--- Scala nativa per il Desktop
    
    SCRIPT_MOUNT = os.path.join(BASE_DIR, "mount.sh")
    SCRIPT_UNMOUNT = os.path.join(BASE_DIR, "unmount.sh")
    
    # --- JOB BACKUP DESKTOP MULTIPLO (2 Soli Job) ---
    BACKUP_JOBS = [
        {
            "id": 0,
            "name": "Backup 1st",
            "local": "/home/YOUR_USER",
            "remote": "YOUR_USER@IP:PATH",
            "exclude_file": EXCLUDE_DESK
        },
        {
            "id": 1,
            "name": "Backup 2nd",
            "local": "/home/YOUR_USER",
            "remote": "YOUR_USER@IP:PATH",
            "exclude_file": EXCLUDE_DESK
        }
    ]

# Log directory globale per i backup
BACKUP_LOG_FILE = os.path.join(BASE_DIR, "log_rsync", "rsync_backup.log")
