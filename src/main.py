from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .schema import Drug, SessionLocal, DrugResponse, DrugAdd

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/add")
def add_molecule(molecule: DrugAdd, db: Session = Depends(get_db)):
    db_molecule = db.query(Drug).filter(Drug.name == molecule.name).first()
    if db_molecule:
        raise HTTPException(status_code=400, detail="Molecule identifier already exists")
    new_molecule = Drug(name=molecule.name, smiles=molecule.smiles)
    db.add(new_molecule)
    db.commit()
    db.refresh(new_molecule)
    return DrugResponse(id=new_molecule.id, name=new_molecule.name, smiles=new_molecule.smiles)

@app.get("/molecules/{identifier}")
def get_molecule(identifier: int, db: Session = Depends(get_db)):
    molecule = db.query(Drug).filter(Drug.id == identifier).first()
    if not molecule:
        raise HTTPException(status_code=404, detail="Molecule not found")
    return DrugResponse(id=molecule.id, name=molecule.name, smiles=molecule.smiles)

@app.put("/molecules/{identifier}")
def update_molecule(identifier: int, molecule: DrugAdd, db: Session = Depends(get_db)):
    db_molecule = db.query(Drug).filter(Drug.id == identifier).first()
    if not db_molecule:
        raise HTTPException(status_code=404, detail="Molecule not found")
    db_molecule.name = molecule.name
    db_molecule.smiles = molecule.smiles
    db.commit()
    return DrugResponse(id=db_molecule.id, name=db_molecule.name, smiles=db_molecule.smiles)

@app.delete("/molecules/{identifier}")
def delete_molecule(identifier: int, db: Session = Depends(get_db)):
    db_molecule = db.query(Drug).filter(Drug.id == identifier).first()
    if not db_molecule:
        raise HTTPException(status_code=404, detail="Molecule not found")
    db.delete(db_molecule)
    db.commit()
    return {"detail": f"Molecule with identifier {identifier} is deleted"}

@app.get("/molecules/")
def list_molecules(db: Session = Depends(get_db)):
    molecules = db.query(Drug).all()
    return [DrugResponse(id=molecule.id, name=molecule.name, smiles=molecule.smiles) for molecule in molecules]
