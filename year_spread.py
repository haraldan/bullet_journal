import calendar

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# --- SETTINGS ---
PAGE_WIDTH, PAGE_HEIGHT = A5
DOT_SPACING = 5 * mm
MARGIN_LEFT = 13 * mm
MARGIN_RIGHT = 5 * mm
TEXT_VERTICAL_ADJUST = 0.5 * mm
DOT_RADIUS = 0.25 * mm
LINE_WIDTH = DOT_RADIUS * 2

# Fonts
TEXT_FONT_FILE = "Merienda/static/Merienda-Medium.ttf"
BOLD_FONT_FILE = "Merienda/static/Merienda-Black.ttf"
TEXT_FONT = "Merienda_medium"
BOLD_FONT = "Merienda_black"
pdfmetrics.registerFont(TTFont(TEXT_FONT, TEXT_FONT_FILE))
pdfmetrics.registerFont(TTFont(BOLD_FONT, BOLD_FONT_FILE))

year = 2025
cal = calendar.Calendar(firstweekday=0)


def draw_dot_grid(c, mirror_margins=False):
    c.setFillGray(0.7)
    left_margin = MARGIN_LEFT
    right_margin = MARGIN_RIGHT
    if mirror_margins:
        left_margin, right_margin = MARGIN_RIGHT, MARGIN_LEFT
    x = left_margin
    while x <= PAGE_WIDTH - right_margin:
        y = DOT_SPACING
        while y <= PAGE_HEIGHT - DOT_SPACING:
            c.circle(x, y, DOT_RADIUS, fill=1, stroke=0)
            y += DOT_SPACING
        x += DOT_SPACING
    c.setFillGray(0)


def draw_text_in_cell(
    c, text, x, y, font_name=TEXT_FONT, font_size=9, color=colors.black
):
    c.setFont(font_name, font_size)
    c.setFillColor(color)
    text_width = c.stringWidth(text, font_name, font_size)
    ascent = c._fontsize * 0.8
    descent = c._fontsize * 0.2
    text_height = ascent + descent
    cx = x + (DOT_SPACING - text_width) / 2
    cy = y + (DOT_SPACING - text_height) / 2 + descent - TEXT_VERTICAL_ADJUST
    c.drawString(cx, cy, text)
    c.setFillColor(colors.black)


def draw_text_vertically_centered(c, text, x, y, font_name=TEXT_FONT, font_size=11):
    c.setFont(font_name, font_size)
    cy = y + (DOT_SPACING - font_size * 0.8) / 2
    c.drawString(x, cy, text)


def draw_text_across_grid(c, text, start_x, base_y, font_name=BOLD_FONT, font_size=11):
    c.setFont(font_name, font_size)
    x = start_x
    for letter in text:
        draw_text_in_cell(c, letter, x, base_y, font_name, font_size)
        x += DOT_SPACING


def draw_title_page(c, title):
    draw_dot_grid(c)
    c.saveState()
    c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
    c.rotate(90)  # 90 degrees counterclockwise
    font_size = 80
    c.setFont(TEXT_FONT, font_size)
    text_width = c.stringWidth(title, TEXT_FONT, font_size)
    c.drawString(-text_width / 2, -font_size / 2, title)
    c.restoreState()


def draw_year_page(c, year):
    draw_dot_grid(c)
    str_year = str(year)
    top_pair = str_year[:2]
    bottom_pair = str_year[2:]
    font_size = 180
    gap = 20  # gap between top and bottom pair

    c.setFont(TEXT_FONT, font_size)

    # Approximate ascent for centering
    ascent = font_size * 0.8  # typical ascent factor

    total_height = ascent + gap + ascent  # top + gap + bottom

    # Starting y so total block is vertically centered
    y_start = (PAGE_HEIGHT - total_height) / 2 + gap

    # X positions to center horizontally
    x_top = PAGE_WIDTH / 2 - c.stringWidth(top_pair, TEXT_FONT, font_size) / 2
    x_bottom = PAGE_WIDTH / 2 - c.stringWidth(bottom_pair, TEXT_FONT, font_size) / 2

    # Draw top and bottom pairs
    c.drawString(x_top, y_start + ascent + gap, top_pair)
    c.drawString(x_bottom, y_start, bottom_pair)


def draw_calendar(c, month, start_x, start_y):
    y = start_y
    for week in cal.monthdayscalendar(year, month):
        x = start_x
        for day in week:
            if day != 0:
                draw_text_in_cell(c, str(day), x, y)
            x += DOT_SPACING
        y -= DOT_SPACING
    return y


def draw_calendar_page(c, months, mirror=False):
    draw_dot_grid(c, mirror_margins=not mirror)

    left_margin = MARGIN_RIGHT if not mirror else MARGIN_LEFT
    right_margin = MARGIN_LEFT if not mirror else MARGIN_RIGHT
    line_length_left = 35 * mm
    line_gap = 5 * mm
    current_y = PAGE_HEIGHT - 2 * DOT_SPACING

    # Compute last dot column based on the dot grid
    x_start = left_margin
    x_end = PAGE_WIDTH - right_margin
    num_dots = int((x_end - x_start) / DOT_SPACING)
    last_dot_x = x_start + num_dots * DOT_SPACING

    for month in months:
        # Draw horizontal line with gap
        c.setLineWidth(LINE_WIDTH)
        c.line(left_margin, current_y, left_margin + line_length_left, current_y)
        c.line(
            left_margin + line_length_left + line_gap, current_y, last_dot_x, current_y
        )

        # Draw month abbreviation above the left line
        abbrev = calendar.month_name[month][:3].upper()
        total_width = len(abbrev) * DOT_SPACING
        sep_start_x = left_margin + (line_length_left - total_width) / 2
        draw_text_across_grid(c, abbrev, sep_start_x, current_y, font_name=TEXT_FONT)

        # Draw calendar directly below the line
        draw_calendar(c, month, left_margin, current_y - DOT_SPACING)

        # Move to next line 55mm below current
        current_y -= 55 * mm

    # Draw "MISC" line below last month
    c.line(left_margin, current_y, last_dot_x, current_y)
    if mirror:
        draw_text_vertically_centered(c, "LEGEND", left_margin, current_y)

        additional_texts = [
            "Important",
            "Birthdays",
            "Other",
            "Trips",
            "Schulferien",
            "NRW Feiertage",
        ]
        smaller_font_size = 10  # 1 size smaller
        for line in additional_texts:
            current_y -= DOT_SPACING
            draw_text_vertically_centered(
                c, line, left_margin + 5 * mm, current_y, TEXT_FONT, smaller_font_size
            )
    else:
        draw_text_vertically_centered(c, "MISC", left_margin, current_y)


def create_pdf(filename=None):
    if filename is None:
        filename = f"bullet_journal_{year}_full.pdf"
    c = canvas.Canvas(filename, pagesize=A5)

    # Page 1: Year
    draw_year_page(c, year)
    c.showPage()

    # Page 2: Jan–Mar, mirrored margins as before
    draw_calendar_page(c, [1, 2, 3], mirror=False)
    c.showPage()

    # Page 3: Apr–Jun, mirrored
    draw_calendar_page(c, [4, 5, 6], mirror=True)
    c.showPage()

    # Page 4: Jul–Sep, mirrored margins like page 2
    draw_calendar_page(c, [7, 8, 9], mirror=False)
    c.showPage()

    # Page 5: Oct–Dec, mirrored like page 3
    draw_calendar_page(c, [10, 11, 12], mirror=True)
    c.showPage()

    draw_dot_grid(c, mirror_margins=True)
    c.showPage()

    c.save()


if __name__ == "__main__":
    create_pdf()
