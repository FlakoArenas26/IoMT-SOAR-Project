import time
import subprocess
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURACIÓN ---
LOG_FILE = '/var/log/suricata/eve.json'
# Lista blanca para evitar autobloqueo
WHITELIST_IPS = ['127.0.0.1', 'localhost', '0.0.0.0', '192.168.1.17', '192.168.1.12']

# --- CONFIGURACIÓN DE NOTIFICACIONES ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'serviceiomt@gmail.com'
SENDER_PASSWORD = 'TU_CONTRASEÑA_DE_APLICACION_AQUI'  # <--- OJO: No subir la real a GitHub público

RECIPIENTS = [
    'serviceiomt@gmail.com', 
    'rarenas5@estudiantes.areandina.edu.co',
    'jcastro197@estudiantes.areandina.edu.co',
    'jmaldonado34@estudiantes.areandina.edu.co'
]

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def send_alert_email(ip, attack_type, timestamp, target_service):
    """Envía un correo con diseño HTML estilo reporte SOC"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENTS)
        msg['Subject'] = f'🚨 [IoMT-SOC] Amenaza Bloqueada: {ip}'
        
        # Plantilla HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; background-color: #f4f4f4; }}
                .card {{ background-color: #fff; width: 600px; margin: 20px auto; border-top: 5px solid #d9534f; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 15px; text-align: center; border-radius: 5px; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #333; }}
                .badge {{ background-color: #d9534f; color: white; padding: 5px; border-radius: 4px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class='card'>
                <div class='header'><h2>🏥 IoMT Security Operations</h2></div>
                <br>
                <center><span class='badge'>AMENAZA NEUTRALIZADA (IPS DROP)</span></center>
                <hr>
                <p><span class='label'>📅 Fecha:</span> {timestamp}</p>
                <p><span class='label'>🌍 Atacante:</span> <strong style='color:#d9534f'>{ip}</strong></p>
                <p><span class='label'>🦠 Ataque:</span> {attack_type}</p>
                <p><span class='label'>⚕️ Objetivo:</span> {target_service}</p>
                <p><span class='label'>🛡️ Acción:</span> Bloqueo Permanente (Firewall)</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f'📧 [SOAR] Alerta enviada a {len(RECIPIENTS)} destinatarios.')
    except Exception as e:
        print(f'❌ Error enviando correo: {e}')

def block_ip(ip, attack_type, timestamp, target_service):
    """Ejecuta el bloqueo en IPTABLES y dispara la notificación"""
    if ip in WHITELIST_IPS: return

    # Verificar si ya está bloqueada para no repetir
    try:
        check = subprocess.run(['iptables', '-L', 'INPUT', '-n'], capture_output=True, text=True)
        if ip in check.stdout: return
    except: pass

    print(f'⛔ DETECTADO: {ip} -> BLOQUEANDO...')
    try:
        # Comando de bloqueo
        subprocess.run(['iptables', '-I', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
        
        # Registro local
        with open('/opt/soar/logs/blocked_ips.log', 'a') as f:
            f.write(f'{timestamp} - Blocked: {ip} - {attack_type} -> {target_service}\n')
        
        # Notificación
        send_alert_email(ip, attack_type, timestamp, target_service)
        
    except Exception as e:
        print(f'Error ejecutando bloqueo: {e}')

def monitor():
    """Bucle principal de monitoreo de logs"""
    print('🛡️  SOAR IoMT Monitor v4.0 Iniciado...')
    
    # Esperar a que exista el log
    while not os.path.exists(LOG_FILE):
        time.sleep(1)

    # Leer el log en tiempo real (equivalente a tail -f)
    p = subprocess.Popen(['tail', '-F', LOG_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        if line:
            try:
                line_str = line.decode('utf-8')
                log = json.loads(line_str)
                
                # Procesar alertas o drops
                if log.get('event_type') == 'alert':
                    src_ip = log.get('src_ip')
                    timestamp = log.get('timestamp')
                    alert = log.get('alert', {})
                    attack_type = alert.get('signature', 'Unknown')
                    
                    # Identificación dinámica del servicio atacado
                    dest_port = log.get('dest_port')
                    proto = log.get('proto', '')
                    
                    if dest_port == 5000:
                        target_service = 'Dispositivos Médicos (Puerto 5000)'
                    elif dest_port == 22:
                        target_service = 'Gestión Remota SSH (Puerto 22)'
                    elif 'ICMP' in proto:
                        target_service = 'Infraestructura de Red (ICMP Ping)'
                    else:
                        target_service = f'Puerto Desconocido ({dest_port})'

                    if src_ip: 
                        local_time = get_current_time()
                        block_ip(src_ip, attack_type, local_time, target_service)
            except ValueError:
                continue
            except Exception as e:
                print(f"Error procesando linea: {e}")

if __name__ == '__main__':
    monitor()