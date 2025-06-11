import os
print(f"Current PATH: {os.environ['PATH']}")
os.environ["PATH"] += os.pathsep + "/programs/x86_64-linux/system/sbgrid_bin/"
from rdkit import Chem
from rdkit.Chem import AllChem
import subprocess

# Configuration for docking
vina_config = {
    "center_x": 108.555,
    "center_y": 108.554,
    "center_z": 117.948,
    "size_x": 24,
    "size_y": 20,
    "size_z": 12,
    "exhaustiveness": 8,
    "num_modes": 9,
    "energy_range": 3,
    "cpu": 10,  # Define the number of CPUs to use
    "spacing": 1,
}

def prepare_receptor(receptor_pdb, output_pdbqt):
    """Convert the receptor PDB file to PDBQT format."""
    subprocess.run(["/opt/sbgrid/x86_64-linux/system/sbgrid_bin/prepare_receptor4.py", "-r", receptor_pdb, "-o", output_pdbqt], check=True)

def prepare_ligand(input_file, output_pdbqt):
    """Convert ligand file to PDBQT format."""
    mol = Chem.MolFromMolFile(input_file) or Chem.MolFromMol2File(input_file)
    if mol is None:
        raise ValueError(f"Could not read ligand file: {input_file}")
    
    # Add hydrogens and optimize geometry
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol)
    AllChem.MMFFOptimizeMolecule(mol)
    
    # Write to PDB format
    temp_pdb = input_file.replace(".mol2", ".pdb").replace(".sdf", ".pdb")
    Chem.MolToPDBFile(mol, temp_pdb)
    
    # Use MGLTools to convert to PDBQT
    subprocess.run(["/opt/sbgrid/x86_64-linux/system/sbgrid_bin/prepare_ligand4.py", "-l", temp_pdb, "-o", output_pdbqt], check=True)
    os.remove(temp_pdb)

def dock_ligand_vina(receptor_pdbqt, ligand_pdbqt, output_file, config):
    """Dock a ligand using Vina."""
    
    # Construct vina command
    command = [
        "/programs/x86_64-linux/system/sbgrid_bin/vina",
        "--receptor", receptor_pdbqt,
        "--ligand", ligand_pdbqt,
        "--out", output_file,
        "--center_x", str(config["center_x"]),
        "--center_y", str(config["center_y"]),
        "--center_z", str(config["center_z"]),
        "--size_x", str(config["size_x"]),
        "--size_y", str(config["size_y"]),
        "--size_z", str(config["size_z"]),
        "--exhaustiveness", str(config["exhaustiveness"]),
        "--num_modes", str(config["num_modes"]),
        "--energy_range", str(config["energy_range"]),
        "--cpu", str(config["cpu"]),
        "--spacing", str(config["spacing"]),
    ]

    # Print the command being run
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=True)

def find_ligand_files(ligand_dir):
    """Recursively find all ligand files in the given directory as a generator."""
    for root, _, files in os.walk(ligand_dir):
        for file in files:
            if file.endswith((".mol2", ".sdf")):
                yield os.path.join(root, file)

def process_ligands(ligand_generator, output_dir, receptor_pdbqt, total_count=None):
    """Process ligands using a generator."""
    completed_count = 0
    for idx, ligand_file in enumerate(ligand_generator, start=1):
        output_file = os.path.join(output_dir, os.path.basename(ligand_file).replace(".mol2", "_out.pdbqt").replace(".sdf", "_out.pdbqt"))
        
        # Skip if output already exists
        if os.path.exists(output_file):
            completed_count += 1
            continue

        try:
            ligand_pdbqt = os.path.join(output_dir, os.path.basename(ligand_file).replace(".mol2", ".pdbqt").replace(".sdf", ".pdbqt"))
            prepare_ligand(ligand_file, ligand_pdbqt)
            dock_ligand_vina(receptor_pdbqt, ligand_pdbqt, output_file, vina_config)
            
            completed_count += 1
            remaining_count = total_count - completed_count if total_count else "Unknown"
            print(f"Docking complete for {ligand_file} ({completed_count}/{total_count or '???'} completed, {remaining_count} remaining).")
        except Exception as e:
            print(f"Error processing {ligand_file}: {e}")

def main():
    # Ask user for paths
    ligand_dir = input("Enter the directory containing ligand files (searches recursively): ").strip()
    receptor_file = input("Enter the path to the receptor PDB file: ").strip()
    output_dir = input("Enter the directory to save docking results: ").strip()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    receptor_pdbqt = os.path.join(output_dir, "receptor.pdbqt")
    if not os.path.exists(receptor_pdbqt):
        prepare_receptor(receptor_file, receptor_pdbqt)

    # Prepare ligands generator
    ligand_generator = find_ligand_files(ligand_dir)
    total_ligands = sum(1 for _ in find_ligand_files(ligand_dir))  # Count total ligands
    print(f"Found {total_ligands} ligand files.")

    # Start processing ligands
    process_ligands(ligand_generator, output_dir, receptor_pdbqt, total_ligands)

if __name__ == "__main__":
    main()
