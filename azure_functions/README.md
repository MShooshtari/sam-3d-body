# Azure Functions API for SAM-3D-Body

This folder contains a Python Azure Functions HTTP endpoint that accepts an image via POST and runs SAM-3D-Body inference, returning `outputs` (JSON) and `rend_img` (PNG as base64).

## Structure
- `function_app/` – Azure Functions app root
  - `host.json` – Host config
  - `local.settings.json` – Local dev settings
  - `requirements.txt` – Python dependencies for the function
  - `HttpInfer/__init__.py` – HTTP trigger implementation
  - `HttpInfer/function.json` – Trigger config
- `frontend/` – Simple HTML+JS uploader consuming the API

## Local Dev (Windows PowerShell)

```powershell
# 1) Install Azure Functions Core Tools if needed
#    https://learn.microsoft.com/azure/azure-functions/functions-run-local
# 2) Create/activate a Python venv for the function
$env:FUNC_PY=".\.venv"
python -m venv $env:FUNC_PY
. $env:FUNC_PY\Scripts\Activate.ps1

# 3) Install function dependencies
cd azure_functions\function_app
pip install -r requirements.txt

# 4) Ensure project deps are installed (from repo root)
cd ..\..\
pip install -e .

# 5) Start the Functions host
cd azure_functions\function_app
func start
```

The endpoint will be available at: `http://localhost:7071/api/infer`.

### Request
- POST `multipart/form-data` with a file field named `image`.
- Optional JSON fields: `render`: true/false; `return_outputs`: true/false.

### Response
```json
{
  "outputs": { ... },
  "rend_img": "<base64 PNG>",
  "meta": {
    "inference_ms": 1234,
    "model": "sam-3d-body"
  }
}
```

## Frontend
Open `azure_functions/frontend/index.html` in a browser. Update `API_URL` if not running locally.