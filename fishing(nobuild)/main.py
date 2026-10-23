import pygame
import sys
from ui_manager import (load_pixel_font, load_assets, draw_menu, draw_game, draw_text,
                        draw_result_window, draw_inventory_button, draw_map_screen, draw_balance,
                        draw_inventory_screen, draw_tooltip, draw_map_button, draw_shop_ui)
from fishing import FishingMiniGame
from data import FISH_TYPES, Fish, get_random_fish, LOCATIONS
from inventory import Inventory
from game_logic import create_player_inventory
from shop_logic import ShopManager
import random

clock = pygame.time.Clock()
pygame.init()


def run_game():
    screen = pygame.display.set_mode((1280, 720))
    load_assets()
    game_icon = pygame.image.load("icon1.ico")
    pygame.display.set_icon(game_icon)
    pygame.display.set_caption("FISH FISH FISH v0.1.0")
    shop_manager = ShopManager()
    shop_trade_ui = {"fish_cells": [], "prev_page": pygame.Rect(0, 0, 0, 0), "next_page": pygame.Rect(0, 0, 0, 0)}

    font = load_pixel_font(46)
    tip_font = load_pixel_font(34)

    #ректы кнопок
    play_rect = pygame.Rect(0, 0, 0, 0)
    exit_rect = pygame.Rect(0, 0, 0, 0)
    inv_btn_rect = pygame.Rect(0, 0, 0, 0)
    map_btn_rect = pygame.Rect(0, 0, 0, 0)

    shop_manager.sell_button_rect = pygame.Rect(390, 450, 260, 80)
    shop_manager.close_btn_rect = pygame.Rect(0, 0, 0, 0)

    base_luck = 1.0
    active_luck_multiplier = 1.0
    current_cast_luck = 1.0

    player_balance = 0

    bait_applied = False
    message_timer = 0
    show_message = ""

    player_inv = create_player_inventory()

    STATE_MENU = "menu"
    STATE_GAME = "game"
    STATE_INVENTORY = "inventory"
    current_state = STATE_MENU

    FISHING_IDLE = "idle"
    FISHING_WAITING = "waiting"
    FISHING_PROCESS = "fishing"
    FISHING_RESULT = "result"

    WAIT_TIME_RANGE = (2, 4)
    REACTION_WINDOW = 800

    casting_start_time = 0
    target_wait_time = 0
    show_map = False
    current_location = "dock"

    map_point_dock = pygame.Rect(400, 300, 100, 100)
    map_point_shop = pygame.Rect(800, 300, 100, 100)

    result_start_time = 0
    RESULT_DELAY = 1500

    fishing_state = FISHING_IDLE
    current_mini_game = None
    catch_result = None
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == STATE_INVENTORY or show_map:
                        current_state = STATE_GAME
                        show_map = False
                    elif current_state == STATE_GAME:
                        current_state = STATE_MENU
                        fishing_state = FISHING_IDLE
                    else:
                        running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_state == STATE_MENU:
                    if play_rect.collidepoint(mouse_pos):
                        current_state = STATE_GAME
                    elif exit_rect.collidepoint(mouse_pos):
                        running = False

                elif current_state == STATE_INVENTORY:
                    if 'inv_ui' in locals() and inv_ui:
                        if inv_ui["close"].collidepoint(mouse_pos):
                            current_state = STATE_GAME
                        elif inv_ui["prev_cat"].collidepoint(mouse_pos):
                            player_inv.switch_category(-1)
                        elif inv_ui["next_cat"].collidepoint(mouse_pos):
                            player_inv.switch_category(1)
                        elif inv_ui["prev_page"].collidepoint(mouse_pos):
                            player_inv.prev_page()
                        elif inv_ui["next_page"].collidepoint(mouse_pos):
                            player_inv.next_page()
                        for cell in inv_ui["item_cells"]:
                            if cell["rect"].collidepoint(mouse_pos):
                                clicked_item = cell["item"]
                                if clicked_item.get("can_use"):
                                    if not bait_applied:
                                        if player_inv.use_item(clicked_item['name'], "consumables"):
                                            active_luck_multiplier = 1.25
                                            bait_applied = True
                                            current_luck_display = base_luck * active_luck_multiplier
                                            show_message = f"Bait applied! Luck x{current_luck_display}"
                                            message_timer = current_time
                                    else:
                                        show_message = "Bait is already active!"
                                        message_timer = current_time

                elif current_state == STATE_GAME:
                    if show_map:
                        if map_point_dock.collidepoint(mouse_pos):
                            current_location = "dock"
                            show_map = False
                        elif map_point_shop.collidepoint(mouse_pos):
                            current_location = "shop"
                            show_map = False
                        else:
                            show_map = False

                    # 1. магаз
                    elif current_location == "shop" and shop_manager.state == "TRADING":
                        if shop_trade_ui is not None:
                            if shop_manager.close_btn_rect.collidepoint(mouse_pos):
                                shop_manager.state = "TALKING"
                                shop_manager.show_message("Need something else, honey?")

                            elif shop_trade_ui["prev_page"].collidepoint(mouse_pos):
                                if player_inv.page > 0:
                                    player_inv.page -= 1

                            elif shop_trade_ui["next_page"].collidepoint(mouse_pos):
                                items_per_page = 8
                                total_items = len(player_inv.categories.get("catch", []))
                                if (player_inv.page + 1) * items_per_page < total_items:
                                    player_inv.page += 1

                            else:
                                for cell in shop_trade_ui.get("fish_cells", []):
                                    if cell["rect"].collidepoint(mouse_pos):
                                        fish_to_sell = cell["item"]
                                        price = fish_to_sell.get("price", 10)

                                        player_balance += price

                                        player_inv.remove_item_by_index("catch", cell["global_index"])

                                        if len(player_inv.categories[
                                                   "catch"]) <= player_inv.page * 8 and player_inv.page > 0:
                                            player_inv.page -= 1
                                        break

                    # 2. рыбалка
                    elif fishing_state == FISHING_WAITING:
                        time_passed = current_time - casting_start_time
                        if time_passed >= target_wait_time:
                            if current_time - (casting_start_time + target_wait_time) <= REACTION_WINDOW:
                                fishing_state = FISHING_PROCESS
                                active_luck_multiplier = 1.0
                                selected_fish = get_random_fish(current_cast_luck)
                                current_mini_game = FishingMiniGame(selected_fish)
                            else:
                                casting_start_time = current_time
                                target_wait_time = random.randint(WAIT_TIME_RANGE[0] * 1000,
                                                                  WAIT_TIME_RANGE[1] * 1000)
                        else:
                            fishing_state = FISHING_IDLE

                    # 3. ловля
                    elif fishing_state == FISHING_PROCESS:
                        pass

                    # 4. результат
                    elif fishing_state == FISHING_RESULT:
                        if current_time - result_start_time > RESULT_DELAY:
                            fishing_state = FISHING_IDLE
                            catch_result = None

                    # 5. айдал
                    else:
                        if map_btn_rect.collidepoint(mouse_pos):
                            show_map = True
                        elif inv_btn_rect.collidepoint(mouse_pos):
                            current_state = STATE_INVENTORY

                        elif current_location == "shop" and shop_manager.state == "TALKING":
                            if shop_manager.sell_button_rect.collidepoint(mouse_pos):
                                shop_manager.state = "TRADING"

                        elif current_location == "dock":
                            if LOCATIONS[current_location]["can_fish"]:
                                current_cast_luck = base_luck * active_luck_multiplier
                                bait_applied = False
                                fishing_state = FISHING_WAITING
                                casting_start_time = current_time
                                target_wait_time = random.randint(WAIT_TIME_RANGE[0] * 1000,
                                                                  WAIT_TIME_RANGE[1] * 1000)

                            elif fishing_state == FISHING_WAITING:
                                time_passed = current_time - casting_start_time
                                if time_passed >= target_wait_time:
                                    if current_time - (casting_start_time + target_wait_time) <= REACTION_WINDOW:
                                        fishing_state = FISHING_PROCESS
                                        active_luck_multiplier = 1.0
                                        selected_fish = get_random_fish(current_cast_luck)
                                        current_mini_game = FishingMiniGame(selected_fish)
                                    else:
                                        casting_start_time = current_time
                                        target_wait_time = random.randint(WAIT_TIME_RANGE[0] * 1000,
                                                                                          WAIT_TIME_RANGE[1] * 1000)

                            elif fishing_state == FISHING_RESULT:
                                if current_time - result_start_time > RESULT_DELAY:
                                     fishing_state = FISHING_IDLE
                                     catch_result = None


        # ЛОГИКА ОБНОВЛЕНИЯ
        if current_state == STATE_GAME:
            if current_location == "shop" and not shop_manager.active:
                shop_manager.enter_shop()
            elif current_location != "shop":
                shop_manager.active = False

            if fishing_state == FISHING_PROCESS and current_mini_game:
                current_mini_game.update()
                if current_mini_game.game_over:
                    fishing_state = FISHING_IDLE
                elif current_mini_game.progress >= 100:
                    catch_result = current_mini_game.fish.get_catch_data()
                    added = player_inv.add_item(catch_result, "catch")
                    fishing_state = FISHING_RESULT
                    result_start_time = pygame.time.get_ticks()

        # ОТРИСОВКА
        if current_state == STATE_MENU:
            play_rect, exit_rect = draw_menu(screen, font)
        else:
            draw_game(screen, font, fishing_state, current_location)

            if current_state == STATE_GAME:
                is_trading = (current_location == "shop" and shop_manager.state == "TRADING")

                if not show_map and not is_trading:
                    inv_btn_rect = draw_inventory_button(screen)
                    map_btn_rect = draw_map_button(screen)

                # логика магазина
                if current_location == "shop":
                    shop_manager.update()
                    shop_trade_ui = draw_shop_ui(screen, font, shop_manager.current_message, shop_manager, player_inv)

                # логика рыбалки
                elif current_location == "dock":
                    if fishing_state == FISHING_PROCESS and current_mini_game:
                        current_mini_game.draw(screen)
                    if fishing_state == FISHING_WAITING:
                        time_passed = current_time - casting_start_time
                        if time_passed >= target_wait_time:
                            if current_time - (casting_start_time + target_wait_time) <= REACTION_WINDOW:
                                bite_font = load_pixel_font(100)
                                bite_text = bite_font.render("! BITE !", True, (255, 50, 50))
                                screen.blit(bite_text, (screen.get_width() // 2 - bite_text.get_width() // 2,
                                                        screen.get_height() // 2 - 100))
                                pygame.draw.rect(screen, (255, 255, 255), (0, 0, 1280, 720), 10)

                    if fishing_state == FISHING_RESULT and catch_result:
                        can_skip = current_time - result_start_time > RESULT_DELAY
                        draw_result_window(screen, font, catch_result, can_skip)

                if show_map:
                    draw_map_screen(screen, font, mouse_pos)
                    dock_x, dock_y = 440, 190
                    shop_x, shop_y = 775, 500
                    btn_size = 40
                    small_font = load_pixel_font(30)
                    map_point_dock = pygame.Rect(dock_x, dock_y, btn_size, btn_size)
                    map_point_shop = pygame.Rect(shop_x, shop_y, btn_size, btn_size)

                    dock_color = (0, 255, 0) if map_point_dock.collidepoint(mouse_pos) else (0, 180, 0)
                    pygame.draw.rect(screen, (0, 0, 0), map_point_dock.inflate(6, 6))
                    pygame.draw.rect(screen, dock_color, map_point_dock)
                    draw_text(screen, "DOCK", small_font, (255, 255, 255), dock_x + (btn_size // 2) - 30, dock_y - 35)

                    shop_color = (255, 0, 0) if map_point_shop.collidepoint(mouse_pos) else (180, 0, 0)
                    pygame.draw.rect(screen, (0, 0, 0), map_point_shop.inflate(6, 6))
                    pygame.draw.rect(screen, shop_color, map_point_shop)
                    draw_text(screen, "SHOP", small_font, (255, 255, 255), shop_x + (btn_size // 2) - 25, shop_y - 35)

            elif current_state == STATE_INVENTORY:
                inv_ui = draw_inventory_screen(screen, font, player_inv, mouse_pos)
                if inv_ui and inv_ui.get("hovered"):
                    draw_tooltip(screen, tip_font, inv_ui["hovered"], mouse_pos)

        if show_message:
            if current_time - message_timer < 2000:
                msg_img = font.render(show_message, True, (255, 255, 0))
                msg_rect = msg_img.get_rect(center=(screen.get_width() // 2, 100))
                pygame.draw.rect(screen, (0, 0, 0), msg_rect.inflate(20, 10))
                screen.blit(msg_img, msg_rect)
            else:
                show_message = ""

        is_trading = (current_location == "shop" and shop_manager.state == "TRADING")
        is_inventory = (current_state == STATE_INVENTORY)
        if current_state != STATE_MENU and not is_inventory:
            draw_balance(screen, font, player_balance)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()