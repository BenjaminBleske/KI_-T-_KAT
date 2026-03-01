mac:
brew install docker 
brew install --cask docker
brew install --cask orbstack

pi:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

chmod -R 777 ./telegram_push
___
#Start
docker compose up -d
docker compose down

--
 🚀 Installation & Start (Raspberry Pi 5) live_scanner.py


tmux new -s yolo2
python -m venv yolo2-env
source yolo2-env/bin/activate
pip install ultralytics opencv-python
python live_scanner.py

zurückholen?: 
tmux attach -t yolo2
tmux kill-session -t yolo2

# 🚀 Installation & Start (Mac) live_scanner.py
conda create --name yolo112-env python=3.12 -y
conda activate yolo112-env
pip install ultralytics
caffeinate -i python live_scanner.py
--

🐾 Projekt: Katzen-KI Live-Scanner (Rocky & Scratchy)
Dieses System nutzt Computer Vision, um spezifische Katzen an einem Scanner zu erkennen und Echtzeit-Benachrichtigungen via Telegram zu versenden.

🏗 Architektur-Übersicht
Das System folgt einem modularen Producer-Consumer-Modell:

Producer (Python/YOLO): Ein schlankes Skript überwacht den RTSP-Stream, erkennt die Katzen und speichert annotierte Bilder (.jpg) lokal ab.

Bridge (Docker-Volumes): Ein gemeinsames Verzeichnis dient als Übergabepunkt zwischen dem Mac/Pi-System und der isolierten n8n-Umgebung.

Consumer (n8n): Eine automatisierte Pipeline prüft minütlich den Ordner, filtert das neueste Bild und sendet es per Telegram an dein Smartphone.

Aktuelle Dateistruktur
ki_skript/
└── n8n_telegram/               # Hauptverzeichnis für die Live-Logik
    ├── docker-compose.yml      # Herzstück der Infrastruktur
    ├── live_scanner.py         # Das neue "Live-Skript" (in Erstellung)
    ├── best.pt                 # Dein trainiertes KI-Modell
    ├── telegram_push/          # Austausch-Ordner (Input für n8n)
    └── n8n_data/               # Datenbank & Einstellungen (Persistent)

🐳 Docker-Konfiguration
Die docker-compose.yml wurde optimiert, um n8n den Zugriff auf lokale Dateien zu erlauben:

Parameter,Wert / Pfad,Zweck
Volume 1,./n8n_data:/home/node/.n8n,Speichert Workflows dauerhaft.
Volume 2,./telegram_push:/home/node/.n8n-files/cat_previews:ro,Spiegelt Bilder in den n8n-Container (Read-Only).
Permissions,N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false,Erlaubt n8n den Zugriff auf externe Verzeichnisse.

⚡ n8n Workflow-Logik
Der Workflow in n8n ist aktuell wie folgt aufgebaut:

Schedule Trigger: Prüft jede Minute (Intervall).

Read/Write Files from Disk: Scannt /home/node/.n8n-files/cat_previews/*.

Sort: Nutzt das Feld fileName (Descending), um das aktuellste Bild nach oben zu schieben.

Limit: Lässt nur das oberste Element (1 Bild) durch.

Telegram: Sendet das Foto via {{ $binary.data }} an deine Chat-ID.
