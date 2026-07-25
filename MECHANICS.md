# Mechanics

How craft-watermark actually works, why it's built this way, and a real account of the bugs found while getting it to actually work.

## The problem

Hide a small piece of data (an id) inside an image, invisibly, in a way that survives the image being compressed, resized, or re-saved — the real journey an image takes once it leaves your hands (screenshots, reposts, platform recompression).

## Why not just hide data in the pixels directly (LSB steganography)

The simplest possible approach: flip the last bit of some pixels' color values to encode a message. Invisible to the eye, but it lives in exactly the fine detail JPEG compression is designed to discard. Resize or re-save the image, and it's gone.

## The real approach: the frequency domain

Any image can be re-expressed not as "a grid of pixel colors" but as a combination of patterns at different **frequencies** — smooth, gradual color changes (low frequency) versus sharp fine detail (high frequency), the same idea as an audio equalizer splitting sound into bass versus treble.

A **Discrete Wavelet Transform (DWT)** converts an image into this frequency-domain representation, reversibly. This project uses `pywt.dwt2(...)` with the Haar wavelet (the simplest, most standard choice) to split the image's blue channel into four bands:

- **LL** — the coarse, smooth "big picture" content
- **LH / HL** — mid-frequency detail (edges) — **this is where the watermark is embedded**
- **HH** — fine detail/noise — most vulnerable to compression, avoided entirely

JPEG compression specifically discards high-frequency detail (HH) and can distort low-frequency content (LL) enough to become visible if disturbed. The mid-frequency band is the sweet spot: robust enough to survive typical compression, subtle enough to stay invisible.

Blue is used specifically because human vision is least sensitive to changes in blue — a common choice in steganography for the same reason.

## The embedding trick: relative, not absolute, values

Rather than setting one coefficient to an exact value (fragile — any small disturbance changes it), each bit is encoded as a **relationship between two adjacent coefficients**: "A > B" means 1, "A < B" means 0. Real-world distortion tends to nudge both values similarly, preserving their relative relationship even as their exact values shift.

`EMBED_STRENGTH` controls how large a gap is forced between the two coefficients — this is the project's central tradeoff: too weak, and compression quantizes the gap away entirely; too strong, and the watermark can become visible, especially after compression is layered on top.

## The watermark payload: an id, not identity

The embedded value is a plain integer — a `creator_id` from a local SQLite database — never a name, phone number, or other identifying information directly. Extracting the id from an image reveals nothing on its own; it's only meaningful when looked up against the database. This mirrors how real forensic watermarking systems work, and avoids embedding PII into images that are, by design, meant to be shared publicly.

## Debugging story: three real bugs, in the order they were found

**1. `EMBED_STRENGTH` too weak for real JPEG compression.**
The original value (15.0) failed completely, even at 95% quality. Direct inspection of the actual coefficient values before/after compression showed both being quantized all the way to `0.00` — the forced gap wasn't just weakened, it was erased entirely. Retuned empirically; too high (1000.0) introduced visible artifacts specifically _after_ compression (not visible in the uncompressed file alone, which made this easy to miss on a first pass). Settled on a value that stayed invisible through compression down to 50% quality.

**2. A cross-library inconsistency between embedding and extraction.**
`embed_watermark` read images with `cv2.IMREAD_UNCHANGED` (preserving all channels); `extract_watermark` used plain `cv2.imread` (silently dropping/altering channel data for images with transparency). The two functions were reading the same file differently, corrupting extraction for any image with an alpha channel. Fixed by matching the read flag exactly between both functions.

**3. Watermarking transparent pixel data that was never stable to begin with.**
Even after fixing #2, extraction still failed — but only for images with genuine transparency. The root cause: a PNG's color data underneath fully-transparent pixels is considered meaningless by the format itself, and different tools store arbitrary values there (this also caused a separate, visible bug: PIL's default RGB conversion exposed a stray green tint hidden under transparent regions). The watermark was landing partly in this throwaway data, which never survived being flattened to a non-transparent format — a step any real-world JPEG conversion requires. Fixed by explicitly compositing transparent images onto a solid white background _before_ embedding, not after, so the watermark is written into the same color values the image will actually have wherever it ends up.

## Tested robustness (final results)

With the fixes above in place and a tuned `EMBED_STRENGTH`, the watermark was tested by saving the same source image as JPEG at decreasing quality levels and attempting extraction at each:

| Quality      | Result                            |
| ------------ | --------------------------------- |
| 95–60        | Extracted correctly, 0 bit errors |
| 50 and Below | Extraction unreliable             |

Not tested: resizing, cropping, or multiple rounds of re-compression — a reasonable next step if this were taken further.

## Security model

- **File validation** happens before any watermarking logic runs: uploaded files are checked against a maximum size, then actually opened and verified as genuine image data (via Pillow), not trusted based on filename/extension alone — a renamed non-image file is rejected regardless of what it claims to be.
- **Database queries use parameterized placeholders**, never raw string interpolation, to prevent SQL injection.
- **No arbitrary data can be hidden** — only a small numeric id fits in the available embedding capacity, meaningfully limiting this tool's use for smuggling hidden messages, unlike general-purpose steganography software.
- **Known, accepted limitation:** no authentication, rate limiting, or per-user isolation — reasonable for a small portfolio tool, not something to rely on for a production service without further hardening.
