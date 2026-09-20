#!/bin/bash
# Vers. 3.1.0
# ==============================================================================
# SixNexus Hub - Host Provisioning & Dependencies Setup
# ==============================================================================
set -e

echo "[1/4] Aggiornamento sorgenti e installazione pacchetti di sistema..."
sudo apt update
sudo apt install -y python3-pip python3-venv rsync sshfs nfs-common tailscale git fuse3

echo "[2/4] Abilitazione modulo SSHFS per utenti non-root..."
sudo chmod u+s "$(which fusermount3)" || sudo chmod u+s "$(which fusermount)"

echo "[3/4] Installazione librerie Python necessarie..."
pip3 install -r ../requirements.txt || pip3 install --break-system-packages -r ../requirements.txt

echo "[4/4] Creazione directory di lavoro locali..."
mkdir -p "$HOME/NAS_Home" "$HOME/NFS_Backup" "$HOME/NFS_DLNA_POOL" "../log_rsync"
touch "../log_rsync/.gitkeep"

echo "[SUCCESS] Provisioning completato con successo. SixNexus Hub è pronto all'uso."