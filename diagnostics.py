"""Optional packaged-build verification; never reads the real player profiles."""

import json
import os
from pathlib import Path
import sys
import tempfile
import traceback


def run_self_test(app_factory, report_path):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    import pygame
    from scores import ScoreStore

    checks = []
    report = {"frozen": bool(getattr(sys, "frozen", False)), "checks": checks}
    try:
        with tempfile.TemporaryDirectory(prefix="goldfish-test-") as directory:
            store = ScoreStore(Path(directory) / "scores.json")
            app = app_factory(store)
            app.name_input = "Test"
            app.draw_name()
            app.create_player()
            checks.append("startup, name entry, images, fonts and audio")
            for _ in range(8):
                pearl = app.game.spawn_pearl(x=100, y=200)
                app.game.collect_pearl(pearl)
            assert app.game.pearls_collected == 8
            assert app.game.shield_ready
            app.game.activate_shield()
            assert app.game.shield_remaining == 5
            checks.append("pearls, combo and shield")
            app.game.player.health = 78
            healing = app.game.spawn_healing()
            app.game.collect_healing(healing)
            assert app.game.player.health == 88
            checks.append("healing pickup")
            app.game.player.launch_projectile()
            assert len(app.game.player.all_projectile) == 1
            app.game.fleche.lance_fall()
            assert len(app.game.fleche.all_lance) == 4
            checks.append("projectiles, sharks and swordfish resources")
            for _ in range(60):
                app.delta = 1 / 60
                app.buttons = []
                app.draw_playing()
            app.change_state("pause")
            app.buttons = []
            app.draw_pause()
            app.end_from_pause()
            app.buttons = []
            app.draw_end()
            expected = app.last_score
            assert ScoreStore(store.path).players["Test"]["scores"] == [expected]
            checks.append("pause, end screen and persistent score")
            app.change_state("players")
            app.buttons = []
            app.draw_players()
            app.choose_player("Test")
            app.buttons = []
            app.draw_menu()
            checks.append("player selection and main menu")
            app.start_game()
            assert app.game.score == 0 and app.game.player.health == 100
            assert len(app.game.healing_bubbles) == 0
            checks.append("replay resets the round")
            app.change_state("menu")
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            app.run()
            checks.append("normal event loop and clean exit")
        report["ok"] = True
    except Exception:
        report.update(ok=False, error=traceback.format_exc())
        pygame.quit()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if report["ok"] else 1
