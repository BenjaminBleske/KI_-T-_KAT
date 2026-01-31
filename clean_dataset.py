import os

# --- KONFIGURATION ---
DIR_PREVIEW = "annotated_previews"
DIR_TRAINING = "raw_training_data"

def cleanup_and_health_check():
    if not os.path.exists(DIR_PREVIEW) or not os.path.exists(DIR_TRAINING):
        print("Fehler: Einer der Ordner wurde nicht gefunden.")
        return

    # --- PHASE 1: Synchronisation mit dem Vorschau-Ordner ---
    # Wir holen uns alle Namen der Bilder, die du behalten hast
    keep_names = {os.path.splitext(f)[0] for f in os.listdir(DIR_PREVIEW) if f.endswith(".jpg")}
    
    print(f"--- Phase 1: Synchronisation ---")
    print(f"Bilder im Kontroll-Ordner: {len(keep_names)}")

    all_training_files = os.listdir(DIR_TRAINING)
    sync_removed = 0

    for filename in all_training_files:
        base_name = os.path.splitext(filename)[0]
        if base_name not in keep_names:
            os.remove(os.path.join(DIR_TRAINING, filename))
            sync_removed += 1
    
    print(f"Synchronisation abgeschlossen. {sync_removed} Dateien entfernt.")

    # --- PHASE 2: Health-Check (Orphan-Suche) ---
    print(f"\n--- Phase 2: Health-Check ---")
    
    # Aktuellen Stand im Trainingsordner neu einlesen
    current_training_files = os.listdir(DIR_TRAINING)
    jpg_names = {os.path.splitext(f)[0] for f in current_training_files if f.endswith(".jpg")}
    txt_names = {os.path.splitext(f)[0] for f in current_training_files if f.endswith(".txt")}

    orphan_removed = 0

    # 1. Prüfe auf Bilder ohne TXT
    for name in jpg_names:
        if name not in txt_names:
            os.remove(os.path.join(DIR_TRAINING, f"{name}.jpg"))
            print(f"Gelöscht: {name}.jpg (Label-Datei fehlte)")
            orphan_removed += 1

    # 2. Prüfe auf TXT-Dateien ohne Bild
    for name in txt_names:
        if name not in jpg_names:
            os.remove(os.path.join(DIR_TRAINING, f"{name}.txt"))
            print(f"Gelöscht: {name}.txt (Bilddatei fehlte)")
            orphan_removed += 1

    if orphan_removed == 0:
        print("Health-Check bestanden: Alle Paare sind vollständig.")
    else:
        print(f"Health-Check beendet: {orphan_removed} verwaiste Dateien (Orphans) bereinigt.")

    print("\nDein Datensatz ist jetzt bereit für das Training!")

if __name__ == "__main__":
    cleanup_and_health_check()
