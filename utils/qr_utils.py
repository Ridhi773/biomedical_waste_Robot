"""
QR-code helpers. There's no physical scanner here, so "scanning" in the GUI
means the driver picks/enters a code that gets compared to the expected one
stored against the compartment or destination - this module generates those
codes, renders them as real scannable QR images, and does the comparison.
"""

import uuid

try:
    import qrcode
    from PIL import ImageTk
    QR_IMAGE_SUPPORT = True
except ImportError:
    # qrcode/Pillow aren't installed - the app still works fine without
    # them, screens just fall back to showing the plain text code instead
    # of a QR image (see generate_qr_photoimage below).
    QR_IMAGE_SUPPORT = False


def generate_code(prefix="CODE"):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def codes_match(scanned_code, expected_code):
    if not scanned_code or not expected_code:
        return False
    return scanned_code.strip().upper() == expected_code.strip().upper()


def generate_qr_photoimage(data, box_size=6, border=2):
    """
    Returns a Tkinter-displayable QR code image encoding `data`, or None
    if the qrcode/Pillow libraries aren't installed (or anything about
    generating the image goes wrong - the screen falls back to showing
    the plain text code instead of crashing). Callers should keep a
    reference to the returned object (e.g. self.qr_photo = ...) - Tkinter
    doesn't display images whose only reference got garbage collected.
    """
    if not QR_IMAGE_SUPPORT or not data:
        return None
    try:
        qr = qrcode.QRCode(box_size=box_size, border=border)
        qr.add_data(data)
        qr.make(fit=True)
        pil_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        return ImageTk.PhotoImage(pil_image)
    except Exception:
        return None
