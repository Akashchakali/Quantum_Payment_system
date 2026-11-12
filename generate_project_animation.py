from __future__ import annotations

import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont


WIDTH = 1280
HEIGHT = 720
FPS = 12
OUTPUT = Path("quantumpay_payment_flow.mp4")
MUSIC_FILE = Path("project_music.mp3")
OUTPUT_WITH_MUSIC = Path("quantumpay_payment_flow_with_music.mp4")

APP_BG_A = "#06110f"
APP_BG_B = "#10231f"
APP_BG_C = "#081614"
TEXT = "#e8fff9"
MUTED = "#a7c9c0"
MINT = "#5eead4"
GREEN = "#34d399"
RED = "#fb7185"
YELLOW = "#facc15"
PANEL = (8, 28, 25, 212)
LINE = (103, 232, 205, 90)
BUTTON_A = "#37cfc0"
BUTTON_B = "#f0bd05"


@dataclass
class Scene:
    name: str
    seconds: float
    renderer: callable


def rgba(color: str, alpha: int) -> tuple[int, int, int, int]:
    r, g, b = ImageColor.getrgb(color)
    return (r, g, b, alpha)


def blend(a: str, b: str, t: float) -> tuple[int, int, int]:
    ar, ag, ab = ImageColor.getrgb(a)
    br, bg, bb = ImageColor.getrgb(b)
    return (
        int(ar + (br - ar) * t),
        int(ag + (bg - ag) * t),
        int(ab + (bb - ab) * t),
    )


def load_font(size: int, bold: bool = False):
    choices = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in choices:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_HERO = load_font(44, bold=True)
FONT_TITLE = load_font(36, bold=True)
FONT_LABEL = load_font(22, bold=True)
FONT_BODY = load_font(22)
FONT_SMALL = load_font(18)
FONT_TINY = load_font(16)
FONT_METRIC = load_font(28, bold=True)


def draw_gradient(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        if t < 0.45:
            color = blend(APP_BG_A, APP_BG_B, t / 0.45)
        else:
            color = blend(APP_BG_B, APP_BG_C, (t - 0.45) / 0.55)
        draw.line((0, y, WIDTH, y), fill=color)


def draw_background(frame: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    # Draw the quantum-themed background used across all video scenes.
    img = Image.new("RGBA", (WIDTH, HEIGHT), APP_BG_A)
    draw_gradient(img)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")

    dx = (frame % 44)
    dy = (frame % 36)
    for x in range(-44, WIDTH + 44, 44):
        od.line((x + dx, 0, x + dx, HEIGHT), fill=rgba(MINT, 16), width=1)
    for y in range(-44, HEIGHT + 44, 44):
        od.line((0, y + dy, WIDTH, y + dy), fill=rgba(MINT, 14), width=1)

    od.ellipse((40, 28, 310, 300), fill=rgba(MINT, 20))
    od.ellipse((970, -10, 1240, 210), fill=rgba(YELLOW, 16))
    od.ellipse((940, 500, 1240, 760), fill=rgba(GREEN, 16))

    img = Image.alpha_composite(img, overlay)
    return img, ImageDraw.Draw(img, "RGBA")


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int = 10) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=PANEL, outline=LINE, width=2)


def text_fit(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], font, fill, gap: int = 6) -> None:
    x1, y1, x2, y2 = box
    width = x2 - x1
    est = max(16, int(width / max(font.size * 0.6, 8)))
    y = y1
    for line in textwrap.wrap(text, width=est):
        bbox = draw.textbbox((0, 0), line, font=font)
        if bbox[2] - bbox[0] > width and est > 16:
            return text_fit(draw, text, box, load_font(max(font.size - 2, 14), bold=font.size >= FONT_LABEL.size), fill, gap)
        draw.text((x1, y), line, font=font, fill=fill)
        y += font.size + gap
        if y > y2:
            break


def pill(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], color: str) -> None:
    draw.rounded_rectangle(box, radius=10, fill=rgba(color, 34), outline=rgba(color, 220), width=1)
    text_fit(draw, text, (box[0] + 12, box[1] + 8, box[2] - 12, box[3] - 8), FONT_SMALL, TEXT, 2)


def button(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], active: bool = True) -> None:
    fill = blend(BUTTON_A, BUTTON_B, 0.6 if active else 0.2)
    draw.rounded_rectangle(box, radius=8, fill=fill, outline=rgba(TEXT, 110), width=1)
    bbox = draw.textbbox((0, 0), text, font=FONT_LABEL)
    tx = box[0] + ((box[2] - box[0]) - (bbox[2] - bbox[0])) / 2
    ty = box[1] + ((box[3] - box[1]) - (bbox[3] - bbox[1])) / 2 - 1
    draw.text((tx, ty), text, font=FONT_LABEL, fill=APP_BG_A)


def topbar(draw: ImageDraw.ImageDraw) -> None:
    panel(draw, (28, 20, 1252, 92), radius=8)
    draw.rounded_rectangle((52, 34, 96, 78), radius=8, fill=rgba(MINT, 44), outline=rgba(MINT, 150), width=2)
    draw.text((67, 42), "Q", font=FONT_LABEL, fill=APP_BG_A)
    draw.text((112, 34), "QuantumPay Shield", font=FONT_LABEL, fill=TEXT)
    draw.text((112, 60), "BB84 secured payment simulator with QBER based authorization", font=FONT_SMALL, fill=MUTED)
    pill(draw, "Guttur Subhahan | Quantum National Bank", (872, 32, 1236, 76), MINT)


def channel_idle(draw: ImageDraw.ImageDraw, caption: str) -> None:
    # Show the channel in an idle state before or after transfer.
    draw.text((126, 636), "Alice", font=FONT_LABEL, fill=TEXT)
    draw.text((1092, 636), "Bob", font=FONT_LABEL, fill=TEXT)
    draw.ellipse((86, 556, 166, 636), outline=rgba(MINT, 200), width=3)
    draw.ellipse((1112, 556, 1192, 636), outline=rgba(YELLOW, 220), width=3)
    draw.line((166, 596, 1112, 596), fill=rgba(MINT, 70), width=4)
    pill(draw, caption, (330, 664, 950, 706), MINT)


def channel_active(draw: ImageDraw.ImageDraw, frame: int, attack: bool, caption: str) -> None:
    # Animate qubit transfer during secure or attacked BB84 exchange.
    draw.text((126, 636), "Alice", font=FONT_LABEL, fill=TEXT)
    draw.text((1092, 636), "Bob", font=FONT_LABEL, fill=TEXT)
    draw.ellipse((86, 556, 166, 636), outline=rgba(MINT, 200), width=3)
    draw.ellipse((1112, 556, 1192, 636), outline=rgba(YELLOW, 220), width=3)
    draw.line((166, 596, 1112, 596), fill=rgba(MINT, 130), width=5)

    for i in range(7):
        t = ((frame * 2.2 + i * 22) % 100) / 100
        x = int(190 + 890 * t)
        y = 596
        value = "1" if i % 2 else "0"
        pill(draw, value, (x - 20, y - 20, x + 20, y + 20), GREEN if not attack else MINT)

    if attack:
        draw.ellipse((606, 480, 686, 560), outline=rgba(RED, 220), width=3)
        draw.text((632, 570), "Eve", font=FONT_SMALL, fill=RED)
        draw.line((646, 560, 646, 596), fill=RED, width=4)

    pill(draw, caption, (330, 664, 950, 706), MINT if not attack else RED)


def step_box(draw: ImageDraw.ImageDraw, active: int, note: str) -> None:
    # Show a compact list of the main demo steps.
    panel(draw, (835, 168, 1195, 324), radius=8)
    draw.text((856, 188), "Step-by-step process", font=FONT_LABEL, fill=TEXT)
    steps = [
        "Login completed",
        "Home page opened",
        "Make Payment opened",
        "Payment details entered",
        "Password verified",
        "BB84 and QBER checked",
    ]
    y = 228
    for idx, step in enumerate(steps):
        color = GREEN if idx <= active else "#315752"
        draw.ellipse((856, y + 2, 876, y + 22), fill=rgba(color, 255))
        draw.text((894, y), step, font=FONT_TINY, fill=TEXT if idx <= active else MUTED)
        y += 20
    pill(draw, note, (850, 340, 1178, 386), YELLOW)


def steps_page_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Show the full project flow once on a separate page after login.
    topbar(draw)
    page_title(draw, "Procedure", "Step-by-step payment flow", YELLOW)
    panel(draw, (58, 236, 1180, 620))
    draw.text((88, 274), "Project procedure", font=FONT_TITLE, fill=TEXT)
    steps = [
        "1. User logs in to the application.",
        "2. Home page opens and the user selects Make Payment.",
        "3. Payment details are entered for the receiver.",
        "4. Password verification starts secure BB84 processing.",
        "5. If QBER stays low, the payment succeeds and the bill is shown.",
        "6. A second payment is attempted to demonstrate attack detection.",
        "7. If QBER becomes high, the payment fails and the reason is shown.",
        "8. BB84 sample data is displayed for explanation.",
        "9. The video returns to the home page at the end.",
    ]
    y = 326
    for step in steps:
        draw.ellipse((92, y + 6, 108, y + 22), fill=rgba(MINT, 255))
        text_fit(draw, step, (126, y, 1120, y + 34), FONT_SMALL, TEXT, 3)
        y += 31


def page_title(draw: ImageDraw.ImageDraw, badge_text: str, title: str, badge_color: str) -> None:
    pill(draw, badge_text, (56, 122, 250, 166), badge_color)
    draw.text((56, 182), title, font=FONT_HERO, fill=TEXT)


def login_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Opening scene: user logs into the payment app.
    topbar(draw)
    page_title(draw, "Login", "Login to QuantumPay", MINT)
    panel(draw, (40, 236, 1040, 548))
    text_fit(
        draw,
        "Enter your user name and password to open the payment dashboard.",
        (66, 268, 1000, 306),
        FONT_SMALL,
        MUTED,
        4,
    )
    labels = [
        ("User name", "Guttur Subhahan"),
        ("Password", "**********"),
    ]
    y = 346
    for title, value in labels:
        draw.text((66, y), title, font=FONT_TINY, fill=TEXT)
        panel(draw, (66, y + 16, 1024, y + 58), radius=8)
        draw.text((86, y + 28), value, font=FONT_SMALL, fill=TEXT)
        y += 86
    button(draw, "Login", (66, 500, 160, 544))


def home_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Show the dashboard before the payment journey begins.
    topbar(draw)
    page_title(draw, "Home", "Dashboard", GREEN)
    panel(draw, (40, 226, 1040, 684))
    draw.text((66, 258), "Choose an action", font=FONT_TITLE, fill=TEXT)
    cards = [
        ("Make Payment", "Pay a saved contact or custom number."),
        ("Transfer Money", "Transfer to another bank account."),
        ("Balance Enquiry", "Check balances after password verification."),
        ("Transaction History", "Review success and failed payments."),
        ("Graph Analysis", "Analyze QBER and payment trends."),
        ("Generate QR Code", "Create a payment QR code."),
    ]
    positions = [
        (66, 312, 376, 438), (392, 312, 702, 438), (718, 312, 1028, 438),
        (66, 458, 376, 584), (392, 458, 702, 584), (718, 458, 1028, 584),
    ]
    for (title, subtitle), box in zip(cards, positions):
        panel(draw, box)
        draw.text((box[0] + 16, box[1] + 18), title, font=FONT_SMALL, fill=TEXT)
        text_fit(draw, subtitle, (box[0] + 16, box[1] + 58, box[2] - 16, box[3] - 12), FONT_TINY, MUTED, 2)
    button(draw, "Make Payment", (66, 618, 376, 662))
    button(draw, "Balance Enquiry", (392, 618, 702, 662))
    button(draw, "Graph Analysis", (718, 618, 1028, 662))
    button(draw, "Transfer Money", (66, 672, 376, 716))
    button(draw, "Transaction History", (392, 672, 702, 716))
    button(draw, "Generate QR Code", (718, 672, 1028, 716))


def payment_form_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # The user fills payment details before quantum verification starts.
    topbar(draw)
    page_title(draw, "Make Payment", "Enter payment details", YELLOW)
    panel(draw, (58, 242, 760, 598))
    draw.text((86, 274), "Make Payment", font=FONT_TITLE, fill=TEXT)
    draw.text((86, 326), "Receiver type", font=FONT_SMALL, fill=MUTED)
    panel(draw, (86, 350, 290, 404))
    draw.text((110, 368), "Saved contact", font=FONT_SMALL, fill=TEXT)
    panel(draw, (86, 432, 724, 498))
    draw.text((110, 452), "Sai Preethi | 9123456780 | Quantum National Bank", font=FONT_SMALL, fill=TEXT)
    panel(draw, (86, 524, 300, 578))
    draw.text((110, 542), "Amount: INR 1,500", font=FONT_SMALL, fill=TEXT)
    panel(draw, (322, 524, 724, 578))
    draw.text((346, 542), "Note: Quantum secured transfer", font=FONT_SMALL, fill=TEXT)
    button(draw, "Pay", (86, 612, 254, 656))
    channel_idle(draw, "No qubits move while the form is being filled.")


def success_verify_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Secure payment attempt where BB84 exchange succeeds.
    topbar(draw)
    page_title(draw, "Success Attempt", "Confirm successful payment", GREEN)
    panel(draw, (58, 238, 760, 560))
    draw.text((86, 270), "Confirm Payment", font=FONT_TITLE, fill=TEXT)
    draw.text((86, 322), "Receiver: Sai Preethi", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 356), "Amount: INR 1,500", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 390), "Note: Quantum secured transfer", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 448), "UPI password", font=FONT_SMALL, fill=MUTED)
    panel(draw, (86, 472, 724, 524))
    draw.text((110, 489), "**********", font=FONT_SMALL, fill=TEXT)
    button(draw, "Confirm and Verify Quantum Channel", (86, 602, 470, 648))
    channel_active(draw, frame, False, "Alice sends qubits to Bob. Bases match and QBER stays low.")


def success_bill_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Show the successful payment bill after approval.
    topbar(draw)
    page_title(draw, "Success Bill", "Successful payment bill", GREEN)
    panel(draw, (58, 236, 760, 586))
    pill(draw, "Payment successful", (86, 272, 330, 318), GREEN)
    draw.text((86, 350), "Transaction ID: QTX104500321", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 382), "Receiver: Sai Preethi", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 414), "Amount: INR 1,500", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 446), "QBER: 0.08%", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 478), "Key length: 41 bits", font=FONT_SMALL, fill=TEXT)
    pill(draw, "Secure BB84 channel verified. The transfer is approved.", (86, 522, 700, 568), GREEN)
    text_fit(draw, "The app shows the successful bill after secure verification.", (820, 250, 1180, 330), FONT_BODY, TEXT, 6)


def second_form_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Start a second payment attempt to demonstrate failure.
    topbar(draw)
    page_title(draw, "Second Attempt", "Send another amount", YELLOW)
    panel(draw, (58, 242, 760, 598))
    draw.text((86, 274), "Make Payment", font=FONT_TITLE, fill=TEXT)
    draw.text((86, 326), "Receiver type", font=FONT_SMALL, fill=MUTED)
    panel(draw, (86, 350, 290, 404))
    draw.text((110, 368), "Saved contact", font=FONT_SMALL, fill=TEXT)
    panel(draw, (86, 432, 724, 498))
    draw.text((110, 452), "Sai Preethi | 9123456780 | Quantum National Bank", font=FONT_SMALL, fill=TEXT)
    panel(draw, (86, 524, 300, 578))
    draw.text((110, 542), "Amount: INR 2,000", font=FONT_SMALL, fill=TEXT)
    panel(draw, (322, 524, 724, 578))
    draw.text((346, 542), "Note: Second quantum payment", font=FONT_SMALL, fill=TEXT)
    button(draw, "Pay", (86, 612, 254, 656))


def failure_verify_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Failed payment attempt where attack raises the QBER.
    topbar(draw)
    page_title(draw, "Failed Attempt", "Confirm failed payment", RED)
    panel(draw, (58, 238, 760, 560))
    draw.text((86, 270), "Confirm Payment", font=FONT_TITLE, fill=TEXT)
    draw.text((86, 322), "Receiver: Sai Preethi", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 356), "Amount: INR 2,000", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 390), "Note: Second quantum payment", font=FONT_SMALL, fill=TEXT)
    draw.text((86, 448), "UPI password", font=FONT_SMALL, fill=MUTED)
    panel(draw, (86, 472, 724, 524))
    draw.text((110, 489), "**********", font=FONT_SMALL, fill=TEXT)
    button(draw, "Confirm and Verify Quantum Channel", (86, 602, 470, 648))
    channel_active(draw, frame, True, "Eavesdropping changes the qubits, so the error rate becomes high.")


def failure_bill_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Show the failed payment bill and the reason for rejection.
    topbar(draw)
    page_title(draw, "Failure Bill", "Failed payment bill", RED)
    panel(draw, (58, 236, 760, 604))
    pill(draw, "Payment failed", (86, 272, 290, 318), RED)
    pill(draw, "Eavesdropping detected. QBER crossed the allowed threshold.", (86, 344, 700, 390), RED)
    draw.text((86, 434), "Observed QBER: 0.24%", font=FONT_METRIC, fill=RED)
    draw.text((86, 482), "Threshold: 0.11%", font=FONT_SMALL, fill=YELLOW)
    text_fit(draw, "Reason: payment blocked because the quantum channel was disturbed during transmission.", (86, 520, 700, 570), FONT_SMALL, TEXT, 4)
    text_fit(draw, "The app explains the failed bill and highlights the high-QBER attack detection.", (820, 250, 1180, 344), FONT_BODY, TEXT, 6)


def bb84_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # Display a sample BB84 data table used in the project.
    topbar(draw)
    page_title(draw, "BB84 Data", "BB84 sample data page", MINT)
    panel(draw, (58, 236, 1160, 596))
    draw.text((86, 266), "View BB84 sample data", font=FONT_TITLE, fill=TEXT)
    headers = ["No.", "Alice Bit", "Alice Basis", "Bob Basis", "Bob Bit", "Result"]
    col_x = [86, 170, 308, 484, 650, 796]
    for x, label in zip(col_x, headers):
        draw.text((x, 322), label, font=FONT_SMALL, fill=MUTED)
    rows = [
        ("1", "1", "+", "+", "1", "Matched"),
        ("2", "0", "x", "x", "0", "Matched"),
        ("3", "1", "+", "x", "0", "Mismatch"),
        ("4", "0", "x", "x", "0", "Matched"),
        ("5", "1", "+", "+", "1", "Matched"),
    ]
    y = 362
    for row in rows:
        panel(draw, (78, y - 8, 1100, y + 28), radius=6)
        for x, value in zip(col_x, row):
            draw.text((x, y), value, font=FONT_TINY, fill=TEXT if value not in ("Matched", "Mismatch") else (GREEN if value == "Matched" else RED))
        y += 50


def final_home_scene(draw: ImageDraw.ImageDraw, frame: int, progress: float) -> None:
    # End the video by returning to the dashboard view.
    topbar(draw)
    page_title(draw, "Home", "Dashboard", GREEN)
    panel(draw, (40, 226, 1040, 684))
    draw.text((66, 258), "Choose an action", font=FONT_TITLE, fill=TEXT)
    cards = [
        ("Make Payment", "Pay a saved contact or custom number."),
        ("Transfer Money", "Transfer to another bank account."),
        ("Balance Enquiry", "Check balances after password verification."),
        ("Transaction History", "Review success and failed payments."),
        ("Graph Analysis", "Analyze QBER and payment trends."),
        ("Generate QR Code", "Create a payment QR code."),
    ]
    positions = [
        (66, 312, 376, 438), (392, 312, 702, 438), (718, 312, 1028, 438),
        (66, 458, 376, 584), (392, 458, 702, 584), (718, 458, 1028, 584),
    ]
    for (title, subtitle), box in zip(cards, positions):
        panel(draw, box)
        draw.text((box[0] + 16, box[1] + 18), title, font=FONT_SMALL, fill=TEXT)
        text_fit(draw, subtitle, (box[0] + 16, box[1] + 58, box[2] - 16, box[3] - 12), FONT_TINY, MUTED, 2)
    button(draw, "Make Payment", (66, 618, 376, 662))
    button(draw, "Balance Enquiry", (392, 618, 702, 662))
    button(draw, "Graph Analysis", (718, 618, 1028, 662))
    button(draw, "Transfer Money", (66, 672, 376, 716))
    button(draw, "Transaction History", (392, 672, 702, 716))
    button(draw, "Generate QR Code", (718, 672, 1028, 716))


SCENES = [
    Scene("login", 3.0, login_scene),
    Scene("home", 3.0, home_scene),
    Scene("steps_page", 4.0, steps_page_scene),
    Scene("payment_form", 4.0, payment_form_scene),
    Scene("success_verify", 5.0, success_verify_scene),
    Scene("success_bill", 4.0, success_bill_scene),
    Scene("second_form", 4.0, second_form_scene),
    Scene("failure_verify", 5.0, failure_verify_scene),
    Scene("failure_bill", 4.0, failure_bill_scene),
    Scene("bb84_data", 4.0, bb84_scene),
    Scene("final_home", 3.0, final_home_scene),
]


def make_frame(scene: Scene, local_frame: int, total_frame: int) -> np.ndarray:
    img, draw = draw_background(total_frame)
    progress = local_frame / max(int(scene.seconds * FPS) - 1, 1)
    scene.renderer(draw, total_frame, progress)
    return np.array(img.convert("RGB"))


def build_video() -> None:
    # Render all scenes into the final MP4 video.
    writer = imageio.get_writer(
        OUTPUT,
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=None,
    )
    try:
        total_frame = 0
        for scene in SCENES:
            frame_count = int(scene.seconds * FPS)
            for local_frame in range(frame_count):
                writer.append_data(make_frame(scene, local_frame, total_frame))
                total_frame += 1
    finally:
        writer.close()


def add_music_if_present() -> Path:
    # Attach background music when an MP3 file is available.
    if not MUSIC_FILE.exists():
        return OUTPUT

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(OUTPUT),
            "-stream_loop",
            "-1",
            "-i",
            str(MUSIC_FILE),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(OUTPUT_WITH_MUSIC),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return OUTPUT_WITH_MUSIC


if __name__ == "__main__":
    build_video()
    final_output = add_music_if_present()
    print(f"Created {final_output.resolve()}")
