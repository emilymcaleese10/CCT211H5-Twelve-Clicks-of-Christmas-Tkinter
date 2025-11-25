import tkinter as tk

def round_rect(canvas, x1, y1, x2, y2, r=35, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def pill(canvas, x1, y1, x2, y2, **kwargs):
    r = (y2 - y1) // 2
    canvas.create_oval(x1, y1, x1 + 2*r, y2, **kwargs)
    canvas.create_oval(x2 - 2*r, y1, x2, y2, **kwargs)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
