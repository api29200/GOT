from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "game_data.json"

# ✅ Initialize Game State
def initialize_game_data():
    """Reset game data to a clean state"""
    initial_state = {
        "players": {},
        "turn_order": [],
        "game_status": "waiting",
        "current_turn": None,
        "ai_players": [],
        "votes_to_start": {},
        "game_events": [],
        "last_attacks": {},
        "ai_difficulty": "normal"
    }
    save_game_data(initial_state)

# ✅ Load Game State
def load_game_data():
    """Load the game state from JSON file or reset if missing/corrupted"""
    if not os.path.exists(DATA_FILE):
        initialize_game_data()
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        initialize_game_data()
        return load_game_data()

# ✅ Save Game State
def save_game_data(game_data):
    """Save the game state to JSON file"""
    with open(DATA_FILE, "w") as file:
        json.dump(game_data, file, indent=4)

# ✅ API Endpoints

@app.route('/check_server', methods=['GET'])
def check_server():
    """Check if the server is running"""
    return jsonify({"message": "✅ Server is running."}), 200

@app.route('/game_state', methods=['GET'])
def game_state():
    """Retrieve the current game state"""
    return jsonify(load_game_data()), 200

@app.route('/reset_game', methods=['POST'])
def reset_game():
    """Reset the game to its initial state"""
    initialize_game_data()
    return jsonify({"message": "Game state has been reset."}), 200

@app.route('/create_player', methods=['POST'])
def create_player():
    """Create a new player"""
    data = request.json
    player_name = data.get("name")
    house = data.get("house")
    player_type = data.get("type", "human")  # Default type is human

    if not player_name or not house:
        return jsonify({"error": "Missing player name or house"}), 400

    game_data = load_game_data()
    if player_name in game_data["players"]:
        return jsonify({"error": "Player already exists"}), 400

    game_data["players"][player_name] = {
        "house": house,
        "power": 5,
        "castles": 1,
        "influence": 3,
        "eliminated": False,
        "type": player_type
    }
    game_data["turn_order"].append(player_name)
    save_game_data(game_data)

    return jsonify({"message": f"Player {player_name} from House {house} created successfully."}), 201

@app.route('/start_game', methods=['POST'])
def start_game():
    """Start the game if conditions are met"""
    game_data = load_game_data()
    if len(game_data["players"]) < 3:
        return jsonify({"error": "At least 3 players required to start."}), 400

    game_data["game_status"] = "in progress"
    game_data["current_turn"] = game_data["turn_order"][0]  # First player starts
    save_game_data(game_data)

    return jsonify({"message": "Game has started!"}), 200

@app.route('/execute_action', methods=['POST'])
def execute_action():
    """Execute an action for the current turn"""
    data = request.json
    player = data.get("player")
    action = data.get("action")

    game_data = load_game_data()

    if player not in game_data["players"]:
        return jsonify({"message": "Player does not exist.", "status": "failed"}), 400

    if game_data["players"][player]["eliminated"]:
        return jsonify({"message": f"Player {player} is eliminated and cannot act.", "status": "failed"}), 400

    if game_data["current_turn"] != player:
        return jsonify({"message": "It is not your turn.", "status": "failed"}), 400

    # ✅ Process Action
    game_data["game_events"].append(f"{player} executed {action}.")
    
    # ✅ Rotate Turn
    next_turn_index = (game_data["turn_order"].index(player) + 1) % len(game_data["turn_order"])
    game_data["current_turn"] = game_data["turn_order"][next_turn_index]

    save_game_data(game_data)

    return jsonify({"message": f"{player} executed {action}.", "status": "success"}), 200

@app.route('/api_schema.json', methods=['GET'])
def api_schema():
    """Dynamically generate OpenAPI schema for Custom GPT"""
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Game of Thrones API",
            "description": "API for managing the Game of Thrones board game.",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://4klf6he0m0.eu.loclx.io",
                "description": "Public API Server"
            }
        ],
        "paths": {
            "/check_server": {
                "get": {
                    "operationId": "checkServer",
                    "summary": "Check if server is running",
                    "responses": {"200": {"description": "Server is running."}}
                }
            },
            "/game_state": {
                "get": {
                    "operationId": "getGameState",
                    "summary": "Retrieve the current game state",
                    "responses": {"200": {"description": "Returns game state"}}
                }
            },
            "/reset_game": {
                "post": {
                    "operationId": "resetGame",
                    "summary": "Reset the game",
                    "responses": {"200": {"description": "Game reset successfully."}}
                }
            },
            "/create_player": {
                "post": {
                    "operationId": "createPlayer",
                    "summary": "Create a new player",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "example": {"name": "JonSnow", "house": "Stark", "type": "human"}
                            }
                        }
                    },
                    "responses": {"201": {"description": "Player created successfully"}}
                }
            },
            "/start_game": {
                "post": {
                    "operationId": "startGame",
                    "summary": "Start the game",
                    "responses": {"200": {"description": "Game has started."}}
                }
            },
            "/execute_action": {
                "post": {
                    "operationId": "executeAction",
                    "summary": "Execute an action",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "example": {"player": "JonSnow", "action": "attack"}
                            }
                        }
                    },
                    "responses": {"200": {"description": "Action executed successfully"}}
                }
            }
        }
    }
    return jsonify(schema), 200

if __name__ == '__main__':
    print("🔄 Resetting game state...")
    initialize_game_data()
    print("✅ Game state has been reset.")
    app.run(host="0.0.0.0", port=5000)
