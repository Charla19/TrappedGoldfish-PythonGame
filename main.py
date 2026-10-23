"""Trapped Goldfish: menus, player profiles and the game window."""

import os
import sys
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

import controls
import ui
from game import Game
from ocean import Ocean
from scores import ScoreStore


WIDTH, HEIGHT = 961, 650
INK, PALE, AQUA, CORAL = ui.INK, ui.PALE, ui.AQUA, ui.CORAL


class App:
    def __init__(self, store=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TRAPPED GOLDFISH")
        pygame.display.set_icon(pygame.image.load("assets/poisson.ico"))
        self.background = pygame.image.load("assets/as.jpg").convert()
        self.banner = pygame.image.load("assets/sary.png").convert()
        self.store = store or ScoreStore()
        self.game = Game()
        self.ocean = Ocean(self.background)
        self.font_title = ui.font(34, True)
        self.font_heading = ui.font(24, True)
        self.font_button = ui.font(20, True)
        self.font_body = ui.font(20)
        self.font_small = ui.font(17)
        self.game.motion_enabled = self.store.settings["background_motion"]
        self.player_name = self.store.last_player
        self.state = "menu" if self.player_name else "name"
        self.name_input = ""
        self.name_error = ""
        self.page = 0
        self.last_score = 0
        self.running = True
        self.buttons = []
        self.focus_index = 0
        self.keyboard_mode = False
        self.button_tweens = {}
        self.delta = 1 / 60
        self.accumulator = 0.0
        self.scrim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.scrim.fill((1, 13, 23, 150))
        self.clock = pygame.time.Clock()
        if self.state == "name":
            pygame.key.start_text_input()

    def panel(self, rect, alpha=240):
        ui.panel(self.screen, rect, alpha)

    def text(self, message, font, color, center, max_width=None):
        message = str(message)
        if max_width:
            while message and font.size(message)[0] > max_width:
                message = message[:-2] + "…" if len(message) > 2 else ""
        surface = font.render(str(message), True, color)
        self.screen.blit(surface, surface.get_rect(center=center))

    def button(self, label, rect, action, accent=False, enabled=True, subtitle=None):
        rect = pygame.Rect(rect)
        focused = self.keyboard_mode and len(self.buttons) == self.focus_index and enabled
        hovered = (not self.keyboard_mode and rect.collidepoint(pygame.mouse.get_pos()) and enabled)
        key = (self.state, rect.x, rect.y)
        target = 1.0 if hovered or focused else 0.0
        previous = self.button_tweens.get(key, 0.0)
        blend = previous + (target - previous) * min(1.0, max(0, self.delta) * 16)
        self.button_tweens[key] = blend
        base = CORAL if accent else (16, 68, 89)
        fill = tuple(min(255, round(value + blend * 16)) for value in base)
        if not enabled:
            fill = (22, 48, 62)
        pygame.draw.rect(self.screen, fill, rect, border_radius=14)
        border = PALE if focused or hovered else ui.LINE
        pygame.draw.rect(self.screen, border, rect, 2 if focused else 1, border_radius=14)
        foreground = INK if accent else PALE if enabled else ui.MUTED
        center = rect.center if not subtitle else (rect.centerx, rect.centery - 10)
        self.text(label, self.font_button, foreground, center, rect.width - 20)
        if subtitle:
            self.text(subtitle, self.font_small, foreground,
                      (rect.centerx, rect.centery + 15), rect.width - 16)
        self.buttons.append({"rect": rect, "action": action, "enabled": enabled})

    def backdrop(self, banner=False):
        self.screen.blit(self.banner if banner else self.background, (0, 0))

    def podium(self, x, y, width=350):
        self.panel(pygame.Rect(x, y, width, 205), 222)
        self.text("TOP 3 DES POISSONS", self.font_heading, AQUA,
                  (x + width // 2, y + 35))
        ranking = self.store.top_three()
        if not ranking:
            self.text("Aucun score pour le moment", self.font_small, PALE,
                      (x + width // 2, y + 110))
        for index, (name, score) in enumerate(ranking):
            row_y = y + 77 + index * 40
            ui.text(self.screen, str(index + 1), (x + 22, row_y - 12), 19, CORAL, True)
            ui.text(self.screen, name, (x + 52, row_y - 12), 20, PALE, max_width=width - 166)
            value = ui.label(str(score), 20, AQUA, True)
            self.screen.blit(value, value.get_rect(midright=(x + width - 24, row_y)))

    def draw_menu(self):
        self.backdrop(banner=True)
        self.panel(pygame.Rect(42, 225, 425, 397))
        self.text(f"Joueur : {self.player_name or 'à créer'}", self.font_heading,
                  AQUA, (255, 265), 380)
        self.button("JOUER", (95, 301, 320, 59), self.start_game,
                    accent=True, enabled=bool(self.player_name))
        self.button("CHOISIR UN JOUEUR", (95, 372, 320, 55),
                    lambda: self.change_state("players"))
        self.button("NOUVEAU JOUEUR", (95, 440, 320, 55),
                    lambda: self.change_state("name"))
        self.button("QUITTER", (95, 507, 320, 55), self.quit)
        self.podium(510, 286, 405)
        self.panel((510, 508, 405, 114))
        self.text("↑ ↓  Nager   ·   Entrée / Espace  Tirer",
                  self.font_small, PALE, (712, 532))
        self.text("→ / E  Bouclier   ·   P  Pause",
                  self.font_small, AQUA, (712, 565))
        self.text("↑ ↓ / Tab : choisir   ·   Entrée : valider",
                  self.font_small, ui.MUTED, (712, 599))

    def draw_players(self):
        self.backdrop()
        self.panel(pygame.Rect(125, 38, 711, 578))
        self.text("CHOISIR UN JOUEUR", self.font_title, PALE, (480, 88))
        names = list(self.store.players)
        total_pages = max(1, (len(names) + 5) // 6)
        self.page = max(0, min(self.page, total_pages - 1))
        visible = names[self.page * 6:self.page * 6 + 6]
        for index, name in enumerate(visible):
            y = 130 + index * 64
            best = self.store.best(name)
            label = f"{name}   ·   record {best}"
            self.button(label, (205, y, 551, 53),
                        lambda chosen=name: self.choose_player(chosen),
                        accent=name == self.player_name)
        self.text(f"Page {self.page + 1} / {total_pages}", self.font_small,
                  PALE, (480, 540))
        self.button("←", (205, 555, 75, 48), self.previous_page,
                    enabled=self.page > 0)
        self.button("RETOUR", (345, 555, 270, 48),
                    lambda: self.change_state("menu"))
        self.button("→", (680, 555, 75, 48), self.next_page,
                    enabled=self.page < total_pages - 1)

    def draw_name(self):
        self.backdrop()
        self.panel(pygame.Rect(155, 100, 651, 455))
        self.text("NOUVEAU JOUEUR", self.font_title, PALE, (480, 160))
        self.text("Choisis un nom pour garder tes scores", self.font_body,
                  AQUA, (480, 213))
        self.text("Nom du joueur · 18 caractères maximum", self.font_small,
                  ui.MUTED, (480, 240))
        field = pygame.Rect(245, 255, 471, 66)
        pygame.draw.rect(self.screen, PALE, field, border_radius=12)
        self.text(self.name_input or "Ton nom...", self.font_button,
                  INK if self.name_input else (92, 117, 127), field.center)
        if self.name_error:
            self.text(self.name_error, self.font_small, CORAL, (480, 348))
        self.button("CRÉER ET JOUER", (246, 384, 470, 57),
                    self.create_player, accent=True)
        self.button("RETOUR", (321, 460, 320, 54),
                    lambda: self.change_state("menu") if self.player_name else self.quit())

    def draw_playing(self):
        self.advance_game(self.delta)
        if not self.game.is_playing:
            self.finish_game()
            self.buttons = []
            self.draw_end()
            return
        self.ocean.draw(self.screen, self.game.motion_enabled)
        self.game.draw_world(self.screen, max(0.0, min(1.0, self.accumulator * 120)))
        shield_label = (f"PROTÉGÉ  {self.game.shield_remaining:.1f}s"
                        if self.game.shield_remaining > 0 else
                        "BOUCLIER PRÊT" if self.game.shield_ready else
                        f"BOUCLIER  {self.game.shield_charge}/8")
        self.button(shield_label, (638, 28, 204, 56), self.game.activate_shield,
                    accent=self.game.shield_ready, enabled=self.game.shield_ready,
                    subtitle="→ / E" if self.game.shield_ready else
                    "Protection active" if self.game.shield_remaining > 0 else "Collecte des perles")
        self.button("Pause", (854, 28, 78, 56), lambda: self.change_state("pause"), subtitle="P")

    def advance_game(self, dt):
        if self.game.paused:
            return
        self.accumulator += min(0.1, max(0.0, dt))
        step = 1 / 120
        while self.accumulator >= step - 1e-9 and self.game.is_playing:
            self.game.step(step)
            self.ocean.update(step, self.game.motion_enabled)
            self.accumulator -= step

    def draw_pause(self):
        self.ocean.draw(self.screen, self.game.motion_enabled)
        self.game.draw_world(self.screen)
        self.screen.blit(self.scrim, (0, 0))
        self.panel((260, 108, 441, 470))
        self.text("PAUSE", self.font_title, PALE, (480, 155))
        self.button("Reprendre", (310, 204, 341, 56), self.resume,
                    accent=True)
        self.button("Recommencer", (310, 276, 341, 56), self.restart_from_pause)
        self.button("Terminer la partie", (310, 348, 341, 56),
                    self.end_from_pause)
        self.button("Décor animé : " + ("oui" if self.game.motion_enabled else "non"),
                    (310, 420, 341, 56), self.toggle_motion)
        self.text("P / Échap : reprendre   ·   M : décor calme",
                  self.font_small, ui.MUTED, (480, 532))

    def draw_end(self):
        self.backdrop(banner=True)
        self.panel(pygame.Rect(45, 210, 425, 416), 232)
        self.text("PARTIE TERMINÉE", self.font_heading, PALE, (257, 248))
        self.text(f"{self.player_name} : {self.last_score} points",
                  self.font_heading, CORAL, (257, 293), 380)
        self.text(f"Record personnel : {self.store.best(self.player_name)}",
                  self.font_small, AQUA, (257, 330))
        self.button("REJOUER", (96, 358, 320, 53), self.start_game,
                    accent=True)
        self.button("AUTRE JOUEUR", (96, 422, 320, 50),
                    lambda: self.change_state("players"))
        self.button("NOUVEAU JOUEUR", (96, 483, 320, 50),
                    lambda: self.change_state("name"))
        self.button("MENU", (96, 544, 320, 50),
                    lambda: self.change_state("menu"))
        self.podium(515, 290, 400)
        self.panel(pygame.Rect(515, 514, 400, 106))
        self.text(f"{self.game.pearls_collected} perles  ·  meilleur combo x{self.game.best_multiplier}",
                  self.font_body, CORAL, (715, 548))
        self.text(f"Boucliers utilisés : {self.game.shield_uses}",
                  self.font_small, AQUA, (715, 586))

    def change_state(self, state):
        if self.state == "name" and state != "name":
            pygame.key.stop_text_input()
        if state == "name" and self.state != "name":
            self.name_input = ""
            self.name_error = ""
            pygame.key.start_text_input()
        if state == "pause":
            self.game.paused = True
            self.game.clear_input()
        self.focus_index = 0
        self.buttons = []
        self.button_tweens.clear()
        self.state = state

    def toggle_motion(self):
        self.game.motion_enabled = not self.game.motion_enabled
        self.store.settings["background_motion"] = self.game.motion_enabled
        self.store.save()

    def choose_player(self, name):
        self.player_name = self.store.select_player(name)
        self.change_state("menu")

    def create_player(self):
        try:
            self.player_name = self.store.add_player(self.name_input)
        except ValueError as exc:
            self.name_error = str(exc)
            return
        self.change_state("menu")
        self.start_game()

    def start_game(self):
        if not self.player_name:
            self.change_state("name")
            return
        self.store.select_player(self.player_name)
        self.game.start()
        self.accumulator = 0.0
        self.change_state("playing")

    def resume(self):
        self.game.paused = False
        self.accumulator = 0.0
        self.change_state("playing")

    def finish_game(self):
        if self.state != "playing" and self.state != "pause":
            return
        self.last_score = self.game.score
        self.store.record_score(self.player_name, self.last_score)
        self.change_state("end")

    def end_from_pause(self):
        self.game.is_playing = False
        self.finish_game()

    def restart_from_pause(self):
        self.game.is_playing = False
        self.finish_game()
        self.start_game()

    def previous_page(self):
        self.page -= 1

    def next_page(self):
        self.page += 1

    def quit(self):
        if self.state in ("playing", "pause"):
            self.game.is_playing = False
            self.finish_game()
        self.running = False

    def handle_event(self, event):
        if event.type == pygame.WINDOWFOCUSLOST and self.state == "playing":
            self.change_state("pause")
            return
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == pygame.MOUSEMOTION:
            self.keyboard_mode = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.keyboard_mode = False
            for button in reversed(self.buttons):
                if button["rect"].collidepoint(event.pos):
                    if button["enabled"]:
                        button["action"]()
                    return
            if self.state == "playing":
                self.game.mouse_fire = True
                self.game.player.launch_projectile()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.game.mouse_fire = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.state == "playing":
            self.game.activate_shield()
        elif event.type == pygame.MOUSEWHEEL and self.state == "players":
            self.page -= event.y
        elif event.type == pygame.TEXTINPUT and self.state == "name":
            candidate = self.name_input + event.text
            if len(candidate) <= 18 and all(ord(char) >= 32 for char in candidate):
                self.name_input = candidate
                self.name_error = ""
        elif event.type == pygame.KEYDOWN:
            if getattr(event, "repeat", False) and event.key in (*controls.SHIELD, *controls.PAUSE, pygame.K_m):
                return
            if event.key == pygame.K_m and self.state in ("playing", "pause", "menu"):
                self.toggle_motion()
                return
            navigation = self.state != "playing" and (self.state != "name" or event.key == pygame.K_TAB)
            if navigation and event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
                self.move_focus(-1 if event.key == pygame.K_UP or
                                (event.key == pygame.K_TAB and getattr(event, "mod", 0) & pygame.KMOD_SHIFT)
                                else 1)
                return
            if self.state != "playing" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.keyboard_mode:
                if self.buttons and self.focus_index < len(self.buttons):
                    button = self.buttons[self.focus_index]
                    if button["enabled"]:
                        button["action"]()
                        return
            if self.state == "name":
                if event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self.create_player()
                elif event.key == pygame.K_ESCAPE and self.player_name:
                    self.change_state("menu")
            elif self.state == "playing":
                if event.key in controls.PAUSE:
                    self.change_state("pause")
                elif event.key in controls.FIRE:
                    self.game.pressed[event.key] = True
                    self.game.player.launch_projectile()
                elif event.key in controls.SHIELD:
                    self.game.activate_shield()
                else:
                    self.game.pressed[event.key] = True
            elif self.state == "pause" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                self.resume()
            elif self.state == "menu" and event.key == pygame.K_RETURN:
                self.start_game()
            elif self.state == "end" and event.key == pygame.K_RETURN:
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.change_state("menu")
        elif event.type == pygame.KEYUP and self.state == "playing":
            self.game.pressed[event.key] = False

    def move_focus(self, direction):
        available = [index for index, button in enumerate(self.buttons) if button["enabled"]]
        if not available:
            return
        if not self.keyboard_mode:
            self.focus_index = available[0] if direction > 0 else available[-1]
        else:
            current = available.index(self.focus_index) if self.focus_index in available else -1
            self.focus_index = available[(current + direction) % len(available)]
        self.keyboard_mode = True

    def run(self):
        while self.running:
            self.delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            if not self.running:
                break
            self.buttons = []
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "players":
                self.draw_players()
            elif self.state == "name":
                self.draw_name()
            elif self.state == "playing":
                self.draw_playing()
            elif self.state == "pause":
                self.draw_pause()
            else:
                self.draw_end()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        from diagnostics import run_self_test
        raise SystemExit(run_self_test(App, Path(sys.argv[2])))
    App().run()
