import os
import uuid
from typing import List

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db
from services.face_detection import FaceError, get_face_encoding
from services.face_matching import encoding_to_json, find_best_match

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Face Recognition API")


@app.post("/register", response_model=schemas.PersonOut)
async def register(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    data = await file.read()
    try:
        encoding = get_face_encoding(data)
    except FaceError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        f.write(data)

    person = models.Person(name=name, encoding=encoding_to_json(encoding), image_path=path)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@app.post("/recognize", response_model=schemas.RecognizeResult)
async def recognize(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = await file.read()
    try:
        unknown = get_face_encoding(data)
    except FaceError as e:
        raise HTTPException(status_code=400, detail=str(e))

    persons = db.query(models.Person).all()
    person, distance = find_best_match(unknown, persons)

    if person is None:
        return schemas.RecognizeResult(matched=False, distance=distance)

    return schemas.RecognizeResult(
        matched=True,
        person_id=person.id,
        name=person.name,
        distance=round(distance, 4),
        confidence=round((1 - distance) * 100, 2),
    )


@app.get("/persons", response_model=List[schemas.PersonOut])
def list_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


@app.delete("/persons/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.get(models.Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.image_path and os.path.exists(person.image_path):
        os.remove(person.image_path)
    db.delete(person)
    db.commit()
    return {"deleted": person_id}
