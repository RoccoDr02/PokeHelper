import tkinter as tk
from io import BytesIO
import requests
from PIL import Image, ImageTk
import tkinter.font as tkFont
import threading
import sqlite3
import json
import os
# ======================
# MODELS
# ======================

class Team:
    def __init__(self, name: str, game_version: str = "platinum"):
        self.name = name
        self.game_version = game_version
        self.pokemon = []  # Liste von Pokemon-Objekten

    def add_pokemon(self, pokemon):
        if len(self.pokemon) < 6:
            self.pokemon.append(pokemon)

    def save_to_db(self, db):
        # Später: db.save_team(self)
        pass

    @classmethod
    def load_from_db(cls, db, team_id):
        # Später: return db.load_team(team_id)
        return None


class Pokemon:
    def __init__(self, name: str, level: int = 100, types=None, moves=None, image_data=None, image_path=None, locations=None):
        self.name = name.lower()
        self.level = level
        self.types = types or []
        self.moves = moves or []
        self.image_data = image_data  # Bytes für API
        self.image_path = image_path  # Pfad für DB (später)
        self.locations = locations or []


# ======================
# START SCREEN
# ======================

class StartScreen:
    def __init__(self, root, on_create_team):
        self.root = root
        self.on_create_team = on_create_team
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Pokémon Team Builder")
        self.root.geometry("600x450")
        self.root.configure(bg="#222222")

        tk.Label(
            self.root, text="Willkommen zum Pokémon Team Builder!",
            font=("Helvetica", 18, "bold"), fg="white", bg="#222222"
        ).pack(pady=30)

        tk.Label(
            self.root, text="Wähle deine Spielversion:",
            font=("Helvetica", 12), fg="white", bg="#222222"
        ).pack()

        self.version_var = tk.StringVar(value="platinum")
        versions = [
            "platinum", "diamond", "pearl",
            "scarlet", "violet", "sword", "shield"
        ]
        tk.OptionMenu(self.root, self.version_var, *versions).pack(pady=10)

        tk.Button(
            self.root, text="✨ Neues Team erstellen",
            command=self._create_new_team,
            bg="#558855", fg="white", font=("Helvetica", 12, "bold"),
            padx=20, pady=8
        ).pack(pady=20)

    def _create_new_team(self):
        version = self.version_var.get()
        self.on_create_team(version)


# ======================
# TEAM EDITOR (dein Original-Code, jetzt als Klasse)
# ======================

class TeamEditor:
    def __init__(self, root, game_version):
        self.root = root
        self.game_version = game_version  # Kann später für versionsspezifische Teams genutzt werden
        self.team_data = [None] * 6
        self.resize_job = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title(f"Pokémon Team – {self.game_version.title()}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#333333")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        team_container = tk.Frame(self.root, bg="#333333")
        team_container.grid(row=0, column=0, sticky="nsew")

        for r in range(2):
            team_container.rowconfigure(r, weight=1)
        for c in range(3):
            team_container.columnconfigure(c, weight=1)

        self.team_frames = []
        self.img_labels = []
        self.name_entries = []
        self.level_entries = []
        self.stats_labels = []

        for i in range(2):
            for j in range(3):
                idx = i * 3 + j
                frame = tk.Frame(team_container, bg="#333333", bd=2, relief="raised")
                frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                frame.grid_propagate(False)
                frame.rowconfigure(0, weight=3)
                frame.rowconfigure(1, weight=3)
                frame.rowconfigure(2, weight=3)
                frame.columnconfigure(0, weight=2)
                self.team_frames.append(frame)

                img_label = tk.Label(frame, bg="#333333")
                img_label.place(relx=0.5, rely=0.25, anchor="center")
                self.img_labels.append(img_label)

                input_frame = tk.Frame(frame, bg="#444444")
                input_frame.grid(row=1, column=0, sticky="ew", pady=5, padx=5)
                tk.Label(input_frame, text="Name:", bg="#444444", fg="white").grid(row=0, column=0)
                name_entry = tk.Entry(input_frame, width=12)
                name_entry.grid(row=0, column=1, padx=3)
                tk.Label(input_frame, text="Level:", bg="#444444", fg="white").grid(row=0, column=2)
                level_entry = tk.Entry(input_frame, width=5)
                level_entry.grid(row=0, column=3, padx=3)
                tk.Button(
                    input_frame, text="Suchen",
                    command=lambda s=idx: self.change_pokemon(s)
                ).grid(row=0, column=4, padx=3)
                self.name_entries.append(name_entry)
                self.level_entries.append(level_entry)

                stats_label = tk.Label(frame, text="", bg="#333333", fg="white", justify="left", anchor="n")
                stats_label.place(relx=0.5, rely=0.75, anchor="center", relwidth=0.9)
                self.stats_labels.append(stats_label)

        self.root.bind("<Configure>", self.on_resize)

    # ===== DATENBANK-ZUGRIFF =====
    def _get_pokemon_from_db(self, name):
        """Lädt Pokémon aus all_pokedex.db – erwartet Spalte 'raw_data' mit JSON."""
        try:
            conn = sqlite3.connect("all_pokedex.db")
            cursor = conn.cursor()
            cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row[0])
            return None
        except Exception as e:
            print("DB-Fehler:", e)
            return None

    # ===== POKÉMON-LADELOGIK (vollständig offline) =====
    def get_pokemon_data(self, name, level=100):
        data = self._get_pokemon_from_db(name)
        if not data:
            return None

        # Extrahiere Moves basierend auf Version und Level
        valid_moves = []
        for move_entry in data.get("moves", []):
            move_name = move_entry.get("name", "unknown")
            learned_in_version = False

            for method in move_entry.get("learn_methods", []):
                if (method.get("method") == "level-up" and
                        method.get("version_group") == self.game_version and
                        method.get("level", 999) <= level):
                    learned_in_version = True
                    break  # Einmal reicht

            if learned_in_version:
                valid_moves.append(move_name)

        return {
            "name": data["name"],
            "types": data["types"],
            "moves": valid_moves,  # ← nur relevante Moves
            "image_path": data.get("image_path"),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", [])
        }

    def analyze_team(self):
        if not any(self.team_data):
            return "Kein Team vorhanden."

        all_weaknesses = []
        all_strengths = []
        move_types = set()

        for poke in self.team_data:
            if poke:
                all_weaknesses.extend(poke.get("weaknesses", []))
                all_strengths.extend(poke.get("strengths", []))
                # Extrahiere Move-Typen (später aus DB)
                # move_types.update(...)

        # Zähle häufige Schwächen
        from collections import Counter
        weakness_counts = Counter(all_weaknesses)
        critical_weaknesses = [typ for typ, count in weakness_counts.items() if count >= 3]

        report = {
            "critical_weaknesses": critical_weaknesses,
            "coverage": list(set(all_strengths)),
            "team_size": sum(1 for p in self.team_data if p)
        }
        return report

    # ===== GUI-HILFSFUNKTIONEN =====
    def update_text_font(self, label, frame):
        text_height = int(frame.winfo_height() * 0.55)
        size = max(8, min(12, int(text_height / 20)))
        font = tkFont.Font(family="Helvetica", size=size)
        label.config(font=font)

    def update_team_display(self):
        for idx, frame in enumerate(self.team_frames):
            data = self.team_data[idx]
            img_label = self.img_labels[idx]
            stats_label = self.stats_labels[idx]

            if data:
                # Bild aus Datei laden (offline)
                if "img_pil" not in data:
                    image_path = data.get("image_path")
                    if image_path and os.path.exists(image_path):
                        data["img_pil"] = Image.open(image_path).convert("RGBA")
                    else:
                        # Fallback: graues Platzhalter-Bild
                        data["img_pil"] = Image.new("RGBA", (80, 80), (50, 50, 50, 255))

                img = data["img_pil"]
                frame_width = frame.winfo_width()
                frame_height = int(frame.winfo_height() * 0.45)
                if frame_width > 1 and frame_height > 1:
                    img_ratio = img.width / img.height
                    frame_ratio = frame_width / frame_height
                    if frame_ratio > img_ratio:
                        new_height = frame_height
                        new_width = int(img_ratio * new_height)
                    else:
                        new_width = frame_width
                        new_height = int(new_width / img_ratio)
                    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img_resized)
                    img_label.configure(image=img_tk)
                    img_label.image = img_tk

                # Text mit Stärken/Schwächen (bereits in DB!)
                strengths = data.get("strengths", [])
                weaknesses = data.get("weaknesses", [])
                stats_text = (
                    f"Typen: {', '.join(data['types'])}\n"
                    f"Moves: {', '.join(data['moves'])}\n"
                    f"Strengths: {', '.join(strengths) if strengths else '-'}\n"
                    f"Weakness: {', '.join(weaknesses) if weaknesses else '-'}"
                )
                stats_label.config(text=stats_text)
                self.update_text_font(stats_label, frame)
            else:
                img_label.configure(image="")
                img_label.image = None
                stats_label.config(text="")

    # ===== SUCHE MIT THREADING =====
    def change_pokemon(self, slot):
        def load_data():
            name = self.name_entries[slot].get().strip()
            if not name:
                return
            try:
                level = int(self.level_entries[slot].get())
            except:
                level = 100
            data = self.get_pokemon_data(name, level)
            if data:
                self.team_data[slot] = data
                self.root.after(0, self.update_team_display)
            else:
                self.team_data[slot] = None
                # Zeige Fehler in stats_label
                self.stats_labels[slot].config(text="❌ Pokémon nicht gefunden!", fg="red")

        threading.Thread(target=load_data, daemon=True).start()

    # ===== RESIZING =====
    def actually_resize(self):
        for idx, frame in enumerate(self.team_frames):
            stats_label = self.stats_labels[idx]
            stats_label.config(wraplength=int(frame.winfo_width() * 0.9))
        self.update_team_display()

    def on_resize(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(150, self.actually_resize)


# ======================
# MAIN
# ======================

def main():
    root = tk.Tk()

    def start_new_team(game_version):
        for widget in root.winfo_children():
            widget.destroy()
        TeamEditor(root, game_version)

    StartScreen(root, on_create_team=start_new_team)
    root.mainloop()


if __name__ == "__main__":
    main()