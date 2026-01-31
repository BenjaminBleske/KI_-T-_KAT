Nachdem man den raw_training_data Ordner mit den finalen Bildern gefüllt hat, muss man das perpare_data.py Skript straten. Dann kann man das Training mit (s.u.) starten.
 

conda create --name yolo8-env python=3.12 -y
conda activate yolo11-env
pip install ultralytics

yolo detect train data=data.yaml model=yolov8n.pt epochs=90 imgsz=640




