import tkinter as tk, math, time, random

root = tk.Tk()
root.attributes("-fullscreen", True)
root.update_idletasks()
W, H = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (W, H))
root.configure(bg="#0a3858")

cv = tk.Canvas(root, bg="#0a3858", highlightthickness=0)
cv.pack(fill="both", expand=True)

FILL = "#134870"
GOLD = "#ffcc44"
IRID = ["#ff7ea8", "#b090ff", "#5aa8ff", "#5fd08a", "#ffc857"]

def lerp(c1, c2, t):
    h1 = c1.lstrip("#"); h2 = c2.lstrip("#")
    r1, g1, b1 = int(h1[0:2],16), int(h1[2:4],16), int(h1[4:6],16)
    r2, g2, b2 = int(h2[0:2],16), int(h2[2:4],16), int(h2[4:6],16)
    t = max(0.0, min(1.0, t))
    return "#%02x%02x%02x" % (
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

t0 = time.time()
bubbles = []
for i in range(3):
    bubbles.append({
        "cx": W * (0.30 + i * 0.20),
        "cy": H * (0.30 + (i % 2) * 0.15),
        "r":  min(W, H) * 0.14,
        "phase": random.uniform(0, 6.28),
    })

def draw():
    cv.delete("all")
    t = time.time() - t0
    # background water bands
    for i in range(40):
        y0 = H * i / 40
        y1 = H * (i + 1) / 40 + 2
        c = lerp("#0a3858", "#02141c", i / 40)
        cv.create_rectangle(0, y0, W, y1, fill=c, outline="")

    for b in bubbles:
        cx, cy, r = b["cx"], b["cy"], b["r"]
        # body
        cv.create_oval(cx-r, cy-r, cx+r, cy+r,
                       fill=FILL, outline="")
        # iridescent rim: many small arcs around the edge
        n = 36
        for i in range(n):
            a0 = (i / n) * 360 + math.sin(t * 0.6 + b["phase"]) * 25
            col = IRID[i % len(IRID)]
            span = 12
            cv.create_arc(cx-r, cy-r, cx+r, cy+r,
                          start=a0, extent=span,
                          style="arc", outline=col, width=4)
        # bright top-left reflection arc
        cv.create_arc(cx-r*0.92, cy-r*0.92,
                      cx+r*0.92, cy+r*0.92,
                      start=100, extent=70,
                      style="arc",
                      outline="#ffffff", width=3)
        # inverted sheen: water band lifted, curved
        sh = r * 0.55
        cv.create_arc(cx-r*0.65, cy-r*0.2 - sh,
                      cx+r*0.65, cy+r*0.2 - sh,
                      start=200, extent=140,
                      style="arc",
                      outline=lerp(FILL, "#ffffff", 0.28),
                      width=6)
        # inner glow ring
        cv.create_oval(cx-r*0.82, cy-r*0.82,
                       cx+r*0.82, cy+r*0.82,
                       outline=lerp(FILL, "#ffffff", 0.10),
                       width=2)
        # highlight blob, drifting gently
        hr = r * 0.14
        hx = cx - r*0.60 + math.sin(t*0.7 + b["phase"]) * r*0.05
        hy = cy - r*0.60 + math.cos(t*0.6 + b["phase"]) * r*0.05
        cv.create_oval(hx-hr, hy-hr, hx+hr, hy+hr,
                       fill="#ffffff", outline="")
        # small trailing sparkle
        sr = hr * 0.45
        sx = hx + r*0.22
        sy = hy + r*0.10
        cv.create_oval(sx-sr, sy-sr, sx+sr, sy+sr,
                       fill=lerp("#ffffff", FILL, 0.35), outline="")
        # text
        cv.create_text(cx, cy, text="Small\nkindnesses,\nrepeated.",
                       fill=GOLD,
                       font=("Courier", -int(r*0.14), "bold"),
                       justify="center")

    root.after(40, draw)

draw()
root.mainloop()