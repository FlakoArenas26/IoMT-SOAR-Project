# Sistema SOAR para Protección de Infraestructura IoMT

Este repositorio contiene el código fuente y las configuraciones para la implementación de un sistema **SOAR (Security Orchestration, Automation and Response)** Host-Based, diseñado para proteger dispositivos médicos (IoMT) contra ciberataques.

## 📋 Descripción

El sistema integra **Suricata (IPS)** y **Python** para detectar y bloquear amenazas en tiempo real, garantizando la continuidad operativa de dispositivos críticos como bombas de infusión y monitores de signos vitales.

## 🚀 Funcionalidades

* **Prevención de Fuga de Datos (DLP):** Bloqueo de Inyección SQL en puerto 5000 (Modo IPS Inline).
* **Protección contra Fuerza Bruta:** Detección de patrones de ataque en SSH (Puerto 22).
* **Anti-DoS:** Mitigación de inundaciones ICMP (Ping Flood).
* **Notificaciones:** Alertas automáticas vía Email con reporte forense.

## 🛠️ Tecnologías

* **Motor IDS/IPS:** Suricata 7.0
* **Automatización:** Python 3
* **Firewall:** Iptables + NFQUEUE
* **Simulación:** Flask (Python)

## 👥 Autores

* Rafael José Arenas Restrepo
* Johnatan Castro Hernández
* José Enrique Maldonado Parra
