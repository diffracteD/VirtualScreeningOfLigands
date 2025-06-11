import os
"""
Identify Molecules by ZINC* Name:
The script identifies the start of each molecule by the @<TRIPOS>MOLECULE tag.
It extracts the molecule's name from the lines starting with ZINC.
Output Directory:
Creates a directory named <input_filename>_split (e.g., input.mol2_split) to store the individual .mol2 files.
File Naming:
Each molecule is saved as ZINC12345678.mol2 based on its identifier.


How to Run:
Save the script as split_zinc_mol2.py.
Run the script in a terminal:
bash
Copy code
python split_zinc_mol2.py
Provide the path to the combined .mol2 file when prompted.

"""
def split_zinc_mol2(input_file):
    """Split a ZINC .mol2 file into separate files using ZINC identifiers as filenames."""
    # Get the base name of the input file (without extension) for the output directory
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = f"{base_name}_split"

    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(input_file, 'r') as infile:
            molecule_data = []
            zinc_name = None

            for line in infile:
                if line.startswith("@<TRIPOS>MOLECULE"):
                    # If we already have data for a molecule, write it to a file
                    if molecule_data and zinc_name:
                        output_file = os.path.join(output_dir, f"{zinc_name}.mol2")
                        with open(output_file, 'w') as outfile:
                            outfile.writelines(molecule_data)
                        molecule_data = []  # Reset for the next molecule
                        zinc_name = None

                # Collect the current line
                molecule_data.append(line)

                # Identify the ZINC* name
                if not zinc_name and line.startswith("ZINC"):
                    zinc_name = line.strip()

            # Write the last molecule if any
            if molecule_data and zinc_name:
                output_file = os.path.join(output_dir, f"{zinc_name}.mol2")
                with open(output_file, 'w') as outfile:
                    outfile.writelines(molecule_data)

        print(f"Splitting completed. Files are saved in '{output_dir}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_mol2_file = input("Enter the path to the combined .mol2 file: ").strip()
    if os.path.exists(input_mol2_file) and input_mol2_file.endswith(".mol2"):
        split_zinc_mol2(input_mol2_file)
    else:
        print("Invalid file path. Please provide a valid .mol2 file.")
