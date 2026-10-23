import pygame

class ShopManager:
    def __init__(self):
        self.active = False
        self.text_start_time = 0
        self.current_message = ""
        self.can_skip = False
        self.state = "TALKING"
        self.sell_button_rect = pygame.Rect(0, 0, 0, 0)

    def enter_shop(self):
        self.active = True
        self.state = "TALKING"
        self.show_message("Hello again. Whacha have today?")

    def show_message(self, text):
        self.current_message = text
        self.text_start_time = pygame.time.get_ticks()
        self.can_skip = False

    def update(self):
        if not self.can_skip:
            if pygame.time.get_ticks() - self.text_start_time > 500:
                self.can_skip = True

    def handle_click(self):
        if self.state == "TALKING" and self.can_skip:
            self.state = "TRADING"
            return True
        return False