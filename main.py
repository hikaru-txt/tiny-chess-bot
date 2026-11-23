import json, os, sys, urllib.request

E = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("No ENV_URL")
V = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}

def post(p, b):
    req = urllib.request.Request(E + p, data=json.dumps(b).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(req) as res: return json.load(res)

def board_of(fen):
    b = {}
    for i, row in enumerate(fen.split()[0].split("/")):
        file = 0
        for c in row:
            if c.isdigit(): file += int(c)
            else: b["abcdefgh"][file] + str(8 - i)] = c; file += 1
    return b

def choose(fen, legal):
    board = board_of(fen)
    def score_move(move):
        src, dst = move[:2], move[2:4]
        mover = board.get(src, "")
        victim = board.get(dst)
        if not victim and mover.lower() == "p" and src[0] != dst[0]: victim = "p"
        taken = V.get(victim.lower(), 0) if victim else 0
        promo = V.get(move[4].lower(), 0) if len(move) == 5 else 0
        
        # Positional bonus for center control & advancement
        center_bonus = 25 if dst in {"d4", "d5", "e4", "e5"} else (10 if dst[0] in "cdef" and dst[1] in "36" else 0)
        pawn_advance = (int(dst[1]) - int(src[1])) * 15 if mover.lower() == "p" else 0
        
        return taken * 20 - V.get(mover.lower(), 100) + promo + center_bonus + pawn_advance
    return max(legal, key=score_move)

while True:
    g = post("/game", {})
    if g["status"] == "done": break
    while g["status"] == "your_move":
        g = post("/move", {"game": g["game"], "move": choose(g["fen"], g["legal_moves"])})
    print(f"game {g['game']}: {g['outcome']} by {g['reason']}", file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost", file=sys.stderr)
