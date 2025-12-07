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
MARGIN_LEFT = 13 * mm  # 1.3 cm
MARGIN_RIGHT = 5 * mm  # 0.5 cm
TEXT_VERTICAL_ADJUST = 0.5 * mm  # fine-tune vertical position of text

LINE_Y = PAGE_HEIGHT - (2 * DOT_SPACING)  # 2nd dot row from top
LINE_X_START = MARGIN_LEFT
LINE_X_SPLIT = LINE_X_START + 85 * mm  # 8.5 cm first line length
LINE_X_GAP = 5 * mm  # 5 mm gap
LINE_X_RESUME = LINE_X_SPLIT + LINE_X_GAP
LINE_X_END = LINE_X_RESUME + 35 * mm  # 35 mm second line length

# Vertical line starting point
VERTICAL_LINE_X = LINE_X_SPLIT
VERTICAL_LINE_Y_START = LINE_Y
VERTICAL_LINE_Y_END = LINE_Y - (155 * mm)  # 15.5 cm down

# Calendar settings
year, month = 2025, 11
cal = calendar.Calendar(firstweekday=0)
month_name_full = calendar.month_name[month].upper()  # full month name
month_name_short = calendar.month_name[month][:3].upper()

# Dot settings
DOT_RADIUS = 0.25 * mm  # smaller dots
LINE_WIDTH = DOT_RADIUS * 2
GREY_LINE_WIDTH = DOT_RADIUS * 1.2  # slightly thinner grey line

# Fonts
TEXT_FONT_FILE = "Merienda/static/Merienda-Medium.ttf"
BOLD_FONT_FILE = "Merienda/static/Merienda-Black.ttf"
LIGHT_FONT_FILE = "Merienda/static/Merienda-Light.ttf"
LIGHT_FONT = "Merienda_light"
TEXT_FONT = "Merienda_medium"
BOLD_FONT = "Merienda_black"

# Register custom fonts
pdfmetrics.registerFont(TTFont(TEXT_FONT, TEXT_FONT_FILE))
pdfmetrics.registerFont(TTFont(BOLD_FONT, BOLD_FONT_FILE))
pdfmetrics.registerFont(TTFont(LIGHT_FONT, LIGHT_FONT_FILE))


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


def draw_first_page(c):
    draw_dot_grid(c)
    c.saveState()
    c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
    c.rotate(90)  # 90 degrees counterclockwise
    font_size = 80
    c.setFont(TEXT_FONT, font_size)
    text_width = c.stringWidth(month_name_full, TEXT_FONT, font_size)
    c.drawString(-text_width / 2, -font_size / 2, month_name_full)
    c.restoreState()


def draw_bullet_line(c, text, x, y, font_name=TEXT_FONT, font_size=10, bullet_size=12):
    # Draw the bullet
    bullet = "• "
    c.setFont(font_name, bullet_size)
    bullet_width = c.stringWidth(bullet, font_name, bullet_size)
    draw_text_vertically_centered(c, bullet, x, y, font_name, bullet_size)

    # Draw the text next to it
    c.setFont(font_name, font_size)
    draw_text_vertically_centered(
        c, text, x + bullet_width + 2, y, font_name, font_size
    )


def draw_second_page(c):
    draw_dot_grid(c, mirror_margins=True)
    headings = ["MONTHLY TASKS", "ADMINISTRATIVE", "HOME", "OTHER"]
    line_spacings = [0, 35 * mm, 60 * mm, 55 * mm]
    current_y = PAGE_HEIGHT - (2 * DOT_SPACING)

    for i, heading in enumerate(headings):
        # c.setLineWidth(LINE_WIDTH)
        # c.line(MARGIN_RIGHT, current_y, PAGE_WIDTH - MARGIN_LEFT, current_y)
        draw_text_vertically_centered(c, heading, MARGIN_RIGHT, current_y, TEXT_FONT)
        # If we're at MONTHLY TASKS, add the bullet list
        if heading == "MONTHLY TASKS":
            tasks = [
                "Prepare monthly spread",
                "Update family budget sheet",
                "Change cat's fountain filter",
                "Book canteen for next month",
                "Change cat's fountain filter x2",
            ]

            bullet_font_size = 10
            task_y = current_y - DOT_SPACING  # a bit of space below heading

            for task in tasks:
                x_pos = MARGIN_RIGHT + DOT_SPACING / 2 - 1
                draw_bullet_line(
                    c, task, x_pos, task_y, LIGHT_FONT, bullet_font_size, bullet_size=12
                )
                task_y -= DOT_SPACING  # skip one grid row between tasks

        if i < len(line_spacings) - 1:
            current_y -= line_spacings[i + 1]


def draw_layout(c):
    c.setLineWidth(LINE_WIDTH)
    c.line(LINE_X_START, LINE_Y, LINE_X_SPLIT, LINE_Y)
    c.line(LINE_X_RESUME, LINE_Y, LINE_X_END, LINE_Y)
    c.line(VERTICAL_LINE_X, VERTICAL_LINE_Y_START, VERTICAL_LINE_X, VERTICAL_LINE_Y_END)

    draw_text_vertically_centered(c, "TIMELINE", LINE_X_START, LINE_Y, TEXT_FONT)

    sep_text = month_name_short
    total_width = len(sep_text) * DOT_SPACING
    sep_start_x = LINE_X_RESUME + (35 * mm - total_width) / 2
    draw_text_across_grid(c, sep_text, sep_start_x, LINE_Y, BOLD_FONT)

    new_line_y = VERTICAL_LINE_Y_END - 10 * mm
    c.line(LINE_X_START, new_line_y, LINE_X_END, new_line_y)
    draw_text_vertically_centered(c, "NEXT MONTH", LINE_X_START, new_line_y, TEXT_FONT)

    top_35mm_y = LINE_Y
    monthly_tasks_y = top_35mm_y - 40 * mm
    monthly_tasks_line_length = 35 * mm
    c.line(
        LINE_X_RESUME,
        monthly_tasks_y,
        LINE_X_RESUME + monthly_tasks_line_length,
        monthly_tasks_y,
    )
    draw_text_vertically_centered(
        c,
        "MONTHLY TASKS",
        LINE_X_RESUME,
        monthly_tasks_y,
        TEXT_FONT,
    )
    c.line(LINE_X_RESUME, monthly_tasks_y, LINE_X_RESUME, monthly_tasks_y - 5 * mm)

    legend_y = monthly_tasks_y - 15 * mm
    c.line(LINE_X_RESUME, legend_y, LINE_X_RESUME + monthly_tasks_line_length, legend_y)
    draw_text_vertically_centered(c, "LEGEND", LINE_X_RESUME, legend_y, TEXT_FONT)

    additional_texts = [
        "Call Grandma",
        "Call Dad",
        "Call Mom",
        "Sports",
        "PhD",
        "Music",
        "Dancing",
        "Therapy",
        "Date Night",
        "",  # empty line
        "Important",
        "Birthdays",
        "Other",
        "Trips",
        "Schulferien",
        "Holidays",
    ]
    text_y = legend_y - DOT_SPACING
    smaller_font_size = 10  # 1 size smaller
    for line in additional_texts:
        if line == "":
            text_y -= DOT_SPACING
            continue
        draw_text_vertically_centered(
            c, line, LINE_X_RESUME + 5 * mm, text_y, TEXT_FONT, smaller_font_size
        )
        text_y -= DOT_SPACING

    # Calendar grid with colored weekends and grey lines under Sundays
    days_in_month = calendar.monthrange(year, month)[1]
    y = LINE_Y - DOT_SPACING
    for d in range(1, days_in_month + 1):
        weekday = calendar.weekday(year, month, d)
        color = colors.red if weekday >= 5 else colors.black
        draw_text_in_cell(c, str(d), LINE_X_START, y, TEXT_FONT, 9, color=color)
        if weekday == 6:
            line_y = y
            c.setStrokeColor(colors.lightgrey)
            c.setLineWidth(GREY_LINE_WIDTH)
            c.line(
                LINE_X_START + 2 * DOT_SPACING, line_y, VERTICAL_LINE_X - 5 * mm, line_y
            )
            c.setStrokeColor(colors.black)
        y -= DOT_SPACING

    # Draw calendar on the right
    start_x = LINE_X_RESUME
    start_y = LINE_Y - DOT_SPACING
    week_y = start_y
    for week in cal.monthdayscalendar(year, month):
        x = start_x
        for day in week:
            if day != 0:
                draw_text_in_cell(c, str(day), x, week_y, TEXT_FONT, 9)
            x += DOT_SPACING
        week_y -= DOT_SPACING


def create_pdf(filename=None):
    if filename is None:
        filename = f"bullet_journal_{year}_{month}.pdf"

    c = canvas.Canvas(filename, pagesize=A5)
    # First page
    draw_first_page(c)
    c.showPage()
    # Second page
    draw_second_page(c)
    c.showPage()
    # Third page
    draw_dot_grid(c)
    draw_layout(c)
    c.showPage()
    # Fourth page
    draw_dot_grid(c, mirror_margins=True)
    c.showPage()
    c.save()


if __name__ == "__main__":
    create_pdf()
