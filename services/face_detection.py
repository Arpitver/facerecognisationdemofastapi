import io

import face_recognition
import numpy as np
from PIL import Image


class FaceError(Exception):
    pass


def load_image(data: bytes) -> np.ndarray:
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise FaceError("Invalid image file")
    return np.array(img)


def get_face_encoding(data: bytes) -> np.ndarray:
    """Image me exactly 1 face honi chahiye, uska 128-d encoding return karta hai."""
    image = load_image(data)
    locations = face_recognition.face_locations(image, model="hog")  # GPU ho to "cnn"

    if len(locations) == 0:
        raise FaceError("No face detected")
    if len(locations) > 1:
        raise FaceError("multiple faces are present")

    return face_recognition.face_encodings(image, known_face_locations=locations)[0]
