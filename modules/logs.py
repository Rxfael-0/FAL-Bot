import json

MATCH_LOGS_FILE = "database/match_logs.json"


def load_logs():
    try:
        with open(MATCH_LOGS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_logs(data):
    with open(MATCH_LOGS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_match_log(match_id, league, players, winner):
    logs = load_logs()

    logs.append({
        "match_id": match_id,
        "league": league,
        "players": players,
        "winner": winner
    })

    save_logs(logs)
