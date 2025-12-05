import base64
import io
import json
import time
from typing import Any, Dict

import azure.functions as func
from PIL import Image

# Import project modules
try:
    from sam_3d_body.sam_3d_body_estimator import SAM3DBodyEstimator
    from sam_3d_body.visualization.renderer import Renderer
except Exception as e:
    # Lazy imports or alternate paths can be handled here if needed
    raise e


_estimator = None
_renderer = None


def _get_models():
    global _estimator, _renderer
    if _estimator is None:
        # Initialize estimator with default configs; adjust if needed
        _estimator = SAM3DBodyEstimator()
    if _renderer is None:
        _renderer = Renderer()
    return _estimator, _renderer


def _run_inference(img: Image.Image, render: bool = True) -> Dict[str, Any]:
    estimator, renderer = _get_models()
    start = time.time()

    # Run estimator; adapt to your estimator's API
    # Expecting something like: outputs = estimator.predict(img)
    outputs = estimator(img)

    rend_img_b64 = None
    if render:
        rend = renderer.render(outputs, img)
        buf = io.BytesIO()
        rend.save(buf, format="PNG")
        rend_img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    elapsed_ms = int((time.time() - start) * 1000)
    return {
        "outputs": outputs,
        "rend_img": rend_img_b64,
        "meta": {
            "inference_ms": elapsed_ms,
            "model": "sam-3d-body"
        }
    }


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse multipart/form-data
        file = req.files.get('image') if hasattr(req, 'files') else None
        if file is None:
            return func.HttpResponse(
                json.dumps({"error": "No file 'image' in request"}),
                status_code=400,
                mimetype="application/json"
            )

        # Optional flags from JSON body or form fields
        render = True
        return_outputs = True
        try:
            data = req.get_json()
            render = bool(data.get('render', True))
            return_outputs = bool(data.get('return_outputs', True))
        except Exception:
            # Fallback to form fields
            render = req.form.get('render', 'true').lower() != 'false'
            return_outputs = req.form.get('return_outputs', 'true').lower() != 'false'

        img = Image.open(file.stream).convert('RGB')
        result = _run_inference(img, render=render)

        # Optionally strip outputs if not requested
        if not return_outputs:
            result['outputs'] = None

        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        err = {"error": str(e)}
        return func.HttpResponse(json.dumps(err), status_code=500, mimetype="application/json")