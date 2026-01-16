#!/bin/bash
# Script de preparación para Modo IPS en IoMT

echo "🛡️ Configurando entorno de red para IPS..."

# 1. Limpiar reglas previas
sudo iptables -F
sudo iptables -X

# 2. Configurar la intercepción (NFQUEUE)
# Todo el tráfico TCP al puerto 5000 se envía a la cola 0 de Suricata
sudo iptables -I INPUT -p tcp --dport 5000 -j NFQUEUE --queue-num 0

echo "✅ Regla NFQUEUE aplicada al puerto 5000."
echo "⚠️  Recuerda ejecutar Suricata con: sudo suricata -c /etc/suricata/suricata.yaml -q 0"