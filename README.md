# craft-watermark

Invisible, compression-resistant image watermarking, built to prove ownership even after an image has been reposted or recompressed.

Uses DWT (Discrete Wavelet Transform) frequency-domain embedding rather than basic pixel-level steganography, specifically so the watermark survives real-world JPEG compression instead of being destroyed by it.

See [MECHANICS.md](./MECHANICS.md) for how it actually works, the security model, and a real debugging story from building it.

## Try it

_(Streamlit Community Cloud link goes here once deployed)_

## Setup

```bash
git clone https://github.com/dabellar/craft-watermark.git
cd craft-watermark
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run src/app.py
```

## What it does

1. **Embed** — upload an image and a creator id; get back a visually identical copy with an invisible watermark embedded in it.
2. **Verify** — upload any image; if it contains one of this tool's watermarks, the creator it belongs to is looked up and shown.

## Tested robustness

The watermark survives JPEG re-compression down to **~50% quality** before bit errors start appearing. See [MECHANICS.md](./MECHANICS.md) for the full test results and how that number was found.

## Stack

Python, OpenCV, PyWavelets, NumPy, SQLite, Streamlit.

## Known limitations

- Transparent images are flattened to a solid background before watermarking (transparent pixel data is unstable and can't reliably carry a watermark — see MECHANICS.md).
- One shared, simple id-based ownership model — no accounts, auth, or rate limiting; built as a portfolio project, not a production service.
- Not tested against resizing or cropping, only JPEG re-compression.
