import asyncio
import itertools


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


async def animate_frames(canvas, start_row, start_column, frames):
    frames_cycle = itertools.cycle(frames)
    height, width = canvas.getmaxyx()
    border_size = 1

    current_frame = next(frames_cycle)
    frame_size_y, frame_size_x = get_frame_size(current_frame)
    frame_pos_x = round(start_column) - round(frame_size_x / 2)
    frame_pos_y = round(start_row) - round(frame_size_y / 2)

    while True:
        for _ in range(2):
            direction_y, direction_x, _ = read_controls(canvas)

            frame_pos_x += direction_x
            frame_pos_y += direction_y

            frame_x_max = frame_pos_x + frame_size_x
            frame_y_max = frame_pos_y + frame_size_y

            field_x_max = width - border_size
            field_y_max = height - border_size

            frame_pos_x = min(frame_x_max, field_x_max) - frame_size_x
            frame_pos_y = min(frame_y_max, field_y_max) - frame_size_y

            frame_pos_x = max(frame_pos_x, border_size)
            frame_pos_y = max(frame_pos_y, border_size)

            draw_frame(canvas, frame_pos_y, frame_pos_x, current_frame)
            canvas.refresh()

            await asyncio.sleep(0)

            draw_frame(
                canvas,
                frame_pos_y,
                frame_pos_x,
                current_frame,
                negative=True
            )

        current_frame = next(frames_cycle)


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas. Erase text instead of drawing
    if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            # Check that current position it is not in a lower
            # right corner of the window.

            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/urses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment. Returns pair (rows number,
    colums number)"""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed
