# SixNexus Hub 🚀 - # Vers. 1.5

**SixNexus Hub** è un centro di controllo grafico centralizzato ed estremamente efficiente scritto in **Python** e basato su **CustomTkinter**. Progettato specificamente per ambienti Linux avanzati, l'Hub automatizza la gestione delle reti mesh VPN (Tailscale), il montaggio di volumi di rete di tipo NFS, la sincronizzazione rsync multi-thread per backup/ripristino e un modulo integrato di controllo Git.

L'applicazione è nativamente **environment-aware**: analizza l'hostname del sistema per adattare automaticamente la propria interfaccia, i fattori di scaling del display ad alta densità (HiDPI) e i job di backup in base alla distribuzione in uso (es. **Fedora** su Notebook o **CachyOS** su Desktop).

---

## 🗺️ Architettura e Funzionalità Principali

L'applicazione è strutturata in tre sezioni logiche principali, accessibili tramite un'interfaccia a schede fluida e moderna:

### 1. 📁 Gestione Rete
* **Tailscale VPN Integration:** Controllo semplificato del tunnel VPN tramite comandi asincroni dedicati (`tailscale up` con caricamento delle rotte locali e `tailscale down`).
* **NFS Storage Automation:** Script di montaggio e smontaggio dei volumi di rete automatizzati per l'interfacciamento rapido con NAS/Server locali senza bloccare il thread dell'interfaccia utente (UI).

### 2. 💾 Gestione Backup & Restore (`rsync`)
* **Sincronizzazione Avanzata:** Sfrutta la potenza e la precisione di `rsync` applicando i flag `-avrh --progress --delete` per garantire copie mirror perfette.
* **Filtri di Esclusione Dinamici:** Carica ed applica liste di esclusione personalizzate (`.txt`) differenziate per host per evitare il backup di file temporanei o cache.
* **Controllo Runtime Totale:** Possibilità di interrompere immediatamente il processo di copia in esecuzione grazie a un sistema di intercettazione dei processi (`subprocess.Popen.terminate`) completamente sicuro.
* **Log Asincrono in Tempo Reale:** Output dettagliato di `rsync` reindirizzato in una console interna dedicata con salvataggio automatico dello storico dei successi su file di log globale.

### 3. 🚀 Gestore Git Integrato

* **Selezione REPO di Lavoro.
* **Self-Hosting Control:** Consente di monitorare lo stato del codice sorgente dell'hub stesso.
* **Interfaccia Grafica per Git:** Esegue diagnostiche (`git status`), scarica aggiornamenti (`git pull`), organizza l'area di stage ed effettua commit e push (`git push origin main`) direttamente dall'interfaccia grafica.
  > 💡 **Nota di Sicurezza:** Si consiglia di gestire i *Personal Access Tokens (PAT)* tramite variabili d'ambiente (es. file `.env`) per massimizzare la sicurezza.

---

## 📂 Struttura del Progetto

```text
├── main.py            # Entry point dell'applicazione e gestione della GUI (CustomTkinter)
├── config.py          # File di configurazione centralizzato (Scaling, Environment, Parametri Job)
├── backup_utils.py    # Logica di gestione multi-thread dei processi rsync e scrittura log
├── network_utils.py   # Wrapper asincrono per l'esecuzione degli script di rete Shell/Bash
├── mount.sh           # Script bash personalizzabile per il montaggio dei volumi NFS
├── unmount.sh         # Script bash per lo smontaggio dei volumi NFS
├── vpn_start.sh       # Script bash per l'inizializzazione sicura della rete Tailscale
├── vpn_stop.sh        # Script bash per lo spegnimento dell'interfaccia Tailscale
├── icon.png           # Icona dell'applicazione integrata nella Dock di sistema (GNOME/Wayland)
└── .gitignore         # Esclusione automatica di credenziali locali, log e cache di Python
```
### 🛠️ Requisiti di Sistema e Dipendenze

Per poter eseguire correttamente SixNexus Hub, assicuratevi che il vostro sistema Linux disponga dei seguenti componenti:

Dipendenze di Sistema:

* Python >= 3.8
* rsync (installato e configurato nel $PATH)
* tailscale (configurato con permessi amministrativi appropriati o regole sudoers dedicate)

Dipendenze Python:
Si raccomanda l'utilizzo di un ambiente virtuale (venv) per non sporcare i pacchetti di sistema.
Bash

### Creazione e attivazione dell'ambiente virtuale
```Bash
python3 -m venv .venv
source .venv/bin/activate
```
### # Installazione librerie
pip install customtkinter

### 🚀 Configurazione e Installazione

1. Clonare il Repository
```Bash

git clone [https://github.com/SnowDan83/SixNexusHub-git.git](https://github.com/SnowDan83/SixNexusHub-git.git)
cd SixNexusHub-git
```

2. Rendere Eseguibili gli Script Bash
Prima del primo avvio, assicurati che i wrapper di rete abbiano i permessi necessari:
```Bash

chmod +x *.sh
```

3. Configurazione dei File di Esempio
I file di configurazione e gli script contengono segnaposto per garantire la massima privacy e flessibilità. Modifica i file per adattarli alla tua infrastruttura:

* config.py: Configura i percorsi locali (PATH LOCAL), i target remoti (PATH REMOTE) e l'URL del tuo repository Git.
* mount.sh: Sostituisci IP:/Share e PATH/Local-Share-Folder con i dati reali della tua share NFS.


4. Avvio dell'Applicazione

Esegui semplicemente l'entry point principale:
```Bash

python main.py
```

### 🎨 Ottimizzazioni per Ambienti Desktop Professionali

L'applicazione integra nativamente dei fix ingegneristici mirati per superare i problemi noti degli ambienti grafici moderni:

* Fix Mouse Gigante (XWayland/GNOME): Configurazione automatica delle variabili d'ambiente XCURSOR_SIZE e XCURSOR_THEME per evitare lo scaling anomalo del puntatore nei server grafici Wayland.
* HiDPI Dynamic Scaling: Adattamento automatico dei font e delle dimensioni dei widget in base all'ambiente rilevato (Fattore 2.0 su laptop per una leggibilità perfetta, Fattore 1.0 su workstation desktop).
* GNOME Dock Wayland Icon Fix: Assegnazione esplicita della classe dell'istanza dell'app al costruttore per forzare la corretta visualizzazione dell'icona personalizzata sulla barra delle applicazioni di GNOME.
* Gestione nativa Multi Repo GIT
    
    

Autore: Daniele Sanna (SnowDan83)

Licenza: Progetto ad uso personale e di sviluppo libero.
