import os
import sys
import json
import requests
import base64
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path

# ---- Environment Configuration ----
def load_env_azure(path):
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        print(json.dumps({"ok": False, "error": f"Env file not found at {path}"}))
        sys.exit(1)

load_env_azure("/home/thomas/.env.azure")

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")

if not all([ENDPOINT, API_KEY, DEPLOYMENT]):
    print(json.dumps({"ok": False, "error": "Missing required Azure environment variables"}))
    sys.exit(1)

# ---- Argument Parsing ----
args = sys.argv[1:]
if not args or "--help" in args:
    print("Usage: gen.py '<prompt>' [--edit] [--ref path1 path2 ...]")
    sys.exit(0)

prompt = args[0]
is_edit_mode = "--edit" in args
ref_images = []
if "--ref" in args:
    try:
        idx = args.index("--ref") + 1
        for arg in args[idx:]:
            if arg.startswith("--"): break
            ref_images.append(arg)
    except ValueError: pass

# ---- Setup Client ----
client = AzureOpenAI(api_key=API_KEY, api_version=API_VERSION, azure_endpoint=ENDPOINT)
out_dir = Path(__file__).parent / "out"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

try:
    if is_edit_mode:
        if not ref_images:
            raise ValueError("Edit mode requires --ref images")
        
        handles = [open(p, "rb") for p in ref_images]
        try:
            # Removed response_format to prevent "unrecognized parameter" error
            response = client.images.edit(
                model=DEPLOYMENT,
                prompt=prompt,
                image=handles,
                size="1024x1024",
                quality="high",
                extra_body={"input_fidelity": "high"}
            )
        finally:
            for h in handles: h.close()
    else:
        response = client.images.generate(
            model=DEPLOYMENT,
            prompt=prompt,
            size="1024x1024",
            quality="high"
        )

    # ---- Get Image Bytes (URL or base64) ----
    image_item = response.data[0]
    img_data = None

    if getattr(image_item, "url", None):
        img_data = requests.get(image_item.url).content
    elif getattr(image_item, "b64_json", None):
        img_data = base64.b64decode(image_item.b64_json)
    else:
        raise ValueError("Image response missing url and b64_json")

    with open(out_path, "wb") as f:
        f.write(img_data)

    print(json.dumps({
        "ok": True,
        "mode": "edit" if is_edit_mode else "generate",
        "path": str(out_path),
        "prompt": prompt
    }))

except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}))
    sys.exit(1)