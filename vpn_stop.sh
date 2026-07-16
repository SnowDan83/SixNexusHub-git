#!/bin/bash
# Vers. 2.0.0

# -------------------------------------------------------------------------
# SCRIPT DI SPEGNIMENTO TAILSCALE - CENTRO CONTROLLO SVILUPPO
# -------------------------------------------------------------------------

echo "Disconnessione da Tailscale in corso..."

# Smonta l'interfaccia di rete di Tailscale
sudo tailscale down

if [ $? -eq 0 ]; then
    echo "SUCCESS: Tailscale VPN disconnessa con successo."
    exit 0
else
    echo "ERRORE: Impossibile disconnettere Tailscale."
    exit 1
fi