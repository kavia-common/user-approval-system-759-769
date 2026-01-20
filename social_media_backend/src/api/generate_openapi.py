import json
import os

from src.api.main import app

# Ensure schema is generated after app is fully loaded
openapi_schema = app.openapi()

# Write to file inside container's interfaces directory
output_dir = "interfaces"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "openapi.json")

with open(output_path, "w") as f:
    json.dump(openapi_schema, f, indent=2)
