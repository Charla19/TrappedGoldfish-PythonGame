import os
from pathlib import Path
import tempfile
import unittest
import random
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

from scores import ScoreStore
from game import Game
from main import App
from pearl import Pearl
from healing import HealingBubble


class ScoreTests(unittest.TestCase):
    def test_device_isolation_and_session_history(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / "data_score.txt").write_text("40 Charla\n60 Marie\n", encoding="utf-8")
            (folder / "prenom.txt").write_text("marie", encoding="utf-8")
            store = ScoreStore(folder / "scores.json")
            self.assertEqual(store.players, {})
            self.assertIsNone(store.last_player)
            store.add_player("Marie")
            store.record_score("Marie", 60)
            store.record_score("Marie", 0)
            store.add_player("Goldfish")
            store.record_score("Goldfish", 75)
            reloaded = ScoreStore(folder / "scores.json")
            self.assertEqual(reloaded.players["Marie"]["scores"], [60, 0])
            self.assertEqual(reloaded.last_player, "Goldfish")
            self.assertEqual(reloaded.top_three()[0], ("Goldfish", 75))
            with self.assertRaises(ValueError):
                reloaded.add_player("goldfish")
            with patch("scores.sys.platform", "win32"), patch.dict(os.environ, {"LOCALAPPDATA": str(folder / "device-a")}):
                first_device = ScoreStore()
                first_device.add_player("Nemo")
            with patch("scores.sys.platform", "win32"), patch.dict(os.environ, {"LOCALAPPDATA": str(folder / "device-b")}):
                second_device = ScoreStore()
                self.assertEqual(second_device.players, {})
                self.assertIsNone(second_device.last_player)
            with patch("scores.sys.platform", "win32"), patch.dict(os.environ, {"LOCALAPPDATA": str(folder / "device-a")}):
                self.assertEqual(ScoreStore().last_player, "Nemo")


class GameTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((961, 650))
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def test_sharks_keep_spawning_without_kills(self):
        self.game.start()
        self.assertEqual(len(self.game.all_obstacle), 3)
        for _ in range(25):
            self.game.update(self.screen, 0.1)
        self.assertGreaterEqual(len(self.game.all_obstacle), 4)
        self.game.all_obstacle.empty()
        for _ in range(25):
            self.game.update(self.screen, 0.1)
        self.assertGreaterEqual(len(self.game.all_obstacle), 1)

    def test_shark_dodges_and_kills_score(self):
        self.game.start()
        shark = next(iter(self.game.all_obstacle))
        shark.rect.right = -1
        shark.forward()
        self.assertNotIn(shark, self.game.all_obstacle)
        self.assertEqual(self.game.score, 2)
        next_shark = next(iter(self.game.all_obstacle))
        next_shark.damage(60)
        self.assertNotIn(next_shark, self.game.all_obstacle)
        self.assertEqual(self.game.score, 12)

    def collect(self, count):
        for _ in range(count):
            pearl = Pearl(100, 100)
            self.game.pearls.add(pearl)
            self.game.collect_pearl(pearl)

    def test_combo_collects_once_and_multiplies_shark_points(self):
        self.game.start()
        pearl = Pearl(100, 100)
        self.game.pearls.add(pearl)
        self.game.collect_pearl(pearl)
        self.assertEqual(self.game.score, 5)
        self.game.collect_pearl(pearl)
        self.assertEqual(self.game.pearls_collected, 1)
        self.collect(2)
        self.assertEqual(self.game.multiplier, 2)
        score = self.game.score
        next(iter(self.game.all_obstacle)).damage(60)
        self.assertEqual(self.game.score - score, 20)
        self.collect(12)
        self.assertEqual(self.game.multiplier, 5)
        self.assertEqual(self.game.best_multiplier, 5)
        self.assertEqual(self.game.shield_charge, 8)
        self.game.player.damage(12)
        self.assertEqual(self.game.multiplier, 1)
        self.assertEqual(self.game.best_multiplier, 5)

    def test_shield_protects_freezes_in_pause_and_expires(self):
        self.game.start()
        self.assertFalse(self.game.activate_shield())
        self.collect(8)
        self.assertTrue(self.game.activate_shield())
        self.assertFalse(self.game.activate_shield())
        self.game.player.damage(100)
        self.assertEqual(self.game.player.health, 100)
        self.collect(1)
        self.assertEqual(self.game.shield_charge, 0)
        self.game.paused = True
        remaining = self.game.combo_remaining
        self.game.update(self.screen, 0.1)
        self.assertEqual(self.game.shield_remaining, 5)
        self.assertEqual(self.game.combo_remaining, remaining)
        self.game.paused = False
        self.game.update_bonuses(5.1)
        self.assertEqual(self.game.shield_remaining, 0)
        self.assertEqual(self.game.multiplier, 1)
        self.game.player.damage(12)
        self.assertEqual(self.game.player.health, 88)

    def test_pearl_contact_cleanup_and_restart(self):
        self.game.start()
        self.game.pearls.empty()
        pearl = Pearl(*self.game.player.rect.center)
        self.game.pearls.add(pearl)
        self.game.update_bonuses(0)
        self.assertEqual(self.game.pearls_collected, 1)
        missed = Pearl(-100, 100)
        self.game.pearls.add(missed)
        self.game.update_bonuses(0.1)
        self.assertFalse(missed.alive())
        self.game.update_bonuses(4.5)
        self.assertGreater(len(self.game.pearls), 0)
        self.collect(8)
        self.game.activate_shield()
        self.game.start()
        self.assertEqual(self.game.pearls_collected, 0)
        self.assertEqual(self.game.shield_charge, 0)
        self.assertEqual(self.game.shield_remaining, 0)
        self.assertEqual(self.game.shield_uses, 0)
        self.assertEqual(self.game.best_multiplier, 1)

    def test_pearls_arrive_progressively_with_varied_heights(self):
        random.seed(41)
        self.game.start()
        self.assertEqual(len(self.game.pearls), 0)
        seen, births, heights = set(), [], []
        for frame in range(220):
            self.game.update_bonuses(0.05)
            new = set(self.game.pearls) - seen
            if new:
                births.append(frame)
                self.assertLessEqual(len(new), 2)
                for pearl in new:
                    self.assertGreater(pearl.rect.left, self.game.WIDTH)
                    heights.append(pearl.base_y)
            seen.update(new)
        self.assertGreaterEqual(len(births), 9)
        intervals = {b - a for a, b in zip(births, births[1:])}
        self.assertGreater(len(intervals), 3)
        self.assertGreater(max(heights) - min(heights), 180)
        self.assertGreater(len(set(heights)), 8)

    def test_healing_first_arrival_and_single_pickup_limit(self):
        self.game.start()
        for _ in range(299):
            self.game.update_bonuses(0.1)
        self.assertEqual(len(self.game.healing_bubbles), 0)
        self.game.update_bonuses(0.1)
        self.assertEqual(len(self.game.healing_bubbles), 1)
        self.assertIsNone(self.game.spawn_healing())
        first = next(iter(self.game.healing_bubbles))
        for _ in range(299):
            self.game.update_bonuses(0.1)
        self.assertEqual(len(self.game.healing_bubbles), 0)
        self.game.update_bonuses(0.1)
        self.assertEqual(len(self.game.healing_bubbles), 1)
        self.assertNotIn(first, self.game.healing_bubbles)
        self.game.heal_timer = 0
        self.game.update_bonuses(0)
        self.assertEqual(len(self.game.healing_bubbles), 1)
        bubble = next(iter(self.game.healing_bubbles))
        self.assertGreater(bubble.rect.left, self.game.WIDTH)

    def test_healing_repairs_ten_points_and_caps_at_full_health(self):
        self.game.start()
        self.game.combo_count = 3
        self.game.combo_remaining = 3
        self.game.player.health = 83
        bubble = HealingBubble(*self.game.player.rect.center)
        self.game.healing_bubbles.add(bubble)
        self.game.update_bonuses(0)
        self.assertEqual(self.game.player.health, 93)
        self.game.collect_healing(bubble)
        self.assertEqual(self.game.player.health, 93)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.shield_charge, 0)
        self.assertEqual(self.game.combo_count, 3)
        self.game.player.health = 98
        bubble = HealingBubble(*self.game.player.rect.center)
        self.game.healing_bubbles.add(bubble)
        self.game.update_bonuses(0)
        self.assertEqual(self.game.player.health, 100)
        self.assertEqual(self.game.popups[-1]["text"], "+2 PV")
        bubble = HealingBubble(*self.game.player.rect.center)
        self.game.healing_bubbles.add(bubble)
        self.game.update_bonuses(0)
        self.assertEqual(self.game.player.health, 100)
        self.assertEqual(self.game.popups[-1]["text"], "Vie au maximum")

    def test_healing_pause_cleanup_and_round_reset(self):
        self.game.start()
        self.game.heal_timer = 0.1
        self.game.paused = True
        self.game.step(0.1)
        self.assertEqual(self.game.heal_timer, 0.1)
        self.assertEqual(len(self.game.healing_bubbles), 0)
        self.game.paused = False
        self.game.update_bonuses(0.1)
        bubble = next(iter(self.game.healing_bubbles))
        position = bubble.rect.center
        self.game.paused = True
        self.game.step(0.1)
        self.assertEqual(bubble.rect.center, position)
        self.assertEqual(self.game.heal_timer, 30)
        self.game.paused = False
        bubble.update(8)
        self.assertFalse(bubble.alive())
        self.game.update_bonuses(0.1)
        self.assertEqual(len(self.game.healing_bubbles), 0)
        self.game.start()
        self.assertEqual(self.game.heal_timer, 30)
        self.assertEqual(len(self.game.healing_bubbles), 0)


class AppTests(unittest.TestCase):
    def test_arrow_shield_enter_attack_and_keyboard_navigation(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ScoreStore(Path(folder) / "scores.json")
            store.add_player("Nemo")
            app = App(store)
            app.draw_menu()
            app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
            app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
            app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
            self.assertEqual(app.state, "players")
            app.start_game()
            for key in (pygame.K_RIGHT, pygame.K_e):
                app.game.start()
                app.game.shield_charge = 8
                app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
                self.assertEqual(app.game.shield_uses, 1)
            app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
            self.assertEqual(len(app.game.player.all_projectile), 1)
            for _ in range(48):
                app.advance_game(1 / 60)
            self.assertGreaterEqual(len(app.game.player.all_projectile), 3)
            app.handle_event(pygame.event.Event(pygame.KEYUP, key=pygame.K_RETURN))
            last_shot = app.game.player.last_shot
            app.advance_game(0.1)
            self.assertEqual(app.game.player.last_shot, last_shot)
            app.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
            self.assertEqual(app.state, "pause")
            frozen = (app.game.elapsed, app.ocean.time)
            app.advance_game(1)
            self.assertEqual((app.game.elapsed, app.ocean.time), frozen)
            pygame.quit()

    def test_motion_setting_is_local_and_persistent(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ScoreStore(Path(folder) / "scores.json")
            store.add_player("Nemo")
            app = App(store)
            app.toggle_motion()
            self.assertFalse(ScoreStore(store.path).settings["background_motion"])
            app.start_game()
            app.advance_game(0.1)
            self.assertEqual(app.ocean.time, 0)
            self.assertGreater(app.game.elapsed, 0)
            pygame.quit()

    def test_fixed_simulation_matches_at_different_render_rates(self):
        results = []
        with tempfile.TemporaryDirectory() as folder:
            for fps in (30, 60, 144):
                random.seed(73)
                store = ScoreStore(Path(folder) / f"{fps}.json")
                store.add_player("Nemo")
                app = App(store)
                app.start_game()
                app.game.player.velocity = 100
                app.game.pressed[pygame.K_UP] = True
                for _ in range(fps):
                    app.advance_game(1 / fps)
                results.append((round(app.game.elapsed, 5), app.game.player.rect.y,
                                next(iter(app.game.all_obstacle)).rect.x, app.game.score))
                pygame.quit()
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])

    def test_create_finish_and_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ScoreStore(Path(folder) / "scores.json")
            app = App(store)
            self.assertEqual(app.state, "name")
            app.name_input = "Nemo"
            app.create_player()
            self.assertEqual(app.state, "playing")
            for _ in range(3):
                pearl = Pearl(100, 100)
                app.game.pearls.add(pearl)
                app.game.collect_pearl(pearl)
            saved_score = app.game.score
            self.assertEqual(saved_score, 20)
            app.game.shield_charge = 8
            app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
            self.assertGreater(app.game.shield_remaining, 0)
            app.game.game_over()
            app.finish_game()
            self.assertEqual(app.state, "end")
            self.assertEqual(store.players["Nemo"]["scores"], [saved_score])
            app.draw_end()
            app.start_game()
            self.assertEqual(app.game.score, 0)
            self.assertEqual(app.player_name, "Nemo")
            app.game.score = 3
            app.quit()
            self.assertEqual(ScoreStore(store.path).players["Nemo"]["scores"], [saved_score, 3])
            pygame.quit()


if __name__ == "__main__":
    unittest.main()
