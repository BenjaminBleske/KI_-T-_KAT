# 🐱 Cat-AI: Echtzeit-Erkennung & Datensammler
Dieses Projekt dient der automatisierten Überwachung und Datensammlung für die Katzen Rocky und Scratchy mittels YOLOv8 auf einem Raspberry Pi 5. 

📖 Projektübersicht (3-Teilig)
## 1. test_detecion.py
Das Herzstück des Projekts ist das Skript test_detection.py. Es erfüllt drei Hauptaufgaben:

Live-Überwachung: Verarbeitet einen RTSP-Kamerastream in Echtzeit.

KI-Klassifizierung: Erkennt Katzen und ordnet sie den trainierten Klassen zu.

Daten-Farming: Speichert automatisch neue Bilder inklusive fertiger YOLO-Labels ab, um den Datensatz für zukünftige Trainingsläufe (Fine-Tuning) zu erweitern.


## 2. Datenkuratierungs-Workflow
Um eine hohe Datenqualität für das Modell-Training sicherzustellen, wurde ein effizienter Bereinigungs-Workflow implementiert:

Sichten & Filtern: Nach dem Datensammeln mit test_detection.py werden die Ergebnisse im Ordner annotated_previews begutachtet. „False Positives“ (Fehlerkennungen) oder qualitativ schlechte Bilder werden hier manuell gelöscht.

Synchronisieren: Das Skript clean_dataset.py vergleicht anschließend die Inhalte von annotated_previews mit dem Ordner raw_training_data.

Bereinigen: Alle Bilder und Labels in raw_training_data, die zuvor in den Previews gelöscht wurden, werden vom Skript automatisch entfernt.

## 3. Yolo-Training
Darüber hinaus ist eine Ordnerstruktur mit dem Namen *Training* implementiert. Die kuratierten Fotos aus raw_training_data müssen in Training/yolotraining_folder gemovet werden. Anschließend muss im Verzeichnis das perpare_data.py Skript ausgeführt werden. 
Dann kann man das Training mit den untenstehenden Befehlen starten.
 
    conda create --name yolo8-env python=3.12 -y
    conda activate yolo8-env
    pip install ultralytics

    yolo train data=data.yaml model=yolov8n.pt epochs=90 imgsz=640 device=mps batch=16 workers=8

    oder ein anderes yolo Modell
    conda create --name yolo11-env python=3.12 -y
    conda activate yolo11-env
    pip install ultralytics
    yolo train data=data.yaml model=yolo11s.pt epochs=90 imgsz=640 device=mps batch=16 workers=8

# 🚀 Installation & Start (Raspberry Pi 5) test_detection.py

cd ki_skript
tmux new -s yolo
python -m venv yolo-env
source yolo-env/bin/activate
pip install ultralytics opencv-python
python test_detection.py

zurückholen?: 
tmux attach -t yolo
tmux kill-session -t yolo

# 🚀 Installation & Start (Mac) test_detection.py
conda create --name yolo8-env python=3.12 -y
conda activate yolo8-env
pip install ultralytics
caffeinate -i python test_detection.py

# 🛠 Funktionsweise des Skripts test_detection.py
Das Skript arbeitet in einem hybriden Modus und passt sich seiner Umgebung an:

Headless-Modus (SSH): Erkennt automatisch, wenn kein Monitor angeschlossen ist (z. B. bei einer SSH-Verbindung auf dem Pi) und deaktiviert die grafische Anzeige, um CPU-Ressourcen zu sparen.

Heartbeat-Log: Gibt im Terminal regelmäßig Statusmeldungen aus ("Scan aktiv..."), damit der Betrieb auch ohne Videobild überwacht werden kann.

Intelligentes Speichern (Debouncing): Um Speicherplatz zu sparen, wird nach einer erfolgreichen Erkennung eine Sperrfrist (standardmäßig 5 Sekunden) aktiviert, bevor für dieselbe Katze ein neues Bild gespeichert wird.

# 📂 Ordnerstruktur die durch test_detection.py erstellt wird
Nach dem Start des Skripts werden automatisch zwei Verzeichnisse verwaltet:

Ordner | Inhalt | Zweck
--|--|--|
raw_training_data/ | Saubere .jpg + .txt | Die Rohdaten für das nächste KI-Training.
annotated_previews/ | Bilder mit grünen Boxen | Zur schnellen menschlichen Kontrolle: Hat die KI recht?


## Prozess test_detection.py beenden
tmux kill-session -t yolo

# 🔄 Der Workflow (Kurzzusammenfassung)
Um das Modell immer besser zu machen, folgt das Projekt diesem Kreislauf:

Sammeln: Der Pi lässt das Skript test_detection.py laufen und füllt die Ordner.

Sichten: Du löschst in annotated_previews alle Bilder, die Fehler enthalten (falsche Katze oder Fehlalarm).

Bereinigen: Das Skript clean_dataset.py synchronisiert raw_training_data (löscht die dazugehörigen Labels der entfernten Bilder).

Trainieren: Die sauberen Daten werden für ein neues Training genutzt.

Tipp: Da typischerweise über ssh in den PI connected wird, bietet es sich an die beiden Dateien annotaded_previews und raw_training_data herunterzuladen und anschließend auf dem PI zu löschen. Das hat auch den Vorteil, dass der Raspi nicht so schnell volläuft.

# Konfiguration test_detection.py
Wichtige Parameter am Anfang der test_detection.py:

CONF_THRESHOLD: Ab welcher Sicherheit (z.B. 0.40) soll eine Katze gezählt werden?

MIN_TIME_BETWEEN_SAVES: Zeitabstand zwischen Speicherungen derselben Katze.

SOURCE: Die RTSP-Adresse deiner Kamera.

# Weitere Ordner

Ordner | Zweck |
--|--|
Training/model_trained_on/raw_trainig_data | Rohdaten (Bilder inkl. Labels) für best.pt |
Training/yolotraining_folder | Yolo-Training-Folder: Für ein Training muss der Ordner raw_training_data gefüllt werden, der sich ebenfalls yolotraining_folder befinden muss|

# git push
git status
git add .
git commit -m "Readme-Update"
git push
