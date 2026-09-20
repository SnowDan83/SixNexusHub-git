#!/bin/bash
# Vers. 3.1.0
# ==============================================================================
# SixNexus Hub - Unmount NFS Shares
# ==============================================================================
TARGET_USER="${USER:-$(whoami)}"
USER_HOME="${HOME:-/home/$TARGET_USER}"

DIR_BACKUP="$USER_HOME/NFS_Backup"
DIR_DLNA="$USER_HOME/NFS_DLNA_POOL"

echo "[INFO] Smontaggio volumi NFS per utente $TARGET_USER..."
if mountpoint -q "$DIR_BACKUP"; then
    sudo umount "$DIR_BACKUP"
fi

if mountpoint -q "$DIR_DLNA"; then
    sudo umount "$DIR_DLNA"
fi

echo "[SUCCESS] Smontaggio volumi completato."