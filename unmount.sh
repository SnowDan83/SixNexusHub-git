# Vers. 3.0.1
#!/usr/bin/env bash

MOUNT_BASE="${HOME}/NFS_Shares"

# Smontaggio lazy (-l) per prevenire blocchi di sistema in caso di latenza o disconnessione di rete
sudo umount -l "${MOUNT_BASE}/Backup" 2>/dev/null || true
sudo umount -l "${MOUNT_BASE}/Data" 2>/dev/null || true
sudo umount -l "${MOUNT_BASE}/Media" 2>/dev/null || true

echo "[SUCCESS] Tutte le unita NFS sono state smontate correttamente."
