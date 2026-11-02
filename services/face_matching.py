import json
from typing import List, Optional, Tuple

import face_recognition
import numpy as np

from models import Person

TOLERANCE = 0.5  # 0.6 default; kam = strict


def encoding_to_json(enc: np.ndarray) -> str:
    return json.dumps(enc.tolist())


def json_to_encoding(s: str) -> np.ndarray:
    return np.array(json.loads(s))


def find_best_match(
    unknown: np.ndarray, persons: List[Person]
) -> Tuple[Optional[Person], Optional[float]]:
    if not persons:
        return None, None

    known = [json_to_encoding(p.encoding) for p in persons]
    distances = face_recognition.face_distance(known, unknown)
    best = int(np.argmin(distances))
    best_distance = float(distances[best])

    if best_distance <= TOLERANCE:
        return persons[best], best_distance
    return None, best_distance
