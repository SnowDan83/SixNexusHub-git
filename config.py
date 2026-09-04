# Vers. 3.0.1
#!/usr/bin/env python3
# ==============================================================================
# SixNexus Hub - Central Configuration (Linux Cross-Host)
# Repository: https://github.com/SnowDan83/SixNexusHub-git
# ==============================================================================

import os
import socket
import shutil

# -----------------------------------------------------------------------------
# PERCORSI BASE DEL PROGETTO
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_HOME = os.path.expanduser("~")
CURRENT_USER = os.environ.get("USER", "user")

# -----------------------------------------------------------------------------
# RILEVAMENTO DINAMICO DELL'AMBIENTE (NOTEBOOK VS DESKTOP)
# -----------------------------------------------------------------------------
HOSTNAME = socket.gethostname().lower()

# Verifica pattern host tipici dei laptop o installazioni notebook
IS_NOTEBOOK_HOST = any(k in HOSTNAME for k in ["nb", "notebook", "laptop", "ubuntu", "fedora"])
HAS_BATTERY = os.path.exists("/sys/class/power_supply/BAT0")

# Se non ha batteria e non corrisponde a pattern notebook, è considerato Desktop
IS_DESKTOP = not (IS_NOTEBOOK_HOST or HAS_BATTERY)
AMB_NAME = f"{socket.gethostname()} ({'Desktop' if IS_DESKTOP else 'Notebook'})"

# -----------------------------------------------------------------------------
# GESTIONE REPOSITORY GIT
# -----------------------------------------------------------------------------
# Dizionario con "Nome Visualizzato": "Percorso Locale"
GIT_REPOS = {
    "SixNexus Hub": BASE_DIR,
    # Aggiungi qui gli altri repository locali, es.:
    # "Altro Progetto": os.path.join(USER_HOME, "Sviluppo", "AltroProgetto"),
}

# -----------------------------------------------------------------------------
# GESTIONE JOB DI BACKUP (RSYNC SSH / NFS)
# -----------------------------------------------------------------------------
BACKUP_EXCLUDE_NB = os.path.join(BASE_DIR, "list_nb.txt")
BACKUP_EXCLUDE_DESK = os.path.join(BASE_DIR, "list_desk.txt")
BACKUP_EXCLUDE_OTHER = os.path.join(BASE_DIR, "list_other.txt")

# Placeholder configurabili per la connessione remota (sostituire con i propri dati)
NAS_HOST = "nas.local"  # oppure IP es. "192.168.1.50"
NAS_BACKUP_ROOT = "/export/BACKUP"

if not IS_DESKTOP:
    # Configurazione Notebook: backup incrementale della Home via SSH
    BACKUP_JOBS = [
        {
            "name": "Home Notebook (SSH NAS)",
            "source": USER_HOME,
            "dest": f"{CURRENT_USER}@{NAS_HOST}:{NAS_BACKUP_ROOT}/Notebook_Backup",
            "exclude": BACKUP_EXCLUDE_NB,
        }
    ]
else:
    # Configurazione Desktop: backup su mount point locali (NFS)
    BACKUP_JOBS = [
        {
            "name": "Dati Principali (Data_00)",
            "source": "/mnt/Data_00/Data",
            "dest": "/mnt/NFS_Backup/Desktop_Data00",
            "exclude": BACKUP_EXCLUDE_DESK,
        },
        {
            "name": "Backup Secondario (Data_01)",
            "source": "/mnt/Data_01/Other_Backup",
            "dest": "/mnt/NFS_Backup/Desktop_Data01",
            "exclude": BACKUP_EXCLUDE_OTHER,
        },
    ]

# -----------------------------------------------------------------------------
# SCRIPT DI RETE (NFS & TAILSCALE)
# -----------------------------------------------------------------------------
SCRIPT_MOUNT = os.path.join(BASE_DIR, "mount.sh")
SCRIPT_UNMOUNT = os.path.join(BASE_DIR, "unmount.sh")
SCRIPT_VPN_START = os.path.join(BASE_DIR, "vpn_start.sh")
SCRIPT_VPN_STOP = os.path.join(BASE_DIR, "vpn_stop.sh")

# -----------------------------------------------------------------------------
# SERVER UNSLOTH AI (ABILITATO SOLO SU DESKTOP)
# -----------------------------------------------------------------------------
UNSLOTH_BIN = shutil.which("unsloth") or os.path.join(USER_HOME, ".local", "bin", "unsloth")
UNSLOTH_CMD = [UNSLOTH_BIN, "studio"] if os.path.exists(UNSLOTH_BIN) else ["python3", "-m", "http.server", "8000"]
UNSLOTH_CWD = USER_HOME
UNSLOTH_URL = "http://localhost:8000"

# -----------------------------------------------------------------------------
# TEMA GRAFICO QSS (ADWAITA / GNOME DARK)
# -----------------------------------------------------------------------------
QSS_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Cantarell', 'Inter', 'Ubuntu', sans-serif;
    font-size: 13px;
    outline: none;
}

QTabWidget {
    border: none;
    outline: none;
}

QTabWidget::pane {
    border: 1px solid #333333;
    border-radius: 8px;
    background-color: #1e1e1e;
    top: -1px;
}

QTabBar {
    border: none;
    outline: none;
    qproperty-drawBase: 0;
}

QTabBar::tab {
    background-color: #2b2b2b;
    color: #a0a0a0;
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #3584e4;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #383838;
    color: #ffffff;
}

QFrame#CardFrame {
    background-color: #272727;
    border: 1px solid #383838;
    border-radius: 8px;
    padding: 12px;
}

QPushButton {
    background-color: #383838;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 22px;
}

QPushButton:hover {
    background-color: #484848;
}

QPushButton:pressed {
    background-color: #222222;
}

QPushButton:disabled {
    background-color: #242424;
    color: #666666;
}

QLineEdit, QComboBox {
    background-color: #141414;
    border: 1px solid #383838;
    border-radius: 6px;
    padding: 6px 10px;
    color: #ffffff;
    selection-background-color: #3584e4;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #3584e4;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QTextEdit {
    background-color: #121214;
    border: 1px solid #2d2d30;
    border-radius: 6px;
    color: #c0c0c0;
    font-family: 'JetBrains Mono', 'Fira Code', 'Ubuntu Mono', monospace;
    font-size: 12px;
    padding: 8px;
}

QScrollBar:vertical {
    background: #1e1e1e;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #383838;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #484848;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
