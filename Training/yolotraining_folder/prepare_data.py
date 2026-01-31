import os
import random
import shutil
from pathlib import Path

# --- KONFIGURATION ---
# Nutzt das Verzeichnis, in dem dieses Skript liegt
BASE_DIR = Path(__file__).parent
RAW_DATA_PATH = BASE_DIR / "raw_training_data"
DEST_PATH = BASE_DIR / "YOLO_Dataset"

def split_data(train_ratio=0.8):
    # Prüfen, ob der Quellordner überhaupt existiert
    if not RAW_DATA_PATH.exists():
        print(f"❌ FEHLER: Der Ordner '{RAW_DATA_PATH}' wurde nicht gefunden!")
        print("Stelle sicher, dass das Skript im selben Verzeichnis wie 'raw_training_data' liegt.")
        return

    # Unterordner für YOLO erstellen
    for split in ['train', 'val']:
        (DEST_PATH / 'images' / split).mkdir(parents=True, exist_ok=True)
        (DEST_PATH / 'labels' / split).mkdir(parents=True, exist_ok=True)

    # Alle Bilder finden (.jpg)
    images = [f for f in os.listdir(RAW_DATA_PATH) if f.lower().endswith('.jpg')]
    
    if not images:
        print("⚠️ Keine .jpg Bilder im Quellordner gefunden.")
        return

    # Mischen für Zufallsauswahl
    random.shuffle(images)

    # Index für den Split berechnen
    split_idx = int(len(images) * train_ratio)
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    def move_files(files, split):
        count = 0
        for img_name in files:
            # Passende Textdatei (.txt) suchen
            label_name = img_name.rsplit('.', 1)[0] + '.txt'
            
            src_img = RAW_DATA_PATH / img_name
            src_label = RAW_DATA_PATH / label_name
            
            # Nur kopieren, wenn Bild UND Label existieren
            if src_label.exists():
                shutil.copy(src_img, DEST_PATH / 'images' / split / img_name)
                shutil.copy(src_label, DEST_PATH / 'labels' / split / label_name)
                count += 1
        return count

    # Kopiervorgang starten
    train_count = move_files(train_images, 'train')
    val_count = move_files(val_images, 'val')

    print("-" * 30)
    print(f"✅ Erfolg! Datensatz wurde erstellt.")
    print(f"📍 Ziel: {DEST_PATH}")
    print("-" * 30)
    
    # Kleine Übersichtstabelle in der Konsole
    print(f"{'Split':<10} | {'Bilder':<10}")
    print(f"{'-'*11}+{'-'*11}")
    print(f"{'Train':<10} | {train_count:<10}")
    print(f"{'Validation':<10} | {val_count:<10}")
    print("-" * 30)

if __name__ == "__main__":
    split_data()