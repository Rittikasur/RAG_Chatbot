import os
import json
import requests

# Directory containing the JSON files
dataset_dir = './test/dataset'

# URL for the POST request
url = 'http://localhost:5000/content'

# Iterate over all files in the dataset directory
for filename in os.listdir(dataset_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(dataset_dir, filename)
        
        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            # Ensure the data is a list
            if isinstance(data, list):
                for element in data:
                    # Send the POST request
                    response = requests.post(url, json=element)
                    
                    # Print the response
                    print(f"Response for {filename} element: {response.status_code}")
                    if response.status_code not in [200, 409]:
                        print(response.text)
                        input("Press Enter to continue...")
            else:
                print(f"File {filename} does not contain a list")

print("All requests completed.")