#!/usr/bin/env python3
# Vers. 3.1.0
# ==============================================================================
# SixNexus Hub - Central Configuration (Linux Cross-Host)
# Autore: Daniele Sanna (SnowDan83)
# Framework: PySide6 (Qt6) - Cross-Desktop Material Edition (GNOME & KDE)
# ==============================================================================

import os
import socket
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------------------------
# RILEVAMENTO DINAMICO DELL'AMBIENTE E UTENTE CORRENTE
# -----------------------------------------------------------------------------
CURRENT_USER = os.getenv("USER", Path.home().name)
HOSTNAME = socket.gethostname().lower()

# Rilevamento dinamico Notebook vs Desktop tramite hostname o presenza batteria
IS_NOTEBOOK_HOST = any(k in HOSTNAME for k in ["nb", "laptop", "notebook", "portable"])
HAS_BATTERY = os.path.exists("/sys/class/power_supply/BAT0")

IS_DESKTOP = not (IS_NOTEBOOK_HOST or HAS_BATTERY)
AMB_NAME = f"{HOSTNAME.upper()} ({'Desktop' if IS_DESKTOP else 'Notebook'})"

# -----------------------------------------------------------------------------
# GESTIONE REPOSITORY GIT
# -----------------------------------------------------------------------------
GIT_REPOS = {
    "SixNexus Hub": BASE_DIR,
}

# -----------------------------------------------------------------------------
# PARAMETRI RETE E STORAGE NAS REMOTO
# -----------------------------------------------------------------------------
NAS_IP = os.getenv("SIXNEXUS_NAS_IP", "192.168.1.50")
NAS_USER = os.getenv("SIXNEXUS_NAS_USER", CURRENT_USER)
NAS_REMOTE_HOME = os.getenv("SIXNEXUS_NAS_REMOTE_HOME", f"/home/{NAS_USER}")

# Punto di mount locale utente
LOCAL_MOUNT_POINT = os.path.expanduser(os.getenv("SIXNEXUS_MOUNT_POINT", "~/NAS_Home"))

# Opzioni SSHFS per resilienza e modalità non interattiva
SSHFS_OPTIONS = [
    "-o", "reconnect",
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=3",
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=5",
    "-o", "follow_symlinks",
    "-o", "idmap=user"
]

# -----------------------------------------------------------------------------
# GESTIONE JOB DI BACKUP (RSYNC SSH / NFS)
# -----------------------------------------------------------------------------
BACKUP_EXCLUDE_NB = os.path.join(BASE_DIR, "list_nb.txt")
BACKUP_EXCLUDE_DESK = os.path.join(BASE_DIR, "list_desk.txt")
BACKUP_EXCLUDE_OTHER = os.path.join(BASE_DIR, "list_other.txt")

if not IS_DESKTOP:
    # Configurazione Notebook: backup via SSH diretto verso storage NAS
    BACKUP_JOBS = [
        {
            "name": f"Home {CURRENT_USER} (SSH NAS)",
            "source": os.path.expanduser("~"),
            "dest": f"{NAS_USER}@{NAS_IP}:/export/BACKUP/{CURRENT_USER}-NB",
            "exclude": BACKUP_EXCLUDE_NB,
        }
    ]
else:
    # Configurazione Desktop: backup su storage NAS (personalizzabile via ENV)
    DESK_SRC_DATA0 = os.getenv("SIXNEXUS_DESK_SRC0", f"/mnt/Data_00/{CURRENT_USER}")
    DESK_SRC_DATA1 = os.getenv("SIXNEXUS_DESK_SRC1", "/mnt/Data_01/Other Backup")

    BACKUP_JOBS = [
        {
            "name": "Dati Principali (Data_00)",
            "source": DESK_SRC_DATA0,
            "dest": f"{NAS_USER}@{NAS_IP}:/export/BACKUP/{CURRENT_USER}",
            "exclude": BACKUP_EXCLUDE_DESK,
        },
        {
            "name": "Backup Secondario (Data_01)",
            "source": DESK_SRC_DATA1,
            "dest": f"{NAS_USER}@{NAS_IP}:/export/BACKUP/Other Backup",
            "exclude": BACKUP_EXCLUDE_OTHER,
        },
    ]

# -----------------------------------------------------------------------------
# SCRIPT DI RETE ESTERNI (NFS & TAILSCALE)
# -----------------------------------------------------------------------------
SCRIPT_MOUNT = os.path.join(BASE_DIR, "mount.sh")
SCRIPT_UNMOUNT = os.path.join(BASE_DIR, "unmount.sh")
SCRIPT_VPN_START = os.path.join(BASE_DIR, "vpn_start.sh")
SCRIPT_VPN_STOP = os.path.join(BASE_DIR, "vpn_stop.sh")

# -----------------------------------------------------------------------------
# SERVER UNSLOTH AI (DESKTOP ONLY)
# -----------------------------------------------------------------------------
UNSLOTH_BIN = os.path.expanduser("~/.local/bin/unsloth")
UNSLOTH_CMD = [UNSLOTH_BIN, "studio"] if os.path.exists(UNSLOTH_BIN) else ["python3", "-m", "http.server", "8888"]
UNSLOTH_CWD = os.path.expanduser("~")
UNSLOTH_URL = os.getenv("SIXNEXUS_UNSLOTH_URL", "http://localhost:8888")

# -----------------------------------------------------------------------------
# STILE GRAFICO QSS: MATERIAL DARK CROSS-DESKTOP (GNOME & KDE)
# -----------------------------------------------------------------------------
QSS_STYLE = """
/* -------------------------------------------------------------------------
   1. STRUTTURA BASE E FINESTRA PRINCIPALE
   ------------------------------------------------------------------------- */
QMainWindow, QWidget {
    background-color: #16151a;
    color: #e5e1e6;
    font-family: 'Inter', 'Noto Sans', 'Cantarell', 'Ubuntu', sans-serif;
    font-size: 13px;
    outline: none;
}

/* -------------------------------------------------------------------------
   2. SCHEDE DI NAVIGAZIONE A PILLOLA
   ------------------------------------------------------------------------- */
QTabWidget {
    border: 0px solid transparent;
    background: transparent;
    outline: none;
}

QTabWidget::pane {
    border: 0px solid transparent;
    background-color: transparent;
    top: 0px;
    margin: 0px;
    padding: 0px;
}

QTabBar {
    background-color: #201e26;
    border: 0px solid transparent;
    outline: none;
    border-radius: 12px;
    padding: 4px;
}

QTabBar::tab {
    background-color: transparent;
    color: #a5a0ac;
    font-weight: bold;
    padding: 8px 16px;
    margin: 2px;
    border: 0px solid transparent;
    outline: none;
    border-radius: 8px;
    min-height: 24px;
}

/* Scheda attiva */
QTabBar::tab:selected {
    background-color: #6750a4;
    color: #ffffff;
    border: 0px solid transparent;
    outline: none;
}

/* Schede non selezionate */
QTabBar::tab:!selected {
    background-color: transparent;
    color: #a5a0ac;
    border: 0px solid transparent;
    outline: none;
}

QTabBar::tab:hover:!selected {
    background-color: #2b2933;
    color: #e5e1e6;
    border: 0px solid transparent;
    outline: none;
}

/* -------------------------------------------------------------------------
   3. SCHEDE INTERNE E CONTENITORI (CardFrame)
   ------------------------------------------------------------------------- */
QFrame#CardFrame {
    background-color: #222028;
    border: 1px solid #302d38;
    border-radius: 12px;
    padding: 14px;
}

QLabel {
    background-color: transparent;
    color: #e5e1e6;
}

/* -------------------------------------------------------------------------
   4. AREE DI TESTO E INPUT
   ------------------------------------------------------------------------- */
QLineEdit, QComboBox {
    background-color: #222028;
    border: 1px solid #3e3a47;
    border-radius: 8px;
    padding: 7px 12px;
    color: #f2eff4;
    selection-background-color: #6750a4;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #9a82db;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QTextEdit, QTextEdit#LogTerminal {
    background-color: #222028;
    border: 1px solid #302d38;
    border-radius: 10px;
    color: #d6d1db;
    font-family: 'JetBrains Mono', 'Fira Code', 'Ubuntu Mono', monospace;
    font-size: 12px;
    padding: 10px;
}

/* -------------------------------------------------------------------------
   5. PULSANTI COLORATI MATERIAL
   ------------------------------------------------------------------------- */
QPushButton {
    background-color: #443e52;
    color: #ffffff;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    min-height: 22px;
}

QPushButton:hover {
    background-color: #554e66;
}

QPushButton:pressed {
    background-color: #353040;
}

QPushButton:disabled {
    background-color: #26242c;
    color: #635f69;
}

QPushButton#BtnPrimary {
    background-color: #3f6eb5;
    color: #ffffff;
}

QPushButton#BtnPrimary:hover {
    background-color: #4b82d4;
}

QPushButton#BtnPrimary:pressed {
    background-color: #315894;
}

QPushButton#BtnSuccess {
    background-color: #248a52;
    color: #ffffff;
}

QPushButton#BtnSuccess:hover {
    background-color: #2ca462;
}

QPushButton#BtnSuccess:pressed {
    background-color: #1c6d41;
}

QPushButton#BtnDestructive {
    background-color: #a82e38;
    color: #ffffff;
}

QPushButton#BtnDestructive:hover {
    background-color: #c43743;
}

QPushButton#BtnDestructive:pressed {
    background-color: #87232c;
}

QPushButton#BtnWarning {
    background-color: #c4820a;
    color: #16151a;
}

QPushButton#BtnWarning:hover {
    background-color: #e0960d;
}

QPushButton#BtnWarning:pressed {
    background-color: #9e6807;
}

/* -------------------------------------------------------------------------
   6. SCROLLBAR MINIMALISTA
   ------------------------------------------------------------------------- */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #443e52;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6750a4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""