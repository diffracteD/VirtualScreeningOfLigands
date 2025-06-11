import os
import csv

def extract_binding_energy_and_molecule_name(pdbqt_file):
    """Extract the best binding energy and molecule name from a Vina docking output file."""
    energy = None
    molecule_name = None

    try:
        with open(pdbqt_file, 'r') as file:
            for line in file:
                if line.startswith("REMARK VINA RESULT"):
                    # Extract the energy value
                    energy = float(line.split()[3])
                elif line.startswith("REMARK") and "ZINC" in line:
                    # Extract the molecule name starting with ZINC
                    parts = line.split()
                    molecule_name = next((part for part in parts if part.startswith("ZINC")), None)
                
                # Stop if both energy and molecule name are found
                if energy is not None and molecule_name is not None:
                    break

        if molecule_name is None:
            molecule_name = "Unknown"  # Fallback if molecule name is not found

    except Exception as e:
        print(f"Error reading {pdbqt_file}: {e}")

    return molecule_name, energy

def parse_docking_results(output_dir, csv_file):
    """Parse all docking output files and save results to a CSV file, sorted by energy."""
    results = []

    # Iterate through all .pdbqt files in the output directory
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith("_out.pdbqt"):
                pdbqt_file = os.path.join(root, file)
                molecule_name, energy = extract_binding_energy_and_molecule_name(pdbqt_file)
                
                if energy is not None:
                    results.append({
                        "Molecule Name": molecule_name,
                        "PDBQT File": file,
                        "Binding Energy (kcal/mol)": energy
                    })
                else:
                    print(f"Could not extract energy from {pdbqt_file}")

    # Sort results in descending order of binding energy
    results.sort(key=lambda x: x["Binding Energy (kcal/mol)"], reverse=True)

    # Write results to a CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ["Molecule Name", "PDBQT File", "Binding Energy (kcal/mol)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results saved to {csv_file}. Total ligands processed: {len(results)}.")

# Example usage
if __name__ == "__main__":
    output_directory = input("Enter the directory containing docking output files: ").strip()
    csv_output_file = input("Enter the path for the CSV output file: ").strip()
    parse_docking_results(output_directory, csv_output_file)
