import math


class Inventory:
    def __init__(self, max_weight=50.0):
        self.max_weight = max_weight
        self.current_weight = 0.0

        # категории
        self.categories = {
            "catch": [],        # улов
            "tackle": [],       # снасти
            "consumables": [],  # расходники (стак)
            "rods": []          # удочки (или снаряжение?)
        }

        self.category_names = ["catch", "tackle", "consumables", "rods"]
        self.current_cat_idx = 0
        self.page = 0
        self.items_per_page = 20  # кол-во ячеек на одном экране

    def get_current_category(self):
        return self.category_names[self.current_cat_idx]

    def add_item(self, item_data, category):
        unit_weight = item_data.get('weight', 0)
        total_item_weight = unit_weight * item_data.get('count', 1)

        if self.current_weight + total_item_weight > self.max_weight: # чек перегруза
            return False

        if category == "consumables":
            # поиск существующего предмета с таким же именем - СТАК
            found = False
            for existing_item in self.categories["consumables"]:
                if existing_item['name'] == item_data['name']:
                    existing_item['count'] += item_data.get('count', 1)
                    found = True
                    break
            if not found:
                self.categories["consumables"].append(item_data)
        else:
            self.categories[category].append(item_data)

        self.recalculate_weight() # общий вес
        return True

    def recalculate_weight(self):
        total = 0.0
        for cat in self.categories.values():
            for item in cat:
                w = item.get('weight', 0.0)
                count = item.get('count', 1)
                total += w * count

        self.current_weight = round(total, 2)

    def use_item(self, item_name, category):
        for i, item in enumerate(self.categories[category]):
            if item['name'] == item_name:
                if 'count' in item:
                    item['count'] -= 1
                    if item['count'] <= 0:
                        self.categories[category].pop(i)
                else:
                    self.categories[category].pop(i)

                self.recalculate_weight()
                return True
        return False

    # !!! ДОБАВИТЬ В КОНЦЕ !!!
    def is_shop_unlocked(self):
        catch_weight = sum(item.get('weight', 0) for item in self.categories["catch"])
        return catch_weight >= 10.0  # магазин откроется после 10 кг рыбы

    def get_items_for_current_page(self):
        cat = self.get_current_category()
        items = self.categories[cat]

        start = self.page * self.items_per_page
        end = start + self.items_per_page
        return items[start:end]

    def total_pages(self):
        cat = self.get_current_category()
        count = len(self.categories[cat])
        if count == 0: return 1
        return math.ceil(count / self.items_per_page)

    def next_page(self):
        if self.page < self.total_pages() - 1:
            self.page += 1

    def prev_page(self):
        if self.page > 0:
            self.page -= 1

    def switch_category(self, direction):
        # 1 вперед или -1 назад
        self.current_cat_idx = (self.current_cat_idx + direction) % len(self.category_names)
        self.page = 0

    def remove_item_by_index(self, category, index):
        if category in self.categories and 0 <= index < len(self.categories[category]):
            self.categories[category].pop(index)
            self.recalculate_weight()
            return True
        return False

