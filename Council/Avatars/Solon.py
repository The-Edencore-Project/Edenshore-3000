import tkinter as tk, math, time

root = tk.Tk()
root.title("Solon")
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

SKIN   = "#8aaa6a"
SKIND  = "#5f7a48"
SHELL  = "#5a8a4a"
SHELD  = "#3a5a32"
PLATE  = "#6a9252"
PLATL  = "#8fb878"
EYEW   = "#f4f4e8"
EYED   = "#1a1a12"
GOLD   = "#d4a94a"
GOLDD  = "#8a6a1a"
BLUSH  = "#e8a8a0"

t0 = time.time()


def flipper_paddle(bx, by, ang, s, wob, colour=SKIND):
    a = ang + wob
    ca = math.cos(a); sa = math.sin(a)
    def rot(px, py):
        return bx + px*ca - py*sa, by + px*sa + py*ca
    p1 = rot(-s*0.05, -s*0.14)
    p2 = rot( s*0.55, -s*0.24)
    p3 = rot( s*0.70,  0.0)
    p4 = rot( s*0.55,  s*0.24)
    p5 = rot(-s*0.05,  s*0.14)
    cv.create_polygon(*p1, *p2, *p3, *p4, *p5,
                      fill=colour, outline="", smooth=True)


def draw_solon(cx, cy, s, t):
    breath = math.sin(t * 0.9) * 0.06

    # four paddle legs, drawn behind the shell
    for (fx, fy, ang, sc) in [(-0.90,-0.58,-0.35,0.85),
                              (-0.90, 0.58, 0.35,0.85),
                              ( 0.50,-0.58,-0.35,1.05),
                              ( 0.50, 0.58, 0.35,1.05)]:
        bx = cx + fx*s; by = cy + fy*s
        wob = math.sin(t * 1.6 + fx * 3) * 0.08
        flipper_paddle(bx, by, ang, s*sc, wob)

    # shell
    rx = s * (1.05 + breath*0.3)
    ry = s * (0.85 + breath*0.3)
    cv.create_oval(cx-rx*1.06, cy-ry*1.06, cx+rx*1.06, cy+ry*1.06,
                   fill=GOLD, outline=GOLDD,
                   width=max(2, int(s*0.014)))
    cv.create_oval(cx-rx, cy-ry, cx+rx, cy+ry,
                   fill=SHELD, outline="")
    rx2 = rx*0.94; ry2 = ry*0.94
    cv.create_oval(cx-rx2, cy-ry2, cx+rx2, cy+ry2,
                   fill=SHELL, outline="")

    # radiating plate lines
    for i in range(8):
        a = i * (6.28/8)
        cv.create_line(cx + math.cos(a)*rx2*0.20,
                       cy + math.sin(a)*ry2*0.20,
                       cx + math.cos(a)*rx2*0.95,
                       cy + math.sin(a)*ry2*0.95,
                       fill=SHELD, width=max(2, int(s*0.020)))

    # centre plate
    pr = s*0.20
    cv.create_oval(cx-pr, cy-pr*0.7, cx+pr, cy+pr*0.7,
                   fill=PLATL, outline=SHELD,
                   width=max(2, int(s*0.016)))

    # ring of small plates
    for i in range(8):
        a = i * (6.28/8) + (3.14/8)
        px = cx + math.cos(a)*rx2*0.68
        py = cy + math.sin(a)*ry2*0.68
        r = s*0.11
        cv.create_oval(px-r, py-r*0.75, px+r, py+r*0.75,
                       fill=PLATE, outline=SHELD,
                       width=max(1, int(s*0.010)))

    # top highlight
    cv.create_arc(cx-rx2*0.85, cy-ry2*0.95,
                  cx+rx2*0.85, cy+ry2*0.35,
                  start=40, extent=100, style="arc",
                  outline=lerp(SHELL, "#ffffff", 0.30),
                  width=max(3, int(s*0.028)))

    # head + neck
    d = 1
    hx = cx + d*s*1.32
    hy = cy - s*0.05
    cv.create_polygon(cx+d*s*0.95, cy-s*0.18,
                      hx-d*s*0.10, hy-s*0.22,
                      hx-d*s*0.10, hy+s*0.22,
                      cx+d*s*0.95, cy+s*0.18,
                      fill=SKIN, outline="", smooth=True)
    cv.create_oval(hx-s*0.38, hy-s*0.34, hx+s*0.38, hy+s*0.34,
                   fill=SKIN, outline=SKIND,
                   width=max(2, int(s*0.014)))
    # blush
    cv.create_oval(hx-s*0.30, hy+s*0.00,
                   hx-s*0.12, hy+s*0.18,
                   fill=BLUSH, outline="")
    # brow
    cv.create_arc(hx-s*0.32, hy-s*0.36,
                  hx+s*0.36, hy+s*0.06,
                  start=20, extent=120, style="arc",
                  outline=SKIND, width=max(2, int(s*0.018)))
    # beak
    cv.create_polygon(hx+s*0.22, hy-s*0.05,
                      hx+s*0.44, hy+s*0.02,
                      hx+s*0.22, hy+s*0.12,
                      fill=SKIN, outline=SKIND, width=1)
    # smile
    cv.create_arc(hx-s*0.06, hy+s*0.06,
                  hx+s*0.24, hy+s*0.26,
                  start=200, extent=140, style="arc",
                  outline=SKIND, width=max(1, int(s*0.010)))
    # eye
    er = s*0.095*1.25
    ex = hx + d*s*0.08
    ey = hy - s*0.06
    cv.create_oval(ex-er, ey-er, ex+er, ey+er,
                   fill=EYEW, outline=SKIND, width=1)
    pr = er*0.62
    cv.create_oval(ex-pr, ey-pr, ex+pr, ey+pr,
                   fill=EYED, outline="")
    hr = er*0.24
    cv.create_oval(ex-er*0.35-hr, ey-er*0.35-hr,
                   ex-er*0.35+hr, ey-er*0.35+hr,
                   fill="#ffffff", outline="")
    hr2 = er*0.13
    cv.create_oval(ex+er*0.10-hr2, ey+er*0.20-hr2,
                   ex+er*0.10+hr2, ey+er*0.20+hr2,
                   fill="#ffffff", outline="")


def draw():
    cv.delete("all")
    t = time.time() - t0
    for i in range(40):
        y0 = H * i / 40
        y1 = H * (i + 1) / 40 + 2
        c = lerp("#0a3858", "#02141c", i / 40)
        cv.create_rectangle(0, y0, W, y1, fill=c, outline="")

    s = min(W, H) * 0.26
    cx = W * 0.5
    cy = H * 0.5
    draw_solon(cx, cy, s, t)

    cv.create_text(W * 0.5, H * 0.92,
                   text="S O L O N",
                   fill="#d4a94a",
                   font=("Times", -int(H*0.022), "bold"))
    root.after(40, draw)

draw()
root.mainloop()