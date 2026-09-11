from PIL import Image, ImageDraw
import io, time
from app.ml.pest.pest_model_loader import load_pest_yolo
from app.ml.pest.pest_registry import primary_pest_spec

spec = primary_pest_spec()
t0 = time.time()
model, names, arch, load_s = load_pest_yolo(spec.model_id)
t1 = time.time()
img = Image.new("RGB", (640, 640), (40, 120, 40))
d = ImageDraw.Draw(img)
d.ellipse((200, 200, 400, 400), fill=(80, 60, 40))
path = "/tmp/_e2e_pest.jpg"
img.save(path, format="JPEG")
res = model.predict(path, conf=0.25, verbose=False)
t2 = time.time()
boxes = res[0].boxes
n = 0 if boxes is None else len(boxes)
print(
    f"REAL_PEST_SMOKE model={spec.model_id} arch={arch} classes={len(names)} "
    f"load_s={load_s} wall_load_s={t1-t0:.2f} infer_s={t2-t1:.2f} detections={n}"
)
if n == 0:
    print("REAL MODEL EXECUTED — ZERO DETECTIONS")
else:
    print("detections_present")
