# Vers. 3.0.1
#!/usr/bin/env bash
set -e

# Configurazione endpoint e share NFS (personalizzare con i parametri della propria rete)
NAS_HOST="${NAS_HOST:-nas.local}" # oppure indirizzo IP, es. 192.168.1.50
MOUNT_BASE="${HOME}/NFS_Shares"

# Creazione delle directory locali se non presenti
mkdir -p "${MOUNT_BASE}/Backup"
mkdir -p "${MOUNT_BASE}/Data"
mkdir -p "${MOUNT_BASE}/Media"

# Montaggio dei volumi NFS tramite privilegi sudo
sudo mount -t nfs "${NAS_HOST}:/export/BACKUP" "${MOUNT_BASE}/Backup"
sudo mount -t nfs "${NAS_HOST}:/export/DATA" "${MOUNT_BASE}/Data"
sudo mount -t nfs "${NAS_HOST}:/export/MEDIA" "${MOUNT_BASE}/Media"

echo "[SUCCESS] Tutte le unita NFS sono state montate correttamente in ${MOUNT_BASE}."
