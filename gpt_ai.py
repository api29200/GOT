import random
import json

DATA_FILE = "game_data.json"

def load_game_data():
    """Load the game state"""
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def generate_ai_action(player_name):
    """Generate an AI player's action based on difficulty and game history"""
    game_data = load_game_data()

    if game_data["players"].get(player_name, {}).get("eliminated"):
        return "No Action"

    difficulty = game_data["ai_difficulty"]
    last_attack = game_data["last_attacks"].get(player_name)

    if difficulty == "easy":
        return random.choice(["Defend", f"Attack {random.choice(list(game_data['players'].keys()))}"])
    elif difficulty == "intermediate":
        return "Defend" if last_attack else f"Attack {random.choice(game_data['turn_order'])}"
    elif difficulty == "advanced":
        return f"Attack {sorted(game_data['turn_order'], key=lambda x: game_data['players'].get(x, {}).get('power', 0))[0]}"

    return "Defend"
