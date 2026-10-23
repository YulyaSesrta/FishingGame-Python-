from inventory import Inventory
from items import ConsumableItem


def create_player_inventory():
    # стартовый инвентарь
    inv = Inventory(max_weight=100.0)

    worms = ConsumableItem(
        name="Worm",
        weight=0.01,
        price=1,
        image_name="worm",
        count=20
    )

    inv.add_item(worms.get_data(), category="consumables")

    return inv