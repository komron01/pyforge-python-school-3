from fastapi import FastAPI, HTTPException, UploadFile, File
from rdkit import Chem

app = FastAPI()

molecules = dict() 

#Get molecule by identifier
@app.get("/molecules/{identifier}")
def get_molecule(identifier):
    if identifier not in molecules:
        raise HTTPException(status_code=404, detail="molecule not found")
    return {"identifier": identifier, "smiles": molecules[identifier]}

# Add molecule (smiles) and its identifier
@app.post("/add")
def add_molecule(identifier, smiles):
    if identifier in molecules:
        raise HTTPException(status_code=400, detail="molecule identifier already exists")
    molecules[identifier] = smiles
    return {"identifier": identifier, "smiles": smiles}

#Updating a molecule by identifier
@app.put("/molecules/{identifier}")
def update_molecule(identifier, smiles):
    if identifier not in molecules:
        raise HTTPException(status_code=404, detail="molecule not found")
    molecules[identifier] = smiles
    return {"identifier": identifier, "smiles": smiles}

#Delete a molecule by identifier
@app.delete("/molecules/{identifier}")
def delete_molecule(identifier):
    if identifier not in molecules:
        raise HTTPException(status_code=404, detail="molecule not found")
    temp_molecule = molecules[identifier]
    del molecules[identifier]
    return {"detail": temp_molecule + " with identifier "+identifier+" is deleted"}

#List all molecules
@app.get("/molecules/")
def list_molecules():
    if not molecules:
        return {"detail": "no molecules found"}
    return [{"identifier": identifier, "smiles": smiles} for identifier, smiles in molecules.items()]

# @app.post("/molecules/search/")
def substructure_search(mols, mol):

    substructure = Chem.MolFromSmiles(mol) #convering into smiles
    if substructure is None:
        raise ValueError("Invalid substructure SMILES string") # IF WE CAN'T convert into SMILES we'll get exception
    matched_molecules = [] #storing matches here
    for smiles in mols: #iterating through the given list
        molecule = Chem.MolFromSmiles(smiles)
        if molecule is None:
            continue  # Skip invalid SMILES strings
        if molecule.HasSubstructMatch(substructure): 
            matched_molecules.append(smiles)
    return matched_molecules

@app.post("/molecules/search/")
def substructure_search_api(substructure):
    if not molecules:
        return {"detail": "No molecules available for search"}
    matches = substructure_search(list(molecules.values()), substructure)
    matched_identifiers = [
        {"identifier": identifier, "smiles": smiles}
        for identifier, smiles in molecules.items()
        if smiles in matches
    ]
    if not matched_identifiers:
        return {"detail": "No matches found"}
    return matched_identifiers
'''
Uploading the file is little bit complex here.
I'll be using here txt file to upload with the strict format:
identifier:mol
mol1:CCO
mol2:CC(=O)Oc1ccccc1C(=O)O
...
Also, I'm using the async function because I need to make sure that program read the file and only then 
goes further.
'''
async def upload_molecules(file: UploadFile): 
    if file.content_type != 'text/plain':
        raise HTTPException(status_code=400, detail="Invalid file format. Only text files are supported.")
    
    try:
        content = await file.read()
        lines = content.decode('utf-8').splitlines()
        for line in lines:
            if not line.strip():
                continue  # skipping empty lines
            try:
                identifier, smiles = line.split(':')
                if identifier in molecules:
                    continue  # skipping if the molecule identifier already exists
                molecules[identifier.strip()] = smiles.strip()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid file format. Each line must be 'identifier:SMILES'")
        
        return {"detail": "Molecules uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/molecules/upload/")
async def upload_molecules_endpoint(file: UploadFile = File(...)):
    return await upload_molecules(file)