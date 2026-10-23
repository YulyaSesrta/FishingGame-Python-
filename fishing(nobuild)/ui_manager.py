import pygame
import os
from data import LOCATIONS

pygame.font.init()
FONT_PATH = "VT323.ttf"

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GRAY = (120, 128, 144)
DARK_BLUE = (15, 15, 35)

# Ассеты
bg_idle = None
bg_fishing0 = None
bg_fishing1 = None
map_bg = None
backpack_icon = None
map_icon = None
fish_shop_bg = None
dialogue_box_img = None
ASSETS = {}


def load_pixel_font(size):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except:
        return pygame.font.SysFont("Monospace", size)


def load_assets():
    global bg_idle, bg_fishing0, bg_fishing1, \
        backpack_icon, map_icon, fish_shop_bg, \
        map_bg, dialogue_box_img

    # фоны
    bg_idle = pygame.image.load("images/bg.jpg").convert()
    bg_fishing0 = pygame.image.load("images/fishing0.png").convert()
    bg_fishing1 = pygame.image.load("images/fishing1.png").convert()
    fish_shop_bg = pygame.image.load("images/fish_shop.jpg").convert()
    map_bg = pygame.image.load("images/map.jpg").convert()
    dialogue_box_img = pygame.image.load("images/dialogue.png").convert_alpha()

    # иконки для кнопок
    backpack_icon = pygame.image.load("images/backpack_icon.png").convert_alpha()
    map_icon = pygame.image.load("images/map_icon.png").convert_alpha()

    # предметы
    worm_img = pygame.image.load("images/worm.png").convert_alpha()
    ASSETS["worm"] = pygame.transform.scale(worm_img, (80, 80))


def draw_text(screen, text, font, color, x, y, shadow=True):
    if shadow:
        shadow_img = font.render(text, False, (20, 20, 20))
        screen.blit(shadow_img, (x + 3, y + 3))

    img = font.render(text, False, color)
    screen.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))

def draw_pixel_border(screen, rect, color, width=2):
    pygame.draw.rect(screen, BLACK, rect.inflate(width*2, width*2))
    pygame.draw.rect(screen, color, rect)


def draw_menu(screen, font):
    screen.fill(DARK_BLUE)
    sw = screen.get_width()

    # 1. заголовок
    h_font = load_pixel_font(80)
    title_img = h_font.render("FISH FISH FISH", False, (255, 200, 0))
    title_x = (screen.get_width() - title_img.get_width()) // 2
    screen.blit(title_img, (title_x, 150))

    # размеры кнопок
    btn_w, btn_h = 250, 60
    center_x = (sw - btn_w) // 2

    # 2. Кнопка плей
    play_rect_raw = pygame.Rect(center_x, 350, btn_w, btn_h)
    draw_pixel_border(screen, play_rect_raw, GRAY)

    play_txt = " PLAY "
    tw, th = font.size(play_txt)
    draw_text(screen, play_txt, font, WHITE,
              play_rect_raw.x + (btn_w - tw) // 2,
              play_rect_raw.y + (btn_h - th) // 2)

    # 3. Кнопка эксит
    exit_rect_raw = pygame.Rect(center_x, 450, btn_w, btn_h)
    draw_pixel_border(screen, exit_rect_raw, (180, 50, 50))

    exit_txt = " EXIT "
    etw, eth = font.size(exit_txt)
    draw_text(screen, exit_txt, font, WHITE,
              exit_rect_raw.x + (btn_w - etw) // 2,
              exit_rect_raw.y + (btn_h - eth) // 2)

    return play_rect_raw, exit_rect_raw


def draw_game(screen, font, fishing_state, current_location):
    if current_location == "shop":
        bg = fish_shop_bg
    else:
        # МЕНЯТЬ под удочки!!!
        if fishing_state == "waiting":
            bg = bg_fishing0
        elif fishing_state == "fishing":
            bg = bg_fishing1
        else:
            bg = bg_idle

    bg_scaled = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))
    screen.blit(bg_scaled, (0, 0))

    loc_desc = LOCATIONS[current_location]["description"]
    draw_text(screen, loc_desc, font, WHITE, 20, 20)

    if fishing_state == "idle" and LOCATIONS[current_location]["can_fish"]:
        draw_text(screen, "Click to cast!", font, (200, 200, 200), 50, 80)
    elif not LOCATIONS[current_location]["can_fish"]: return
        #draw_text(screen, "Wanna sell something?", font, (255, 215, 0), 50, 80)


def draw_result_window(screen, font, catch_data, can_skip):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # настройки окна
    win_w, win_h = 550, 400
    x = (screen.get_width() - win_w) // 2
    y = (screen.get_height() - win_h) // 2

    # пиксельная рамка окна + цвет редкости
    color = catch_data["rarity_color"]
    pygame.draw.rect(screen, (20, 20, 20), (x, y, win_w, win_h))  # Фон
    pygame.draw.rect(screen, color, (x, y, win_w, win_h), 4)  # Цветная рамка

    lines = [
        (f"YOU CAUGHT: {catch_data['name']}", 35, color),
        (f"Rarity: {catch_data['rarity']}", 95, color),
        (f"Weight: {catch_data['weight']} kg", 155, WHITE),
        (f"Price: {catch_data['price']} rub", 205, WHITE)
    ]

    for text, offset_y, t_color in lines:
        img = font.render(text, False, t_color)
        screen.blit(img, (x + (win_w - img.get_width()) // 2, y + offset_y))

    if can_skip:
        skip_img = font.render("Click to continue...", False, (200, 200, 200))
        screen.blit(skip_img, (x + (win_w - skip_img.get_width()) // 2, y + 335))


def draw_map_button(screen):
    btn_size = 100
    # отступ 120 пикселей
    x = (screen.get_width() - btn_size) // 2 + 470
    y = 20
    btn_rect = pygame.Rect(x, y, btn_size, btn_size)
    icon_scaled = pygame.transform.scale(map_icon, (btn_size - 16, btn_size - 16))
    screen.blit(icon_scaled, (x + 8, y + 8))
    return btn_rect


def draw_map_screen(screen, font, mouse_pos):

    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    win_w, win_h = 1000, 600
    win_x = (screen.get_width() - win_w) // 2
    win_y = (screen.get_height() - win_h) // 2
    rect_map = pygame.Rect(win_x, win_y, win_w, win_h)

    if map_bg:
        scaled_map = pygame.transform.scale(map_bg, (win_w, win_h))
        screen.blit(scaled_map, (win_x, win_y))
    else:
        pygame.draw.rect(screen, (50, 50, 50), rect_map)
    pygame.draw.rect(screen, WHITE, rect_map, 4)
    draw_text(screen, "TOWN MAP", font, (255, 215, 0), win_x, win_y - 50)

    return rect_map

def draw_inventory_button(screen):
    btn_size = 100
    x, y = (screen.get_width() - btn_size) // 2 + 350, 20
    btn_rect = pygame.Rect(x, y, btn_size, btn_size)
    icon_scaled = pygame.transform.scale(backpack_icon, (btn_size - 16, btn_size - 16))
    screen.blit(icon_scaled, (x + 8, y + 8))
    return btn_rect


def draw_inventory_screen(screen, font, inventory, mouse_pos):
    item_rects = []

    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    win_w, win_h = 1000, 600
    win_x = (screen.get_width() - win_w) // 2
    win_y = (screen.get_height() - win_h) // 2

    pygame.draw.rect(screen, (30, 30, 45), (win_x, win_y, win_w, win_h))
    pygame.draw.rect(screen, (200, 200, 200), (win_x, win_y, win_w, win_h), 4)

    cat_area_width = 450
    cat_area_center_x = (win_x + 50) + cat_area_width // 2

    cat_name = f" {inventory.get_current_category().upper()} "
    header_text = font.render(cat_name, True, WHITE)
    header_rect = header_text.get_rect(center=(cat_area_center_x, win_y + 45))
    screen.blit(header_text, header_rect)

    # Вес
    weight_text = font.render(f"{inventory.current_weight}/{inventory.max_weight} kg", True, (200, 200, 200))
    screen.blit(weight_text, (win_x + win_w - weight_text.get_width() - 50, win_y + 25))

    # Кнопка Х
    close_btn_size = 40
    close_rect = pygame.Rect(win_x + win_w - close_btn_size + 50, win_y, close_btn_size, close_btn_size)

    close_color = (180, 50, 50)
    if close_rect.collidepoint(mouse_pos):
        close_color = (255, 80, 80)

    pygame.draw.rect(screen, close_color, close_rect)
    pygame.draw.rect(screen, WHITE, close_rect, 2)  # Рамка кнопки

    pygame.draw.line(screen, WHITE, (close_rect.x + 10, close_rect.y + 10),
                     (close_rect.right - 10, close_rect.bottom - 10), 3)
    pygame.draw.line(screen, WHITE, (close_rect.right - 10, close_rect.top + 10),
                     (close_rect.left + 10, close_rect.bottom - 10), 3)


    # 4. сетка ячеек - 20 ячеек
    cell_size = 100
    gap_x, gap_y = 30, 15
    start_x = win_x + (win_w - (5 * cell_size + 4 * gap_x)) // 2
    start_y = win_y + 90

    items = inventory.get_items_for_current_page()
    hovered_item = None

    for i in range(inventory.items_per_page):
        row = i // 5
        col = i % 5
        cell_x = start_x + col * (cell_size + gap_x)
        cell_y = start_y + row * (cell_size + gap_y)
        cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)

        # пустая ячейка
        pygame.draw.rect(screen, (45, 45, 60), cell_rect)
        pygame.draw.rect(screen, (100, 100, 130), cell_rect, 2)

        if i < len(items):
            item = items[i]
            item_rects.append({"rect": cell_rect, "item": item})

            # рисуем картинку если есть
            has_image = False
            if "image" in item and item["image"] in ASSETS:
                img = ASSETS[item["image"]]
                img_rect = img.get_rect(center=cell_rect.center)
                screen.blit(img, img_rect)
                has_image = True

            # текст, если нет картинки
            if not has_image:
                name_txt = font.render(item['name'][:7], True, (255, 255, 255))
                tx = cell_x + (cell_size - name_txt.get_width()) // 2
                ty = cell_y + (cell_size - name_txt.get_height()) // 2
                screen.blit(name_txt, (tx, ty))

            # сам счетчик
            if 'count' in item:
                count_text = font.render(f"x{item['count']}", True, (255, 200, 0))
                screen.blit(count_text, (cell_x + cell_size - count_text.get_width() + 15, cell_y + cell_size - 30))

            # наведение
            if cell_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (255, 255, 255), cell_rect, 3)
                hovered_item = item

    # кнопки стрелочки
    prev_cat_rect = pygame.Rect(header_rect.left - 45, win_y + 25, 30, 40)
    next_cat_rect = pygame.Rect(header_rect.right + 15, win_y + 25, 30, 40)

    prev_page_rect = pygame.Rect(win_x + win_w // 2 - 120, win_y + win_h - 45, 40, 30)
    next_page_rect = pygame.Rect(win_x + win_w // 2 + 80, win_y + win_h - 45, 40, 30)

    def draw_arrow(rect, direction="left"):
        color = WHITE
        if direction == "left":
            pts = [(rect.right, rect.top), (rect.right, rect.bottom), (rect.left, rect.centery)]
        else:
            pts = [(rect.left, rect.top), (rect.left, rect.bottom), (rect.right, rect.centery)]
        if rect.collidepoint(mouse_pos):
            color = (255, 200, 0)
        pygame.draw.polygon(screen, color, pts)

    draw_arrow(prev_cat_rect, "left")
    draw_arrow(next_cat_rect, "right")
    draw_arrow(prev_page_rect, "left")
    draw_arrow(next_page_rect, "right")

    page_txt = font.render(f"{inventory.page + 1}/{max(1, inventory.total_pages())}", True, WHITE)
    page_rect = page_txt.get_rect(center=(win_x + win_w // 2, win_y + win_h - 30))
    screen.blit(page_txt, page_rect)

    return {
        "prev_cat": prev_cat_rect,
        "next_cat": next_cat_rect,
        "prev_page": prev_page_rect,
        "next_page": next_page_rect,
        "close": close_rect,
        "hovered": hovered_item,
        "item_cells": item_rects
    }


def draw_tooltip(screen, font_obj, item, mouse_pos):
    if not item:
        return

    lines = [f"NAME: {item['name'].upper()}"]
    is_consumable = item.get("can_use", False)

    if not is_consumable and 'rarity' in item:
        lines.append(f"RARITY: {item['rarity']}")

    lines.append(f"WEIGHT: {item.get('weight', 0)} kg")
    lines.append(f"PRICE: {item.get('price', 0)} rub")

    if not is_consumable and 'count' in item:
        lines.append(f"AMOUNT: {item['count']} pcs")

    padding_x, padding_y = 20, 15
    line_spacing = 28

    max_text_width = max([font_obj.size(line)[0] for line in lines])
    tip_w = max(300, max_text_width + (padding_x * 2))
    tip_h = (len(lines) * line_spacing) + (padding_y * 2)

    tx, ty = mouse_pos[0] + 20, mouse_pos[1] + 20
    if tx + tip_w > 1280: tx = mouse_pos[0] - tip_w - 10
    if ty + tip_h > 720: ty = mouse_pos[1] - tip_h - 10

    tip_rect = pygame.Rect(tx, ty, tip_w, tip_h)
    pygame.draw.rect(screen, (20, 20, 30), tip_rect)

    border_color = item.get('rarity_color', (150, 150, 150))
    pygame.draw.rect(screen, border_color, tip_rect, 2)

    for i, line in enumerate(lines):
        txt_img = font_obj.render(line, False, (255, 255, 255))
        screen.blit(txt_img, (tx + padding_x, ty + padding_y + i * line_spacing - 5))


def draw_shop_ui(screen, font, current_text, shop_manager, player_inv):
    diag_w, diag_h = 580, 300
    diag_x, diag_y = 70, 130
    text_rect = pygame.Rect(diag_x, diag_y, diag_w, diag_h)

    if shop_manager.state == "TALKING":
        if dialogue_box_img:
            scaled_diag = pygame.transform.scale(dialogue_box_img, (diag_w, diag_h))
            screen.blit(scaled_diag, (diag_x, diag_y))

        if current_text:
            draw_text_centered_wrapped(screen, current_text, font, (255, 255, 255), text_rect)

        btn_w, btn_h = 260, 80
        btn_x = diag_x + diag_w - btn_w
        btn_y = diag_y + diag_h + 20

        sell_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        mouse_pos = pygame.mouse.get_pos()
        color = (255, 215, 0) if sell_btn_rect.collidepoint(mouse_pos) else (200, 180, 0)

        pygame.draw.rect(screen, (0, 0, 0), sell_btn_rect)
        pygame.draw.rect(screen, color, sell_btn_rect, 5)

        btn_font = load_pixel_font(42)
        text_surf = btn_font.render("SELL FISH", True, color)
        screen.blit(text_surf, (sell_btn_rect.centerx - text_surf.get_width() // 2,
                                sell_btn_rect.centery - text_surf.get_height() // 2))

        shop_manager.sell_button_rect = sell_btn_rect
        return {"fish_cells": [], "prev_page": pygame.Rect(0, 0, 0, 0), "next_page": pygame.Rect(0, 0, 0, 0)}

    elif shop_manager.state == "TRADING":
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        win_w, win_h = 1000, 540
        win_x = (screen.get_width() - win_w) // 2
        win_y = (screen.get_height() - win_h) // 2

        pygame.draw.rect(screen, (30, 30, 45), (win_x, win_y, win_w, win_h))
        pygame.draw.rect(screen, (200, 200, 200), (win_x, win_y, win_w, win_h), 4)

        close_btn_size = 40
        close_rect = pygame.Rect(win_x + win_w - close_btn_size + 50, win_y, close_btn_size, close_btn_size)

        mouse_pos = pygame.mouse.get_pos()
        close_color = (180, 50, 50) if not close_rect.collidepoint(mouse_pos) else (255, 80, 80)

        pygame.draw.rect(screen, close_color, close_rect)
        pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)
        pygame.draw.line(screen, (255, 255, 255), (close_rect.x + 10, close_rect.y + 10),
                         (close_rect.right - 10, close_rect.bottom - 10), 3)
        pygame.draw.line(screen, (255, 255, 255), (close_rect.right - 10, close_rect.top + 10),
                         (close_rect.left + 10, close_rect.bottom - 10), 3)
        shop_manager.close_btn_rect = close_rect

        title_text = font.render(" SELL YOUR FISH ", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(win_x + win_w // 2, win_y + 45))
        screen.blit(title_text, title_rect)

        prev_page_rect = pygame.Rect(win_x + win_w // 2 - 120, win_y + win_h - 45, 40, 30)
        next_page_rect = pygame.Rect(win_x + win_w // 2 + 80, win_y + win_h - 45, 40, 30)

        def draw_arrow(rect, direction="left"):
            color = (255, 255, 255)
            if rect.collidepoint(mouse_pos):
                color = (255, 200, 0)  # золотой/жёлтый
            if direction == "left":
                pts = [(rect.right, rect.top), (rect.right, rect.bottom), (rect.left, rect.centery)]
            else:
                pts = [(rect.left, rect.top), (rect.left, rect.bottom), (rect.right, rect.centery)]
            pygame.draw.polygon(screen, color, pts)

        draw_arrow(prev_page_rect, "left")
        draw_arrow(next_page_rect, "right")

        current_page = getattr(player_inv, 'page', 0)
        total_items = len(player_inv.categories.get("catch", []))
        total_pages = max(1, (total_items + 7) // 8)  # 8 предметов на страниц

        page_txt = font.render(f"{current_page + 1}/{total_pages}", True, (255, 255, 255))
        page_rect = page_txt.get_rect(center=(win_x + win_w // 2, win_y + win_h - 30))
        screen.blit(page_txt, page_rect)

        ui_data = {
            "fish_cells": [],
            "prev_page": prev_page_rect,
            "next_page": next_page_rect
        }

        # 6. сетка товаров - 8 ячеек
        cell_size = 120
        gap = 40
        start_x = win_x + (win_w - (4 * cell_size + 3 * gap)) // 2
        start_y = win_y + 120

        catch_list = player_inv.categories.get("catch", [])
        for i in range(8):
            idx = current_page * 8 + i
            if idx < len(catch_list):
                col = i % 4
                row = i // 4
                cx = start_x + col * (cell_size + gap)
                cy = start_y + row * (cell_size + gap + 20)
                cell_rect = pygame.Rect(cx, cy, cell_size, cell_size)

                pygame.draw.rect(screen, (45, 45, 60), cell_rect)
                pygame.draw.rect(screen, (100, 100, 130), cell_rect, 2)

                fish = catch_list[idx]
                f_name = font.render(fish['name'][:8], True, (255, 255, 255))
                screen.blit(f_name, (cx + 5, cy + 5))
                f_price = font.render(f"{fish.get('price', 10)} rub", True, (255, 200, 0))
                screen.blit(f_price, (cx + 5, cy + cell_size - 30))

                ui_data["fish_cells"].append({"rect": cell_rect, "item": fish, "global_index": idx})

        return ui_data

    return {"fish_cells": [], "prev_page": pygame.Rect(0, 0, 0, 0), "next_page": pygame.Rect(0, 0, 0, 0)}


def draw_text_centered_wrapped(screen, text, font, color, rect):
    # отступы
    padding_x = 80
    max_width = rect.width - (padding_x * 2)

    words = text.split(' ')
    lines = []
    current_line = ""

    # разбиение на строки, чтоб текст помещался
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    line_height = font.get_linesize()
    total_height = len(lines) * line_height
    start_y = rect.centery - (total_height // 2)

    text_color = (0, 0, 0)

    for i, line in enumerate(lines):
        text_surface = font.render(line.strip(), True, text_color)
        text_x = rect.centerx - (text_surface.get_width() // 2)
        text_y = start_y + (i * line_height)
        screen.blit(text_surface, (text_x, text_y))


def draw_balance(screen, font, balance):
    balance_text = f"{balance} rub" # БАЛАНС деньги

    text_color = (255, 215, 200)
    text_surface = font.render(balance_text, True, text_color)

    x = (screen.get_width() - text_surface.get_width()) // 2
    y = screen.get_height() - text_surface.get_height() - 25

    bg_rect = text_surface.get_rect(topleft=(x, y)).inflate(30, 15)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 180))
    screen.blit(bg_surface, bg_rect.topleft)

    pygame.draw.rect(screen, (200, 200, 200), bg_rect, 2)
    screen.blit(text_surface, (x, y))