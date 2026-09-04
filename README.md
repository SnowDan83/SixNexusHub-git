Markdown
# SixNexus Hub 🚀 3.0.1

**SixNexus Hub** è un centro di controllo grafico avanzato, reattivo e modulare scritto in **Python** e basato su **PySide6 (Qt6)** con design **Adwaita Dark**. Progettato specificamente per workstation Linux (CachyOS, Arch, Ubuntu, Fedora), centralizza la gestione della rete VPN, il montaggio di share NFS, la sincronizzazione asincrona dei backup (rsync) e le operazioni Git multi-repository.

---

## 🛠️ Caratteristiche Principali

* **📁 Gestione Rete & Storage:** Controllo rapido della VPN mesh **Tailscale** e montaggio/smontaggio non bloccante di volumi **NFS** su script asincroni dedicati.
* **🚀 Controller Git Integrato:** Selezione rapida tra molteplici repository locali, lettura immediata del branch attivo, esecuzione di `git status`, `git pull` e workflow automatizzato di commit e push con output in tempo reale.
* **💾 Motore Backup Rsync:** Esecuzione multi-thread di backup incrementali e ripristini con parsing continuo dei log e pulsante di interruzione immediata senza blocco dell'interfaccia.
* **🦥 Integrazione AI (Desktop):** Scheda dedicata per l'avvio, l'arresto e l'apertura rapida dell'interfaccia Web per modelli locali (es. Unsloth AI Studio).

---

## 📦 Requisiti di Sistema

* **Python** >= 3.8
* **rsync** (nel `$PATH` di sistema)
* **tailscale** (per la gestione VPN)
* **git**

### Installazione Dipendenze

#### Tramite ambiente virtuale (consigliato):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Tramite gestori pacchetti di sistema:
Arch / CachyOS: sudo pacman -S python-pyside6 rsync

Fedora: sudo dnf install -y python3-pyside6 rsync

Ubuntu / Debian: sudo apt install -y python3-pyside6 rsync

⚙️ Configurazione e Avvio
Clonare il repository:

Bash
git clone [https://github.com/SnowDan83/SixNexusHub-git.git](https://github.com/SnowDan83/SixNexusHub-git.git)
cd SixNexusHub-git
Rendere eseguibili gli script bash:

Bash
chmod +x *.sh
Personalizzazione parametri (config.py):

Configura i percorsi dei tuoi progetti nel dizionario GIT_REPOS.

Definisci sorgenti, destinazioni ed esclusioni nella lista BACKUP_JOBS.

Configura gli hostname o gli indirizzi IP nei file mount.sh e config.py.

Avvio dell'applicazione:

Bash
python3 main.py
🖥️ Integrazione nel Desktop Environment
Per agganciare l'applicazione alla dock o al menu delle app (GNOME / KDE) senza generare finestre duplicate:

Modifica sixnexus-hub.desktop impostando il percorso assoluto a main.py e icon.png.

Copia il file lanciatore:

Bash
cp sixnexus-hub.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
