#!/bin/bash
# Vers. 3.1.0
# ==============================================================================
# SixNexus Hub - Mount NFS Shares
# ==============================================================================
set -e

NAS_IP="${SIXNEXUS_NAS_IP:-192.168.1.50}"
TARGET_USER="${USER:-$(whoami)}"
USER_HOME="${HOME:-/home/$TARGET_USER}"

DIR_BACKUP="$USER_HOME/NFS_Backup"
DIR_DLNA="$USER_HOME/NFS_DLNA_POOL"

mkdir -p "$DIR_BACKUP" "$DIR_DLNA"

echo "[INFO] Montaggio condivisioni NFS da $NAS_IP..."
sudo mount -t nfs "$NAS_IP:/BACKUP" "$DIR_BACKUP"
sudo mount -t nfs "$NAS_IP:/export/DLNA" "$DIR_DLNA"
echo "[SUCCESS] Volumi NFS montati correttamente."