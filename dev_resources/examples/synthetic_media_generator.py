"""Example intentionally containing Article 50-style transparency signals."""


def generate_image(prompt: str) -> bytes:
    return b"synthetic_media"


def add_c2pa_watermark(image: bytes) -> bytes:
    # Evidence of provenance / machine-readable marking.
    return image
