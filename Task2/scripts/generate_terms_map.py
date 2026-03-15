import json
from pathlib import Path

def create_terms_mapping():
    terms_map = {
        "Return of the Jedi": "Return of the Sentinels",
        "The Empire Strikes Back": "The Dominion Strikes Back",
        "A New Hope": "A New Hope",
        "The Force Awakens": "The Synth Awakens",
        "Revenge of the Sith": "Revenge of the Shadow Order",
        "Attack of the Clones": "Attack of the Clones",
        "The Phantom Menace": "The Phantom Menace",
        "The Clone Wars": "The Unity Wars",
        "Darth Vader": "Xarn Velgor",
        "Luke Skywalker": "Kael Thornix",
        "Princess Leia": "Archon Lyra",
        "Leia Organa": "Lyra Organa",
        "Han Solo": "Drake Vex",
        "Obi-Wan Kenobi": "Jorin Quell",
        "Yoda": "Master Zyn",
        "Emperor Palpatine": "Supreme Draven",
        "Darth Sidious": "Darth Sidious",
        "Anakin Skywalker": "Kael Vorn",
        "Rey Skywalker": "Nova Ryze",
        "Kylo Ren": "Morg Kross",
        "Qui-Gon Jinn": "Jorin the Elder",
        "Padmé Amidala": "Padmé Valestra",
        "Vader": "Velgor",
        "Luke": "Kael",
        "Leia": "Lyra",
        "Han": "Drake",
        "Obi-Wan": "Jorin",
        "Palpatine": "Draven",
        "Anakin": "Vorn",
        "Rey": "Nova",
        "Death Star": "Void Core",
        "Lightsaber": "Plasma Blade",
        "Millennium Falcon": "Nexus Hawk",
        "TIE fighter": "Vex Interceptor",
        "X-wing": "Delta Strike",
        "Star Destroyer": "Titan Cruiser",
        "AT-AT": "Siege Walker",
        "lightsaber": "plasma blade",
        "TIE fighters": "Vex Interceptors",
        "X-wings": "Delta Strikes",
        "Tatooine": "Koreon",
        "Coruscant": "Nexara",
        "Hoth": "Glacius",
        "Endor": "Verdion",
        "Naboo": "Zephyra",
        "Dagobah": "Murkon",
        "Alderaan": "Altheon",
        "The Force": "The Synth",
        "the Force": "the Synth",
        "Force": "Synth",
        "Jedi": "Sentinels",
        "Sith": "Shadow Order",
        "Galactic Empire": "Dominion Collective",
        "Empire": "Dominion",
        "Imperial": "Dominion",
        "Rebel Alliance": "Liberation Front",
        "Rebels": "Liberators",
        "Rebel": "Liberation",
        "First Order": "Prime Directive",
        "Resistance": "Uprising",
        "Wookiee": "Ursanii",
        "Wookiees": "Ursanii",
        "Droid": "Synth-unit",
        "Droids": "Synth-units",
        "droid": "synth-unit",
        "droids": "synth-units",
        "Ewok": "Vexling",
        "Ewoks": "Vexlings",
        "Jedi Knight": "Sentinel Guardian",
        "Jedi Master": "High Sentinel",
        "Padawan": "Initiate",
        "Dark Side": "Shadow Path",
        "Light Side": "Radiant Path",
        "Jedi Order": "Sentinel Order",
        "Jedi Council": "Sentinel Council",
        "Stormtrooper": "Dominion Soldier",
        "Stormtroopers": "Dominion Soldiers",
        "Clone Wars": "Unity Wars",
        "Galactic Republic": "United Worlds",
        "Republic": "Union",
        "Hyperspace": "Void-space",
        "hyperspace": "void-space",
        "Star Wars": "Void Chronicles",
        "Destroyer": "Dreadnought",
        "Cruiser": "Battleship",
        "Blaster": "Pulse rifle",
        "blaster": "pulse rifle",
        "blasters": "pulse rifles",
    }

    return terms_map


def save_terms_map(terms_map, filename='terms_map.json'):
    data = {
        "metadata": {
            "source_universe": "Star Wars",
            "target_universe": "Void Chronicles",
            "description": "Fictional universe created by replacing all Star Wars terms",
            "total_terms": len(terms_map),
            "creation_method": "Custom-generated fictional names to make content unrecognizable"
        },
        "mappings": terms_map
    }

    filepath = Path(filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Terms mapping saved to {filename}")
    print(f"  Total terms: {len(terms_map)}")
    print(f"\nSample mappings:")
    for i, (orig, new) in enumerate(list(terms_map.items())[:10], 1):
        print(f"  {i}. {orig:30} → {new}")


if __name__ == "__main__":
    print("Generating terms mapping...")
    print("="*60)

    terms_map = create_terms_mapping()
    save_terms_map(terms_map)

    print(f"\n{'='*60}")
    print("Done! Use this mapping with replace_terms.py to transform documents.")
