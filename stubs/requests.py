"""
Stub para requests - Biblioteca HTTP para desenvolvimento fora do Anki
"""

class Response:
    def __init__(self, text="", status_code=200):
        self.text = text
        self.status_code = status_code
        
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

def get(url, **kwargs):
    """Mock get request"""
    return Response("Mock response", 200)

def post(url, **kwargs):
    """Mock post request"""
    return Response("Mock response", 200)

class RequestException(Exception):
    """Mock requests exception"""
    pass
