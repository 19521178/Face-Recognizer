# Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the requirements
pip install -r requirements.txt

# Create database collection if not exists
python3 /src/services/repository.py
# Or alternative
curl 'http://localhost:6333/collections/faces' \
  -X 'PUT' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  --data-raw '{"vectors":{"size":512,"distance":"Cosine"}}'

# Restore collection
curl -X POST 'http://localhost:6333/collections/faces/snapshots/upload?priority=snapshot' -H 'Content-Type:multipart/form-data' -F 'snapshot=@faces-shapshot.snapshot'


PUT collections/faces
{
  "vectors": {
    "size": 512,
    "distance": "Cosine"
  }
}
