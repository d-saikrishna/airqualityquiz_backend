import base64
import json

# Path to your .json file
json_file_path = 'constitutionbot-3e833b17dba1.json'

# Open and read the file
with open(json_file_path, 'rb') as file:
    # Read the contents of the file as bytes
    file_content = file.read()

    # Encode the file content in base64
    encoded_content = base64.b64encode(file_content).decode('utf-8')

# Print or use the base64 encoded content
print(encoded_content)
