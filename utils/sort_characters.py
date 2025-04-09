import json

FILE_PATH = "data/characters.json"

RARITY_ORDER = {
    "common": 0,
    "uncommon": 1,
    "rare": 2,
    "epic": 3,
    "legendary": 4
}

def sort_by_rarity(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        characters = json.load(file)

    sorted_characters = sorted(
        characters,
        key=lambda x: RARITY_ORDER.get(x.get("rarity", "").lower(), 999)
    )

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(sorted_characters, file, indent=2, ensure_ascii=False)

    print(f"File successfully overwritten: {path}")

if __name__ == "__main__":
    sort_by_rarity(FILE_PATH)
