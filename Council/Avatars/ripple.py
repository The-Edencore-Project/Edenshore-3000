import tkinter as tk, math, time

root = tk.Tk()
root.title("Ripple")
root.attributes("-fullscreen", True)
root.update_idletasks()
W, H = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (W, H))
root.configure(bg="#0a3858")

cv = tk.Canvas(root, bg="#0a3858", highlightthickness=0)
cv.pack(fill="both", expand=True)

def lerp(c1, c2, t):
    h1 = c1.lstrip("#"); h2 = c2.lstrip("#")
    r1, g1, b1 = int(h1[0:2],16), int(h1[2:4],16), int(h1[4:6],16)
    r2, g2, b2 = int(h2[0:2],16), int(h2[2:4],16), int(h2[4:6],16)
    t = max(0.0, min(1.0, t))
    return "#%02x%02x%02x" % (
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

def grad(stops, t):
    if t <= stops[0][0]: return stops[0][1]
    if t >= stops[-1][0]: return stops[-1][1]
    for i in range(len(stops)-1):
        p0, c0 = stops[i]; p1, c1 = stops[i+1]
        if p0 <= t <= p1:
            local = (t-p0)/(p1-p0) if p1>p0 else 0
            return lerp(c0, c1, local)
    return stops[-1][1]

PAL = [(0.0,"#ffb8d8"),(0.15,"#ff80b8"),(0.35,"#e060b0"),
       (0.55,"#b058c0"),(0.75,"#8050b8"),(1.0,"#5038a0")]
OUTLINE = "#3a1a50"
RIM = "#ffe8f8"
EYE_W = "#ffffff"
EYE_D = "#1a1a12"

t0 = time.time()


def body_without_head(cx, cy, s):
    return [
        (cx + 0.10*s, cy - 0.85*s),
        (cx + 0.15*s, cy - 0.55*s),
        (cx + 0.30*s, cy - 0.15*s),
        (cx + 0.24*s, cy + 0.20*s),
        (cx + 0.10*s, cy + 0.50*s),
        (cx - 0.10*s, cy + 0.50*s),
        (cx - 0.22*s, cy + 0.15*s),
        (cx - 0.26*s, cy - 0.20*s),
        (cx - 0.26*s, cy - 0.55*s),
        (cx - 0.22*s, cy - 0.82*s),
        (cx - 0.14*s, cy - 0.88*s),
    ]


def fill_body(cx, cy, s, stops):
    pts = body_without_head(cx, cy, s)
    ys = [p[1] for p in pts]
    y_min, y_max = min(ys), max(ys)
    bands = 30
    for k in range(bands):
        f0 = k/bands; f1 = (k+1)/bands
        y0 = y_min + (y_max-y_min)*f0
        y1 = y_min + (y_max-y_min)*f1
        xs = []
        n = len(pts)
        for i in range(n):
            p0 = pts[i]; p1 = pts[(i+1) % n]
            if p1[1] != p0[1]:
                if (p0[1] <= y0 <= p1[1]) or (p1[1] <= y0 <= p0[1]):
                    local = (y0-p0[1])/(p1[1]-p0[1])
                    xs.append(p0[0] + (p1[0]-p0[0])*local)
        if len(xs) < 2: continue
        col = grad(stops, (f0+f1)/2)
        cv.create_rectangle(min(xs), y0, max(xs), y1,
                            fill=col, outline="")
    cv.create_polygon(*[c for p in pts for c in p],
                      fill="", outline=OUTLINE,
                      width=max(2, int(s*0.022)), smooth=True)


def tail(cx, cy, s, stops, rings=True):
    pts = [
        (cx - 0.08*s, cy + 0.50*s),
        (cx - 0.20*s, cy + 0.72*s),
        (cx - 0.32*s, cy + 0.95*s),
        (cx - 0.28*s, cy + 1.18*s),
        (cx - 0.05*s, cy + 1.28*s),
        (cx + 0.20*s, cy + 1.18*s),
        (cx + 0.30*s, cy + 0.98*s),
        (cx + 0.20*s, cy + 0.82*s),
        (cx + 0.00*s, cy + 0.78*s),
        (cx - 0.10*s, cy + 0.86*s),
        (cx - 0.10*s, cy + 0.98*s),
        (cx - 0.02*s, cy + 1.04*s),
    ]
    n = len(pts)
    for k in range(n-1):
        f0 = k/(n-1); f1 = (k+1)/(n-1)
        x1, y1 = pts[k]; x2, y2 = pts[k+1]
        w = max(2, int(s*0.20 * (1.0 - 0.70*f0)))
        col = grad(stops, 0.85 + 0.15*((f0+f1)/2))
        cv.create_line(x1, y1, x2, y2, fill=col, width=w,
                       capstyle="round")
    if rings:
        for k in range(1, n-1):
            x, y = pts[k]
            cv.create_oval(x - s*0.020, y - s*0.020,
                           x + s*0.020, y + s*0.020,
                           fill=RIM, outline=OUTLINE, width=1)


def body_rings(cx, cy, s, n=14):
    pts = body_without_head(cx, cy, s)
    ys = [p[1] for p in pts]
    y_min, y_max = min(ys), max(ys)
    for i in range(1, n):
        f = i/n
        yy = y_min + (y_max - y_min)*f
        xs = []
        n_pts = len(pts)
        for k in range(n_pts):
            p0 = pts[k]; p1 = pts[(k+1) % n_pts]
            if p1[1] != p0[1]:
                if (p0[1] <= yy <= p1[1]) or (p1[1] <= yy <= p0[1]):
                    local = (yy-p0[1])/(p1[1]-p0[1])
                    xs.append(p0[0] + (p1[0]-p0[0])*local)
        if len(xs) >= 2:
            cv.create_line(min(xs), yy - 1.2, max(xs), yy - 1.2,
                           fill=RIM, width=max(1, int(s*0.010)))
            cv.create_line(min(xs), yy, max(xs), yy,
                           fill=OUTLINE, width=max(1, int(s*0.011)))


def fin_dorsal(cx, cy, s, col):
    a_x, a_y = cx - 0.24*s, cy - 0.85*s
    b_x, b_y = cx - 0.24*s, cy - 0.40*s
    pts = [
        (a_x, a_y),
        (a_x - 0.55*s, a_y - 0.10*s),
        (a_x - 0.65*s, a_y + 0.20*s),
        (b_x - 0.55*s, b_y + 0.10*s),
        (b_x, b_y),
    ]
    cv.create_polygon(*pts, fill=col, outline=OUTLINE,
                      width=1, smooth=True)
    for i in range(4):
        f = (i+1)/5
        tipx = pts[1][0] + (pts[3][0] - pts[1][0]) * f
        tipy = pts[1][1] + (pts[3][1] - pts[1][1]) * f
        bx = a_x + (b_x - a_x) * f
        by = a_y + (b_y - a_y) * f
        cv.create_line(bx, by, tipx, tipy, fill=RIM, width=1)


def pectoral_fin(cx, cy, s, col):
    pts = [
        (cx + 0.10*s, cy - 0.60*s),
        (cx + 0.26*s, cy - 0.48*s),
        (cx + 0.20*s, cy - 0.26*s),
        (cx + 0.08*s, cy - 0.34*s),
    ]
    cv.create_polygon(*pts, fill=col, outline="", smooth=True)


def head(cx, cy, s):
    """Locked design — long snout with upturned tip"""
    hx = cx + 0.05*s; hy = cy - 1.10*s
    pts = [
        (hx - 0.20*s, hy + 0.10*s),
        (hx - 0.16*s, hy - 0.24*s),
        (hx + 0.02*s, hy - 0.32*s),
        (hx + 0.18*s, hy - 0.22*s),
        (hx + 0.32*s, hy - 0.14*s),
        (hx + 0.58*s, hy - 0.16*s),
        (hx + 0.74*s, hy - 0.14*s),
        (hx + 0.62*s, hy - 0.02*s),
        (hx + 0.32*s, hy + 0.08*s),
        (hx + 0.18*s, hy + 0.20*s),
        (hx + 0.05*s, hy + 0.22*s),
    ]
    cv.create_polygon(*pts, fill=grad(PAL, 0.10),
                      outline=OUTLINE, width=max(2, int(s*0.018)),
                      smooth=True)
    # mouth line at tip
    cv.create_line(hx + 0.70*s, hy - 0.14*s,
                   hx + 0.74*s, hy - 0.08*s,
                   fill=OUTLINE, width=1)


def coronet(cx, cy, s, n=7):
    for i in range(n):
        bx = cx + (0.00 + i*0.062)*s
        by = cy - 1.35*s
        peak = s*(0.22 if i % 2 == 1 else 0.11)
        cv.create_polygon(
            bx - s*0.022, by,
            bx + s*0.010, by - peak,
            bx + s*0.022, by,
            fill=grad(PAL, 0.20), outline=OUTLINE, width=1)
        cv.create_line(bx + s*0.010, by - peak*0.55,
                       bx + s*0.010, by - peak,
                       fill=RIM, width=1)


def eye(cx, cy, s):
    ex = cx + 0.13*s
    ey = cy - 1.16*s
    er = s*0.058
    cv.create_oval(ex-er, ey-er, ex+er, ey+er,
                   fill=EYE_W, outline=OUTLINE, width=1)
    pr = er*0.58
    cv.create_oval(ex-pr, ey-pr, ex+pr, ey+pr,
                   fill=EYE_D, outline="")
    hr = er*0.22
    cv.create_oval(ex-er*0.35-hr, ey-er*0.35-hr,
                   ex-er*0.35+hr, ey-er*0.35+hr,
                   fill="#ffffff", outline="")


def draw_ripple(cx, cy, s, t):
    bob = math.sin(t*1.0)*s*0.05
    cy += bob
    tail(cx, cy, s, PAL, rings=True)
    fill_body(cx, cy, s, PAL)
    body_rings(cx, cy, s, 14)
    fin_dorsal(cx, cy, s, grad(PAL, 0.5))
    pectoral_fin(cx, cy, s, grad(PAL, 0.55))
    head(cx, cy, s)
    coronet(cx, cy, s)
    eye(cx, cy, s)


def draw():
    cv.delete("all")
    t = time.time() - t0
    for i in range(40):
        y0 = H * i / 40
        y1 = H * (i + 1) / 40 + 2
        c = lerp("#0a3858", "#02141c", i / 40)
        cv.create_rectangle(0, y0, W, y1, fill=c, outline="")

    s = min(W, H) * 0.16
    cx = W * 0.5
    cy = H * 0.42
    draw_ripple(cx, cy, s, t)

    cv.create_text(W * 0.5, H * 0.95,
                   text="R I P P L E",
                   fill="#ff7ea8",
                   font=("Times", -int(H*0.022), "bold"))
    root.after(40, draw)

draw()
root.mainloop()