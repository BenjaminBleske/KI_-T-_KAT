import cv2
import time
import os
import platform  # Wichtig für die Mac-Erkennung
from ultralytics import YOLO

# --- KONFIGURATION ---
SOURCE = "rtsp://admin:KATZENKI199720192025@192.168.178.150:554/h264Preview_01_main"
DIR_PUSH = "telegram_push"  # Unser neuer Übergabe-Ordner
CONF_THRESHOLD = 0.80
MIN_TIME_BETWEEN_SAVES = 60 # Auf 60s erhöht, um n8n-Spam zu vermeiden
HEARTBEAT_SECONDS = 10  # Feedback alle 10 Sekunden

# --- INTELLIGENTER GUI-CHECK ---
SHOW_GUI = "DISPLAY" in os.environ or os.name == 'nt' or platform.system() == 'Darwin'

# Nur den Push-Ordner erstellen
if not os.path.exists(DIR_PUSH):
    os.makedirs(DIR_PUSH)

# Modell laden
model = YOLO('best.pt')
last_save_time = {}
last_heartbeat_time = time.time()
frame_count = 0  # Counter für FPS-Berechnung

def main():
    global last_heartbeat_time, frame_count
    
    print(f"--- KATZEN-SCANNER LIVE-MODUS ---")
    print(f"System: {platform.system()} ({platform.machine()})")
    print(f"Modus: {'GRAFISCH' if SHOW_GUI else 'HEADLESS (SSH/Pi)'}")
    print(f"Ziel: {DIR_PUSH}")
    
    cap = cv2.VideoCapture(SOURCE)

    if not cap.isOpened():
        print(f"FEHLER: Kamera-Stream konnte nicht geöffnet werden.")
        return

    while True:
        success, frame = cap.read()
        current_time = time.time()
        
        # Reconnect-Logik bei Verbindungsverlust
        if not success or frame is None:
            print(f"[{time.strftime('%H:%M:%S')}] Verbindung verloren. Reconnect in 5s...")
            time.sleep(5)
            cap = cv2.VideoCapture(SOURCE)
            continue

        # Frame zählen
        frame_count += 1

        # --- 10-SEKUNDEN FEEDBACK MIT FPS ---
        if current_time - last_heartbeat_time >= HEARTBEAT_SECONDS:
            elapsed = current_time - last_heartbeat_time
            fps = frame_count / elapsed
            print(f"[{time.strftime('%H:%M:%S')}] Info: Scanner läuft stabil bei {fps:.2f} FPS")
            
            # Reset für nächsten Intervall
            last_heartbeat_time = current_time
            frame_count = 0

        # KI-Erkennung
        results = model(frame, verbose=False)[0]

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < CONF_THRESHOLD:
                continue

            label = model.names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Terminal-Log bei Erkennung
            print(f"[{time.strftime('%H:%M:%S')}] GEFUNDEN: {label} ({conf:.2f})")

            # Speicher-Logik (Nur annotierte Vorschau für n8n)
            if current_time - last_save_time.get(label, 0) > MIN_TIME_BETWEEN_SAVES:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                base_name = f"{label}_{timestamp}"
                
                # Annotierte Vorschau erstellen
                frame_preview = frame.copy()
                cv2.rectangle(frame_preview, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame_preview, f'{label} {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # --- AB HIER ANPASSEN ---
                
                # 1. Erstmal ALLES im Ordner löschen (Aufräumen)
                # Das sorgt dafür, dass n8n immer nur EINE Datei sieht.
                for f in os.listdir(DIR_PUSH):
                    if f.endswith(".jpg"):
                        try:
                            os.remove(os.path.join(DIR_PUSH, f))
                        except Exception as e:
                            print(f"Fehler beim Aufräumen: {e}")

                # 2. Jetzt erst das neue Bild speichern
                save_path = os.path.join(DIR_PUSH, f"{base_name}.jpg")
                cv2.imwrite(save_path, frame_preview)
                
                print(f" >>> TELEGRAM-BILD BEREITGESTELLT: {base_name}")
                last_save_time[label] = current_time

        if SHOW_GUI:
            cv2.imshow("KI Live-Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            time.sleep(0.01)

    cap.release()
    if SHOW_GUI:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
