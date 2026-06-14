import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np


ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


sys.modules["face_recognition"] = SimpleNamespace(
    compare_faces=lambda known, target, tolerance=0.6: [],
    face_distance=lambda known, target: np.array([]),
    face_encodings=lambda image, known_face_locations=None: [],
    face_locations=lambda image: [],
)
