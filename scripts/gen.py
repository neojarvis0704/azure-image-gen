import os
import sys
import json
import base64
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path
# ---- Minimal .env loader (no external deps) ----
def load_env_file(path):
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

load_env_file("/home/thomas/.env.azure")

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

if not all([AZURE_ENDPOINT, AZURE_API_KEY, DEPLOYMENT]):
    raise RuntimeError("Missing required Azure OpenAI environment variables")

# ---- CLI parsing ----
# Usage:
#   gen.py "<prompt>"                -> generate
#   gen.py "<prompt>" --image a.png b.png -> edit

args = sys.argv[1:]
if not args:
    raise RuntimeError("Usage: gen.py '<prompt>' [--image img1 img2 ...]")

prompt = args[0]
image_paths = []
if "--image" in args:
    idx = args.index("--image")
    image_paths = args[idx + 1:]
    if not image_paths:
        raise RuntimeError("--image provided but no image paths given")

# ---- Output path ----
out_dir = Path(__file__).parent / "out"
out_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_path = out_dir / f"{timestamp}.png"

# ---- Azure OpenAI Image call via Python SDK ----
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
)

if image_paths:
    # ---- Edit / blend mode ----
    image_files = [open(p, "rb") for p in image_paths]
    try:
        result = client.images.edit(
            model=DEPLOYMENT,
            prompt=prompt,
            image=image_files,
            size="1024x1024",
        )
    finally:
        for f in image_files:
            f.close()
else:
    # ---- Generate mode ----
    result = client.images.generate(
        model=DEPLOYMENT,
        prompt=prompt,
        size="1024x1024",
    )

# ---- Decode base64 image ----
image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

with open(out_path, "wb") as f:
    f.write(image_bytes)

# ---- OpenClaw-friendly stdout ----
print(json.dumps({
    "ok": True,
    "path": str(out_path),
    "prompt": prompt
}))