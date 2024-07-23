from rdkit import Chem

def substructure_search(mols, mol):
    
    substructure = Chem.MolFromSmiles(mol) #convering into smiles
    matched_molecules = [] #storing matches here
    for smiles in mols: #iterating through the given list
        molecule = Chem.MolFromSmiles(smiles)
        if molecule.HasSubstructMatch(substructure): 
            matched_molecules.append(smiles)
    return matched_molecules


