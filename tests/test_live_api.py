import urllib.request
import json
import time
import os
import sys

# Add directory root to import test helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.test_onboarding import create_mock_excel_file

def test_api():
    print("Testing Chronos live API server...")
    
    # 1. Test root endpoint
    root_url = "http://127.0.0.1:8000/"
    try:
        with urllib.request.urlopen(root_url) as response:
            res_body = response.read().decode('utf-8')
            print(f"Root endpoint response: {res_body}")
            root_json = json.loads(res_body)
            assert root_json["status"] == "online"
            print("  [PASSED] Root online verification.")
    except Exception as e:
        print(f"  [FAILED] Could not connect to root endpoint: {e}")
        return

    # 2. Test Excel /upload endpoint
    upload_url = "http://127.0.0.1:8000/api/upload?clear_existing=true"
    excel_bytes = create_mock_excel_file()
    
    # Define custom multipart boundary
    boundary = "----ChronosTestBoundary"
    
    # Compile raw multipart bytes body
    body_parts = [
        f"--{boundary}".encode('utf-8'),
        'Content-Disposition: form-data; name="file"; filename="restaurant_onboarding.xlsx"'.encode('utf-8'),
        b'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        b'',
        excel_bytes,
        f"--{boundary}--".encode('utf-8'),
        b''
    ]
    
    request_body = b'\r\n'.join(body_parts)
    
    req = urllib.request.Request(
        upload_url,
        data=request_body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(request_body))
        },
        method='POST'
    )
    
    print("\nSending POST request to live API `/api/upload`...")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print("API Response:")
            print(json.dumps(res_json, indent=2))
            assert res_json["status"] == "success"
            print("\n  [PASSED] Live API Excel upload test!")
    except Exception as e:
        print(f"\n  [FAILED] Excel upload failed: {e}")
        if hasattr(e, 'read'):
            print(f"Error Response Body: {e.read().decode('utf-8')}")

    # 3. Test Graph endpoint skeleton
    graph_url = "http://127.0.0.1:8000/api/graph/1"
    print("\nSending GET request to live API `/api/graph/1`...")
    try:
        with urllib.request.urlopen(graph_url) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            print("API Response:")
            print(json.dumps(res_json, indent=2))
            assert res_json["status"] == "success"
            print("\n  [PASSED] Live API Graph skeleton test!")
    except Exception as e:
        print(f"\n  [FAILED] Graph skeleton retrieval failed: {e}")

if __name__ == "__main__":
    # Small sleep to allow uvicorn startup when run concurrently
    time.sleep(1.5)
    test_api()
