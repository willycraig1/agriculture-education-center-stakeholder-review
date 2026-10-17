"""Side-view figures in local feet (x right, y up). Each returns list of (pts, mat, ink)."""
import numpy as np

def chaikin(pts, it=2, closed=True):
    p = np.array(pts, float)
    for _ in range(it):
        q = []
        n = len(p)
        rng = range(n) if closed else range(n - 1)
        for i in rng:
            a, b = p[i], p[(i + 1) % n]
            q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        if not closed:
            q = [p[0]] + q + [p[-1]]
        p = np.array(q)
    return p

def circle(cx, cy, r, n=28):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([cx + r * np.cos(t), cy + r * np.sin(t)], 1)

def cow():
    P = []
    P.append((chaikin([(5.2, 2.5), (6.0, 2.6), (5.55, 1.35), (5.55, 0.25), (5.15, 0.25), (5.1, 1.4)], 1), 'cow_dark', True))  # rear far leg
    P.append((chaikin([(1.75, 2.5), (2.25, 2.5), (2.15, 0.25), (1.75, 0.25)], 1), 'cow_dark', True))  # front far leg
    P.append((chaikin([(0.9, 3.2), (1.2, 4.3), (2.0, 4.6), (4.0, 4.45), (5.6, 4.62), (6.6, 4.45), (7.05, 3.85),
                       (7.0, 2.9), (6.6, 2.35), (5.6, 2.3), (3.5, 2.15), (1.8, 2.25), (1.0, 2.6)], 2), 'cow_body', True))
    P.append((chaikin([(1.2, 2.55), (1.75, 2.5), (1.45, 0.25), (1.0, 0.25)], 1), 'cow_body', True))  # front near leg
    P.append((chaikin([(5.6, 2.7), (6.6, 2.9), (6.2, 1.35), (6.35, 0.25), (5.9, 0.25), (5.75, 1.3)], 1), 'cow_body', True))  # rear near leg
    # white brisket / underline
    P.append((chaikin([(1.0, 2.7), (1.6, 2.35), (2.4, 2.3), (1.9, 2.8), (1.2, 3.3)], 1), 'cow_white', False))
    # neck + head (white face)
    P.append((chaikin([(1.5, 4.35), (0.9, 4.45), (0.35, 4.2), (0.6, 3.1), (1.2, 2.8)], 1), 'cow_body', True))
    P.append((chaikin([(0.55, 4.25), (0.15, 4.25), (-0.45, 3.75), (-0.85, 3.15), (-0.85, 2.8), (-0.5, 2.7),
                       (0.0, 2.95), (0.55, 3.15)], 1), 'cow_white', True))
    P.append(([(0.15, 4.05), (-0.2, 4.45), (0.4, 4.2)], 'cow_body', True))  # ear
    P.append((circle(-0.68, 2.92, 0.17, 12), 'cow_nose', False))
    for x0 in (1.0, 1.75, 5.15, 5.9):
        P.append(([(x0 - 0.05, 0.0), (x0 + 0.5, 0.0), (x0 + 0.45, 0.28), (x0, 0.28)], 'hoof', False))
    return P

def cow_lines():
    # tail + halter as (pts, mat, width_ft)
    L = []
    L.append((chaikin([(7.0, 4.25), (7.25, 3.4), (7.2, 1.7)], 2, closed=False), 'cow_dark', 0.12))
    L.append(([(-0.05, 3.9), (-0.3, 2.95)], 'halter', 0.07))
    L.append(([(-0.7, 3.2), (-0.15, 3.35)], 'halter', 0.07))
    return L

def tail_tuft():
    return [(chaikin([(7.05, 1.9), (7.4, 1.8), (7.35, 1.3), (7.1, 1.2), (6.95, 1.5)], 1), 'cow_dark', False)]

def student():
    P = []
    P.append(([(0.05, 3.0), (0.45, 3.05), (0.9, 0.38), (0.55, 0.32)], 'jeans_dark', True))   # back leg
    P.append(([(0.5, 0.0), (1.1, 0.0), (1.02, 0.38), (0.56, 0.38)], 'boot', True))
    P.append(([(0.95, 3.38), (0.45, 4.5), (0.2, 4.4), (0.8, 3.3)], 'shirt_dark', True))     # far arm, reaching back
    P.append((circle(0.92, 3.3, 0.13, 10), 'skin', False))
    P.append(([(-0.2, 3.0), (0.32, 3.05), (-0.5, 0.4), (-0.92, 0.45)], 'jeans', True))      # front leg
    P.append(([(-1.35, 0.0), (-0.6, 0.0), (-0.58, 0.42), (-1.0, 0.48)], 'boot', True))
    P.append((chaikin([(-0.38, 3.0), (0.45, 3.0), (0.52, 3.9), (0.42, 4.65), (0.05, 4.85), (-0.35, 4.68), (-0.45, 3.9)], 1), 'shirt', True))
    P.append(([(-0.05, 3.15), (0.42, 3.15), (0.42, 2.98), (-0.05, 2.98)], 'belt', False))
    P.append(([(-0.12, 4.75), (0.12, 4.75), (0.1, 4.95), (-0.1, 4.95)], 'skin', False))
    P.append((circle(-0.05, 5.17, 0.38, 20), 'skin', True))
    P.append((chaikin([(0.05, 5.35), (0.38, 5.05), (0.42, 4.75), (0.28, 4.85), (0.25, 5.1)], 1), 'hair', False))  # ponytail
    P.append((chaikin([(-0.42, 5.3), (0.36, 5.32), (0.3, 5.62), (-0.05, 5.7), (-0.38, 5.58)], 1), 'cap', True))
    P.append(([(-0.85, 5.3), (-0.3, 5.38), (-0.3, 5.28), (-0.8, 5.24)], 'cap', True))
    P.append(([(-0.18, 4.6), (0.15, 4.5), (-0.15, 3.45), (-0.45, 3.5)], 'shirt', True))       # near arm
    P.append((circle(-0.3, 3.38, 0.13, 10), 'skin', False))
    return P

def student_hand():
    return np.array([0.95, 3.28])

def tractor():
    P = []
    P.append((circle(2.3, 2.5, 2.5, 30), 'tire', True))
    P.append((circle(2.3, 2.5, 1.3, 20), 'rim', True))
    P.append((chaikin([(3.4, 2.9), (9.9, 2.9), (10.1, 4.3), (9.6, 4.85), (4.2, 5.05), (3.5, 4.5)], 1), 'tractor', True))
    P.append(([(0.2, 3.6), (0.3, 5.1), (4.3, 5.1), (4.4, 3.6), (3.6, 4.3), (1.0, 4.3)], 'tractor', True))  # fender
    P.append(([(1.8, 5.1), (2.9, 5.1), (2.9, 6.2), (2.2, 6.3)], 'seat', True))
    P.append((circle(8.6, 1.45, 1.45, 24), 'tire', True))
    P.append((circle(8.6, 1.45, 0.7, 14), 'rim', True))
    P.append(([(6.0, 3.0), (7.6, 3.0), (7.6, 2.2), (6.0, 2.2)], 'tire', False))  # frame
    # driver
    P.append(([(2.0, 6.0), (2.9, 6.0), (2.9, 8.0), (2.2, 8.1)], 'shirt_dark', True))
    P.append((circle(2.55, 8.45, 0.38, 14), 'skin', True))
    P.append(([(2.1, 8.6), (3.1, 8.6), (3.0, 8.95), (2.2, 8.95)], 'cap', False))
    return P

def tractor_lines():
    return [([(0.6, 5.1), (0.6, 9.6), (3.9, 9.6), (3.9, 5.1)], 'tire', 0.22),   # ROPS
            ([(8.2, 4.9), (8.2, 7.0)], 'tire', 0.18),                            # exhaust
            ([(3.6, 6.5), (4.6, 7.3)], 'tire', 0.12),
            ([(2.9, 7.6), (3.9, 6.9)], 'shirt_dark', 0.25)]                       # arm to wheel
