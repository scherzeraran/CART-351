"""
PLEASE DON'T LIE  -  CART 351 mini-project
A bureaucratic intake form that asks for your data, then rewards you for corrupting it.

Concept refs: Hito Steyerl, "A Sea of Data: Apophenia and Pattern (Mis-)Recognition" (dirty data as refusal);
Mimi Onuoha, "The Point of Collection" (datasets are the result of their means of collection).

   References and citations:
     - Hito Steyerl, "A Sea of Data: Apophenia and Pattern (Mis-)Recognition", e-flux journal #72 (2016)
     - Mimi Onuoha, "The Point of Collection", Data & Society: Points (2016)
     - CART 351 Fall 2026, "Flask III & Fetch" lecture notes (sessions, fetch GET/POST, JSON responses)
     - Flask documentation: https://flask.palletsprojects.com/
     - AI assistance: Claude (Anthropic) helped double check this code. It was scaffolded, revised, and edited by the author.

Run:  pip install -r requirements.txt  &&  python app.py   ->  http://127.0.0.1:5000
"""
import hashlib, json, os, re, threading, time, uuid
from collections import Counter
from statistics import mean, pstdev

from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
# Signs the session cookie (Flask III lecture). Sessions hold only temporary, non-sensitive data: entry ids.
app.secret_key = 'CHANGE_ME_BAD_SECRET_KEY'
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "submissions.json")
LOCK = threading.Lock()  # one writer at a time so the JSON file never gets corrupted

# The machine's idea of a probable person. Anything outside is cleansed (flagged as dirty data).
NUMERIC = {"age": (18, 85, 35, 15), "sleep": (4, 10, 7, 2), "mood": (1, 10, 6, 3)}
ADJ = ["Probable", "Latent", "Compliant", "Frequent", "Seasonal", "Unverified"]
NOUN = ["Consumer", "Claimant", "Commuter", "Sleeper", "Taxpayer", "Visitor"]


# ---------- storage ----------
def load_rows():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_rows(rows):
    tmp = DATA_FILE + ".tmp"  # write to a temp file, then swap: no half-written JSON
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)


# ---------- the "algorithm" ----------
def dirt_score(e, accepted):
    """0-100: how far this person sits from the collective 'average citizen' (numbers) and
    how rare their words are (text). High = the model is confused = you win."""
    devs = []
    for k, (_, _, fm, fs) in NUMERIC.items():
        vals = [r[k] for r in accepted]
        m = mean(vals) if vals else fm
        s = max(pstdev(vals) if len(vals) > 1 else fs, fs / 2)
        devs.append(min(abs(e[k] - m) / s / 3, 1))
    rarity = []
    for k in ("occupation", "city"):
        vals = [r[k].lower() for r in accepted]
        rarity.append(1 - (vals.count(e[k].lower()) / len(vals) if vals else 0))
    return round(100 * (0.6 * mean(devs) + 0.4 * mean(rarity)))


def classify(eid):
    """Confident nonsense: a deterministic pseudo-category + fake confidence from a hash."""
    h = int(hashlib.sha256(eid.encode()).hexdigest(), 16)
    return f"{ADJ[h % 6]} {NOUN[(h // 7) % 6]}", 80 + (h // 49) % 20


def cleanse_reasons(e):
    """The machine's filters. Any hit = the entry is CLEANSED (removed from the model, but kept on file)."""
    r = []
    if not NUMERIC["age"][0] <= e["age"] <= NUMERIC["age"][1]: r.append("improbable age")
    if not NUMERIC["sleep"][0] <= e["sleep"] <= NUMERIC["sleep"][1]: r.append("improbable sleep")
    if e["mood"] in (1, 10): r.append("implausible mood")                       # nobody is a 1 or a 10
    if len(e["name"].split()) < 2: r.append("incomplete name")                  # bureaucracy wants first + last
    if any(ch.isdigit() for k in ("name", "occupation", "city") for ch in e[k]): r.append("digits in text")
    if any(re.search(r"(.)\1{3,}", e[k]) for k in ("name", "occupation", "city")): r.append("keyboard mash")
    return r


def verdict(dirt):
    if dirt < 25: return "Suspiciously honest. Please lie more."
    if dirt < 60: return "Adequately unreliable. Thank you for your cooperation."
    return "Magnificently dirty. The model is confused."


def composite(rows):
    """The 'Average Person', built ONLY from accepted entries. Cleansed entries are never counted."""
    ok = [r for r in rows if r["status"] == "accepted"]
    avg = lambda k: round(mean(r[k] for r in ok), 1) if ok else None
    tally = lambda k: Counter(r[k].lower() for r in ok).most_common(8)
    return {"age": avg("age"), "sleep": avg("sleep"), "mood": avg("mood"),
            "occupations": tally("occupation"), "cities": tally("city"), "n": len(ok),
            # mood histogram 1-10 (accepted only): the model never contains a 1 or a 10, they are always cleansed
            "moods": [[str(m), sum(1 for r in ok if r["mood"] == m)] for m in range(1, 11)]}


# ---------- routes ----------
@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/submit")  # FETCH #1: front end -> server (saved permanently to JSON)
def submit():
    p = request.get_json(silent=True) or {}
    try:
        e = {k: str(p.get(k, "")).strip()[:80] for k in ("name", "occupation", "city")}
        e["statement"] = str(p.get("statement", "")).strip()[:140]
        e["age"], e["sleep"], e["mood"] = int(float(p["age"])), float(p["sleep"]), int(float(p["mood"]))
    except (KeyError, ValueError, TypeError, OverflowError):
        return jsonify(error="Form incomplete. Fill every box (a lie counts as filling it)."), 400
    if not all(e[k] for k in ("name", "occupation", "city")):
        return jsonify(error="Name, occupation and city are required."), 400
    if not (0 <= e["age"] <= 120 and 0 <= e["sleep"] <= 24 and 1 <= e["mood"] <= 10):
        return jsonify(error="Even lies must fit on the form: age 0-120, sleep 0-24, mood 1-10."), 400

    with LOCK:
        rows = load_rows()
        accepted = [r for r in rows if r["status"] == "accepted"]
        e["id"], e["time"] = uuid.uuid4().hex[:10], int(time.time())
        e["dirt"] = dirt_score(e, accepted)
        # Steyerl's "dirty data": improbable people are cleansed from the model... but we keep them.
        e["reasons"] = cleanse_reasons(e)
        e["status"] = "cleansed" if e["reasons"] else "accepted"
        e["label"], e["confidence"] = classify(e["id"])
        rows.append(e)
        save_rows(rows)
    session["mine"] = session.get("mine", [])[-20:] + [e["id"]]  # remember THIS visitor's entries (client-side cookie)
    return jsonify(id=e["id"], dirt=e["dirt"], status=e["status"], label=e["label"],
                   confidence=e["confidence"], verdict=verdict(e["dirt"]), reasons=e["reasons"])


@app.get("/api/data")  # FETCH #2: server JSON -> front end (collective representation)
def data():
    rows = load_rows()
    return jsonify(
        composite=composite(rows),
        points=[{"id": r["id"], "mood": r["mood"], "age": r["age"], "sleep": r["sleep"], "status": r["status"], "dirt": r["dirt"], "reasons": r.get("reasons", [])} for r in rows],
        statements=[r["statement"] for r in rows[-5:][::-1] if r["statement"]],  # names are never exposed
        mine=session.get("mine", []), total=len(rows), cleansed=sum(r["status"] == "cleansed" for r in rows),
    )


if __name__ == "__main__":
   app.run(debug=True, port=5050)