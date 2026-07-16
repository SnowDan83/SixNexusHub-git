# Vers. 2.0.0
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import subprocess
import threading
import webbrowser
from PIL import Image, ImageTk

# Importiamo i nostri moduli locali
import config
import network_utils
import backup_utils

class ControlCenterApp(ctk.CTk):
    def __init__(self):
        # --- FIX ICONA SULLA DOCK GNOME/WAYLAND ---
        super().__init__(className="SixNexusHub")

        self.title(f"SixNexus Hub - [{config.AMB_NAME}]")
        self.geometry("1100x800")
        self.resizable(True, True)
        
        # Inizializziamo il riferimento al processo del server AI
        self.unsloth_process = None
        
        # 2. Caricamento e Resize dinamico dell'icona (Anti-Crash X11)
        icon_path = os.path.join(config.BASE_DIR, "icon.png")
        if os.path.exists(icon_path):
            try:
                img_high_res = Image.open(icon_path)
                img_scaled = img_high_res.resize((64, 64), Image.Resampling.LANCZOS)
                icon_final = ImageTk.PhotoImage(img_scaled)
                self.iconphoto(True, icon_final)
            except Exception as e:
                print(f"ATTENZIONE: Impossibile caricare l'icona della finestra - {e}")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # --- FIX SCALING DISPLAY AD ALTA DENSITÀ ---
        ctk.set_widget_scaling(config.UI_SCALE)
        ctk.set_window_scaling(config.UI_SCALE)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Schede comuni a entrambi gli ambienti
        self.tab_net = self.tab_view.add("📁 Gestione Rete")
        self.tab_git = self.tab_view.add("🚀 Gestore Git")
        self.tab_bkp = self.tab_view.add("💾 Gestione Backup")
        
        # --- LOGICA ENVIRONMENT-AWARE PER UNSLOTH ---
        # Crea la scheda solo se siamo sul Desktop CachyOS
        if config.AMB_NAME == "CACHYOS":
            self.tab_unsloth = self.tab_view.add("🦥 Server Unsloth")

        # Inizializza gestore backup
        self.bkp_manager = backup_utils.BackupManager()
        self.bkp_action_buttons = []

        # Rendering delle schede
        self.setup_network_tab()
        self.setup_git_tab()
        self.setup_backup_tab()
        
        # Inizializza il layout di Unsloth solo se la scheda esiste
        if config.AMB_NAME == "CACHYOS":
            self.setup_unsloth_tab()

    # -----------------------------------------------------------------
    # SEZIONE RETE
    # -----------------------------------------------------------------
    def setup_network_tab(self):
        self.tab_net.grid_columnconfigure(0, weight=1)
        self.tab_net.grid_rowconfigure(3, weight=1)

        vpn_frame = ctk.CTkFrame(self.tab_net)
        vpn_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        vpn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(vpn_frame, text="Connessione Tailscale VPN", font=("Roboto Medium", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 0))
        ctk.CTkButton(vpn_frame, text="CONNETTI VPN", command=lambda: network_utils.start_vpn_connect(self.log_net), height=40, fg_color="#1F6AA5", hover_color="#144A75").grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        ctk.CTkButton(vpn_frame, text="DISCONNETTI VPN", command=lambda: network_utils.start_vpn_disconnect(self.log_net), height=40, fg_color="#565B5E", hover_color="#3F4345").grid(row=1, column=1, padx=20, pady=15, sticky="ew")

        nfs_frame = ctk.CTkFrame(self.tab_net)
        nfs_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        nfs_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(nfs_frame, text="Volumi di Rete NFS", font=("Roboto Medium", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 0))
        ctk.CTkButton(nfs_frame, text="MONTA VOLUMI", command=lambda: network_utils.start_mount(self.log_net), height=40, fg_color="#2CC985", hover_color="#229A65").grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        ctk.CTkButton(nfs_frame, text="SMONTA VOLUMI", command=lambda: network_utils.start_unmount(self.log_net), height=40, fg_color="#C92C2C", hover_color="#9A2222").grid(row=1, column=1, padx=20, pady=15, sticky="ew")

        self.net_log = ctk.CTkTextbox(self.tab_net, height=220)
        self.net_log.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.net_log.insert("0.0", "Pronto. Centro reti inizializzato...\n")
        self.net_log.configure(state="disabled")

    def log_net(self, message):
        self.net_log.configure(state="normal")
        self.net_log.insert("end", message + "\n")
        self.net_log.see("end")
        self.net_log.configure(state="disabled")

    # -----------------------------------------------------------------
    # SEZIONE GIT (MULTI-REPOSITORY)
    # -----------------------------------------------------------------
    def setup_git_tab(self):
        self.tab_git.grid_columnconfigure(0, weight=1)
        self.tab_git.grid_rowconfigure(5, weight=1)

        self.repo_names = list(config.GIT_REPOS.keys())
        self.current_repo_name = ctk.StringVar(value=self.repo_names[0])
        self.current_git_path = config.GIT_REPOS[self.repo_names[0]]

        selector_frame = ctk.CTkFrame(self.tab_git, fg_color="transparent")
        selector_frame.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        selector_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(selector_frame, text="Repository Selezionato:", font=("Roboto Medium", 14, "bold")).grid(row=0, column=0, padx=(20, 10))
        self.repo_selector = ctk.CTkOptionMenu(selector_frame, values=self.repo_names, variable=self.current_repo_name, command=self.change_git_repo, width=300, fg_color="#1F6AA5", button_color="#144A75")
        self.repo_selector.grid(row=0, column=1, sticky="w")

        self.lbl_repo = ctk.CTkLabel(self.tab_git, text="", font=("Roboto Medium", 16, "bold"))
        self.lbl_repo.grid(row=1, column=0, pady=(15, 2))
        
        self.lbl_branch = ctk.CTkLabel(self.tab_git, text="", text_color="#1F6AA5")
        self.lbl_branch.grid(row=2, column=0, pady=(0, 10))

        git_btn_frame = ctk.CTkFrame(self.tab_git)
        git_btn_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        git_btn_frame.grid_columnconfigure((0,1), weight=1)

        ctk.CTkButton(git_btn_frame, text="1. Stato (Status)", command=self.git_status).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(git_btn_frame, text="2. Scarica (Pull)", command=self.git_pull, fg_color="#D9A000", hover_color="#B88800").grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        commit_frame = ctk.CTkFrame(self.tab_git)
        commit_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        commit_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(commit_frame, text="Messaggio di Commit:").grid(row=0, column=0, padx=10, pady=(5,0), sticky="w")
        self.entry_msg = ctk.CTkEntry(commit_frame, placeholder_text="Aggiornamento codice")
        self.entry_msg.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.entry_msg.insert(0, "Aggiornamento codice")

        ctk.CTkButton(commit_frame, text="ESEGUI COMMIT E PUSH", command=self.git_push_workflow, fg_color="#2CC985", hover_color="#229A65").grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.git_log = ctk.CTkTextbox(self.tab_git, height=180)
        self.git_log.grid(row=5, column=0, padx=20, pady=15, sticky="nsew")
        
        self.change_git_repo(self.repo_names[0])

    def change_git_repo(self, selected_repo_name):
        self.current_git_path = config.GIT_REPOS[selected_repo_name]
        self.git_log.configure(state="normal")
        self.git_log.delete('1.0', 'end')
        self.git_log.configure(state="disabled")

        if os.path.exists(self.current_git_path):
            self.lbl_repo.configure(text=f"Repo: {os.path.basename(self.current_git_path)}")
            self.git_status()
        else:
            self.lbl_repo.configure(text=f"ERRORE: Percorso non trovato")
            self.lbl_branch.configure(text="Branch: Sconosciuto")
            self.log_git(f"ERRORE: La cartella {self.current_git_path} non esiste.")

    def get_current_branch(self):
        try:
            return subprocess.check_output(["git", "branch", "--show-current"], cwd=self.current_git_path).strip().decode('utf-8')
        except:
            return "Sconosciuto"

    def log_git(self, message):
        self.git_log.configure(state="normal")
        self.git_log.insert("end", message + "\n")
        self.git_log.see("end")
        self.git_log.configure(state="disabled")

    def run_git_command(self, command_list):
        cmd_str = " ".join(command_list)
        self.log_git(f"--- Esecuzione: {cmd_str} ---")
        try:
            result = subprocess.run(command_list, capture_output=True, text=True, check=False, cwd=self.current_git_path)
            if result.stdout: self.log_git(result.stdout)
            if result.stderr: self.log_git("INFO/ERR: " + result.stderr)
            return result.returncode == 0
        except Exception as e:
            self.log_git(f"ERRORE CRITICO: {e}")
            return False

    def git_status(self):
        self.git_log.configure(state="normal")
        self.git_log.delete('1.0', 'end')
        self.git_log.configure(state="disabled")
        self.run_git_command(["git", "status"])
        self.lbl_branch.configure(text=f"Branch attuale: {self.get_current_branch()}")

    def git_pull(self):
        self.run_git_command(["git", "pull"])

    def git_push_workflow(self):
        commit_msg = self.entry_msg.get()
        if not commit_msg:
            messagebox.showwarning("Attenzione", "Inserisci un messaggio di commit!")
            return
        threading.Thread(target=self._push_thread, args=(commit_msg,)).start()

    def _push_thread(self, commit_msg):
        self.log_git("\n*** INIZIO PROCEDURA PUSH ***")
        if not self.run_git_command(["git", "add", "."]): return
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.current_git_path).stdout
        if not status:
            self.log_git("Nessuna modifica da committare.")
        else:
            if not self.run_git_command(["git", "commit", "-m", commit_msg]): return

        branch = self.get_current_branch()
        if self.run_git_command(["git", "push", "origin", branch]):
            self.log_git("*** PROCEDURA COMPLETATA CON SUCCESSO ***")
            messagebox.showinfo("Successo", "Codice inviato al repository!")
        else:
            self.log_git("*** ERRORE DURANTE IL PUSH ***")
            messagebox.showerror("Errore", "Impossibile eseguire il Push. Controlla i log.")
        self.git_status()

    # -----------------------------------------------------------------
    # SEZIONE BACKUP
    # -----------------------------------------------------------------
    def setup_backup_tab(self):
        self.tab_bkp.grid_columnconfigure(0, weight=1)
        self.tab_bkp.grid_rowconfigure(3, weight=1)

        jobs_container = ctk.CTkScrollableFrame(self.tab_bkp, height=200)
        jobs_container.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        jobs_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(jobs_container, text=f"Job Configurati per: {config.AMB_NAME}", font=("Roboto Medium", 14, "bold")).grid(row=0, column=0, pady=(5, 10))

        for idx, job in enumerate(config.BACKUP_JOBS):
            job_frame = ctk.CTkFrame(jobs_container, fg_color="#383838")
            job_frame.grid(row=idx+1, column=0, padx=10, pady=5, sticky="ew")
            job_frame.grid_columnconfigure(1, weight=1)

            lbl_name = ctk.CTkLabel(job_frame, text=f"📂 {job['name']}", font=("Roboto", 13, "bold"))
            lbl_name.grid(row=0, column=0, padx=15, pady=10, sticky="w")

            btn_frame = ctk.CTkFrame(job_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=1, sticky="e", padx=10)

            btn_bkp = ctk.CTkButton(btn_frame, text="BACKUP (PC -> NAS)", width=150, fg_color="#287A40", hover_color="#1E5E30",
                                    command=lambda j=job: self.start_rsync_gui("backup", j))
            btn_bkp.pack(side="left", padx=5)
            
            btn_rst = ctk.CTkButton(btn_frame, text="RIPRISTINA (NAS -> PC)", width=150, fg_color="#9C5D00", hover_color="#7A4900",
                                    command=lambda j=job: self.confirm_restore_gui(j))
            btn_rst.pack(side="left", padx=5)

            self.bkp_action_buttons.extend([btn_bkp, btn_rst])

        control_frame = ctk.CTkFrame(self.tab_bkp, fg_color="transparent")
        control_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)

        self.lbl_bkp_status = ctk.CTkLabel(control_frame, text="Pronto", font=("Roboto", 13, "bold"), text_color="#AAAAAA")
        self.lbl_bkp_status.grid(row=0, column=0, sticky="w")

        self.btn_bkp_stop = ctk.CTkButton(control_frame, text="⏹ INTERROMPI PROCESSO", fg_color="#8F1D1D", hover_color="#631313",
                                          state="disabled", command=lambda: self.bkp_manager.stop_process(self.log_bkp))
        self.btn_bkp_stop.grid(row=0, column=1, sticky="e")

        self.bkp_log = ctk.CTkTextbox(self.tab_bkp, height=250, text_color="#00FF00", font=("Consolas", 12))
        self.bkp_log.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.bkp_log.configure(state="disabled")

    def log_bkp(self, message):
        self.after(0, self._insert_bkp_log, message)

    def _insert_bkp_log(self, message):
        self.bkp_log.configure(state="normal")
        self.bkp_log.insert("end", message)
        self.bkp_log.see("end")
        self.bkp_log.configure(state="disabled")

    def confirm_restore_gui(self, job):
        risposta = messagebox.askyesno("Attenzione - Ripristino", 
                                       f"Job: {job['name']}\n\nStai per sovrascrivere i file LOCALI con quelli del NAS.\nSei sicuro di voler procedere?")
        if risposta:
            self.start_rsync_gui("restore", job)

    def start_rsync_gui(self, mode, job):
        for btn in self.bkp_action_buttons:
            btn.configure(state="disabled")
        self.btn_bkp_stop.configure(state="normal")
        text_mode = "BACKUP" if mode == "backup" else "RIPRISTINO"
        color_mode = "#4CAF50" if mode == "backup" else "#FF9800"
        self.lbl_bkp_status.configure(text=f"Esecuzione {text_mode} su '{job['name']}'...", text_color=color_mode)
        self.bkp_manager.start_sync(mode, job, self.log_bkp, self.on_rsync_complete_gui)

    def on_rsync_complete_gui(self, success, reason):
        self.after(0, self._reset_bkp_ui, success, reason)

    def _reset_bkp_ui(self, success, reason):
        for btn in self.bkp_action_buttons:
            btn.configure(state="normal")
        self.btn_bkp_stop.configure(state="disabled")
        if success:
            self.lbl_bkp_status.configure(text="Operazione Completata", text_color="#FFFFFF")
            messagebox.showinfo("Successo", "Operazione terminata correttamente!")
        else:
            self.lbl_bkp_status.configure(text=f"Processo Terminato: {reason}", text_color="#FF5555")
            if "Annullato" not in reason:
                messagebox.showerror("Errore", "Si sono verificati errori o l'operazione è stata interrotta. Controlla i log.")

    # -----------------------------------------------------------------
    # SEZIONE SERVER UNSLOTH (SOLO SU DESKTOP CACHYOS)
    # -----------------------------------------------------------------
    def setup_unsloth_tab(self):
        self.tab_unsloth.grid_columnconfigure(0, weight=1)
        self.tab_unsloth.grid_rowconfigure(2, weight=1)

        ctrl_frame = ctk.CTkFrame(self.tab_unsloth)
        ctrl_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        ctrl_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_start_unsloth = ctk.CTkButton(ctrl_frame, text="▶ AVVIA SERVER", command=self.start_unsloth_server, height=45, fg_color="#287A40", hover_color="#1E5E30")
        self.btn_start_unsloth.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        self.btn_open_unsloth = ctk.CTkButton(ctrl_frame, text="🌐 APRI WEBAPP", command=self.open_unsloth_webapp, height=45, fg_color="#1F6AA5", hover_color="#144A75")
        self.btn_open_unsloth.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        self.btn_stop_unsloth = ctk.CTkButton(ctrl_frame, text="⏹ STOPPA SERVER", command=self.stop_unsloth_server, height=45, fg_color="#8F1D1D", hover_color="#631313", state="disabled")
        self.btn_stop_unsloth.grid(row=0, column=2, padx=15, pady=15, sticky="ew")

        self.lbl_unsloth_status = ctk.CTkLabel(self.tab_unsloth, text="Stato: Server Spento", font=("Roboto", 13, "bold"), text_color="#AAAAAA")
        self.lbl_unsloth_status.grid(row=1, column=0, padx=25, pady=2, sticky="w")

        self.unsloth_log = ctk.CTkTextbox(self.tab_unsloth, height=350, text_color="#00FF00", font=("Consolas", 12))
        self.unsloth_log.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="nsew")
        self.unsloth_log.insert("0.0", "Pronto. Modulo Server Unsloth caricato...\n")
        self.unsloth_log.configure(state="disabled")

    def log_unsloth(self, message):
        """Scrittura thread-safe nell'area di log di Unsloth"""
        self.after(0, self._insert_unsloth_log, message)

    def _insert_unsloth_log(self, message):
        self.unsloth_log.configure(state="normal")
        self.unsloth_log.insert("end", message + "\n")
        self.unsloth_log.see("end")
        self.unsloth_log.configure(state="disabled")

    def start_unsloth_server(self):
        """Avvia il server Unsloth in background senza freezare la GUI"""
        if self.unsloth_process is not None and self.unsloth_process.poll() is None:
            messagebox.showwarning("Attenzione", "Il server Unsloth è già in esecuzione!")
            return

        if not os.path.exists(config.UNSLOTH_CWD):
            messagebox.showerror("Errore", f"La cartella di lavoro specificata non esiste:\n{config.UNSLOTH_CWD}")
            return

        self.log_unsloth("\n--- INIZIO AVVIO SERVER UNSLOTH ---")
        self.lbl_unsloth_status.configure(text="Stato: Avvio in corso...", text_color="#FF9800")
        self.btn_start_unsloth.configure(state="disabled")
        self.btn_stop_unsloth.configure(state="normal")

        try:
            self.unsloth_process = subprocess.Popen(
                config.UNSLOTH_START_CMD,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=config.UNSLOTH_CWD,
                bufsize=1
            )
            threading.Thread(target=self._read_unsloth_stream, daemon=True).start()
        except Exception as e:
            self.lbl_unsloth_status.configure(text="Stato: Errore di avvio", text_color="#FF5555")
            self.btn_start_unsloth.configure(state="normal")
            self.btn_stop_unsloth.configure(state="disabled")
            messagebox.showerror("Errore Critico", f"Impossibile avviare il processo:\n{e}")

    def _read_unsloth_stream(self):
        """Legge continuamente lo stdout del server Unsloth"""
        self.lbl_unsloth_status.configure(text="Stato: Server Attivo", text_color="#2CC985")
        while self.unsloth_process and self.unsloth_process.poll() is None:
            line = self.unsloth_process.stdout.readline()
            if not line:
                break
            self.log_unsloth(line.strip())
        
        self.after(0, self._handle_unsloth_exit)

    def _handle_unsloth_exit(self):
        self.lbl_unsloth_status.configure(text="Stato: Server Spento", text_color="#AAAAAA")
        self.btn_start_unsloth.configure(state="normal")
        self.btn_stop_unsloth.configure(state="disabled")
        self.log_unsloth("--- SERVER TERMINATO ---")
        self.unsloth_process = None

    def open_unsloth_webapp(self):
        """Apre l'URL della WebApp nel browser di sistema"""
        self.log_unsloth(f"Apertura browser su: {config.UNSLOTH_URL}")
        webbrowser.open(config.UNSLOTH_URL)

    def stop_unsloth_server(self):
        """Interrompe in modo pulito il server Unsloth"""
        if self.unsloth_process and self.unsloth_process.poll() is None:
            self.log_unsloth("\n--- RICHIESTA INTERRUZIONE SERVER ---")
            self.unsloth_process.terminate()
            self.unsloth_process = None
        else:
            self._handle_unsloth_exit()

if __name__ == "__main__":
    app = ControlCenterApp()
    app.mainloop()
