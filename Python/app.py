import csv
import os
import platform
import subprocess
from datetime import datetime
from collections import deque

import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

SERIAL_PORT = "/dev/tty.usbmodem142201"   
BAUD_RATE = 9600
MAX_POINTS = 30

OUTPUT_DIR = "output"

CSV_FILE = os.path.join(OUTPUT_DIR, "bpm_log.csv")
PDF_FILE = os.path.join(OUTPUT_DIR, "Heart_Rate_Report.pdf")
CHART_FILE = os.path.join(OUTPUT_DIR, "bpm_chart.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIN_BPM = 40
MAX_BPM = 140

AUTHOR_NAME = "Ahmed Gamal"
GITHUB_LINK = "https://github.com/AGamal-X"
LINKEDIN_LINK = "https://www.linkedin.com/in/ahmdgamall/"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

x_data = deque(maxlen=MAX_POINTS)
y_data = deque(maxlen=MAX_POINTS)

all_readings = []
session_rows = []
reading_index = 0
last_bpm = None


def get_status(bpm: int) -> str:
    if bpm < 60:
        return "Low"
    if bpm <= 100:
        return "Normal"
    if bpm <= 120:
        return "Elevated"
    return "High"


def is_valid_bpm(bpm: int) -> bool:
    return MIN_BPM <= bpm <= MAX_BPM


def save_reading(timestamp_text: str, index: int, bpm: int, status: str) -> None:
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp_text, index, bpm, status])


def get_overall_status(avg_bpm: float) -> str:
    if avg_bpm < 60:
        return "Low"
    if avg_bpm <= 100:
        return "Normal"
    if avg_bpm <= 120:
        return "Elevated"
    return "High"


def get_trend(first_bpm: int, last_bpm: int) -> str:
    difference = last_bpm - first_bpm

    if difference >= 8:
        return "Increasing"
    if difference <= -8:
        return "Decreasing"
    return "Stable"


def get_variation(min_bpm: int, max_bpm: int) -> str:
    spread = max_bpm - min_bpm

    if spread <= 10:
        return "Low"
    if spread <= 20:
        return "Moderate"
    return "High"


def get_summary(bpm_values: list[int]) -> dict:
    average_bpm = sum(bpm_values) / len(bpm_values)
    min_bpm = min(bpm_values)
    max_bpm = max(bpm_values)
    first_bpm = bpm_values[0]
    last_bpm = bpm_values[-1]

    return {
        "total_readings": len(bpm_values),
        "average_bpm": average_bpm,
        "min_bpm": min_bpm,
        "max_bpm": max_bpm,
        "first_bpm": first_bpm,
        "last_bpm": last_bpm,
        "overall_status": get_overall_status(average_bpm),
        "trend": get_trend(first_bpm, last_bpm),
        "variation": get_variation(min_bpm, max_bpm),
    }


def get_conclusion(summary: dict) -> str:
    avg_bpm = summary["average_bpm"]
    trend = summary["trend"]
    variation = summary["variation"]
    total_readings = summary["total_readings"]

    if total_readings < 5:
        return (
            "The session includes a limited number of readings, so the result should be treated "
            "as an initial estimate rather than a strong heart rate trend."
        )

    if avg_bpm < 60:
        return (
            f"The session shows a relatively low average heart rate with a {trend.lower()} trend "
            f"and {variation.lower()} variation. This may be normal during rest or in fit individuals, "
            "but weaker sensor contact may also affect some readings."
        )

    if avg_bpm <= 100:
        return (
            f"The session shows a normal average heart rate with a {trend.lower()} trend "
            f"and {variation.lower()} variation. The readings appear reasonable for a resting "
            "or lightly active condition."
        )

    if avg_bpm <= 120:
        return (
            f"The session shows a moderately elevated average heart rate with a {trend.lower()} trend "
            f"and {variation.lower()} variation. This may happen because of recent activity, movement, "
            "stress, or unstable finger placement."
        )

    return (
        f"The session shows a high average heart rate with a {trend.lower()} trend "
        f"and {variation.lower()} variation. This may reflect physical effort, unstable measurement, "
        "or a genuinely elevated pulse."
    )


def get_recommendation(summary: dict) -> str:
    avg_bpm = summary["average_bpm"]
    variation = summary["variation"]
    total_readings = summary["total_readings"]

    if total_readings < 5:
        return (
            "Record a longer session with steadier finger placement so the system can provide "
            "a more reliable summary."
        )

    if variation == "High":
        return (
            "Repeat the session with better finger stability and less movement. High variation "
            "usually indicates changing signal quality during measurement."
        )

    if avg_bpm < 60:
        return (
            "Repeat the measurement under stable resting conditions and compare it with a manual pulse count "
            "or another trusted device for validation."
        )

    if avg_bpm <= 100:
        return (
            "Keep using stable finger placement and record longer sessions to improve consistency "
            "and make the trend more representative."
        )

    if avg_bpm <= 120:
        return (
            "Repeat the session after resting for a few minutes in a calm seated position, "
            "and compare the result with a reference device if needed."
        )

    return (
        "Repeat the session in a calm resting state and compare the results with a reliable reference device. "
        "If high readings stay consistent, the result deserves closer attention."
    )


def create_chart(bpm_values: list[int], chart_file: str):
    x_values = list(range(len(bpm_values)))

    plt.figure(figsize=(9, 4.5))
    plt.plot(x_values, bpm_values, marker="o", linewidth=2)
    plt.title("Heart Rate Readings")
    plt.xlabel("Reading Number")
    plt.ylabel("BPM")
    plt.ylim(40, 140)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(chart_file, dpi=150)
    plt.close()


def build_pdf(pdf_file: str, rows: list[dict], bpm_values: list[int], chart_file: str):
    summary = get_summary(bpm_values)
    conclusion = get_conclusion(summary)
    recommendation = get_recommendation(summary)

    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        leading=16,
        spaceAfter=8
    )

    link_style = ParagraphStyle(
        "LinkStyle",
        parent=styles["BodyText"],
        textColor=colors.HexColor("#1a73e8"),
        leading=15
    )

    elements = []
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    elements.append(Paragraph("Heart Rate Monitoring Report", styles["Title"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Generated on: {created_at}", styles["Normal"]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f"Prepared by: {AUTHOR_NAME}", styles["Normal"]))
    elements.append(Paragraph(f'GitHub: <link href="{GITHUB_LINK}">{GITHUB_LINK}</link>', link_style))
    elements.append(Paragraph(f'LinkedIn: <link href="{LINKEDIN_LINK}">{LINKEDIN_LINK}</link>', link_style))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Session Summary", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    summary_data = [
        ["Total Readings", str(summary["total_readings"])],
        ["First BPM", str(summary["first_bpm"])],
        ["Last BPM", str(summary["last_bpm"])],
        ["Average BPM", f'{summary["average_bpm"]:.1f}'],
        ["Minimum BPM", str(summary["min_bpm"])],
        ["Maximum BPM", str(summary["max_bpm"])],
        ["Overall Status", summary["overall_status"]],
        ["Trend", summary["trend"]],
        ["Variation", summary["variation"]],
    ]

    summary_table = Table(summary_data, colWidths=[170, 180])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Heart Rate Trend", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Image(chart_file, width=500, height=250))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Conclusion", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(conclusion, body_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Recommendation", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(recommendation, body_style))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Recorded Data", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    table_data = [["Timestamp", "Reading #", "BPM", "Status"]]
    for row in rows:
        table_data.append([
            row["Timestamp"],
            row["ReadingNumber"],
            row["BPM"],
            row["Status"]
        ])

    data_table = Table(table_data, repeatRows=1, colWidths=[180, 70, 60, 90])
    data_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E3A46")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    elements.append(data_table)
    doc.build(elements)


def open_file(path: str):
    system_name = platform.system()

    try:
        if system_name == "Darwin":
            subprocess.run(["open", path], check=False)
        elif system_name == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception as error:
        print(f"Could not open file automatically: {error}")


with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "ReadingNumber", "BPM", "Status"])

fig, ax = plt.subplots(figsize=(10, 6))
line, = ax.plot([], [], marker="o", linewidth=2)

ax.set_title("Live Heart Rate Monitoring", fontsize=16, pad=15)
ax.set_xlabel("Reading Number", fontsize=11)
ax.set_ylabel("BPM", fontsize=11)
ax.set_ylim(40, 140)
ax.set_xlim(0, MAX_POINTS)
ax.grid(True, alpha=0.3)

stats_text = ax.text(
    0.02,
    0.96,
    "",
    transform=ax.transAxes,
    verticalalignment="top",
    fontsize=10,
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85, edgecolor="lightgray")
)

instruction_text = ax.text(
    0.5,
    -0.18,
    "Keep your finger steady for 20–30 seconds before closing the window to ensure an accurate report.",
    transform=ax.transAxes,
    ha="center",
    va="top",
    fontsize=10
)


def update(frame):
    global reading_index, last_bpm

    try:
        raw_line = ser.readline().decode(errors="ignore").strip()

        if raw_line.startswith("BPM:"):
            bpm = int(raw_line.split(":")[1])

            if is_valid_bpm(bpm) and bpm != last_bpm:
                timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status = get_status(bpm)

                x_data.append(reading_index)
                y_data.append(bpm)
                all_readings.append(bpm)

                row = {
                    "Timestamp": timestamp_text,
                    "ReadingNumber": str(reading_index),
                    "BPM": str(bpm),
                    "Status": status
                }
                session_rows.append(row)
                save_reading(timestamp_text, reading_index, bpm, status)

                print(f"[{timestamp_text}] BPM: {bpm} | Status: {status}")

                line.set_data(x_data, y_data)

                reading_index += 1
                last_bpm = bpm

                if reading_index > MAX_POINTS:
                    ax.set_xlim(reading_index - MAX_POINTS, reading_index)
                else:
                    ax.set_xlim(0, MAX_POINTS)

                avg_bpm = sum(all_readings) / len(all_readings)
                min_bpm = min(all_readings)
                max_bpm = max(all_readings)

                stats_text.set_text(
                    f"Last BPM: {bpm}\n"
                    f"Status: {status}\n"
                    f"Average: {avg_bpm:.1f}\n"
                    f"Min: {min_bpm}\n"
                    f"Max: {max_bpm}"
                )

    except Exception as error:
        print("Error:", error)

    return line, stats_text, instruction_text


ani = FuncAnimation(fig, update, interval=500, cache_frame_data=False)
plt.tight_layout()
plt.subplots_adjust(bottom=0.22)
plt.show()

ser.close()

if all_readings:
    create_chart(all_readings, CHART_FILE)
    build_pdf(PDF_FILE, session_rows, all_readings, CHART_FILE)
    print(f"\nReport created: {PDF_FILE}")
    open_file(PDF_FILE)
else:
    print("\nNo valid BPM readings were recorded.")