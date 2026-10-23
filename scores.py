"""Persistent player profiles and scores for Trapped Goldfish."""

import json
import os
from pathlib import Path
import tempfile
import sys


def local_scores_path():
    """Keep profiles outside the game folder, local to this device and OS user."""
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return root / "TrappedGoldfish" / "scores.json"


class ScoreStore:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else local_scores_path()
        self.players = {}
        self.last_player = None
        self.settings = {"background_motion": True}
        if self.path.exists():
            self._load()
        else:
            self.save()

    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.settings["background_motion"] = bool(
                data.get("settings", {}).get("background_motion", True))
            for name, record in data.get("players", {}).items():
                clean = self.validate_name(name)
                scores = [max(0, int(score)) for score in record.get("scores", [])]
                self.players[clean] = {"scores": scores}
            previous = data.get("last_player")
            self.last_player = self.find_player(previous) if previous else None
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"Impossible de lire {self.path}: {exc}") from exc

    @staticmethod
    def validate_name(name):
        if not isinstance(name, str):
            raise ValueError("Nom invalide")
        name = " ".join(name.split())
        if not 1 <= len(name) <= 18 or any(ord(char) < 32 for char in name):
            raise ValueError("Le nom doit contenir entre 1 et 18 caractères")
        return name

    def find_player(self, name):
        if not isinstance(name, str):
            return None
        return next((saved for saved in self.players if saved.casefold() == name.casefold()), None)

    def add_player(self, name):
        name = self.validate_name(name)
        if self.find_player(name):
            raise ValueError("Ce joueur existe déjà")
        self.players[name] = {"scores": []}
        self.last_player = name
        self.save()
        return name

    def select_player(self, name):
        found = self.find_player(name)
        if not found:
            raise ValueError("Joueur introuvable")
        self.last_player = found
        self.save()
        return found

    def record_score(self, name, score):
        found = self.select_player(name)
        self.players[found]["scores"].append(max(0, int(score)))
        self.save()

    def best(self, name):
        found = self.find_player(name)
        scores = self.players[found]["scores"] if found else []
        return max(scores, default=0)

    def top_three(self):
        return sorted(
            ((name, self.best(name)) for name in self.players),
            key=lambda item: (-item[1], item[0].casefold()),
        )[:3]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "last_player": self.last_player,
                "players": self.players, "settings": self.settings}
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".scores-", suffix=".tmp", delete=False) as file:
                temporary = file.name
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temporary, self.path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
