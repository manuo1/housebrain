#!/bin/bash
# Installation et configuration de Redis
if ! command -v redis-server &> /dev/null; then
    sudo apt-get install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    echo "Redis installé et démarré."
else
    echo "Redis est déjà installé."
fi

# Vérification du service
if systemctl is-active --quiet redis-server; then
    echo "Redis est actif."
else
    echo "Redis n'a pas démarré correctement."
fi
