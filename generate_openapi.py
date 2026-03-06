import json
from app.main import app

def generate_openapi():
    openapi_schema = app.openapi()
    
    # Add general servers block for RapidAPI import compatibility
    if "servers" not in openapi_schema:
        openapi_schema["servers"] = [
            {
                "url": "https://your-api-domain.com",
                "description": "Production Server (Update this URL in RapidAPI)"
            }
        ]
        
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)

if __name__ == "__main__":
    generate_openapi()
    print("openapi.json generated successfully with servers block")
