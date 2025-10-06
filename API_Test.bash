# Upload a photo
curl -X POST "http://localhost:8000/upload-photo" \
  -F "file=@delivery_note.jpg" \
  -F "driver_name=John Smith"

# Check alerts
curl "http://localhost:8000/alerts"

# View customer balance
curl "http://localhost:8000/customers/Tesco%20Warrington/balance"