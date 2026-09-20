<!-- # Vers. 3.1.0 -->
# SixNexus Hub

Control Center cross-host sviluppato in **PySide6 (Qt6)** con design **Material Dark Pro** per la gestione centralizzata di backup Rsync atomici, repository Git, mount di rete (NFS e SFTP/SSHFS) e tunnel VPN Tailscale tra workstation Desktop e Notebook Ubuntu.

## Requisiti di Sistema

* **OS:** Ubuntu Linux 22.04 LTS o superiore
* **Python:** 3.10 o successivo
* **Pacchetti di sistema:**
  ```bash
  sudo apt update
  sudo apt install -y python3-pip rsync sshfs nfs-common tailscale git fuse3
---

## 📦 Requisiti di Sistema

* **Python** >= 3.8
* **rsync** (nel `$PATH` di sistema)
* **tailscale** (per la gestione VPN)
* **git**

##Installazione Rapida
Clona il repository:

##Bash
git clone [https://github.com/tuo-utente/SixNexusHub-git.git](https://github.com/tuo-utente/SixNexusHub-git.git)
cd SixNexusHub-git
Esegui il provisioning dell'host:

##Bash
chmod +x Provisioning/setup.sh *.sh main.py
cd Provisioning && ./setup.sh && cd ..
(Opzionale) Configura le credenziali di rete:

##Bash
cp Provisioning/credentials.env.example Provisioning/credentials.env

##Variabili d'Ambiente Supportate
È possibile personalizzare l'hub senza modificare il codice sorgente:

* SIXNEXUS_NAS_IP: Indirizzo IP dello storage NAS (Default: 192.168.1.50)

* SIXNEXUS_NAS_USER: Utente SSH/SFTP del NAS (Default: $USER locale)

* SIXNEXUS_MOUNT_POINT: Percorso locale del mount SFTP (Default: ~/NAS_Home)

* SIXNEXUS_DESK_SRC0: Sorgente Data 0 Desktop (Default: /mnt/Data_00/$USER)

* SIXNEXUS_DESK_SRC1: Sorgente Data 1 Desktop (Default: /mnt/Data_01/Other Backup)

##Esecuzione
Avvia il control center:

##Bash
python3 main.py
