class ConsumableItem:
    def __init__(self, name, weight, price, image_name, count=1):
        self.name = name
        self.weight = weight
        self.price = price
        self.image_name = image_name
        self.count = count

    def get_data(self):
        return {
            "name": self.name,
            "weight": self.weight,
            "price": self.price,
            "image": self.image_name,
            "count": self.count,
            "can_use": True,
            "type": "consumable"
        }


class Worm(ConsumableItem):
    def __init__(self, count=20):
        super().__init__(
            name="Worm",
            weight=0.01,
            price=1,
            image_name="worm",
            count=count
        )