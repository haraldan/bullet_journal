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
    cy = y + (DOT_SPACING - font_size) / 2
    c.drawString(x, cy, text)

def draw_text_right_justified(c, text, x, y, font_name=TEXT_FONT, font_size=11):
    c.setFont(font_name, font_size)
    text_width = c.stringWidth(text, font_name, font_size)
    cx = x - text_width  # move left by text width to right-justify
    cy = y + (DOT_SPACING - font_size) / 2  # vertically center between dots
    c.drawString(cx, cy, text)


def draw_text_across_grid(c, text, start_x, base_y, font_name=BOLD_FONT, font_size=11):
    c.setFont(font_name, font_size)
    x = start_x
    for letter in text:
        draw_text_in_cell(c, letter, x, base_y, font_name, font_size)
        x += DOT_SPACING

def draw_title_page(c,title):
    draw_dot_grid(c)
    c.saveState()
    c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
    c.rotate(90)  # 90 degrees counterclockwise
    font_size = 80
    c.setFont(TEXT_FONT, font_size)
    text_width = c.stringWidth(title, TEXT_FONT, font_size)
    c.drawString(-text_width / 2, -font_size / 2, title)
    c.restoreState()

def draw_full_grid_page(c, mirror=False, text="" ):
    # Draw dotted background
    draw_dot_grid(c, mirror_margins=not mirror)

    # Calculate margins
    left_margin = MARGIN_RIGHT if not mirror else MARGIN_LEFT
    right_margin = MARGIN_LEFT if not mirror else MARGIN_RIGHT
    x_start = left_margin
    x_end = PAGE_WIDTH - right_margin
    y_start = DOT_SPACING
    y_end = PAGE_HEIGHT - DOT_SPACING

    # Compute dot columns and rows
    num_cols = int((x_end - x_start) / DOT_SPACING) + 1
    dot_columns = [x_start + i * DOT_SPACING for i in range(num_cols)]

    num_rows = int((y_end - y_start) / DOT_SPACING) + 1
    dot_rows = [y_start + i * DOT_SPACING for i in range(num_rows)]

    # Determine bottom limit for mirrored pages
    bottom_limit = 40 * mm if mirror else dot_rows[0]

    # --- Horizontal lines ---
    for i, y in enumerate(dot_rows):
        # Skip lowest line on mirrored pages
        if mirror and i == 0:
            continue
        # Skip lines below bottom limit
        if mirror and y < bottom_limit:
            continue
        if text and i == num_rows - 1:
            # Shortened top line
            c.line(dot_columns[1], y, dot_columns[-3], y)
        else:
            # Full width
            c.line(dot_columns[0], y, dot_columns[-1], y)

    # --- Vertical lines ---
    bottom_limit = bottom_limit-5 * mm
    vertical_indices = [1, num_cols - 3, num_cols - 2]
    vertical_columns = [dot_columns[i] for i in vertical_indices]

    top_y_index = -2 if text else -1
    top_y = dot_rows[top_y_index]

    for x in vertical_columns:
        c.line(x, bottom_limit, x, top_y)  # x fixed, from bottom limit to top

    # --- Add page text ---
    if text:
        text_y = dot_rows[-2]
        text_x = vertical_columns[0]
        draw_text_vertically_centered(c, text, text_x, text_y)

    # --- Add ratings text ---
    if mirror:
        smaller_font_size = 10
        ratings = ["Great", "Good", "OK", "Meh", "Didn't finish"][::-1]
        start_y = dot_rows[0]
        x_pos = dot_columns[-1] - 30 * mm
        for i, rating in enumerate(ratings):
            y_pos = start_y + i * DOT_SPACING
            draw_text_vertically_centered(c, rating, x_pos, y_pos,font_size=smaller_font_size)

        # --- Add right-justified tracking text ---
        tracking_lines = ["New", "Repeat", "Previously unfinished"][::-1]
        start_row_index = 1  # 2nd row from bottom
        x_pos = dot_columns[-1] - 45 * mm  # 45 mm from rightmost dot column
        for i, line in enumerate(tracking_lines):
            y_pos = dot_rows[start_row_index + i]
            draw_text_right_justified(c, line, x_pos, y_pos,font_size=smaller_font_size)






def create_pdf(filename=None):
    if filename is None:
        filename = f"bullet_journal_2025_books.pdf"
    c = canvas.Canvas(filename, pagesize=A5)

    draw_title_page(c,"BOOKS")
    c.showPage()

    draw_full_grid_page(c,False,"FANTASY & SCI_FI")
    c.showPage()
    draw_full_grid_page(c,True,"")
    c.showPage()
    draw_full_grid_page(c,False,"MODERN PROSE & NON-FICTION")
    c.showPage()
    draw_full_grid_page(c,True,"FOREIGN LANGUAGES")
    c.showPage()
    draw_dot_grid(c)
    c.showPage()

    draw_title_page(c,"MOVIES")
    c.showPage()
    draw_full_grid_page(c,False,"LIGHT FILMS")
    c.showPage()
    draw_full_grid_page(c,True,"")
    c.showPage()
    draw_full_grid_page(c,False,"SERIOUS FILMS")
    c.showPage()
    draw_full_grid_page(c,True,"")
    c.showPage()
    draw_full_grid_page(c,False,"LIGHT SERIES")
    c.showPage()
    draw_full_grid_page(c,True,"")
    c.showPage()
    draw_full_grid_page(c,False,"SERIOUS SERIES")
    c.showPage()
    draw_full_grid_page(c,True,"")
    c.showPage()
    draw_full_grid_page(c,False,"GAMES")
    c.showPage()
    draw_full_grid_page(c,True,"")
    c.showPage()
    draw_dot_grid(c)
    c.showPage()

    c.save()


if __name__ == "__main__":
    create_pdf()
