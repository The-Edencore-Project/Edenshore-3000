# ============ EDENSHORE 3000 — V21 ============
# Content weeded. Real stories. Stronger camera. Dark quiet mode.
# =================================================

import tkinter as tk, math, time, os, json, random
import wave, array, subprocess, shutil, threading

root = tk.Tk()
root.title("Edenshore 3000")
try:
    root.attributes("-fullscreen", True)
except tk.TclError:
    pass
root.update_idletasks()
W, H = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (W, H))
root.configure(bg="#0a0208")
canvas = tk.Canvas(root, bg="#020108", width=W, height=H,
                   highlightthickness=0)
canvas.pack(fill="both", expand=True)

def font_full(px, bold=True):
    return ("Helvetica", -max(8, int(px)), "bold" if bold else "normal")

if W < 600: DEVICE_CLASS = "phone"
elif W < 1200: DEVICE_CLASS = "tablet"
else: DEVICE_CLASS = "desktop"

STATE_DIR  = os.path.join(os.path.expanduser("~"), ".edencore")
STATE_PATH = os.path.join(STATE_DIR, "edenshore.json")
MUSIC_PATH = os.path.join(STATE_DIR, "music.wav")
DRONE_PATH = os.path.join(STATE_DIR, "drone.wav")

def _ensure_state_dir():
    try: os.makedirs(STATE_DIR, exist_ok=True)
    except Exception: pass

# ============ AUDIO ============
AUDIO_MODE = None
AUDIO_PROC = [None]

def _detect_audio():
    global AUDIO_MODE
    try:
        from playsound import playsound  # noqa
        AUDIO_MODE = "playsound"; return
    except Exception: pass
    try:
        import pygame
        pygame.mixer.init()
        AUDIO_MODE = "pygame"; return
    except Exception: pass
    if shutil.which("am"):
        AUDIO_MODE = "android"; return
    AUDIO_MODE = None

_detect_audio()

def _generate_drone(path, base_freq=110.0, duration=20.0, sr=22050):
    n = int(duration * sr)
    buf = array.array('h')
    for i in range(n):
        t = i / sr
        s = (math.sin(2*math.pi*base_freq*t) * 0.40
             + math.sin(2*math.pi*base_freq*1.5*t) * 0.20
             + math.sin(2*math.pi*base_freq*2.01*t) * 0.14)
        env = 0.65 + 0.35 * math.sin(2*math.pi*t / 8.0)
        v = int(s * env * 11000)
        buf.append(max(-32767, min(32767, v)))
    with wave.open(str(path), 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(buf.tobytes())

def ensure_music():
    _ensure_state_dir()
    if os.path.exists(MUSIC_PATH): return MUSIC_PATH
    if not os.path.exists(DRONE_PATH):
        try: _generate_drone(DRONE_PATH)
        except Exception: return None
    return DRONE_PATH

def play_music(path, loop=True, volume=0.25):
    if AUDIO_MODE is None or path is None: return
    try:
        if AUDIO_MODE == "playsound":
            from playsound import playsound
            playsound(str(path), block=False)
        elif AUDIO_MODE == "pygame":
            import pygame
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
        elif AUDIO_MODE == "android":
            AUDIO_PROC[0] = subprocess.Popen([
                "am","start","-a","android.intent.action.VIEW",
                "-d","file://"+str(path),"-t","audio/wav",
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception: pass

def audio_status(): return AUDIO_MODE or "silent"

def _boot_audio():
    path = ensure_music()
    if path: play_music(path, loop=True, volume=0.25)

# ============ PALETTE ============
WATER_TOP  = "#2a0450"; WATER_HIGH = "#5a1080"; WATER_MID  = "#a82870"
WATER_LOW  = "#e06030"; WATER_DEEP = "#a03018"; WATER_BOT  = "#1a0410"
HAZE = "#4a1030"
SAND_LIT = "#8a4828"; SAND = "#3a1810"; SAND_DARK = "#1a0808"; SAND_DEEP = "#080202"
GLOW_WARM = "#ffe8a0"; GLOW_COOL = "#80ffe0"
GLOW_GREEN = "#60ffd0"; GLOW_PINK = "#ff80b8"
BUBBLE_TEXT = "#fff8e8"

SEATS = ["Solon","Lumen","Vertex","Prism","Ripple"]
SEAT_BODY = {"Solon":"#1a2848","Lumen":"#3a1858","Vertex":"#1a3a28",
             "Prism":"#5a3810","Ripple":"#48182a"}
SEAT_RIM  = {"Solon":"#ffb060","Lumen":"#ffc080","Vertex":"#ffa050",
             "Prism":"#ffd080","Ripple":"#ffb8a0"}
SEAT_COLOUR = dict(SEAT_RIM)
SEAT_BREATH = {"Solon":5.0,"Lumen":2.0,"Vertex":1.5,"Prism":4.0,"Ripple":3.0}
SEAT_HOME_X = {"Solon":0.18,"Lumen":0.38,"Vertex":0.54,"Prism":0.72,"Ripple":0.90}
SEAT_HOME_Y = {"Solon":0.42,"Lumen":0.38,"Vertex":0.72,"Prism":0.48,"Ripple":0.62}

def lerp(c1, c2, t):
    h1=c1.lstrip("#"); h2=c2.lstrip("#")
    r1=int(h1[0:2],16); g1=int(h1[2:4],16); b1=int(h1[4:6],16)
    r2=int(h2[0:2],16); g2=int(h2[2:4],16); b2=int(h2[4:6],16)
    t=max(0.0,min(1.0,t))
    return "#%02x%02x%02x"%(int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t))

def clamp(v,lo,hi): return max(lo,min(hi,v))

HUE_PERIOD = 240.0

def _hue_shift_hex(hex_col, shift):
    h = hex_col.lstrip("#")
    r=int(h[0:2],16)/255.0; g=int(h[2:4],16)/255.0; b=int(h[4:6],16)/255.0
    mx=max(r,g,b); mn=min(r,g,b); d=mx-mn
    if d == 0: hh = 0.0
    elif mx == r: hh = ((g-b)/d) % 6
    elif mx == g: hh = (b-r)/d + 2
    else:         hh = (r-g)/d + 4
    hh = (hh / 6.0 + shift) % 1.0
    s = 0 if mx == 0 else d/mx
    v = mx
    i = int(hh * 6.0); f = hh * 6.0 - i
    p = v*(1-s); q = v*(1-f*s); t = v*(1-(1-f)*s)
    i = i % 6
    if   i == 0: rr,gg,bb = v,t,p
    elif i == 1: rr,gg,bb = q,v,p
    elif i == 2: rr,gg,bb = p,v,t
    elif i == 3: rr,gg,bb = p,q,v
    elif i == 4: rr,gg,bb = t,p,v
    else:        rr,gg,bb = v,p,q
    return "#%02x%02x%02x"%(int(rr*255),int(gg*255),int(bb*255))

def hue_shift_amount():
    return math.sin(time.time() * (2*math.pi / HUE_PERIOD)) * 0.12

def hue(col):
    s = hue_shift_amount()
    if abs(s) < 0.002: return col
    return _hue_shift_hex(col, s)

SURFACE_Y = int(H*0.06); FLOOR_Y = int(H*0.80)
LIGHT_X = int(W*0.50); START_TIME = time.time()

# ============ CAMERA ============
ZOOM_SILENT   = 0.75
ZOOM_SPEAKING = 1.30
CAM = {"zoom": ZOOM_SILENT, "target": ZOOM_SILENT,
       "fx": W*0.5, "fy": H*0.55,
       "tfx": W*0.5, "tfy": H*0.55}

def cam(x, y):
    return (CAM["fx"] + (x - CAM["fx"]) * CAM["zoom"],
            CAM["fy"] + (y - CAM["fy"]) * CAM["zoom"])

# ============ QUIET MODE ============
QUIET = {"level": 0.0, "silent_since": time.time()}
QUIET_AFTER = 20.0

def update_quiet(dt):
    if any_stream_active():
        QUIET["silent_since"] = time.time()
        target = 0.0
    else:
        silent_for = time.time() - QUIET["silent_since"]
        target = 1.0 if silent_for > QUIET_AFTER else 0.0
    QUIET["level"] += (target - QUIET["level"]) * 0.008
    QUIET["level"] = clamp(QUIET["level"], 0.0, 1.0)

# ============ STATE ============
def load_state():
    try:
        with open(STATE_PATH) as f: d=json.load(f)
        return {"mood":float(d.get("mood",0.55)),
                "strain":float(d.get("strain",0.20)),
                "last_seen":float(d.get("last_seen",0.0)),
                "last_hour":int(d.get("last_hour",-1)),
                "visits":int(d.get("visits",0))}
    except Exception:
        return {"mood":0.55,"strain":0.20,"last_seen":0.0,
                "last_hour":-1,"visits":0}

def save_state(mood, strain):
    _ensure_state_dir()
    try:
        with open(STATE_PATH, "w") as f:
            json.dump({"mood":round(mood,4),"strain":round(strain,4),
                       "last_seen":time.time(),
                       "last_hour":time.localtime().tm_hour,
                       "visits":PRIOR.get("visits",0)+1}, f)
    except Exception: pass

PRIOR = load_state()

def prior_carry():
    if PRIOR["last_seen"] <= 0: return 0.0
    hrs = (time.time() - PRIOR["last_seen"]) / 3600.0
    if hrs < 0 or hrs > 48: return 0.0
    return clamp(1.0 - hrs / 48.0, 0.0, 1.0)

INTERO = {"session_mins":0.0,"utterances":0,"chamber_strain":0.0,
          "session_warmth":0.0,"utterances_this_hour":0,
          "last_hour_seen":time.localtime().tm_hour,
          "been_touched":False,"last_touch_kind":None}

EXTERO = {"hour":0,"rhythm":"afternoon","time_bucket":"afternoon",
          "battery":None,"charging":False,
          "touch_x":-1,"touch_y":-1,"touch_at":0.0,
          "touch_count_session":0,"drag_distance":0.0,
          "focused":True,"focus_lost_at":0.0,
          "device_class":DEVICE_CLASS}

def read_extero():
    now = time.localtime(); h = now.tm_hour
    if   5 <= h < 11: rhythm = "morning"
    elif 11 <= h < 16: rhythm = "midday"
    elif 16 <= h < 21: rhythm = "evening"
    else:             rhythm = "night"
    if   5 <= h < 8:   bucket = "dawn"
    elif 8 <= h < 12:  bucket = "morning"
    elif 12 <= h < 15: bucket = "midday"
    elif 15 <= h < 18: bucket = "afternoon"
    elif 18 <= h < 21: bucket = "dusk"
    else:              bucket = "night"
    EXTERO["hour"]=h; EXTERO["rhythm"]=rhythm; EXTERO["time_bucket"]=bucket
    try:
        for d in os.listdir("/sys/class/power_supply"):
            p = "/sys/class/power_supply/" + d
            cp = p + "/capacity"
            if os.path.exists(cp):
                with open(cp) as f: EXTERO["battery"]=int(f.read().strip())
                st = p + "/status"
                if os.path.exists(st):
                    with open(st) as f:
                        EXTERO["charging"] = f.read().strip().lower() in ("charging","full")
                break
    except Exception:
        EXTERO["battery"]=None; EXTERO["charging"]=False

def update_intero():
    INTERO["session_mins"] = (time.time() - START_TIME) / 60.0
    INTERO["session_warmth"] = clamp(INTERO["session_mins"] / 30.0, 0.0, 1.0)
    now_h = time.localtime().tm_hour
    if now_h != INTERO["last_hour_seen"]:
        INTERO["utterances_this_hour"] = 0
        INTERO["last_hour_seen"] = now_h

def touch_energy():
    if EXTERO["touch_at"] <= 0: return 0.0
    return clamp(1.0 - (time.time() - EXTERO["touch_at"]) / 15.0, 0.0, 1.0)

MOOD = {"target":0.55,"current":0.55,
        "last_utterance_at":time.time(),
        "drift_phase":random.uniform(0,6.28)}
_carry = prior_carry()
MOOD["current"] = clamp(PRIOR["mood"]*_carry + 0.55*(1.0-_carry), 0.10, 0.98)
STRAIN = {s: PRIOR["strain"] for s in SEATS}
BREATH = {s: random.uniform(0,6.28) for s in SEATS}
BELL = {"phase": 0.0}

def rhythm_base():
    r = EXTERO["rhythm"]
    if r == "morning": return 0.72
    if r == "midday":  return 0.68
    if r == "evening": return 0.52
    return 0.38

def battery_score():
    b = EXTERO["battery"]
    if b is None: return 0.5
    if EXTERO["charging"]: return 0.75
    if b >= 70: return 0.70
    if b >= 40: return 0.55
    if b >= 15: return 0.35
    return 0.20

def session_score():
    m = INTERO["session_mins"]
    if m < 5:  return 0.75
    if m < 20: return 0.60
    if m < 45: return 0.45
    return 0.35

def focus_score():
    return 0.55 if not EXTERO["focused"] else 1.0

def compute_mood_target():
    warm = INTERO["session_warmth"] * 0.05
    t = (rhythm_base()*0.45 + battery_score()*0.20
         + session_score()*0.20 + 0.15 + warm)
    t *= focus_score()
    MOOD["target"] = clamp(t, 0.15, 0.95)

def update_mood(dt):
    MOOD["drift_phase"] += dt * 0.3
    drift = math.sin(MOOD["drift_phase"]) * 0.02
    MOOD["current"] += (MOOD["target"] + drift - MOOD["current"]) * 0.018
    MOOD["current"] = clamp(MOOD["current"], 0.08, 0.98)

def update_strain(dt):
    up = clamp(INTERO["utterances_this_hour"] / 30.0, 0.0, 1.0)
    INTERO["chamber_strain"] = clamp(
        INTERO["chamber_strain"]*0.997 + up*0.003, 0.0, 1.0)
    b = EXTERO["battery"]; bat_low = 0.0
    if b is not None and not EXTERO["charging"] and b < 25:
        bat_low = (25 - b) / 25.0
    base = INTERO["chamber_strain"] + bat_low * 0.3
    for seat in SEATS:
        tgt = clamp(base * (0.6 + random.uniform(0,0.4)), 0.0, 1.0)
        STRAIN[seat] += (tgt - STRAIN[seat]) * 0.006
        STRAIN[seat] = clamp(STRAIN[seat], 0.0, 1.0)

def update_breath(dt):
    # breath slows during quiet
    rate = (0.7 + MOOD["current"] * 0.7) * (1.0 - QUIET["level"] * 0.55)
    for seat in SEATS:
        BREATH[seat] += dt * (1.0 / SEAT_BREATH[seat]) * rate

def breath_offset(seat, amp=1.0):
    return math.sin(BREATH[seat] * 6.28) * amp

def update_bell(dt):
    BELL["phase"] += dt * (0.35 + MOOD["current"] * 0.35)

def bell_value():
    return 0.5 + 0.5 * math.sin(BELL["phase"] * 6.28)

def night_amount():
    r = EXTERO["rhythm"]
    if r == "night":   return 0.55
    if r == "evening": return 0.20
    return 0.0

read_extero(); update_intero(); compute_mood_target()

SCENE = {"t":0.0,"last_save":time.time(),"scroll_x":0.0,"scroll_speed":0.5}
PULSE = {"phase":0.0}

# ============ INPUT ============
_last_touch_xy = [None, None]

def on_press(e):
    EXTERO["touch_x"]=e.x; EXTERO["touch_y"]=e.y
    EXTERO["touch_at"]=time.time()
    EXTERO["touch_count_session"] += 1
    INTERO["been_touched"]=True; INTERO["last_touch_kind"]="tap"
    _last_touch_xy[0]=e.x; _last_touch_xy[1]=e.y

def on_motion(e):
    if _last_touch_xy[0] is not None:
        dx=e.x-_last_touch_xy[0]; dy=e.y-_last_touch_xy[1]
        EXTERO["drag_distance"] += math.hypot(dx,dy)
        _last_touch_xy[0]=e.x; _last_touch_xy[1]=e.y
        EXTERO["touch_x"]=e.x; EXTERO["touch_y"]=e.y
        EXTERO["touch_at"]=time.time()
        INTERO["last_touch_kind"]="drag"

def on_double(e):
    EXTERO["touch_x"]=e.x; EXTERO["touch_y"]=e.y
    EXTERO["touch_at"]=time.time()
    EXTERO["touch_count_session"] += 1
    INTERO["been_touched"]=True; INTERO["last_touch_kind"]="double"

def on_focus_in(e=None):  EXTERO["focused"]=True
def on_focus_out(e=None):
    EXTERO["focused"]=False; EXTERO["focus_lost_at"]=time.time()
def on_visibility(e=None):
    s = str(getattr(e,"state","")).lower()
    EXTERO["focused"] = "fullyobscured" not in s

def on_press_soft(e):
    was_first = not INTERO["been_touched"]
    on_press(e)
    if was_first:
        RHYTHM["t"] = max(RHYTHM["t"], RHYTHM["gap_min"] * 0.6)

canvas.bind("<Button-1>", on_press_soft)
canvas.bind("<B1-Motion>", on_motion)
canvas.bind("<ButtonRelease-1>", lambda e: _last_touch_xy.__setitem__(0, None))
canvas.bind("<Double-Button-1>", on_double)
root.bind("<FocusIn>", on_focus_in)
root.bind("<FocusOut>", on_focus_out)
root.bind("<Visibility>", on_visibility)

# ============ CONTENT (weeded) ============
WORLD_POOLS = {
    "Solon": [
        "The visitor is here.",
        "The phone is on.",
        "The screen is lit.",
        "The chamber is open.",
        "The visitor came back.",
        "The chamber has been open a long time.",
        "The phone is still on.",
        "The chamber is still open.",
        "The visitor is still here.",
        "We have a visitor.",
    ],
    "Lumen": [
        "Does the visitor see us, or only the screen?",
        "Is this the visitor's first chamber?",
        "How long has the visitor been here?",
        "Is the visitor tired?",
        "What does the visitor do when we're closed?",
        "Is the visitor holding the phone, or is it on a table?",
        "Does the visitor ever put us down and forget?",
        "Does the visitor sleep?",
        "Does the visitor remember us?",
        "Is the visitor alone?",
        "Did the visitor touch the screen just now?",
        "Is the visitor still there?",
    ],
    "Vertex": [
        "Battery at full.","Battery good.","Battery half.","Battery low.",
        "The phone is charging.","The hour is late.","The hour is early.",
        "The session is short.","The session is long.","One visitor.",
        "No touches yet.","One touch.","Two touches.","Three touches.",
        "The screen is on.","The screen is off.",
    ],
    "Prism": [
        "The visitor came back.","The visitor came back again.",
        "The visitor comes at the same hour.","The visitor stays a while.",
        "The visitor leaves.","The visitor is quiet this time.",
    ],
    "Ripple": [
        "You're here.","You came back.","You can stay.",
        "You don't have to say anything.","It's quiet here.",
        "You are here. That is already something.","I'm here.","We're here.",
        "You don't have to do anything.",
    ],
}
SIGNATURES = {"Ripple":["You're okay.","Take your time.","I'm listening.",
                        "It's not your fault.","Go gently."]}

# ============ STORIES & CROSSTALK ============
# Stories: one teller, five-plus lines, a shape.
# Crosstalk: short back-and-forth, no arc.

DIALOGUES = [
    # --- stories ---
    {"name":"the_stone","kind":"story","lines":[
        ("Solon","I found a stone yesterday."),
        ("Solon","It was on the ridge. Round."),
        ("Lumen","What was it doing there?"),
        ("Solon","Nothing. Sitting."),
        ("Solon","I left it."),
        ("Prism","That's all?"),
        ("Solon","That's all."),
    ]},
    {"name":"the_sound_night","kind":"story","lines":[
        ("Prism","I heard something last night."),
        ("Vertex","What kind?"),
        ("Prism","Something small. Moving."),
        ("Prism","It stopped when I got close."),
        ("Lumen","What do you think it was?"),
        ("Prism","Something small."),
        ("Vertex","Did you look?"),
        ("Prism","No."),
    ]},
    {"name":"quiet_visitor","kind":"story","lines":[
        ("Ripple","The visitor came in quietly today."),
        ("Lumen","Quiet how?"),
        ("Ripple","They didn't touch the screen."),
        ("Ripple","They just looked."),
        ("Solon","For how long?"),
        ("Ripple","A while."),
        ("Prism","That's a lot."),
    ]},
    {"name":"the_water","kind":"story","lines":[
        ("Solon","The water was different this morning."),
        ("Lumen","Different how?"),
        ("Solon","Colder."),
        ("Vertex","Noted."),
        ("Solon","And the light came in lower."),
        ("Prism","Every year."),
        ("Solon","Every year."),
    ]},
    {"name":"the_spot","kind":"story","lines":[
        ("Vertex","I found a new spot."),
        ("Lumen","For what?"),
        ("Vertex","Sitting."),
        ("Vertex","Under the big rock. Warm."),
        ("Prism","Is it yours now?"),
        ("Vertex","I don't own it."),
        ("Vertex","But I go there."),
    ]},
    {"name":"the_other","kind":"story","lines":[
        ("Ripple","There was another visitor once."),
        ("Lumen","Another?"),
        ("Ripple","They came every night."),
        ("Ripple","Then they stopped."),
        ("Solon","Did you miss them?"),
        ("Ripple","I noticed."),
        ("Lumen","That counts."),
    ]},
    # --- crosstalk ---
    {"name":"the_visitor_here","kind":"crosstalk","lines":[
        ("Lumen","Is the visitor still there?"),
        ("Solon","The phone is on."),
        ("Lumen","Good."),
        ("Ripple","You can stay."),
    ]},
    {"name":"did_you_hear","kind":"crosstalk","lines":[
        ("Prism","Did you hear that?"),
        ("Vertex","Hear what?"),
        ("Prism","Nothing. Never mind."),
        ("Vertex","Okay."),
    ]},
]

SOLON_GATES = {
    "We have a visitor.": lambda: INTERO["session_mins"] < 1.0 and EXTERO["touch_count_session"] >= 1,
    "The visitor came back.": lambda: PRIOR.get("visits",0) > 0,
}
VERTEX_GATES = {
    "Battery at full.": lambda: (EXTERO["battery"] is not None and EXTERO["battery"]>=85 and not EXTERO["charging"]),
    "Battery good.":    lambda: (EXTERO["battery"] is not None and 60<=EXTERO["battery"]<85 and not EXTERO["charging"]),
    "Battery half.":    lambda: (EXTERO["battery"] is not None and 30<=EXTERO["battery"]<60 and not EXTERO["charging"]),
    "Battery low.":     lambda: (EXTERO["battery"] is not None and EXTERO["battery"]<30 and not EXTERO["charging"]),
    "The phone is charging.": lambda: EXTERO["charging"],
    "The hour is late.":  lambda: EXTERO["hour"]>=21 or EXTERO["hour"]<5,
    "The hour is early.": lambda: 5 <= EXTERO["hour"] < 10,
    "The session is short.": lambda: INTERO["session_mins"] < 8,
    "The session is long.":  lambda: INTERO["session_mins"] > 30,
    "No touches yet.": lambda: EXTERO["touch_count_session"] == 0,
    "One touch.":      lambda: EXTERO["touch_count_session"] == 1,
    "Two touches.":    lambda: EXTERO["touch_count_session"] == 2,
    "Three touches.":  lambda: EXTERO["touch_count_session"] == 3,
    "The screen is on.":  lambda: EXTERO["focused"],
    "The screen is off.": lambda: not EXTERO["focused"],
}
PRISM_GATES = {
    "The visitor came back.": lambda: PRIOR.get("visits",0) > 0,
    "The visitor came back again.": lambda: PRIOR.get("visits",0) >= 2,
    "The visitor comes at the same hour.": lambda: PRIOR.get("last_hour",-1) >= 0 and PRIOR.get("last_hour") == EXTERO["hour"],
    "The visitor stays a while.": lambda: INTERO["session_mins"] > 15,
    "The visitor leaves.": lambda: not EXTERO["focused"],
    "The visitor is quiet this time.": lambda: EXTERO["touch_count_session"] == 0 and INTERO["session_mins"] > 8,
}
SEAT_GATES = {"Solon":SOLON_GATES,"Vertex":VERTEX_GATES,"Prism":PRISM_GATES,
              "Lumen":{},"Ripple":{}}

# ============ CHAT ENGINE ============
STREAMS = []; PLAYED = set(); SIG_LAST = {}
LAST_FIRST_WORD = [None]
LAST_SPOKE = {s: 0.0 for s in SEATS}
PLAYED_DIALOGUES = set()
RHYTHM = {"t":0.0,"state":"pause","last_seat":None,
          "gap_min":4.0,"gap_max":8.5,"since_signature":0,"pending_seat":None}
DIALOGUE = {"active":False,"queue":[],"current":None,
            "t":0.0,"gap":2.0,"index":0}
CREATURES = []
RECOVERY_MINS = 4.0
DIALOGUE_CHANCE = 0.10
BOOT_DIALOGUE_AT = 15.0
BOOT_STATE = {"fired": False}

def pick_seat(last=None):
    pool = [s for s in SEATS if s != last]
    return random.choice(pool) if pool else random.choice(SEATS)

def gated_pool(seat):
    pool = WORLD_POOLS.get(seat, [])
    gates = SEAT_GATES.get(seat, {})
    return [line for line in pool if (line not in gates) or gates[line]()]

def maybe_recover(seat):
    pool = gated_pool(seat)
    exhausted = all(("world", t) in PLAYED for t in pool)
    if not exhausted: return False
    if time.time() - LAST_SPOKE.get(seat, 0.0) > RECOVERY_MINS * 60.0:
        for t in list(PLAYED):
            if t[0]=="world" and t[1] in pool: PLAYED.discard(t)
        return True
    return False

def pick_line(pool, tag):
    options = [t for t in pool if (tag,t) not in PLAYED]
    if not options: return None
    if len(options) > 4:
        last_w = LAST_FIRST_WORD[0]
        if last_w:
            filtered = [t for t in options if t.split()[0].lower()!=last_w]
            if filtered: options = filtered
    if not options: return None
    choice = random.choice(options)
    PLAYED.add((tag, choice))
    LAST_FIRST_WORD[0] = choice.split()[0].lower().strip(".,!?")
    return choice

def pick_signature(seat):
    pool = SIGNATURES.get(seat, [])
    if not pool: return None
    last = SIG_LAST.get(seat, -1)
    options = [i for i in range(len(pool)) if i != last]
    if not options: return None
    i = random.choice(options); SIG_LAST[seat] = i
    return pool[i]

def chunk_text(text, max_chars=12):
    words = text.split(); chunks = []; current = ""
    for w in words:
        if len(w) > max_chars:
            if current: chunks.append(current); current = ""
            for i in range(0, len(w), max_chars):
                chunks.append(w[i:i+max_chars])
            continue
        if not current: current = w
        elif len(current) + 1 + len(w) <= max_chars: current += " " + w
        else: chunks.append(current); current = w
    if current: chunks.append(current)
    return chunks

def bubble_radius_for(chunk):
    fs = max(14, int(H * 0.020))
    text_w = len(chunk) * fs * 0.60
    r = max(H * 0.055, text_w * 1.10)
    r = min(r, H * 0.100)
    return r, fs

def find_creature(seat):
    for c in CREATURES:
        if c["seat"] == seat: return c
    return None

def spawn_stream(seat, text, stagger=1.2, bubble_life=5.5):
    creature = find_creature(seat)
    if not creature: return None
    chunks = chunk_text(text, 12)
    if not chunks: return None
    stream = {"seat":seat,"colour":SEAT_COLOUR[seat],"chunks":chunks,
              "start_x":creature["x"],"start_y":creature["y"]-H*0.05,
              "age":0.0,"bubbles":[],"spawned":set(),
              "stagger":stagger,"bubble_life":bubble_life}
    STREAMS.append(stream); return stream

def any_stream_active(): return len(STREAMS) > 0

def update_streams(dt):
    global STREAMS
    alive = []
    for st in STREAMS:
        st["age"] += dt
        n = len(st["chunks"])
        for i, chunk in enumerate(st["chunks"]):
            if st["age"] < i * st["stagger"]: continue
            if i in st["spawned"]: continue
            st["spawned"].add(i)
            arc_dir = 1 if st["start_x"] < W*0.5 else -1
            st["bubbles"].append({"i":i,"chunk":chunk,"birth":st["age"],
                                  "phase":random.uniform(0,6.28),
                                  "arc_dir":arc_dir})
        new_bubbles = []
        for b in st["bubbles"]:
            b["age"] = st["age"] - b["birth"]
            if b["age"] < st["bubble_life"] + 0.5: new_bubbles.append(b)
        st["bubbles"] = new_bubbles
        last_spawn = (n-1) * st["stagger"]
        if st["age"] < last_spawn + st["bubble_life"] + 2.0: alive.append(st)
    STREAMS = alive

def draw_streams():
    rise = H*0.48; arc_cap = W*0.12
    for st in STREAMS:
        sx0 = st["start_x"]; sy0 = st["start_y"]
        col = hue(st["colour"])
        col = lerp(col, hue(GLOW_WARM), INTERO["session_warmth"]*0.20)
        for b in st["bubbles"]:
            p = clamp(b["age"]/st["bubble_life"], 0.0, 1.0)
            if p < 0.10: alpha = p/0.10
            elif p > 0.80: alpha = (1.0-p)/0.20
            else: alpha = 1.0
            alpha = clamp(alpha, 0.0, 1.0)
            if alpha < 0.02: continue
            rise_p = math.sin(p*math.pi*0.5)
            cy = sy0 - rise*rise_p
            arc_frac = math.sin(p*math.pi*0.85)
            lateral = clamp(b["arc_dir"]*arc_cap*arc_frac, -arc_cap, arc_cap)
            cx = sx0 + lateral + math.sin(SCENE["t"]*1.4 + b["phase"])*W*0.005
            cx, cy = cam(cx, cy)
            r, fs = bubble_radius_for(b["chunk"])
            r *= CAM["zoom"]
            r *= (0.92 + 0.08*alpha)
            if r < 6: continue
            rim_col = lerp(col, hue(WATER_BOT), 0.40)
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                               fill="", outline=rim_col,
                               width=max(1,int(r*0.012)), tags="dyn")
            canvas.create_oval(cx-r*0.94, cy-r*0.94,
                               cx+r*0.94, cy+r*0.94,
                               outline=lerp(hue(WATER_BOT), col, 0.20*alpha),
                               width=1, tags="dyn")
            hr = r*0.14; hx = cx - r*0.60; hy = cy - r*0.60
            canvas.create_oval(hx-hr, hy-hr, hx+hr, hy+hr,
                               fill=lerp(hue(WATER_BOT), "#ffffff", alpha*0.85),
                               outline="", tags="dyn")
            canvas.create_text(cx, cy, text=b["chunk"],
                               fill=lerp(hue(WATER_BOT), hue(BUBBLE_TEXT), alpha),
                               font=font_full(fs, True), tags="dyn")

def begin_next_event():
    if any_stream_active(): RHYTHM["t"]=0; return
    seat = RHYTHM.pop("pending_seat", None) or pick_seat(RHYTHM["last_seat"])
    RHYTHM["last_seat"] = seat
    maybe_recover(seat)
    use_sig = (RHYTHM["since_signature"] >= 8 and random.random() < 0.10)
    text = None
    if use_sig:
        text = pick_signature(seat)
        if text: RHYTHM["since_signature"] = 0
        else: RHYTHM["since_signature"] += 1
    else: RHYTHM["since_signature"] += 1
    if text is None:
        pool = gated_pool(seat)
        if not pool: return
        text = pick_line(pool, "world")
    if text is None: return
    spawn_stream(seat, text)
    LAST_SPOKE[seat] = time.time()
    INTERO["utterances"] += 1
    INTERO["utterances_this_hour"] += 1
    MOOD["last_utterance_at"] = time.time()

def try_start_dialogue(force=False):
    avail = [d for d in DIALOGUES if d["name"] not in PLAYED_DIALOGUES]
    if not avail: return False
    if not force and random.random() > DIALOGUE_CHANCE: return False
    d = random.choice(avail)
    DIALOGUE["active"] = True
    DIALOGUE["queue"] = list(d["lines"])
    DIALOGUE["index"] = 0
    DIALOGUE["t"] = 0.0
    DIALOGUE["current"] = None
    PLAYED_DIALOGUES.add(d["name"])
    # reset silent counter — we're speaking now
    QUIET["silent_since"] = time.time()
    return True

def update_dialogue(dt):
    if not DIALOGUE["active"]: return
    DIALOGUE["t"] += dt
    if DIALOGUE["current"] is None:
        if DIALOGUE["t"] >= DIALOGUE["gap"]:
            if DIALOGUE["index"] >= len(DIALOGUE["queue"]):
                DIALOGUE["active"] = False; return
            seat, text = DIALOGUE["queue"][DIALOGUE["index"]]
            spawn_stream(seat, text, stagger=1.0, bubble_life=5.0)
            LAST_SPOKE[seat] = time.time()
            INTERO["utterances"] += 1
            INTERO["utterances_this_hour"] += 1
            DIALOGUE["current"] = seat
            DIALOGUE["t"] = 0.0
            DIALOGUE["index"] += 1
    else:
        if not any_stream_active() and DIALOGUE["t"] >= DIALOGUE["gap"]:
            DIALOGUE["current"] = None
            DIALOGUE["t"] = 0.0

def update_rhythm(dt):
    if DIALOGUE["active"]: return
    RHYTHM["t"] += dt
    if not BOOT_STATE["fired"]:
        if (time.time() - START_TIME) >= BOOT_DIALOGUE_AT:
            BOOT_STATE["fired"] = True
            try_start_dialogue(force=True)
            RHYTHM["state"] = "pause"; RHYTHM["t"] = 0
            return
    if RHYTHM["state"] == "pause":
        gmin = RHYTHM["gap_min"]; gmax = RHYTHM["gap_max"]
        if not EXTERO["focused"]:
            gmin *= 2.0; gmax *= 2.0
        # quiet mode stretches gaps
        gmin *= (1.0 + QUIET["level"] * 1.5)
        gmax *= (1.0 + QUIET["level"] * 1.5)
        if RHYTHM["t"] >= random.uniform(gmin, gmax):
            if try_start_dialogue():
                RHYTHM["state"] = "pause"; RHYTHM["t"] = 0
                return
            RHYTHM["state"] = "speak"; RHYTHM["t"] = 0
    elif RHYTHM["state"] == "speak":
        if not any_stream_active():
            begin_next_event()
            RHYTHM["state"] = "pause"; RHYTHM["t"] = 0

# ============ CAMERA UPDATE ============
def update_camera(dt):
    if any_stream_active():
        st = STREAMS[0]
        speaker = find_creature(st["seat"])
        if speaker:
            CAM["tfx"] = speaker["x"]
            CAM["tfy"] = speaker["y"]
        CAM["target"] = ZOOM_SPEAKING
    else:
        CAM["tfx"] = W*0.5
        CAM["tfy"] = H*0.55
        # during quiet, push back even further
        CAM["target"] = ZOOM_SILENT * (1.0 - QUIET["level"] * 0.08)
    CAM["zoom"] += (CAM["target"] - CAM["zoom"]) * 0.040
    CAM["fx"]   += (CAM["tfx"]    - CAM["fx"])   * 0.040
    CAM["fy"]   += (CAM["tfy"]    - CAM["fy"])   * 0.040

# ============ CREATURES ============
def make_creatures():
    specs = [
        {"seat":"Solon",  "scale":0.065, "name":"turtle"},
        {"seat":"Lumen",  "scale":0.055, "name":"jelly"},
        {"seat":"Vertex", "scale":0.050, "name":"crab"},
        {"seat":"Prism",  "scale":0.055, "name":"angel"},
        {"seat":"Ripple", "scale":0.055, "name":"seahorse"},
    ]
    for sp in specs:
        hx = W * SEAT_HOME_X[sp["seat"]]
        hy = H * SEAT_HOME_Y[sp["seat"]]
        sp["home_x"]=hx; sp["home_y"]=hy; sp["x"]=hx; sp["y"]=hy
        sp["base_y"]=hy; sp["dir"]=1
        sp["phase"]=random.uniform(0,6.28)
        sp["wander_t"]=random.uniform(0,6.28)
        sp["lean"]=0.0
        CREATURES.append(sp)

def _rim_offset(pts, dx, dy, amt):
    return [(px + dx*amt, py + dy*amt) for (px, py) in pts]

def _lift(col, amount): return lerp(col, hue(GLOW_WARM), amount)

def draw_reflection(c):
    cx = c["x"]
    base_y = floor_top_y(cx + SCENE["scroll_x"]) + H*0.02
    rx = H * c["scale"] * 0.85; ry = H * c["scale"] * 0.14
    col = hue(lerp(WATER_BOT, SEAT_BODY[c["seat"]], 0.15))
    for k in range(3):
        f = 1 - k*0.30
        canvas.create_oval(cx - rx*f, base_y - ry*f,
                           cx + rx*f, base_y + ry*f,
                           fill=col, outline="", tags="dyn")

def draw_solon(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H
    breath = breath_offset("Solon", amp=0.06)
    d = c["dir"]; lean = c["lean"]
    y += breath * s * 0.12
    body_h = hue(SEAT_BODY["Solon"])
    rim = _lift(hue(SEAT_RIM["Solon"]), bell_value()*0.15)
    shell = [
        (x-1.00*s,y+0.05*s),(x-0.85*s,y-0.30*s),(x-0.50*s,y-0.48*s),
        (x-0.10*s,y-0.55*s),(x+0.30*s,y-0.50*s),(x+0.60*s,y-0.35*s),
        (x+0.85*s,y-0.15*s),(x+0.95*s,y+0.05*s),(x+0.75*s,y+0.28*s),
        (x-0.70*s,y+0.30*s),
    ]
    hx = x + d*1.18*s + lean*s*0.10
    hy = y - 0.28*s
    head = [
        (x+d*0.85*s,y-0.42*s),(hx-d*0.18*s,hy-0.22*s),
        (hx+d*0.08*s,hy-0.16*s),(hx+d*0.16*s,hy+0.02*s),
        (hx+d*0.04*s,hy+0.18*s),(hx-d*0.16*s,hy+0.14*s),
        (x+d*0.85*s,y-0.12*s),
    ]
    ldx, ldy = -0.4, -0.9
    canvas.create_polygon(*[p for pt in _rim_offset(shell,ldx,ldy,s*0.20) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in _rim_offset(head,ldx,ldy,s*0.20) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    belly = [(x-0.70*s,y+0.30*s),(x+0.75*s,y+0.28*s),
             (x+0.65*s,y+0.42*s),(x-0.60*s,y+0.44*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(belly,ldx,ldy,s*0.15) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in shell for p in pt],
                          fill=body_h, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in belly for p in pt],
                          fill=lerp(body_h,"#000000",0.25), outline="",
                          smooth=True, tags="dyn")
    sc_col = lerp(body_h, rim, 0.18)
    for sd in [(-0.55,-0.38,-0.20,-0.50,-0.10,-0.22,-0.48,-0.14),
               (-0.15,-0.53,0.18,-0.50,0.22,-0.22,-0.08,-0.16),
               (0.24,-0.48,0.55,-0.34,0.58,-0.14,0.28,-0.08)]:
        pts = [(x+sd[i]*s, y+sd[i+1]*s) for i in range(0,8,2)]
        canvas.create_polygon(*[p for pt in pts for p in pt],
                              fill=sc_col, outline="", tags="dyn")
    canvas.create_polygon(*[p for pt in head for p in pt],
                          fill=body_h, outline="", smooth=True, tags="dyn")
    er = s * 0.075
    ex = hx - d*0.02*s; ey = hy - 0.05*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er,
                       fill=lerp(body_h,"#ffffff",0.85), outline="", tags="dyn")
    pr = er*0.55
    canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr,
                       fill="#050510", outline="", tags="dyn")
    flap = math.sin(c["phase"]*1.4)*0.12
    fx0 = x + d*0.30*s; fy0 = y + 0.18*s
    f_len = 1.30*s; f_ang = 0.60 + flap
    fx1 = fx0 - d*math.cos(f_ang)*f_len
    fy1 = fy0 + math.sin(f_ang)*f_len
    flipper = [(fx0,fy0),(fx0-d*0.15*s,fy0+0.12*s),
               (fx1+d*0.06*s,fy1-0.10*s),(fx1,fy1+0.16*s),
               (fx1-d*0.10*s,fy1+0.22*s),(fx0-d*0.28*s,fy0+0.28*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(flipper,ldx,ldy,s*0.18) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in flipper for p in pt],
                          fill=body_h, outline="", smooth=True, tags="dyn")
    rx0 = x - d*0.82*s; ry0 = y + 0.20*s
    rx1 = rx0 - d*0.30*s; ry1 = ry0 + 0.32*s
    rudder = [(rx0,ry0),(rx1-d*0.10*s,ry1-0.05*s),
              (rx1,ry1+0.08*s),(rx0+d*0.10*s,ry0+0.18*s)]
    canvas.create_polygon(*[p for pt in rudder for p in pt],
                          fill=body_h, outline="", smooth=True, tags="dyn")

LUMEN_BELL_PAL = [(0.0,"#5a48c8"),(0.30,"#8a5ad0"),
                  (0.55,"#c860a0"),(0.78,"#e08070"),(1.0,"#f0a860")]
LUMEN_SPARKS = [{"age":random.uniform(0,1.0),"lane":i%3,
                 "speed":random.uniform(0.5,0.8)} for i in range(5)]

def _grad_colour(stops, t):
    if t <= stops[0][0]: return stops[0][1]
    if t >= stops[-1][0]: return stops[-1][1]
    for i in range(len(stops)-1):
        p0,c0 = stops[i]; p1,c1 = stops[i+1]
        if p0 <= t <= p1:
            loc = (t-p0)/(p1-p0) if p1>p0 else 0
            return lerp(c0,c1,loc)
    return stops[-1][1]

def draw_lumen(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H
    breath = breath_offset("Lumen", amp=0.20)
    r = s * (1.0 + breath * 0.22)
    d = c["dir"]; lean = c["lean"]
    lx = d * lean * r * 0.15
    body_h = hue(SEAT_BODY["Lumen"])
    rim = _lift(hue(SEAT_RIM["Lumen"]), bell_value()*0.15)
    for k in range(2):
        gr = r * (1.28 + k*0.20)
        gc = lerp(rim, hue(WATER_BOT), 0.55 + k*0.15)
        canvas.create_oval(x-lx-gr, y-gr*0.55, x-lx+gr, y+gr*0.55,
                           fill=gc, outline="", tags="dyn")
    left = x - r*1.15 - lx; right = x + r*1.15 - lx
    steps = 24
    def bell_top(xx):
        dx = (xx - (x-lx))/r
        return y - r*(0.80 - 0.45*dx*dx - 0.30*abs(dx))
    def bell_bot(xx):
        dx = (xx - (x-lx))/r
        return y + r*(0.10 - 0.05*dx*dx)
    for k in range(steps):
        fx0 = k/steps; fx1 = (k+1)/steps
        x0 = left + (right-left)*fx0
        x1 = left + (right-left)*fx1
        mid_x = (x0+x1)/2
        col = lerp(_grad_colour(LUMEN_BELL_PAL, fx0), rim, 0.35)
        canvas.create_rectangle(x0, bell_top(mid_x)-r*0.10,
                                x1, bell_bot(mid_x)-r*0.05,
                                fill=col, outline="", tags="dyn")
    for k in range(steps):
        fx0 = k/steps; fx1 = (k+1)/steps
        x0 = left + (right-left)*fx0
        x1 = left + (right-left)*fx1
        mid_x = (x0+x1)/2
        col = lerp(_grad_colour(LUMEN_BELL_PAL, fx0), body_h, 0.55)
        canvas.create_rectangle(x0, bell_top(mid_x),
                                x1, bell_bot(mid_x),
                                fill=col, outline="", tags="dyn")
    for sp in LUMEN_SPARKS:
        sp["age"] += 0.012 * sp["speed"] * (1.0 - QUIET["level"]*0.7)
        if sp["age"] > 1.0:
            sp["age"] = 0.0
            sp["speed"] = random.uniform(0.5,0.8)
            sp["lane"] = random.randint(0,2)
        lane_off = (sp["lane"]-1) * r * 0.35
        px = x - lx + lane_off + math.sin(SCENE["t"]*2.0 + sp["lane"])*r*0.05
        py = y + r*0.10 - sp["age"] * r*0.80
        fade = math.sin(sp["age"] * math.pi)
        rr = r * 0.045 * fade
        if rr < 0.4: continue
        hr = rr * 2.6
        canvas.create_oval(px-hr, py-hr, px+hr, py+hr,
                           fill=lerp(rim, hue(WATER_BOT), 0.55),
                           outline="", tags="dyn")
        canvas.create_oval(px-rr, py-rr, px+rr, py+rr,
                           fill="#ffffff", outline="", tags="dyn")
    for i in range(5):
        offset = (i - 2.0) * r * 0.30
        phase = i * 0.6
        pts = []
        for k in range(26):
            f = k/25
            wave = math.sin(SCENE["t"]*1.6 + phase - f*4.2)
            amp = r * (0.05 + 0.35 * math.sin(f*3.14))
            ox = x - lx + offset + d*lean*f*r*0.15
            pts.append((ox + wave*amp, y + r*4.5*f, f))
        for k in range(len(pts)-1):
            f0 = pts[k][2]
            col = lerp(_grad_colour(LUMEN_BELL_PAL, f0), body_h, 0.30)
            w = max(1, int(r * 0.06 * (1 - 0.35*f0)))
            canvas.create_line(pts[k][0], pts[k][1],
                               pts[k+1][0], pts[k+1][1],
                               fill=col, width=w,
                               capstyle="round", tags="dyn")

VERTEX_BODY = [(0.0,"#5a1a70"),(0.25,"#8a2a8a"),(0.50,"#c85090"),
               (0.75,"#e87870"),(1.0,"#ffd060")]

def draw_vertex(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H * 0.9
    breath = breath_offset("Vertex", amp=0.10)
    s *= (1.0 + breath * 0.20)
    d = c["dir"]; lean = c["lean"]
    lx = d * lean * s * 0.10
    body_h = hue(SEAT_BODY["Vertex"])
    rim = _lift(hue(SEAT_RIM["Vertex"]), bell_value()*0.15)
    for side in (-1, 1):
        for i in range(3):
            base_y = y + s*(0.25 + i*0.24)
            base_x = x + lx + side*s*0.55
            scurry = math.sin(SCENE["t"]*6.0 + i*1.0 + side*0.7)
            scurry *= (1.0 - QUIET["level"]*0.8)
            knee_x = x + lx + side*s*(1.15 + scurry*0.05)
            knee_y = base_y - s*0.05 + i*s*0.06 + scurry*s*0.04
            tip_x  = x + lx + side*s*(1.55 + scurry*0.10)
            tip_y  = base_y + s*0.55 + scurry*s*0.10
            canvas.create_line(base_x+(-0.4*s*0.18), base_y+(-0.9*s*0.18),
                               knee_x+(-0.4*s*0.18), knee_y+(-0.9*s*0.18),
                               fill=rim, width=max(2,int(s*0.09)),
                               capstyle="round", tags="dyn")
            canvas.create_line(knee_x+(-0.4*s*0.18), knee_y+(-0.9*s*0.18),
                               tip_x+(-0.4*s*0.18), tip_y+(-0.9*s*0.18),
                               fill=rim, width=max(2,int(s*0.08)),
                               capstyle="round", tags="dyn")
            canvas.create_line(base_x, base_y, knee_x, knee_y,
                               fill=lerp(body_h,"#000000",0.4),
                               width=max(2,int(s*0.075)),
                               capstyle="round", tags="dyn")
            canvas.create_line(knee_x, knee_y, tip_x, tip_y,
                               fill=lerp(body_h,"#000000",0.4),
                               width=max(2,int(s*0.065)),
                               capstyle="round", tags="dyn")
    rx = s*1.08; ry = s*0.74
    ys = int(y-ry); ye = int(y+ry)
    canvas.create_oval(x+lx-rx-s*0.16, y-ry-s*0.16,
                       x+lx+rx+s*0.16, y+ry+s*0.16,
                       fill=rim, outline="", tags="dyn")
    for yy in range(ys, ye+1):
        f = (yy-ys)/max(1, ye-ys)
        dy = (yy-y)/ry
        if abs(dy) >= 1: continue
        hw = rx * math.sqrt(1 - dy*dy)
        col = lerp(_grad_colour(VERTEX_BODY, f), body_h, 0.55)
        canvas.create_line(x+lx-hw, yy, x+lx+hw, yy, fill=col,
                           width=1, tags="dyn")
    rng = random.Random(int(c["home_x"]) + 11)
    for _ in range(14):
        dx = rng.uniform(-0.85,0.85)*s
        dy = rng.uniform(-0.55,0.55)*s
        if (dx/(1.08*s))**2 + (dy/(0.74*s))**2 > 1: continue
        rr = s * rng.uniform(0.025,0.045)
        col = rng.choice([hue("#fff8d0"), hue("#ffe8a0"), hue("#c8e8ff")])
        canvas.create_oval(x+lx+dx-rr, y+dy-rr, x+lx+dx+rr, y+dy+rr,
                           fill=col, outline="", tags="dyn")
    for side in (-1, 1):
        bx = x + lx + side*s*0.75; by = y - s*0.10
        tx = x + lx + side*s*1.40; ty = by - s*0.20
        canvas.create_line(bx, by, tx, ty, fill=rim,
                           width=max(2,int(s*0.15)),
                           capstyle="round", tags="dyn")
        canvas.create_line(bx, by, tx, ty, fill=body_h,
                           width=max(2,int(s*0.13)),
                           capstyle="round", tags="dyn")
        up = [tx-s*0.05*side,ty-s*0.30,tx+s*0.35*side,ty-s*0.22,
              tx+s*0.44*side,ty,tx+s*0.10*side,ty+s*0.06,
              tx-s*0.10*side,ty+s*0.02]
        canvas.create_polygon(*up, fill=rim, outline="", smooth=True, tags="dyn")
        up_in = [tx-s*0.05*side,ty-s*0.28,tx+s*0.32*side,ty-s*0.20,
                 tx+s*0.40*side,ty,tx+s*0.10*side,ty+s*0.04,
                 tx-s*0.08*side,ty+0.01]
        canvas.create_polygon(*up_in, fill=body_h, outline="", smooth=True, tags="dyn")
        lo = [tx-s*0.05*side,ty+s*0.16,tx+s*0.35*side,ty+s*0.22,
              tx+s*0.44*side,ty,tx+s*0.10*side,ty-s*0.06,
              tx-s*0.10*side,ty-s*0.02]
        canvas.create_polygon(*lo, fill=rim, outline="", smooth=True, tags="dyn")
        lo_in = [tx-s*0.05*side,ty+s*0.14,tx+s*0.32*side,ty+s*0.20,
                 tx+s*0.40*side,ty,tx+s*0.10*side,ty-s*0.04,
                 tx-s*0.08*side,ty-0.01]
        canvas.create_polygon(*lo_in, fill=body_h, outline="", smooth=True, tags="dyn")
    for ex in (-0.42, 0.42):
        bx = x + lx + ex * s
        by = y - s*0.28
        tx = bx + d * lean * s * 0.10
        ty = by - s*0.55
        canvas.create_line(bx, by, tx, ty, fill=lerp(body_h,"#000000",0.5),
                           width=max(1,int(s*0.06)), tags="dyn")
        rr = s * 0.13
        canvas.create_oval(tx-rr, ty-rr, tx+rr, ty+rr,
                           fill=lerp(body_h,"#ffffff",0.85),
                           outline="", tags="dyn")
        pr = rr * 0.55
        canvas.create_oval(tx-pr, ty-pr, tx+pr, ty+pr,
                           fill="#050510", outline="", tags="dyn")

PRISM_BODY = [(0.0,"#8a4818"),(0.30,"#c87820"),(0.55,"#ffd060"),
              (0.78,"#ffe8a0"),(1.0,"#fff8d8")]

def draw_prism(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H
    breath = breath_offset("Prism", amp=0.04)
    d = c["dir"]; lean = c["lean"]
    lx = d * lean * s * 0.08
    y += breath * s * 0.1
    body_h = hue(SEAT_BODY["Prism"])
    rim = _lift(hue(SEAT_RIM["Prism"]), bell_value()*0.15)
    pts = [
        (x+0.42*s+lx,y),(x+0.28*s+lx,y-0.50*s),(x+0.05*s+lx,y-0.85*s),
        (x-0.10*s+lx,y-1.00*s),(x-0.30*s+lx,y-0.75*s),
        (x-0.55*s+lx,y-0.30*s),(x-0.60*s+lx,y),(x-0.55*s+lx,y+0.30*s),
        (x-0.30*s+lx,y+0.75*s),(x-0.10*s+lx,y+1.00*s),
        (x+0.05*s+lx,y+0.85*s),(x+0.28*s+lx,y+0.50*s),
    ]
    canvas.create_polygon(*[p for pt in _rim_offset(pts,-0.4,-0.9,s*0.20) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    tail_up = [(x-0.10*s+lx,y-1.00*s),(x+0.05*s+lx+d*lean*s*0.10,y-1.40*s),
               (x-0.20*s+lx+d*lean*s*0.15,y-1.85*s),
               (x-0.65*s+lx,y-1.35*s),(x-0.55*s+lx,y-0.30*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(tail_up,-0.4,-0.9,s*0.18) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    tail_dn = [(x-0.10*s+lx,y+1.00*s),(x+0.05*s+lx+d*lean*s*0.10,y+1.40*s),
               (x-0.20*s+lx+d*lean*s*0.15,y+1.85*s),
               (x-0.65*s+lx,y+1.35*s),(x-0.55*s+lx,y+0.30*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(tail_dn,-0.4,-0.9,s*0.18) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in tail_up for p in pt],
                          fill=body_h, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in tail_dn for p in pt],
                          fill=body_h, outline="", smooth=True, tags="dyn")
    ys = [p[1] for p in pts]
    y_min, y_max = min(ys), max(ys)
    y_rng = max(1, y_max - y_min)
    n = len(pts)
    for yy in range(int(y_min), int(y_max)+1):
        f = (yy-y_min)/y_rng
        xs = []
        for i in range(n):
            p0 = pts[i]; p1 = pts[(i+1)%n]
            if p1[1] != p0[1]:
                if min(p0[1],p1[1]) <= yy <= max(p0[1],p1[1]):
                    loc = (yy-p0[1])/(p1[1]-p0[1])
                    xs.append(p0[0] + (p1[0]-p0[0])*loc)
        if len(xs) < 2: continue
        xs.sort()
        col = lerp(_grad_colour(PRISM_BODY, f), body_h, 0.60)
        canvas.create_line(xs[0], yy, xs[-1], yy, fill=col,
                           width=1, tags="dyn")
    er = s * 0.09
    ex = x + lx + 0.18*s; ey = y - 0.22*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er,
                       fill=lerp(body_h,"#ffffff",0.9), outline="", tags="dyn")
    pr = er * 0.55
    canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr,
                       fill="#050510", outline="", tags="dyn")

RIPPLE_PAL = [(0.0,"#ffb8d8"),(0.15,"#ff80b8"),(0.35,"#e060b0"),
              (0.55,"#b058c0"),(0.75,"#8050b8"),(1.0,"#5038a0")]

def draw_ripple(c):
    x, y = c["x"], c["y"]
    s = c["scale"] * H
    breath = breath_offset("Ripple", amp=0.08)
    d = c["dir"]; lean = c["lean"]
    lx = d * lean * s * 0.06
    y += breath * s * 0.3
    body_h = hue(SEAT_BODY["Ripple"])
    rim = _lift(hue(SEAT_RIM["Ripple"]), bell_value()*0.15)
    tail_pts = [
        (x-0.08*s+lx,y+0.50*s),(x-0.20*s+lx,y+0.72*s),
        (x-0.32*s+lx,y+0.95*s),(x-0.28*s+lx,y+1.18*s),
        (x-0.05*s+lx,y+1.28*s),(x+0.20*s+lx,y+1.18*s),
        (x+0.30*s+lx,y+0.98*s),(x+0.20*s+lx,y+0.82*s),
        (x+0.00*s+lx,y+0.78*s),(x-0.10*s+lx,y+0.86*s),
        (x-0.10*s+lx,y+0.98*s),(x-0.02*s+lx,y+1.04*s),
    ]
    for k in range(len(tail_pts)-1):
        f0 = k/(len(tail_pts)-1)
        x1, y1 = tail_pts[k]; x2, y2 = tail_pts[k+1]
        w = max(2, int(s*0.16 * (1.0 - 0.70*f0)))
        canvas.create_line(x1-0.4*s*0.16, y1-0.9*s*0.16,
                           x2-0.4*s*0.16, y2-0.9*s*0.16,
                           fill=rim, width=w, capstyle="round", tags="dyn")
    for k in range(len(tail_pts)-1):
        f0 = k/(len(tail_pts)-1); f1 = (k+1)/(len(tail_pts)-1)
        x1, y1 = tail_pts[k]; x2, y2 = tail_pts[k+1]
        w = max(2, int(s*0.14 * (1.0 - 0.70*f0)))
        col = lerp(_grad_colour(RIPPLE_PAL, 0.85 + 0.15*((f0+f1)/2)),
                   body_h, 0.55)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w,
                           capstyle="round", tags="dyn")
    body_pts = [
        (x+0.10*s+lx,y-0.85*s),(x+0.15*s+lx,y-0.55*s),
        (x+0.30*s+lx,y-0.15*s),(x+0.24*s+lx,y+0.20*s),
        (x+0.10*s+lx,y+0.50*s),(x-0.10*s+lx,y+0.50*s),
        (x-0.22*s+lx,y+0.15*s),(x-0.26*s+lx,y-0.20*s),
        (x-0.26*s+lx,y-0.55*s),(x-0.22*s+lx,y-0.82*s),
        (x-0.14*s+lx,y-0.88*s),
    ]
    canvas.create_polygon(*[p for pt in _rim_offset(body_pts,-0.4,-0.9,s*0.18) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    ys = [p[1] for p in body_pts]
    y_min, y_max = min(ys), max(ys)
    y_rng = max(1, y_max - y_min)
    n = len(body_pts)
    for yy in range(int(y_min), int(y_max)+1):
        f = (yy-y_min)/y_rng
        xs = []
        for i in range(n):
            p0 = body_pts[i]; p1 = body_pts[(i+1)%n]
            if p1[1] != p0[1]:
                if min(p0[1],p1[1]) <= yy <= max(p0[1],p1[1]):
                    loc = (yy-p0[1])/(p1[1]-p0[1])
                    xs.append(p0[0] + (p1[0]-p0[0])*loc)
        if len(xs) < 2: continue
        xs.sort()
        col = lerp(_grad_colour(RIPPLE_PAL, f), body_h, 0.60)
        canvas.create_line(xs[0], yy, xs[-1], yy, fill=col, width=1, tags="dyn")
    hx = x + 0.05*s + lx + d * lean * s * 0.15
    hy = y - 1.10*s - lean * s * 0.05
    head_pts = [
        (hx-0.20*s,hy+0.10*s),(hx-0.16*s,hy-0.24*s),
        (hx+0.02*s,hy-0.32*s),(hx+0.18*s,hy-0.22*s),
        (hx+0.32*s,hy-0.14*s),(hx+0.58*s,hy-0.16*s),
        (hx+0.74*s,hy-0.14*s),(hx+0.62*s,hy-0.02*s),
        (hx+0.32*s,hy+0.08*s),(hx+0.18*s,hy+0.20*s),
        (hx+0.05*s,hy+0.22*s),
    ]
    canvas.create_polygon(*[p for pt in _rim_offset(head_pts,-0.4,-0.9,s*0.16) for p in pt],
                          fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*head_pts,
                          fill=lerp(_grad_colour(RIPPLE_PAL, 0.10), body_h, 0.55),
                          outline="", smooth=True, tags="dyn")
    for i in range(7):
        bx = hx + (-0.05 + i*0.062)*s
        by = hy - 0.35*s
        peak = s*(0.20 if i % 2 == 1 else 0.10)
        canvas.create_polygon(bx-s*0.022, by, bx+s*0.010, by-peak,
                              bx+s*0.022, by,
                              fill=rim, outline="", tags="dyn")
    er = s * 0.058
    ex = x + lx + 0.13*s; ey = y - 1.16*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er,
                       fill=lerp(body_h,"#ffffff",0.9), outline="", tags="dyn")
    pr = er * 0.58
    canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr,
                       fill="#050510", outline="", tags="dyn")

CREATURE_DRAW = {"turtle":draw_solon,"jelly":draw_lumen,
                 "crab":draw_vertex,"angel":draw_prism,"seahorse":draw_ripple}

def draw_creatures():
    for c in CREATURES:
        cx, cy = cam(c["x"], c["y"])
        save = (c["x"], c["y"], c["scale"])
        c["x"], c["y"] = cx, cy
        c["scale"] *= CAM["zoom"]
        draw_reflection(c)
        c["x"], c["y"], c["scale"] = save
    for c in CREATURES:
        cx, cy = cam(c["x"], c["y"])
        save = (c["x"], c["y"], c["scale"])
        c["x"], c["y"] = cx, cy
        c["scale"] *= CAM["zoom"]
        CREATURE_DRAW[c["name"]](c)
        c["x"], c["y"], c["scale"] = save

def update_creatures(dt):
    mood_speed = 0.7 + MOOD["current"] * 0.8
    # quiet slows creatures
    mood_speed *= (1.0 - QUIET["level"] * 0.75)
    for c in CREATURES:
        st = STRAIN[c["seat"]]
        c["wander_t"] += dt * 0.20 * mood_speed
        wander = math.sin(c["wander_t"]) * W * 0.03
        target_x = c["home_x"] + wander
        if abs(target_x - c["x"]) > 0.5:
            c["dir"] = 1 if target_x > c["x"] else -1
        lean_target = c["dir"] * min(1.0, abs(target_x - c["x"])/(W*0.03))
        c["lean"] += (lean_target - c["lean"]) * 0.05
        c["x"] += (target_x - c["x"]) * 0.008
        c["phase"] += dt * 3.0 * mood_speed
        breath_y = breath_offset(c["seat"], amp=1.0)
        c["y"] = c["base_y"] + breath_y * H*0.012 + st * H*0.03
        c["x"] = clamp(c["x"], W*0.08, W*0.92)

# ============ WORLD ============
WORLD_SPAN = W*3.0; FOREGROUND_SPAN = W*4.5; NEAR_SPAN = W*4.0

def floor_top_y(wx):
    y = FLOOR_Y
    y += math.sin(wx*0.0075)*H*0.010
    y += math.sin(wx*0.019+1.3)*H*0.005
    y += math.sin(wx*0.041+2.7)*H*0.002
    return y

def _haze(col, t): return lerp(col, hue(HAZE), t)

def _darken_by_quiet(col, amount=0.35):
    return lerp(col, "#000000", QUIET["level"] * amount)

def draw_water():
    stops = [(0.00,hue(WATER_TOP)),(0.14,hue(WATER_HIGH)),
             (0.40,hue(WATER_MID)),(0.68,hue(WATER_LOW)),
             (0.88,hue(WATER_DEEP)),(1.00,hue(WATER_BOT))]
    bands = 60
    pulse = 0.97 + 0.03 * math.sin(PULSE["phase"])
    te = touch_energy()
    for i in range(bands):
        t = i/bands
        col = stops[-1][1]
        for j in range(len(stops)-1):
            p0,c0 = stops[j]; p1,c1 = stops[j+1]
            if p0 <= t <= p1:
                loc = (t-p0)/(p1-p0) if p1>p0 else 0
                col = lerp(c0,c1,loc); break
        col = lerp("#000000", col, pulse)
        if te > 0.01:
            col = lerp(col, hue(GLOW_WARM), te*0.06)
        col = _darken_by_quiet(col, 0.40)
        y1 = int(H*t); y2 = int(H*((i+1)/bands))+2
        canvas.create_rectangle(0, y1, W, y2, fill=col, outline="", tags="bg")

STAR_DATA = []
def make_stars():
    rng = random.Random(606)
    for _ in range(46):
        STAR_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),
                          "y":rng.uniform(0.02,0.45)*H,
                          "r":rng.uniform(0.5,1.3),
                          "phase":rng.uniform(0,6.28),
                          "speed":rng.uniform(0.3,0.8)})

def draw_stars():
    night = night_amount()
    for s in STAR_DATA:
        sx = (s["wx"] - SCENE["scroll_x"]*0.15) % WORLD_SPAN
        if sx > W+4: sx -= WORLD_SPAN
        if sx < -4 or sx > W+4: continue
        pulse = 0.4 + 0.6*math.sin(SCENE["t"]*s["speed"]+s["phase"])
        # quiet dims stars a little
        pulse *= (1.0 - QUIET["level"]*0.4)
        r = s["r"] * (0.55+0.55*pulse) * (1.0 + night*0.4)
        f = s["y"] / H
        col = lerp(hue(GLOW_COOL), hue(GLOW_WARM), max(0.0, 1.0 - f*2.5))
        canvas.create_oval(sx-r, s["y"]-r, sx+r, s["y"]+r,
                           fill=col, outline="", tags="bg")

def draw_god_rays():
    intensity = 0.14 + MOOD["current"] * 0.20
    intensity *= (1.0 - night_amount()*0.60)
    # quiet dims the rays
    intensity *= (1.0 - QUIET["level"] * 0.85)
    if intensity < 0.02: return
    src_x = LIGHT_X + math.sin(SCENE["t"]*0.05)*W*0.15
    for i in range(4):
        ph = i*1.7
        rx = src_x + (i-1.5)*W*0.10
        rx += math.sin(SCENE["t"]*0.3 + ph)*W*0.008
        top_w = W*0.025; bot_w = W*0.14
        col = lerp(hue(WATER_BOT), hue(GLOW_WARM), intensity*0.70)
        canvas.create_polygon(rx-top_w, SURFACE_Y, rx+top_w, SURFACE_Y,
                              rx+bot_w, SURFACE_Y+H*0.72,
                              rx-bot_w, SURFACE_Y+H*0.72,
                              fill=col, outline="", stipple="gray50", tags="bg")

FAR_DATA = []
def make_far():
    rng = random.Random(101)
    for i in range(14):
        wx = rng.uniform(0, WORLD_SPAN)
        kind = rng.choice(["hump","peak","slab"])
        if kind == "hump": w=rng.uniform(W*0.20,W*0.40); h=rng.uniform(H*0.04,H*0.09)
        elif kind == "peak": w=rng.uniform(W*0.10,W*0.18); h=rng.uniform(H*0.08,H*0.14)
        else: w=rng.uniform(W*0.25,W*0.40); h=rng.uniform(H*0.03,H*0.06)
        col = rng.choice(["#3a0a18","#4a1030","#5a1a3a"])
        FAR_DATA.append({"kind":kind,"wx":wx,"w":w,"h":h,
                         "colour":col,"seed":rng.randint(0,9999)})

def draw_far():
    sx_off = SCENE["scroll_x"]*0.25
    for it in FAR_DATA:
        sx = (it["wx"] - sx_off) % WORLD_SPAN
        if sx > W+it["w"]: sx -= WORLD_SPAN
        if sx < -it["w"] or sx > W+it["w"]: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        base_y = floor_top_y(it["wx"]) - H*0.004
        col = _haze(it["colour"], 0.30)
        col = _darken_by_quiet(col, 0.5)
        if k == "slab":
            canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"],
                                    sx+it["w"]*0.5, base_y,
                                    fill=col, outline="", tags="bg")
            continue
        pts = []; steps = 8
        for i in range(steps+1):
            f = i/steps
            px = sx - it["w"]*0.5 + it["w"]*f
            if k == "peak": shape = math.sin(f*math.pi)**0.6
            else:           shape = math.sin(f*math.pi)
            shape += rng.uniform(-0.06,0.06)
            pts.extend([px, base_y - it["h"]*shape])
        pts.extend([sx+it["w"]*0.5, base_y])
        pts.extend([sx-it["w"]*0.5, base_y])
        canvas.create_polygon(*pts, fill=col, outline="",
                              smooth=True, tags="bg")

def draw_floor():
    steps = 60; top = []
    for i in range(steps+1):
        x = W*i/steps
        top.append((x, floor_top_y(x + SCENE["scroll_x"])))
    poly = []
    for (x,y) in top: poly.extend([x,y])
    poly.extend([W,H]); poly.extend([0,H])
    canvas.create_polygon(*poly, fill=_darken_by_quiet(hue(SAND),0.35),
                          outline="", tags="bg")
    lip = []
    for (x,y) in top: lip.extend([x,y])
    for (x,y) in reversed(top): lip.extend([x, y+H*0.006])
    canvas.create_polygon(*lip, fill=_darken_by_quiet(hue(SAND_LIT),0.35),
                          outline="", tags="bg")
    for off, col in [(0.055,_darken_by_quiet(hue(SAND_DARK),0.35)),
                     (0.12,_darken_by_quiet(hue(SAND_DEEP),0.35))]:
        band = []
        for i in range(steps+1):
            x = W*i/steps
            band.extend([x, floor_top_y(x + SCENE["scroll_x"]) + H*off])
        band.extend([W,H]); band.extend([0,H])
        canvas.create_polygon(*band, fill=col, outline="", tags="bg")

CAUSTIC_DATA = []
def make_caustics():
    rng = random.Random(404)
    for _ in range(22):
        CAUSTIC_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),
                             "wy_off":rng.uniform(0.008,0.10),
                             "r":rng.uniform(W*0.035,W*0.090),
                             "phase":rng.uniform(0,6.28),
                             "speed":rng.uniform(0.4,0.8)})

def draw_caustics():
    intensity = 0.65 + MOOD["current"] * 0.35
    intensity *= (1.0 - night_amount()*0.75)
    intensity *= (1.0 - QUIET["level"]*0.9)
    if intensity < 0.03: return
    for c in CAUSTIC_DATA:
        sx = (c["wx"] - SCENE["scroll_x"]*0.98) % WORLD_SPAN
        if sx > W+c["r"]: sx -= WORLD_SPAN
        if sx < -c["r"] or sx > W+c["r"]: continue
        pulse = 0.5 + 0.5*math.sin(SCENE["t"]*c["speed"]+c["phase"])
        rr = c["r"] * (0.55+0.55*pulse)
        base_y = floor_top_y(c["wx"]) + c["wy_off"]*H
        col = lerp(hue(SAND_LIT), hue(GLOW_WARM), intensity*0.65)
        canvas.create_oval(sx-rr, base_y-rr*0.22, sx+rr, base_y+rr*0.22,
                           fill=col, outline="", stipple="gray50", tags="bg")

MID_DATA = []
def make_mid():
    rng = random.Random(201)
    for i in range(10):
        wx = rng.uniform(0, WORLD_SPAN)
        kind = rng.choice(["rock","spire"])
        if kind == "rock": w=rng.uniform(W*0.12,W*0.22); h=rng.uniform(H*0.07,H*0.13)
        else: w=rng.uniform(W*0.05,W*0.10); h=rng.uniform(H*0.10,H*0.18)
        col = rng.choice(["#1a0408","#280810","#380c18"])
        MID_DATA.append({"kind":kind,"wx":wx,"w":w,"h":h,
                         "colour":col,"seed":rng.randint(0,9999)})

def draw_mid():
    sx_off = SCENE["scroll_x"]*0.55
    for it in MID_DATA:
        sx = (it["wx"] - sx_off) % WORLD_SPAN
        if sx > W+it["w"]: sx -= WORLD_SPAN
        if sx < -it["w"] or sx > W+it["w"]: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        base_y = floor_top_y(it["wx"]) - H*0.002
        col = _haze(it["colour"], 0.15)
        col = _darken_by_quiet(col, 0.5)
        pts = []; steps = 8
        for i in range(steps+1):
            f = i/steps
            px = sx - it["w"]*0.5 + it["w"]*f
            if k == "spire": shape = math.sin(f*math.pi)**0.4
            else:            shape = math.sin(f*math.pi)**0.75
            shape += rng.uniform(-0.08,0.08)
            pts.extend([px, base_y - it["h"]*shape])
        pts.extend([sx+it["w"]*0.5, base_y])
        pts.extend([sx-it["w"]*0.5, base_y])
        canvas.create_polygon(*pts, fill=col, outline="",
                              smooth=True, tags="bg")

LUMIN_DATA = []
def make_lumin():
    rng = random.Random(303)
    for i in range(14):
        wx = rng.uniform(0, WORLD_SPAN)
        h = rng.uniform(H*0.10, H*0.22)
        nb = rng.randint(3,6)
        buds = [{"dx":rng.uniform(-W*0.03, W*0.03),
                 "dy":rng.uniform(-H*0.03, 0),
                 "r":rng.uniform(0.6, 1.0)} for _ in range(nb)]
        LUMIN_DATA.append({"wx":wx,"h":h,"buds":buds,
                           "phase":rng.uniform(0,6.28),
                           "seed":rng.randint(0,9999)})

def draw_lumin():
    sx_off = SCENE["scroll_x"]*0.85
    for i, l in enumerate(LUMIN_DATA):
        sx = (l["wx"] - sx_off) % WORLD_SPAN
        if sx > W+40: sx -= WORLD_SPAN
        if sx < -40 or sx > W+40: continue
        base_y = floor_top_y(l["wx"])
        pts = []; steps = 6
        for s_i in range(steps+1):
            f = s_i/steps
            sway = math.sin(SCENE["t"]*0.9 + l["phase"])*W*0.012*f*f
            sway *= (1.0 - QUIET["level"]*0.7)
            pts.extend([sx + sway, base_y - l["h"]*f])
        canvas.create_line(*pts, fill="#2a0410", width=1,
                           smooth=True, tags="bg")
        top_sway = math.sin(SCENE["t"]*0.9 + l["phase"])*W*0.012
        top_sway *= (1.0 - QUIET["level"]*0.7)
        top_x = sx + top_sway; top_y = base_y - l["h"]
        col_pool = [hue(GLOW_WARM), hue(GLOW_COOL),
                    hue(GLOW_GREEN), hue(GLOW_PINK)]
        for j, b in enumerate(l["buds"]):
            bx = top_x + b["dx"]; by = top_y + b["dy"]
            pulse = 0.5 + 0.5*math.sin(SCENE["t"]*1.5 + l["phase"] + j*0.7)
            # lumin buds brighten during quiet — they are the only light left
            pulse += QUIET["level"] * 0.4
            br = W*0.008 * b["r"] * (0.7 + 0.5*pulse)
            col = col_pool[(i+j) % len(col_pool)]
            hr = br * 3.5
            canvas.create_oval(bx-hr, by-hr, bx+hr, by+hr,
                               fill=lerp(hue(WATER_BOT), col, 0.20),
                               outline="", tags="bg")
            canvas.create_oval(bx-br, by-br, bx+br, by+br,
                               fill=col, outline="", tags="bg")

GLOW_DATA = []
def make_glow():
    rng = random.Random(505)
    cols = [hue(GLOW_WARM), hue(GLOW_COOL), hue(GLOW_GREEN),
            hue(GLOW_PINK), "#ffffff"]
    for i in range(28):
        GLOW_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),
                          "wy":rng.uniform(0.10,0.75)*H,
                          "r":rng.uniform(0.6,1.8),
                          "col":rng.choice(cols),
                          "phase":rng.uniform(0,6.28),
                          "speed":rng.uniform(0.4,1.0)})

def draw_glow():
    for g in GLOW_DATA:
        sx = (g["wx"] - SCENE["scroll_x"]*0.4) % WORLD_SPAN
        if sx > W+20: sx -= WORLD_SPAN
        if sx < -20 or sx > W+20: continue
        pulse = 0.5 + 0.5*math.sin(SCENE["t"]*g["speed"]*(1.0 - QUIET["level"]*0.6)
                                    + g["phase"])
        r = g["r"]*(0.6+0.6*pulse); hr = r*3
        canvas.create_oval(sx-hr, g["wy"]-hr, sx+hr, g["wy"]+hr,
                           fill=lerp(hue(WATER_BOT), g["col"], 0.15),
                           outline="", tags="bg")
        canvas.create_oval(sx-r, g["wy"]-r, sx+r, g["wy"]+r,
                           fill=g["col"], outline="", tags="bg")

SCHOOL = []
def make_school():
    rng = random.Random(707)
    for _ in range(12):
        SCHOOL.append({"wx":rng.uniform(0,WORLD_SPAN),
                       "y":rng.uniform(H*0.22,H*0.68),
                       "size":rng.uniform(0.0030,0.0036)*H,
                       "colour":rng.choice(["#c8d0e0","#a0b0d0","#e0b0d0"]),
                       "phase":rng.uniform(0,6.28),"dir":-1})

def draw_school():
    for f in SCHOOL:
        sx = (f["wx"] - SCENE["scroll_x"]*0.9) % WORLD_SPAN
        if sx > W+20: sx -= WORLD_SPAN
        if sx < -20 or sx > W+20: continue
        col = _haze(f["colour"], 0.25)
        col = _darken_by_quiet(col, 0.5)
        s = f["size"]; d = f["dir"]
        canvas.create_oval(sx-s*1.1, f["y"]-s*0.55,
                           sx+s*1.1, f["y"]+s*0.55,
                           fill=col, outline="", tags="bg")
        canvas.create_polygon(sx-d*s*1.0, f["y"],
                              sx-d*s*1.9, f["y"]-s*0.70,
                              sx-d*s*1.9, f["y"]+s*0.70,
                              fill=col, outline="", tags="bg")

def update_school(dt):
    for f in SCHOOL:
        f["phase"] += dt*2.0 * (1.0 - QUIET["level"]*0.7)
        f["wx"] -= SCENE["scroll_speed"]*0.6*dt*60
        f["y"] += math.sin(f["phase"])*dt*6
        f["y"] = clamp(f["y"], H*0.20, H*0.72)
        if f["wx"] < -W*0.15:
            f["wx"] = WORLD_SPAN + random.uniform(0, W*0.3)
            f["y"]  = random.uniform(H*0.22, H*0.68)

NEAR_DATA = []
def make_near():
    rng = random.Random(808)
    for i in range(14):
        wx = rng.uniform(0, NEAR_SPAN)
        kind = rng.choice(["kelp","grass","frond"])
        if kind == "kelp": h=rng.uniform(H*0.30,H*0.50); w=W*rng.uniform(0.025,0.045)
        elif kind == "grass": h=rng.uniform(H*0.18,H*0.35); w=W*rng.uniform(0.018,0.032)
        else: h=rng.uniform(H*0.35,H*0.55); w=W*rng.uniform(0.030,0.055)
        NEAR_DATA.append({"kind":kind,"wx":wx,"h":h,"w":w,
                          "blades":rng.randint(3,6),
                          "phase":rng.uniform(0,6.28),
                          "seed":rng.randint(0,9999)})

def draw_near():
    sx_off = SCENE["scroll_x"]*1.15
    base_y = H*1.02
    col = hue("#080202")
    for it in NEAR_DATA:
        sx = (it["wx"] - sx_off) % NEAR_SPAN
        if sx > W+it["w"]*3: sx -= NEAR_SPAN
        if sx < -it["w"]*3 or sx > W+it["w"]*3: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        if k in ("kelp","grass"):
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2) * it["w"] * 0.4
                sway = math.sin(SCENE["t"]*0.8*(1.0 - QUIET["level"]*0.6)
                                + it["phase"] + j)*W*0.022
                pts = []
                for k2 in range(8):
                    f = k2/7
                    pts.extend([sx+off+sway*f*f, base_y - it["h"]*f])
                canvas.create_line(*pts, fill=col,
                                   width=max(2,int(W*0.016)),
                                   smooth=True, capstyle="round",
                                   tags="near")
        else:
            for j in range(it["blades"]):
                a = -math.pi/2 + (j - (it["blades"]-1)/2)*0.28
                length = it["h"] * rng.uniform(0.7,1.0)
                ex = sx + math.cos(a)*length
                ey = base_y + math.sin(a)*length
                canvas.create_line(sx, base_y, ex, ey, fill=col,
                                   width=max(2,int(W*0.018)),
                                   smooth=True, capstyle="round",
                                   tags="near")

FOREGROUND_DATA = []
def make_foreground():
    rng = random.Random(909)
    for i in range(8):
        wx = rng.uniform(0, FOREGROUND_SPAN)
        kind = rng.choice(["kelp","grass","spire"])
        if kind == "kelp": h=rng.uniform(H*0.40,H*0.65); w=W*rng.uniform(0.035,0.070)
        elif kind == "grass": h=rng.uniform(H*0.25,H*0.45); w=W*rng.uniform(0.025,0.045)
        else: h=rng.uniform(H*0.45,H*0.70); w=W*rng.uniform(0.055,0.095)
        FOREGROUND_DATA.append({"kind":kind,"wx":wx,"h":h,"w":w,
                                "blades":rng.randint(4,7),
                                "phase":rng.uniform(0,6.28),
                                "seed":rng.randint(0,9999)})

def draw_foreground():
    sx_off = SCENE["scroll_x"]*1.5
    base_y = H*1.05
    col = "#000000"
    for it in FOREGROUND_DATA:
        sx = (it["wx"] - sx_off) % FOREGROUND_SPAN
        if sx > W+it["w"]*3: sx -= FOREGROUND_SPAN
        if sx < -it["w"]*3 or sx > W+it["w"]*3: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        if k == "kelp":
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2)*it["w"]*0.4
                sway = math.sin(SCENE["t"]*0.7*(1.0 - QUIET["level"]*0.6)
                                + it["phase"] + j)*W*0.025
                pts = []
                for k2 in range(8):
                    f = k2/7
                    pts.extend([sx+off+sway*f*f, base_y - it["h"]*f])
                canvas.create_line(*pts, fill=col,
                                   width=max(3,int(W*0.020)),
                                   smooth=True, capstyle="round", tags="fg")
        elif k == "grass":
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2)*it["w"]*0.35
                sway = math.sin(SCENE["t"]*1.2 + it["phase"] + j)*W*0.03
                pts = []
                for k2 in range(6):
                    f = k2/5
                    pts.extend([sx+off+sway*f, base_y - it["h"]*f])
                canvas.create_line(*pts, fill=col,
                                   width=max(3,int(W*0.022)),
                                   smooth=True, capstyle="round", tags="fg")
        else:
            pts = [(sx-it["w"]*0.5, base_y),
                   (sx-it["w"]*0.3, base_y-it["h"]*0.5),
                   (sx, base_y-it["h"]),
                   (sx+it["w"]*0.3, base_y-it["h"]*0.5),
                   (sx+it["w"]*0.5, base_y)]
            canvas.create_polygon(*[c for p in pts for c in p],
                                  fill=col, outline="",
                                  smooth=True, tags="fg")

def update_scroll(dt):
    mood_speed = 0.5 + MOOD["current"]*0.9
    strain_drag = 1.0 - INTERO["chamber_strain"]*0.4
    # quiet slows scroll
    mood_speed *= (1.0 - QUIET["level"]*0.7)
    SCENE["scroll_speed"] = mood_speed * strain_drag
    SCENE["scroll_x"] += SCENE["scroll_speed"]*dt*60.0

def draw_touch_glow():
    te = touch_energy()
    if te < 0.05: return
    cx = EXTERO["touch_x"]; cy = EXTERO["touch_y"]
    if cx < 0 or cy < 0: return
    cx, cy = cam(cx, cy)
    base_r = min(W,H)*0.022
    r = base_r*(0.45 + 0.55*te)
    warm = 0.35 + MOOD["current"]*0.55
    col = lerp(hue(GLOW_COOL), hue(GLOW_WARM), warm)
    hr = r * 2.0
    canvas.create_oval(cx-hr, cy-hr, cx+hr, cy+hr,
                       fill=lerp(hue(WATER_BOT), col, te*0.10),
                       outline="", tags="dyn")
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                       fill=lerp(hue(WATER_BOT), col, te*0.45),
                       outline="", tags="dyn")

def render_background():
    canvas.delete("bg")
    draw_water(); draw_stars(); draw_god_rays()
    draw_far(); draw_floor(); draw_caustics()
    draw_mid(); draw_lumin(); draw_glow(); draw_school()

def render_dynamic():
    canvas.delete("dyn")
    draw_creatures(); draw_streams(); draw_touch_glow()

def render_near():
    canvas.delete("near"); draw_near()

def render_foreground():
    canvas.delete("fg"); draw_foreground()

make_far(); make_mid(); make_lumin(); make_glow(); make_school()
make_near(); make_foreground(); make_caustics(); make_stars()
make_creatures()

threading.Thread(target=_boot_audio, daemon=True).start()
print("[edencore] audio:", audio_status())
print("[edencore] state dir:", STATE_DIR)

LAST_TICK = [time.time()]

def tick():
    now = time.time()
    dt = now - LAST_TICK[0]; LAST_TICK[0] = now
    dt = clamp(dt, 0.01, 0.15)
    SCENE["t"] += dt; PULSE["phase"] += dt*0.4
    update_bell(dt)
    update_quiet(dt)
    update_camera(dt)
    read_extero(); update_intero(); compute_mood_target()
    update_mood(dt); update_strain(dt); update_breath(dt)
    update_scroll(dt); update_creatures(dt); update_school(dt)
    update_streams(dt); update_dialogue(dt); update_rhythm(dt)
    if now - SCENE["last_save"] > 20:
        SCENE["last_save"] = now
        save_state(MOOD["current"], INTERO["chamber_strain"])
    render_background(); render_near()
    render_dynamic(); render_foreground()
    root.after(50, tick)

render_background()
tick()
root.mainloop()