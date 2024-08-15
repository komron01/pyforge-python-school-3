import pytest
from fastapi.testclient import TestClient
from src.main import app  
from rdkit import Chem

client = TestClient(app)

def test_add_molecule():
    #checking add method 
    response = client.post("/add", params={"identifier": "test_mol1", "smiles": "CCO"})
    assert response.status_code == 200
    assert response.json() == {"identifier": "test_mol1", "smiles": "CCO"}

    #deleting after checking for adding 
    delete_response = client.delete("/molecules/test_mol1")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"detail": "CCO with identifier test_mol1 is deleted"}

def test_substructure_search_found():
    #checking for substructre function 
    client.post("/add", params={"identifier": "test_mol2", "smiles": "CCO"})
    client.post("/add", params={"identifier": "test_mol3", "smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    client.post("/add", params={"identifier": "test_mol4", "smiles": "C1CC1"})

    response = client.post("/molecules/search/", params={"substructure": "CCO"})
    assert response.status_code == 200
    #as long as CCO is part of CC(=O)Oc1ccccc1C(=O)O it should return both of the molecules
    assert response.json() == [
        {"identifier": "test_mol2", "smiles": "CCO"},
        {"identifier": "test_mol3", "smiles": "CC(=O)Oc1ccccc1C(=O)O"}
    ]
    client.delete("/molecules/test_mol4")


def test_substructure_search_not_found():
    response = client.post("/molecules/search/", params={"substructure": "C1CC1"})
    assert response.status_code == 200
    assert response.json() == {"detail": "No matches found"}

def test_substructure_search_invalid_smiles():
    response = client.post("/molecules/search/", json={"substructure": "Invalid_SMILES"})
    assert response.status_code == 422  # the response once we get unfamiliar molecule (invalid)
    assert "detail" in response.json()

def test_upload_molecules():
    '''
    While we checked for CRUD operations which is part of business logic (IMO), also
    here is additional checking for file upload testing
    '''
    # upload testing 
    from io import BytesIO
    file_content = b"test_mol5:CCN\n" #creating molecule in the txt to upload 
    file = BytesIO(file_content)
    file.name = 'test_molecules.txt'
    
    response = client.post("/molecules/upload/", files={"file": file})
    assert response.status_code == 200
    assert response.json() == {"detail": "Molecules uploaded successfully"}
    
    # looking for out molecule 
    response = client.get("/molecules/test_mol5")
    assert response.status_code == 200
    assert response.json() == {"identifier": "test_mol5", "smiles": "CCN"}

