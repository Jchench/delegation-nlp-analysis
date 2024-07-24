import os
import pandas as pd

# Directory containing the text files
folder_path = "data/"

# List to store data from all files
all_data = []

# Loop through each text file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)
        
        # Extract the citation from the filename (assuming the format "PL94_240.txt")
        citation = filename.replace(".txt", "").replace("_", " ").replace("PL", "Public Law ")
        
        # Load the text file
        with open(file_path, "r") as file:
            text = file.read()
        
        # Split the text into sections based on typical section headers
        sections = text.split('SEC.')
        
        # Create a DataFrame with the sections data
        for i, section in enumerate(sections):
            if section.strip():  # Ensure the section is not empty
                section_name = f"Section {i}"
                section_id = i
                all_data.append({'name': section_name, 'citation': citation, 'id': section_id, 'text': section.strip()})

# Create a DataFrame from the collected data
df = pd.DataFrame(all_data)

# Write the DataFrame to a CSV file
output_csv_path = "provisions_output.csv"
df.to_csv(output_csv_path, index=False)

# Display the DataFrame
print(df)
