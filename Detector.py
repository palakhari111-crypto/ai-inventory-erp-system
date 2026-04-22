"""
detector.py — YOLOv8 object detection + count with annotated output
Falls back to a mock detector if ultralytics / torch is not available.
"""

import io
import base64
import collections
from PIL import Image, ImageDraw, ImageFont

# ─── Try to load real YOLOv8 ──────────────────────────────────────────────────
_yolo_available = False
_model = None

try:
    from ultralytics import YOLO
    import torch
    _model = YOLO("yolov8n.pt")   # nano – downloads once (~6 MB)
    _yolo_available = True
except Exception:
    pass


# ─── COCO colour palette ──────────────────────────────────────────────────────
_PALETTE = [
    "#FF6B6B","#FFD93D","#6BCB77","#4D96FF","#C77DFF",
    "#FF9A3C","#00C9A7","#F72585","#4CC9F0","#7B2D8B",
    "#FF595E","#FFCA3A","#8AC926","#1982C4","#6A4C93",
    "#F4A261","#2A9D8F","#E76F51","#264653","#A8DADC",
]

def _color_for(label: str) -> str:
    idx = sum(ord(c) for c in label) % len(_PALETTE)
    return _PALETTE[idx]


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ─── Real YOLO detection ──────────────────────────────────────────────────────

def _detect_real(image_bytes: bytes, image_name: str, conf: float = 0.35):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = _model(img, conf=conf, verbose=False)[0]

    counts: dict[str, int] = collections.Counter()
    boxes_info = []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label  = results.names[cls_id]
        conf_v = float(box.conf[0])
        xyxy   = box.xyxy[0].tolist()
        counts[label] += 1
        boxes_info.append((label, conf_v, xyxy))

    annotated = _draw_boxes(img, boxes_info)
    return dict(counts), _img_to_b64(annotated)


# ─── Mock detection (when YOLO unavailable) ───────────────────────────────────

_MOCK_CLASSES = ["person","car","bottle","chair","cup","laptop",
                 "book","cell phone","dog","cat","bicycle","apple"]

import random

def _detect_mock(image_bytes: bytes, image_name: str):
    """
    Deterministic-ish fake detector so the UI works without GPU/torch.
    Uses image byte-sum as seed so same image always gives same result.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    seed = sum(image_bytes[:512]) if len(image_bytes) >= 512 else sum(image_bytes)
    rng  = random.Random(seed)

    n_classes = rng.randint(2, 5)
    chosen    = rng.sample(_MOCK_CLASSES, min(n_classes, len(_MOCK_CLASSES)))
    counts    = {c: rng.randint(1, 4) for c in chosen}

    # Draw fake bounding boxes
    w, h   = img.size
    boxes  = []
    for label, cnt in counts.items():
        for _ in range(cnt):
            x1 = rng.randint(0, w - 80)
            y1 = rng.randint(0, h - 80)
            x2 = min(x1 + rng.randint(60, 160), w)
            y2 = min(y1 + rng.randint(60, 140), h)
            conf_v = round(rng.uniform(0.50, 0.95), 2)
            boxes.append((label, conf_v, [x1, y1, x2, y2]))

    annotated = _draw_boxes(img, boxes)
    return counts, _img_to_b64(annotated)


# ─── Drawing helper ───────────────────────────────────────────────────────────

def _draw_boxes(img: Image.Image, boxes):
    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_conf  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font_label = ImageFont.load_default()
        font_conf  = font_label

    for label, conf_v, xyxy in boxes:
        x1, y1, x2, y2 = [int(v) for v in xyxy]
        hex_col = _color_for(label)
        rgb     = _hex_to_rgb(hex_col)

        # Box fill (semi-transparent) + border
        draw.rectangle([x1, y1, x2, y2],
                       fill=rgb + (30,), outline=rgb + (255,), width=2)

        # Label background
        text = f" {label} {conf_v:.0%} "
        bbox = draw.textbbox((x1, y1 - 22), text, font=font_label)
        draw.rectangle([bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2],
                       fill=rgb + (230,))
        draw.text((x1, y1 - 22), text, fill=(255, 255, 255), font=font_label)

    return img


def _img_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


# ─── Public API ───────────────────────────────────────────────────────────────

def detect(image_bytes: bytes, image_name: str, conf: float = 0.35):
    """
    Returns:
        counts (dict[str, int])  — {class_name: count, …}
        annotated_b64 (str)      — base64-encoded JPEG with drawn boxes
        is_real (bool)           — True if real YOLOv8 was used
    """
    if _yolo_available and _model is not None:
        counts, b64 = _detect_real(image_bytes, image_name, conf)
        return counts, b64, True
    else:
        counts, b64 = _detect_mock(image_bytes, image_name)
        return counts, b64, False


def yolo_status() -> dict:
    return {
        "available": _yolo_available,
        "model": "YOLOv8n (COCO)" if _yolo_available else "Mock detector (install ultralytics for real YOLO)",
    }
