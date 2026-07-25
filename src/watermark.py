"""
Darleine Abellard
Craft Watermark

Core watermarking logic: embeds a numeric watermark id into an image
using Discrete Wavelet Transform (DWT) frequency-domain embedding
"""

import numpy as np
import pywt
import cv2
import hashlib

# the minimum gap forced between the two coefficients being compared
EMBED_STRENGTH = 500.0

# how many bits of the watermark id we embed
WATERMARK_BITS = 32

def embed_watermark(image_path, output_path, watermark_id):
    """
    Embeds a numeric watermark id into a duplicate of the image 
    using DWT-based frequency-domain embedding. The original file
    is left untouched.

    Args:
        image_path (str): path to the original image to watermark
        output_path (str): where to write the watermarked image
        watermark_id (int): the numeric id to embed

    Returns:
        str: the SHA256 hash (hex string) of the watermarked file
            contents

    Raises:
        ValueError: if watermark_id doesn't fit within WATERMARK_BITS
    """
    if watermark_id >= 2 ** WATERMARK_BITS:
        raise ValueError(
            f"watermark_id must fit in {WATERMARK_BITS} bits "
            f"max value: {2 ** WATERMARK_BITS - 1}"
        )
    image_arr = cv2.imread(image_path, cv2.IMREAD_UNCHANGED) # [height, width, BGR]

    # flattens to rgb and remove transparent background
    if image_arr.shape[2] == 4:
        alpha = image_arr[:, :, 3:4].astype(np.float32) / 255.0
        bgr = image_arr[:, :, :3].astype(np.float32)
        white_background = np.full_like(bgr, 255.0)
        image_arr = (bgr * alpha + white_background * (1 - alpha)).astype(np.uint8)

    # isolate the blue channel
    blue_channel = image_arr[:,:,0].astype(np.float32)
    # decompose the blue channel into freq-dom reps
    LL, (LH, HL, HH) = pywt.dwt2(blue_channel, "haar")
    # convert the watermark id into list of bits
    bits = [(watermark_id >> i) & 1 for i in range(WATERMARK_BITS - 1, -1, -1)]
    watermarked_LH = LH.copy()
    for bit_i, bit in enumerate(bits):
        # pick two adjacent coefficients in the LH band to compare
        row = bit_i // (watermarked_LH.shape[1] // 2)
        col = (bit_i % (watermarked_LH.shape[1] // 2)) * 2

        coeff_a = watermarked_LH[row, col]
        coeff_b = watermarked_LH[row, col + 1]

        if bit == 1:
            if coeff_a <= coeff_b:
                average = (coeff_a + coeff_b) / 2
                coeff_a = average + EMBED_STRENGTH / 2
                coeff_b = average - EMBED_STRENGTH / 2
        else:
            if coeff_a >= coeff_b:
                average = (coeff_a + coeff_b) / 2
                coeff_a = average - EMBED_STRENGTH / 2
                coeff_b = average + EMBED_STRENGTH / 2

        watermarked_LH[row, col] = coeff_a
        watermarked_LH[row, col + 1] = coeff_b

    # reconstruct the blue channel from watermarked freq-dom pieces
    watermarked_blue = pywt.idwt2((LL, (watermarked_LH, HL, HH)), "haar")
    watermarked_blue = watermarked_blue[:blue_channel.shape[0], :blue_channel.shape[1]]

    # rebuild the full image with the watermarked blue channel swapped in
    watermarked_img_arr = image_arr.copy()
    watermarked_img_arr[:, :, 0] = np.clip(watermarked_blue, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, watermarked_img_arr)

    with open(output_path, "rb") as f:
        image_hash = hashlib.sha256(f.read()).hexdigest()

    return image_hash


def extract_watermark(image_path):
    """Extracts a previously-embedded numeric watermark id from an image

    Args:
        image_path (str): path to the (possibly watermarked) image

    Returns:
        int: the recovered watermark id
    """
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    blue_channel = img[:, :, 0].astype(np.float32)
    _, (LH, _, _) = pywt.dwt2(blue_channel, "haar")

    bits = []
    # identical row/col calculation as embed_watermark
    for bit_i in range(WATERMARK_BITS):
        row = bit_i // (LH.shape[1] // 2)
        col = (bit_i % (LH.shape[1] // 2)) * 2
        coeff_a = LH[row, col]
        coeff_b = LH[row, col + 1]
        bit = 1 if coeff_a > coeff_b else 0
        bits.append(bit)

    # reassemble the individual bits back into an integer
    watermark_id = 0
    for bit in bits:
        watermark_id = (watermark_id << 1) | bit

    return watermark_id
    
