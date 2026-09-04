# Vers. 3.0.1
#!/usr/bin/env python3
# ==============================================================================
# SixNexus Hub - Control Center
# Framework: PySide6 (Qt6) - Thread-Safe & Wayland Native
# Repository: https://github.com/SnowDan83/SixNexusHub-git
# ==============================================================================

import sys
import os
import subprocess
import threading
import webbrowser

from PySide6.QtCore import Qt, QObject, Signal, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QTextEdit, QComboBox,
    QLineEdit, QMessageBox, QFrame, QScrollArea
)
from PySide6.QtGui import QIcon

import config
import network_utils
import backup_utils


class AppSignaler(QObject):
    """
    Gestore centralizzato dei segnali Qt.
    Assicura che tutte le modifiche alla GUI e la scrittura dei log avvengano
    esclusivamente all'interno del Main Thread, prevenendo race condition e coredump.
    """
    net_log_signal = Signal(str)
    git_log_signal = Signal(str)
    git_log_clear_signal = Signal()
    bkp_log_signal = Signal(str)
    unsloth_log_signal = Signal(str)

    git_branch_signal = Signal(str)
    git_buttons_signal = Signal(bool)
    bkp_status_signal = Signal(str, str)
    bkp_complete_signal = Signal(bool, str)
    unsloth_status_signal = Signal(str, str, bool, bool)
    dialog_signal = Signal(str, str, str)


class ControlCenterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inizializzazione Signaler Qt
        self.signaler = AppSignaler()
        self._connect_signals()

        # Proprietà Finestra Principale
        self.setWindowTitle(f"SixNexus Hub - [{config.AMB_NAME}]")
        self.resize(1100, 800)
        self.setMinimumSize(850, 600)

        # Icona Applicazione
        icon_path = os.path.join(config.BASE_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Manager di Background
        self.bkp_manager = backup_utils.BackupManager()
        self.bkp_action_buttons = []
        self.unsloth_process = None

        # Widget e Layout Base
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        self.tab_widget = QTabWidget(self)
        self.main_layout.addWidget(self.tab_widget)

        # Inizializzazione delle 4 schede
        self.setup_network_tab()
        self.setup_git_tab()
        self.setup_backup_tab()

        # La scheda server AI viene montata solo su host Desktop
        if getattr(config, "IS_DESKTOP", False):
            self.setup_unsloth_tab()

    def _connect_signals(self):
        """Connette i segnali emessi dai worker thread agli slot eseguiti nel GUI thread."""
        self.signaler.net_log_signal.connect(self._append_net_log)
        self.signaler.git_log_signal.connect(self._append_git_log)
        self.signaler.git_log_clear_signal.connect(self._clear_git_log)
        self.signaler.bkp_log_signal.connect(self._append_bkp_log)
        self.signaler.unsloth_log_signal.connect(self._append_unsloth_log)

        self.signaler.git_branch_signal.connect(self._update_git_branch)
        self.signaler.git_buttons_signal.connect(self._toggle_git_buttons)
        self.signaler.bkp_status_signal.connect(self._update_bkp_status)
        self.signaler.bkp_complete_signal.connect(self._handle_bkp_complete)
        self.signaler.unsloth_status_signal.connect(self._update_unsloth_ui)
        self.signaler.dialog_signal.connect(self._show_dialog)

    # -------------------------------------------------------------------------
    # SCHEDA 1: GESTIONE RETE (VPN & NFS)
    # -------------------------------------------------------------------------
    def setup_network_tab(self):
        tab_net = QWidget()
        layout = QVBoxLayout(tab_net)
        layout.setSpacing(14)

        # Card Tailscale VPN
        vpn_card = QFrame()
        vpn_card.setObjectName("CardFrame")
        vpn_layout = QVBoxLayout(vpn_card)

        lbl_vpn = QLabel("🔒 Connessione VPN Mesh (Tailscale)")
        lbl_vpn.setStyleSheet("font-weight: bold; font-size: 14px;")
        vpn_layout.addWidget(lbl_vpn)

        vpn_btn_layout = QHBoxLayout()
        self.btn_vpn_start = QPushButton("AVVIA VPN")
        self.btn_vpn_start.setStyleSheet("background-color: #3584E4; color: white;")
        self.btn_vpn_start.clicked.connect(lambda: network_utils.start_vpn(self.signaler.net_log_signal.emit))

        self.btn_vpn_stop = QPushButton("DISCONNETTI VPN")
        self.btn_vpn_stop.setStyleSheet("background-color: #E01B24; color: white;")
        self.btn_vpn_stop.clicked.connect(lambda: network_utils.stop_vpn(self.signaler.net_log_signal.emit))

        vpn_btn_layout.addWidget(self.btn_vpn_start)
        vpn_btn_layout.addWidget(self.btn_vpn_stop)
        vpn_layout.addLayout(vpn_btn_layout)
        layout.addWidget(vpn_card)

        # Card Volumi NFS
        nfs_card = QFrame()
        nfs_card.setObjectName("CardFrame")
        nfs_layout = QVBoxLayout(nfs_card)

        lbl_nfs = QLabel("📁 Volumi di Rete NFS")
        lbl_nfs.setStyleSheet("font-weight: bold; font-size: 14px;")
        nfs_layout.addWidget(lbl_nfs)

        nfs_btn_layout = QHBoxLayout()
        self.btn_mount = QPushButton("MONTA VOLUMI")
        self.btn_mount.setStyleSheet("background-color: #2EC27E; color: white;")
        self.btn_mount.clicked.connect(lambda: network_utils.start_mount(self.signaler.net_log_signal.emit))

        self.btn_unmount = QPushButton("SMONTA VOLUMI")
        self.btn_unmount.setStyleSheet("background-color: #C01C28; color: white;")
        self.btn_unmount.clicked.connect(lambda: network_utils.start_unmount(self.signaler.net_log_signal.emit))

        nfs_btn_layout.addWidget(self.btn_mount)
        nfs_btn_layout.addWidget(self.btn_unmount)
        nfs_layout.addLayout(nfs_btn_layout)
        layout.addWidget(nfs_card)

        # Console Log
        lbl_net_log = QLabel("Log Attività Rete:")
        lbl_net_log.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_net_log)

        self.net_log_edit = QTextEdit()
        self.net_log_edit.setReadOnly(True)
        self.net_log_edit.append(f"Pronto. Inizializzato su {config.AMB_NAME}...\n")
        layout.addWidget(self.net_log_edit)

        self.tab_widget.addTab(tab_net, "📁 Gestione Rete")

    # -------------------------------------------------------------------------
    # SCHEDA 2: GESTORE GIT MULTI-REPOSITORY
    # -------------------------------------------------------------------------
    def setup_git_tab(self):
        tab_git = QWidget()
        layout = QVBoxLayout(tab_git)
        layout.setSpacing(12)

        # Selezione Repository
        repo_card = QFrame()
        repo_card.setObjectName("CardFrame")
        repo_layout = QVBoxLayout(repo_card)

        sel_layout = QHBoxLayout()
        lbl_repo = QLabel("Repository:")
        lbl_repo.setStyleSheet("font-weight: bold;")
        self.combo_repos = QComboBox()
        if hasattr(config, "GIT_REPOS") and isinstance(config.GIT_REPOS, dict):
            for name in config.GIT_REPOS.keys():
                self.combo_repos.addItem(name)
        self.combo_repos.currentIndexChanged.connect(self.on_repo_selected)

        self.lbl_branch = QLabel("Branch: rilevamento...")
        self.lbl_branch.setStyleSheet("color: #78AEED; font-weight: bold;")

        sel_layout.addWidget(lbl_repo)
        sel_layout.addWidget(self.combo_repos, 1)
        sel_layout.addWidget(self.lbl_branch)
        repo_layout.addLayout(sel_layout)

        btn_action_layout = QHBoxLayout()
        self.btn_git_status = QPushButton("STATUS REPO")
        self.btn_git_status.clicked.connect(self.run_git_status_async)

        self.btn_git_pull = QPushButton("PULL (AGGIORNA)")
        self.btn_git_pull.setStyleSheet("background-color: #E5A50A; color: black;")
        self.btn_git_pull.clicked.connect(self.run_git_pull_async)

        btn_action_layout.addWidget(self.btn_git_status)
        btn_action_layout.addWidget(self.btn_git_pull)
        repo_layout.addLayout(btn_action_layout)
        layout.addWidget(repo_card)

        # Sezione Commit e Push
        push_card = QFrame()
        push_card.setObjectName("CardFrame")
        push_layout = QVBoxLayout(push_card)

        lbl_push = QLabel("Commit & Sincronizzazione Remota")
        lbl_push.setStyleSheet("font-weight: bold; font-size: 13px;")
        push_layout.addWidget(lbl_push)

        self.txt_commit_msg = QLineEdit()
        self.txt_commit_msg.setPlaceholderText("Inserisci il messaggio di commit...")
        push_layout.addWidget(self.txt_commit_msg)

        self.btn_git_push = QPushButton("ESEGUI COMMIT E PUSH")
        self.btn_git_push.setStyleSheet("background-color: #3584E4; color: white;")
        self.btn_git_push.clicked.connect(self.run_git_push_workflow)
        push_layout.addWidget(self.btn_git_push)

        layout.addWidget(push_card)

        # Log Git
        lbl_git_log = QLabel("Output Operazioni Git:")
        lbl_git_log.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_git_log)

        self.git_log_edit = QTextEdit()
        self.git_log_edit.setReadOnly(True)
        layout.addWidget(self.git_log_edit)

        self.tab_widget.addTab(tab_git, "🚀 Gestore Git")
        self.on_repo_selected()

    def get_current_repo_path(self):
        repo_name = self.combo_repos.currentText()
        if hasattr(config, "GIT_REPOS") and repo_name in config.GIT_REPOS:
            return config.GIT_REPOS[repo_name]
        return config.BASE_DIR

    def on_repo_selected(self):
        repo_path = self.get_current_repo_path()
        self.signaler.git_log_clear_signal.emit()
        self.signaler.git_log_signal.emit(f"[INFO] Repository selezionato: {repo_path}\n")

        def _worker():
            try:
                res = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                branch = res.stdout.strip() if res.returncode == 0 else "N/D"
                self.signaler.git_branch_signal.emit(f"Branch: {branch}")
            except Exception:
                self.signaler.git_branch_signal.emit("Branch: Errore")

        threading.Thread(target=_worker, daemon=True).start()

    def run_git_status_async(self):
        repo_path = self.get_current_repo_path()
        self.signaler.git_log_clear_signal.emit()

        def _worker():
            self.signaler.git_buttons_signal.emit(False)
            try:
                res = subprocess.run(["git", "status"], cwd=repo_path, capture_output=True, text=True)
                self.signaler.git_log_signal.emit(res.stdout if res.returncode == 0 else res.stderr)
            except Exception as e:
                self.signaler.git_log_signal.emit(f"[ERRORE] git status: {e}\n")
            finally:
                self.signaler.git_buttons_signal.emit(True)

        threading.Thread(target=_worker, daemon=True).start()

    def run_git_pull_async(self):
        repo_path = self.get_current_repo_path()
        self.signaler.git_log_clear_signal.emit()

        def _worker():
            self.signaler.git_buttons_signal.emit(False)
            self.signaler.git_log_signal.emit("[INFO] Esecuzione git pull...\n")
            try:
                res = subprocess.run(["git", "pull"], cwd=repo_path, capture_output=True, text=True)
                self.signaler.git_log_signal.emit(res.stdout if res.returncode == 0 else res.stderr)
            except Exception as e:
                self.signaler.git_log_signal.emit(f"[ERRORE] git pull: {e}\n")
            finally:
                self.signaler.git_buttons_signal.emit(True)

        threading.Thread(target=_worker, daemon=True).start()

    def run_git_push_workflow(self):
        commit_msg = self.txt_commit_msg.text().strip()
        if not commit_msg:
            QMessageBox.warning(self, "Attenzione", "Inserisci un messaggio di commit prima di procedere!")
            return

        repo_path = self.get_current_repo_path()
        self.signaler.git_log_clear_signal.emit()

        def _worker():
            self.signaler.git_buttons_signal.emit(False)
            self.signaler.git_log_signal.emit("[1/3] Aggiunta file modificati (git add .)...\n")
            try:
                add_res = subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, text=True)
                if add_res.returncode != 0:
                    self.signaler.git_log_signal.emit(f"[ERRORE ADD]\n{add_res.stderr}\n")
                    self.signaler.dialog_signal.emit("error", "Errore Git", "Fallita l'esecuzione di git add.")
                    return

                self.signaler.git_log_signal.emit(f"[2/3] Creazione commit: '{commit_msg}'...\n")
                commit_res = subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                self.signaler.git_log_signal.emit(commit_res.stdout + "\n")

                if commit_res.returncode != 0 and "nothing to commit" not in commit_res.stdout:
                    self.signaler.git_log_signal.emit(f"[ERRORE COMMIT]\n{commit_res.stderr}\n")
                    self.signaler.dialog_signal.emit("error", "Errore Git", "Fallita la creazione del commit.")
                    return

                self.signaler.git_log_signal.emit("[3/3] Push delle modifiche sul server remoto...\n")
                push_res = subprocess.run(["git", "push"], cwd=repo_path, capture_output=True, text=True)
                self.signaler.git_log_signal.emit(push_res.stdout if push_res.returncode == 0 else push_res.stderr)

                if push_res.returncode == 0:
                    self.signaler.git_log_signal.emit("\n[SUCCESS] Push completato con successo!\n")
                    self.signaler.dialog_signal.emit("info", "Successo", "Commit e Push completati con successo!")
                else:
                    self.signaler.dialog_signal.emit("error", "Errore Push", "Impossibile inviare le modifiche.")
            except Exception as e:
                self.signaler.git_log_signal.emit(f"[ECCEZIONE] {e}\n")
                self.signaler.dialog_signal.emit("error", "Errore", str(e))
            finally:
                self.signaler.git_buttons_signal.emit(True)

        threading.Thread(target=_worker, daemon=True).start()

    # -------------------------------------------------------------------------
    # SCHEDA 3: GESTIONE BACKUP (RSYNC MULTI-THREAD)
    # -------------------------------------------------------------------------
    def setup_backup_tab(self):
        tab_bkp = QWidget()
        layout = QVBoxLayout(tab_bkp)
        layout.setSpacing(12)

        # Header di Stato e Stop
        top_bar = QHBoxLayout()
        self.lbl_bkp_status = QLabel("Stato: Pronto")
        self.lbl_bkp_status.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.btn_bkp_stop = QPushButton("🛑 INTERROMPI PROCESSO")
        self.btn_bkp_stop.setEnabled(False)
        self.btn_bkp_stop.setStyleSheet("background-color: #C01C28; color: white;")
        self.btn_bkp_stop.clicked.connect(self.bkp_manager.stop)

        top_bar.addWidget(self.lbl_bkp_status, 1)
        top_bar.addWidget(self.btn_bkp_stop)
        layout.addLayout(top_bar)

        # Area Job con Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        jobs_container = QWidget()
        jobs_layout = QVBoxLayout(jobs_container)
        jobs_layout.setContentsMargins(0, 0, 0, 0)
        jobs_layout.setSpacing(10)

        self.bkp_action_buttons.clear()
        for job in getattr(config, "BACKUP_JOBS", []):
            card = QFrame()
            card.setObjectName("CardFrame")
            card_layout = QHBoxLayout(card)

            info_layout = QVBoxLayout()
            lbl_job_name = QLabel(job.get("name", "Job"))
            lbl_job_name.setStyleSheet("font-weight: bold; font-size: 13px;")

            src_txt = job.get("source", "")
            dst_txt = job.get("dest", "")
            lbl_job_paths = QLabel(f"<b>Sorgente:</b> {src_txt}<br><b>Destinazione:</b> {dst_txt}")
            lbl_job_paths.setStyleSheet("color: #AAAAAA; font-size: 11px;")

            info_layout.addWidget(lbl_job_name)
            info_layout.addWidget(lbl_job_paths)
            card_layout.addLayout(info_layout, 1)

            btn_bkp = QPushButton("BACKUP")
            btn_bkp.setStyleSheet("background-color: #2EC27E; color: white;")
            btn_bkp.clicked.connect(lambda _, j=job: self.start_backup_op("backup", j))

            btn_rst = QPushButton("RIPRISTINO")
            btn_rst.setStyleSheet("background-color: #E5A50A; color: black;")
            btn_rst.clicked.connect(lambda _, j=job: self.confirm_restore_op(j))

            card_layout.addWidget(btn_bkp)
            card_layout.addWidget(btn_rst)

            self.bkp_action_buttons.extend([btn_bkp, btn_rst])
            jobs_layout.addWidget(card)

        jobs_layout.addStretch(1)
        scroll.setWidget(jobs_container)
        layout.addWidget(scroll, 1)

        # Console Log Rsync
        lbl_bkp_log = QLabel("Log Operazioni Rsync:")
        lbl_bkp_log.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_bkp_log)

        self.bkp_log_edit = QTextEdit()
        self.bkp_log_edit.setReadOnly(True)
        layout.addWidget(self.bkp_log_edit, 1)

        self.tab_widget.addTab(tab_bkp, "💾 Gestione Backup")

    def confirm_restore_op(self, job):
        ans = QMessageBox.question(
            self,
            "Conferma Ripristino",
            f"Job: {job['name']}\n\nStai per sovrascrivere i file locali con i dati dal backup remoto.\nSei sicuro di voler continuare?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            self.start_backup_op("restore", job)

    def start_backup_op(self, mode, job):
        for btn in self.bkp_action_buttons:
            btn.setEnabled(False)
        self.btn_bkp_stop.setEnabled(True)

        mode_text = "BACKUP" if mode == "backup" else "RIPRISTINO"
        color = "#2EC27E" if mode == "backup" else "#E5A50A"
        self.signaler.bkp_status_signal.emit(f"Esecuzione {mode_text} su '{job['name']}'...", color)

        self.bkp_manager.start_sync(
            mode,
            job,
            self.signaler.bkp_log_signal.emit,
            lambda s, r: self.signaler.bkp_complete_signal.emit(s, r)
        )

    # -------------------------------------------------------------------------
    # SCHEDA 4: SERVER UNSLOTH AI (SOLO DESKTOP)
    # -------------------------------------------------------------------------
    def setup_unsloth_tab(self):
        tab_unsloth = QWidget()
        layout = QVBoxLayout(tab_unsloth)
        layout.setSpacing(14)

        ctrl_card = QFrame()
        ctrl_card.setObjectName("CardFrame")
        ctrl_layout = QVBoxLayout(ctrl_card)

        self.lbl_unsloth_status = QLabel("Stato: Server Spento")
        self.lbl_unsloth_status.setStyleSheet("font-weight: bold; font-size: 14px; color: #AAAAAA;")
        ctrl_layout.addWidget(self.lbl_unsloth_status)

        btn_layout = QHBoxLayout()
        self.btn_start_unsloth = QPushButton("AVVIA SERVER AI")
        self.btn_start_unsloth.setStyleSheet("background-color: #3584E4; color: white;")
        self.btn_start_unsloth.clicked.connect(self.start_unsloth_server)

        self.btn_web_unsloth = QPushButton("APRI WEB APP")
        self.btn_web_unsloth.setStyleSheet("background-color: #2EC27E; color: white;")
        self.btn_web_unsloth.clicked.connect(self.open_unsloth_webapp)

        self.btn_stop_unsloth = QPushButton("STOP SERVER")
        self.btn_stop_unsloth.setEnabled(False)
        self.btn_stop_unsloth.setStyleSheet("background-color: #E01B24; color: white;")
        self.btn_stop_unsloth.clicked.connect(self.stop_unsloth_server)

        btn_layout.addWidget(self.btn_start_unsloth)
        btn_layout.addWidget(self.btn_web_unsloth)
        btn_layout.addWidget(self.btn_stop_unsloth)
        ctrl_layout.addLayout(btn_layout)
        layout.addWidget(ctrl_card)

        # Log Server AI
        lbl_ai_log = QLabel("Log Output Server AI:")
        lbl_ai_log.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_ai_log)

        self.unsloth_log_edit = QTextEdit()
        self.unsloth_log_edit.setReadOnly(True)
        layout.addWidget(self.unsloth_log_edit)

        self.tab_widget.addTab(tab_unsloth, "🦥 Server Unsloth")

    def start_unsloth_server(self):
        if self.unsloth_process is not None:
            QMessageBox.information(self, "Info", "Il server è già in esecuzione.")
            return

        cmd = getattr(config, "UNSLOTH_CMD", ["python3", "-m", "http.server", "8000"])
        cwd = getattr(config, "UNSLOTH_CWD", config.BASE_DIR)

        self.signaler.unsloth_log_signal.emit(f"[INFO] Avvio server AI in {cwd}...\n")
        try:
            self.unsloth_process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.signaler.unsloth_status_signal.emit("Stato: Server Attivo", "#2EC27E", False, True)

            def _reader():
                for line in iter(self.unsloth_process.stdout.readline, ''):
                    if line:
                        self.signaler.unsloth_log_signal.emit(line)
                self.unsloth_process.stdout.close()
                self.unsloth_process.wait()
                self.unsloth_process = None
                self.signaler.unsloth_status_signal.emit("Stato: Server Spento", "#AAAAAA", True, False)
                self.signaler.unsloth_log_signal.emit("\n--- SERVER TERMINATO ---\n")

            threading.Thread(target=_reader, daemon=True).start()
        except Exception as e:
            self.signaler.unsloth_log_signal.emit(f"[ERRORE] Impossibile avviare il server: {e}\n")
            self.signaler.unsloth_status_signal.emit("Stato: Errore Avvio", "#E01B24", True, False)

    def open_unsloth_webapp(self):
        webbrowser.open(getattr(config, "UNSLOTH_URL", "http://localhost:8000"))

    def stop_unsloth_server(self):
        if self.unsloth_process and self.unsloth_process.poll() is None:
            self.signaler.unsloth_log_signal.emit("[INFO] Arresto del server in corso...\n")
            self.unsloth_process.terminate()

    # -------------------------------------------------------------------------
    # SLOT PRIVATI (ESECUZIONE NEL MAIN THREAD)
    # -------------------------------------------------------------------------
    @Slot(str)
    def _append_net_log(self, text):
        self.net_log_edit.append(text.strip())

    @Slot(str)
    def _append_git_log(self, text):
        self.git_log_edit.append(text.strip())

    @Slot()
    def _clear_git_log(self):
        self.git_log_edit.clear()

    @Slot(str)
    def _append_bkp_log(self, text):
        self.bkp_log_edit.append(text.strip())

    @Slot(str)
    def _append_unsloth_log(self, text):
        self.unsloth_log_edit.append(text.strip())

    @Slot(str)
    def _update_git_branch(self, text):
        self.lbl_branch.setText(text)

    @Slot(bool)
    def _toggle_git_buttons(self, enabled):
        self.btn_git_status.setEnabled(enabled)
        self.btn_git_pull.setEnabled(enabled)
        self.btn_git_push.setEnabled(enabled)

    @Slot(str, str)
    def _update_bkp_status(self, text, color):
        self.lbl_bkp_status.setText(text)
        self.lbl_bkp_status.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")

    @Slot(bool, str)
    def _handle_bkp_complete(self, success, reason):
        for btn in self.bkp_action_buttons:
            btn.setEnabled(True)
        self.btn_bkp_stop.setEnabled(False)

        if success:
            self._update_bkp_status("Stato: Operazione completata", "#2EC27E")
            QMessageBox.information(self, "Successo", "Sincronizzazione rsync completata con successo!")
        else:
            self._update_bkp_status(f"Stato: {reason}", "#E01B24")
            if "Annullato" not in reason:
                QMessageBox.critical(self, "Errore Backup", f"Errore durante l'operazione:\n{reason}")

    @Slot(str, str, bool, bool)
    def _update_unsloth_ui(self, status_text, color, start_state, stop_state):
        if hasattr(self, "lbl_unsloth_status"):
            self.lbl_unsloth_status.setText(status_text)
            self.lbl_unsloth_status.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
            self.btn_start_unsloth.setEnabled(start_state)
            self.btn_stop_unsloth.setEnabled(stop_state)

    @Slot(str, str, str)
    def _show_dialog(self, msg_type, title, message):
        if msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def closeEvent(self, event):
        """Termina i sottoprocessi alla chiusura della finestra."""
        if self.unsloth_process and self.unsloth_process.poll() is None:
            self.unsloth_process.terminate()
        self.bkp_manager.stop()
        event.accept()


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Identificativi per aggancio coerente alla Dock (GNOME / KDE Wayland)
    app.setApplicationName("sixnexus-hub")
    app.setDesktopFileName("sixnexus-hub")

    # Applicazione Stylesheet
    if hasattr(config, "QSS_STYLE"):
        app.setStyleSheet(config.QSS_STYLE)

    window = ControlCenterApp()
    window.show()
    sys.exit(app.exec())
