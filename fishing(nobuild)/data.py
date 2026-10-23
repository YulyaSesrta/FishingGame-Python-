import random
import math

COLOR_TRASH = (120, 120, 120)       # Gray
COLOR_COMMON = (173, 216, 230)      # Light Blue
COLOR_UNCOMMON = (0, 0, 255)        # Blue
COLOR_RARE = (75, 0, 130)           # Deep Blue / Indigo
COLOR_EPIC = (148, 0, 211)          # Purple
COLOR_LEGENDARY = (255, 215, 0)     # Gold
COLOR_MYTHICAL = (255, 0, 255)      # Rainbow (базовый Magenta, ПОТОМ эффект)
COLOR_DIVINE = (255, 255, 255)      # White (для B&W эффекта - ПОТОМ)


class Fish:
    def __init__(self, name, difficulty, rarity_label, rarity_color, price_range, base_weight):
        self.name = name
        self.difficulty = difficulty
        self.rarity_label = rarity_label
        self.rarity_color = rarity_color
        self.price_range = price_range
        self.base_weight = base_weight
        self.size = max(15, 85 - (difficulty * 6))

        min_allowed_size = 56
        calculated_size = 120 - (self.difficulty * 8)
        self.size = max(min_allowed_size, calculated_size)

    def get_catch_data(self):
        min_w = 0.1 * self.difficulty
        max_w = 2.0 * self.difficulty
        weight = round(random.uniform(min_w, max_w), 2)

        price = random.randint(self.price_range[0], self.price_range[1])

        return {
            "name": self.name,
            "weight": weight,
            "rarity": self.rarity_label,
            "rarity_color": self.rarity_color,
            "price": price
        }


# >>> ИЕРАРХИЯ РЕДКОСТИ И ПРИМЕРЫ РЫБ <<<<
FISH_TYPES = {
    # TRASH
    "old_boot": Fish("Old Boot", 0.8, "Trash", COLOR_TRASH, (1, 5), 100),
    "tin_can": Fish("Tin Can", 0.7, "Trash", COLOR_TRASH, (2, 8), 100),

    # COMMON
    "perch": Fish("Perch", 1.0, "Common", COLOR_COMMON, (20, 50), 70),
    "crucian": Fish("Crucian Carp", 1.2, "Common", COLOR_COMMON, (25, 60), 60),

    # UNCOMMON
    "pike": Fish("Pike", 2.5, "Uncommon", COLOR_UNCOMMON, (50, 200), 40),
    "catfish": Fish("Catfish", 3.5, "Uncommon", COLOR_UNCOMMON, (80, 250), 35),

    # RARE
    "salmon": Fish("Salmon", 5.0, "Rare", COLOR_RARE, (150, 320), 15),
    "sturgeon": Fish("Sturgeon", 6.5, "Rare", COLOR_RARE, (170, 400), 12),

    # EPIC
    "swordfish": Fish("Swordfish", 8.5, "Epic", COLOR_EPIC, (600, 800), 7),
    "tuna": Fish("Golden Tuna", 9.5, "Epic", COLOR_EPIC, (800, 1000), 6),

    # LEGENDARY
    "kraken_baby": Fish("Kraken Hatchling", 12.0, "Legendary", COLOR_LEGENDARY, (2000, 3800), 1),
    "sea_dragon": Fish("Sea Dragon", 14.5, "Legendary", COLOR_LEGENDARY, (2500, 5000), 1),

    # MYTHICAL
    "poseidon_pet": Fish("Poseidon's Pet", 20.0, "Mythical", COLOR_MYTHICAL, (10000, 30000), 0.5),

    # DIVINE
    "glitch_fish": Fish("ReALiTy_GLItCh", 50.0, "Divine", COLOR_DIVINE, (999999, 999999), 0.1)
}


def get_random_fish(luck_factor):
    fish_list = list(FISH_TYPES.values())
    modified_weights = []

    for fish in fish_list:
        w = fish.base_weight

        if fish.difficulty > 4:
            bonus = math.pow(luck_factor, (fish.difficulty / 5))
            w *= bonus
        elif fish.difficulty < 1:
            w /= luck_factor

        modified_weights.append(w)

    return random.choices(fish_list, weights=modified_weights, k=1)[0]


LOCATIONS = {
    "dock": {
        "bg_name": "bg_idle",
        "can_fish": True,
        "description": "Old City Dock"
    },
    "shop": {
        "bg_name": "fish_shop_bg",
        "can_fish": False,
        "description": "Fish Market"
    }
}