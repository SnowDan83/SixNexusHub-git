#!/bin/bash
# Vers. 2.0.0

# -------------------------------------------------------------------------
# SCRIPT DI AVVIO TAILSCALE - CENTRO CONTROLLO SVILUPPO
# -------------------------------------------------------------------------

echo "Inizializzazione e connessione a Tailscale Mesh Network..."

# Avvia tailscale configurando il reset dei vecchi flag e l'accettazione delle rotte
sudo tailscale up --reset --accept-routes

# Verifica l'esito del comando
if [ $? -eq 0 ]; then
    echo "SUCCESS: Tailscale attiva. Rotte per la rete locale caricate!"
    echo "Stato attuale:"
    tailscale status | head -n 5
    exit 0
else
    echo "ERRORE: Fallimento durante il 'tailscale up'. Verifica i permessi di sudoers."
    exit 1
fi