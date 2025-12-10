"""
Quick test script to verify the Excel export functionality
"""
import requests
import os
from datetime import datetime

# API endpoint
API_URL = "http://localhost:5100/api/export/excel"

print("🧪 Testing Excel Export Functionality")
print("=" * 60)

try:
    print(f"\n📡 Sending request to: {API_URL}")
    response = requests.get(API_URL, timeout=30)
    
    if response.status_code == 200:
        # Save the file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_export_{timestamp}.xlsx"
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        file_size = os.path.getsize(filename)
        
        print(f"\n✅ Export successful!")
        print(f"📁 File saved: {filename}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        print(f"📍 Location: {os.path.abspath(filename)}")
        
    else:
        print(f"\n❌ Export failed!")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error!")
    print("Make sure the dashboard server is running on http://localhost:5100")
    print("Run: .venv\\Scripts\\python.exe ui\\dashboard.py")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
