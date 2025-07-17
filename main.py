"""
Entry‑point: `python3.11 main.py`
"""
import uvicorn
from api import app   # FastAPI instance

if __name__ == "__main__":
    # adjust host/port as you like
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
