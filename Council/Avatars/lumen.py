import tkinter as tk, math, time, random

root = tk.Tk()
root.title("Lumen")
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

PALETTES = [
    [(0.0, "#5a4ad0"), (0.25, "#a060c0"), (0.50, "#e87090"),
     (0.70, "#f0a050"), (0.85, "#e8d060"), (1.0, "#a0e080")],
    [(0.0, "#4a5ad8"), (0.25, "#8a70d0"), (0.50, "#d070a8"),
     (0.70, "#e8a060"), (0.85, "#d0d870"), (1.0, "#90d090")],
    [(0.0, "#6a4ab8"), (0.25, "#a860c8"), (0.50, "#e07aa0"),
     (0.70, "#f09058"), (0.85, "#e0c860"), (1.0, "#a8d878")],
    [(0.0, "#5050d0"), (0.25, "#a068c8"), (0.50, "#d87890"),
     (0.70, "#e89850"), (0.85, "#dcd060"), (1.0, "#98cc80")],
    [(0.0, "#4a48c8"), (0.25, "#9070cc"), (0.50, "#e07098"),
     (0.70, "#ec9058"), (0.85, "#e0cc68"), (1.0, "#a0d488")],
]

BELL_PAL = [(0.0, "#5a48c8"), (0.30, "#8a5ad0"),
            (0.55, "#c860a0"), (0.78, "#e08070"),
            (1.0, "#f0a860")]

BELL_D = "#7a4ac0"

t0 = time.time()
TENT_N = 5
LINE_W_MUL = 2.2

bell_sparks = [
    {"age": random.uniform(0, 1.0),
     "lane": i % 3,
     "speed": random.uniform(0.5, 0.8)}
    for i in range(5)
]

tentacles = [
    {"sparks": [
        {"age": random.uniform(0, 1.6),
         "speed": random.uniform(0.55, 0.85)}
        for _ in range(2)
    ], "palette": PALETTES[i % len(PALETTES)]}
    for i in range(TENT_N)
]


def draw_bell_gradient(cx, cy, r, t):
    left = cx - r*1.15
    right = cx + r*1.15
    steps = 48
    for k in range(steps):
        fx0 = k / steps
        fx1 = (k+1) / steps
        x0 = left + (right - left) * fx0
        x1 = left + (right - left) * fx1
        col = grad(BELL_PAL, fx0)
        def bell_top(x):
            dx = (x - cx) / r
            return cy - r*(0.80 - 0.45*dx*dx - 0.30*abs(dx))
        def bell_bot(x):
            dx = (x - cx) / r
            return cy + r*(0.10 - 0.05*dx*dx)
        ytop = bell_top((x0 + x1) / 2)
        ybot = bell_bot((x0 + x1) / 2)
        cv.create_rectangle(x0, ytop, x1, ybot,
                            fill=col, outline="")
    cv.create_polygon(
        cx - r*1.15, cy + r*0.10,
        cx - r*1.05, cy - r*0.35,
        cx - r*0.55, cy - r*0.72,
        cx, cy - r*0.80,
        cx + r*0.55, cy - r*0.72,
        cx + r*1.05, cy - r*0.35,
        cx + r*1.15, cy + r*0.10,
        fill="", outline=BELL_D,
        width=max(2, int(r*0.045)), smooth=True)


def draw_bell_sparks(cx, cy, r, t):
    for sp in bell_sparks:
        sp["age"] += 0.012 * sp["speed"]
        if sp["age"] > 1.0:
            sp["age"] = 0.0
            sp["speed"] = random.uniform(0.5, 0.8)
            sp["lane"] = random.randint(0, 2)
        frac = sp["age"]
        lane_off = (sp["lane"] - 1) * r * 0.35
        x = cx + lane_off + math.sin(t*2.0 + sp["lane"]) * r*0.05
        y = cy + r*0.10 - frac * r*0.80
        fade = math.sin(sp["age"] * math.pi)
        rr = r * 0.045 * fade
        if rr < 0.4: continue
        gr = rr * 2.6
        cv.create_oval(x-gr, y-gr, x+gr, y+gr,
                       fill=lerp("#e87090", "#0a3858", 0.55),
                       outline="")
        cv.create_oval(x-rr, y-rr, x+rr, y+rr,
                       fill=lerp("#ffffff", "#ffe8c8", fade*0.5),
                       outline="")


def draw_tentacle_coloured(pts, palette, base_w):
    steps = len(pts) - 1
    for k in range(steps):
        f0 = k / steps
        col = grad(palette, f0)
        w = max(2, int(base_w * (1.0 - 0.35*f0)))
        x1, y1 = pts[k]
        x2, y2 = pts[k+1]
        cv.create_line(x1, y1, x2, y2,
                       fill=col, width=w, capstyle="round")


def wave_3(cx, cy, r, s, t, i, n):
    offset = (i - (n-1)/2.0) * r * 0.30
    phase = i * 0.6
    pts = []
    for k in range(26):
        frac = k / 25
        wave = math.sin(t*1.6 + phase - frac*4.2)
        amp = r * (0.05 + 0.35 * math.sin(frac*3.14))
        pts.append((cx + offset + wave*amp, cy + r*4.5*frac))
    return pts


def draw_lumen(cx, cy, s, t):
    breath = math.sin(t*1.3) * 0.18
    r = s * (1.0 + breath*0.22)
    for k in range(2):
        gr = r * (1.25 + k*0.25)
        gc = lerp(BELL_D, "#0a3858", 0.55 + k*0.15)
        cv.create_oval(cx-gr, cy-gr*0.55, cx+gr, cy+gr*0.55,
                       fill=gc, outline="")
    draw_bell_gradient(cx, cy, r, t)
    draw_bell_sparks(cx, cy, r, t)
    base_w = max(2, int(r * 0.040 * LINE_W_MUL))
    for i in range(TENT_N):
        pts = wave_3(cx, cy, r, s, t, i, TENT_N)
        pal = tentacles[i]["palette"]
        draw_tentacle_coloured(pts, pal, base_w)
        for sp in tentacles[i]["sparks"]:
            sp["age"] += 0.016 * sp["speed"]
            if sp["age"] > 1.0:
                sp["age"] = 0.0
                sp["speed"] = random.uniform(0.55, 0.85)
            frac = 1.0 - sp["age"]
            idx_f = frac * (len(pts)-1)
            k = int(idx_f); local = idx_f - k
            if k >= len(pts)-1:
                px, py = pts[-1]
            else:
                px = pts[k][0] + (pts[k+1][0]-pts[k][0])*local
                py = pts[k][1] + (pts[k+1][1]-pts[k][1])*local
            fade = math.sin(sp["age"] * math.pi)
            rr = r * 0.045 * fade
            if rr < 0.5: continue
            gr = rr * 2.4
            cv.create_oval(px-gr, py-gr, px+gr, py+gr,
                           fill=lerp(BELL_D, "#0a3858", 0.55),
                           outline="")
            cv.create_oval(px-rr, py-rr, px+rr, py+rr,
                           fill=lerp("#ffffff", "#ffe8c8", fade*0.5),
                           outline="")


def draw():
    cv.delete("all")
    t = time.time() - t0
    for i in range(40):
        y0 = H * i / 40
        y1 = H * (i + 1) / 40 + 2
        c = lerp("#0a3858", "#02141c", i / 40)
        cv.create_rectangle(0, y0, W, y1, fill=c, outline="")

    s = min(W, H) * 0.20
    cx = W * 0.5
    cy = H * 0.40
    draw_lumen(cx, cy, s, t)

    cv.create_text(W * 0.5, H * 0.92,
                   text="L U M E N",
                   fill="#b090ff",
                   font=("Times", -int(H*0.022), "bold"))
    root.after(40, draw)

draw()
root.mainloop()