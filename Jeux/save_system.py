import json
import os

SLOTS = {
    1: "save_slot_1.json",
    2: "save_slot_2.json",
    3: "save_slot_3.json"
}

def get_slot_info(slot_num):
    """Retourne les infos principales d'un slot pour l'affichage dans le menu."""
    filename = SLOTS.get(slot_num)
    if not filename or not os.path.exists(filename):
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "money": data.get("money", 0.0),
            "cps": data.get("total_money_earned", 0.0)
        }
    except Exception:
        return None

def save_game(game_state, slot_num=None):
    """Sauvegarde le jeu dans le slot spécifié."""
    if slot_num is None:
        slot_num = game_state.current_slot
    
    filename = SLOTS.get(slot_num, "save_slot_1.json")
    data = {
        "money": game_state.money,
        "total_money_earned": game_state.total_money_earned,
        "click_power": game_state.click_power,
        "bots": game_state.bots,
        "upgrades": game_state.upgrades,
        "items": game_state.items,
        "unlocked_story": list(game_state.unlocked_story),
        "relic_clicks": game_state.relic_clicks
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        game_state.current_slot = slot_num
        return True
    except Exception as e:
        print(f"Erreur de sauvegarde: {e}")
        return False

def load_game(game_state, slot_num):
    """Charge les données d'un slot spécifique."""
    filename = SLOTS.get(slot_num)
    if not filename or not os.path.exists(filename):
        return False
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        game_state.money = data.get("money", 0.0)
        game_state.total_money_earned = data.get("total_money_earned", 0.0)
        game_state.click_power = data.get("click_power", 1.0)
        game_state.relic_clicks = data.get("relic_clicks", 0)
        
        for k, v in data.get("bots", {}).items():
            if k in game_state.bots:
                game_state.bots[k] = v
                
        for k, v in data.get("upgrades", {}).items():
            if k in game_state.upgrades:
                game_state.upgrades[k] = v
                
        for k, v in data.get("items", {}).items():
            if k in game_state.items:
                game_state.items[k] = v
                
        game_state.unlocked_story = set(data.get("unlocked_story", []))
        game_state.current_slot = slot_num
        return True
    except Exception as e:
        print(f"Erreur de chargement: {e}")
        return False

def delete_save(slot_num):
    """Supprime le fichier de sauvegarde correspondant au slot."""
    filename = SLOTS.get(slot_num)
    if filename and os.path.exists(filename):
        try:
            os.remove(filename)
            return True
        except Exception as e:
            print(f"Erreur de suppression: {e}")
            return False
    return False