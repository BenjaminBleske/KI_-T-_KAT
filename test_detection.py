import cv2
import time
import os
import platform  # Wichtig für die Mac-Erkennung
from ultralytics import YOLO

# --- KONFIGURATION ---
SOURCE = "rtsp://admin:KATZENKI199720192025@192.168.178.150:554/h264Preview_01_main"
DIR_PREVIEW = "annotated_previews"
DIR_TRAINING = "raw_training_data"
CONF_THRESHOLD = 0.80
MIN_TIME_BETWEEN_SAVES = 5 
HEARTBEAT_SECONDS = 10  # Feedback alle 10 Sekunden

# --- INTELLIGENTER GUI-CHECK ---
# Aktiviert das Fenster auf Windows, Mac oder Linux mit Monitor (DISPLAY)
SHOW_GUI = "DISPLAY" in os.environ or os.name == 'nt' or platform.system() == 'Darwin'

# Ordner erstellen
for folder in [DIR_PREVIEW, DIR_TRAINING]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Modell laden
model = YOLO('best.pt')
last_save_time = {}
last_heartbeat_time = time.time()

def main():
    global last_heartbeat_time
    
    print(f"--- KATZEN-SCANNER STARTET ---")
    print(f"System: {platform.system()} ({platform.machine()})")
    print(f"Modus: {'GRAFISCH' if SHOW_GUI else 'HEADLESS (SSH)'}")
    print(f"Feedback: Alle {HEARTBEAT_SECONDS} Sekunden")
    
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

        # --- 10-SEKUNDEN FEEDBACK ---
        if current_time - last_heartbeat_time >= HEARTBEAT_SECONDS:
            print(f"[{time.strftime('%H:%M:%S')}] Info: Scanner läuft stabil...")
            last_heartbeat_time = current_time

        # KI-Erkennung von allen Klassen
        results = model(frame, verbose=False)[0]
        # KI-Erkennung von Scratchy
        # results = model(frame, conf=CONF_THRESHOLD, classes=[2, 3], verbose=False)[0]

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < CONF_THRESHOLD:
                continue

            label = model.names[int(box.cls[0])]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Terminal-Log bei Erkennung
            print(f"[{time.strftime('%H:%M:%S')}] GEFUNDEN: {label} ({conf:.2f})")

            # Speicher-Logik
            if current_time - last_save_time.get(label, 0) > MIN_TIME_BETWEEN_SAVES:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                base_name = f"{label}_{timestamp}"
                
                # A. Bild für Training speichern
                cv2.imwrite(os.path.join(DIR_TRAINING, f"{base_name}.jpg"), frame)
                
                # B. YOLO-Label (.txt) erstellen
                h, w, _ = frame.shape
                x_center = ((x1 + x2) / 2) / w
                y_center = ((y1 + y2) / 2) / h
                bw = (x2 - x1) / w
                bh = (y2 - y1) / h
                
                class_id = int(box.cls[0])
                with open(os.path.join(DIR_TRAINING, f"{base_name}.txt"), 'w') as f:
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n")

                # C. Annotierte Vorschau speichern
                frame_preview = frame.copy()
                cv2.rectangle(frame_preview, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame_preview, f'{label} {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.imwrite(os.path.join(DIR_PREVIEW, f"{base_name}.jpg"), frame_preview)
                
                print(f" >>> GESPEICHERT: {base_name}")
                last_save_time[label] = current_time

        # --- GUI ANZEIGE (Nur wenn SHOW_GUI True ist) ---
        if SHOW_GUI:
            cv2.imshow("KI Test-Monitor", frame)
            # Beenden mit Taste 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            # CPU-Schonung im Headless-Modus (ca. 10ms Pause)
            time.sleep(0.01)

    cap.release()
    if SHOW_GUI:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()