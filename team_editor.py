# team_editor.py

import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import threading
import os
import json
import tkinter.simpledialog
import tkinter.messagebox

class TeamEditor:
    def __init__(self, root, game_version, pokemon_service):
        self.root = root
        self.game_version = game_version
        self.pokemon_service = pokemon_service
        self.team_data = [None] * 6
        self.resize_job = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title(f"Pokémon Team – {self.game_version.title()}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#333333")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Hauptcontainer für das Team-Grid
        team_container = tk.Frame(self.root, bg="#333333")
        team_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for r in range(2):
            team_container.rowconfigure(r, weight=1)
        for c in range(3):
            team_container.columnconfigure(c, weight=1)

        self.team_frames = []
        self.img_labels = []
        self.name_entries = []
        self.level_entries = []
        self.stats_labels = []

        # Erstelle 6 Pokémon-Slots (2x3)
        for i in range(2):
            for j in range(3):
                idx = i * 3 + j
                frame = tk.Frame(team_container, bg="#333333", bd=2, relief="raised")
                frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                frame.grid_propagate(False)
                frame.rowconfigure(0, weight=3)
                frame.rowconfigure(1, weight=3)
                frame.rowconfigure(2, weight=3)
                frame.columnconfigure(0, weight=1)
                self.team_frames.append(frame)

                # Bildanzeige
                img_label = tk.Label(frame, bg="#333333")
                img_label.place(relx=0.5, rely=0.25, anchor="center")
                self.img_labels.append(img_label)

                # Eingabefeld für Name/Level
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

                # Statistik-Anzeige (Typen, Moves, Stärken, Schwächen)
                stats_label = tk.Label(frame, text="", bg="#333333", fg="white", justify="left", anchor="n")
                stats_label.place(relx=0.5, rely=0.75, anchor="center", relwidth=0.9)
                self.stats_labels.append(stats_label)

        # Speichern-Button unten rechts
        tk.Button(
            self.root, text="💾 Team speichern",
            command=self.save_team,
            bg="#447744", fg="white", font=("Helvetica", 10),
            padx=10, pady=5
        ).place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

        self.root.bind("<Configure>", self.on_resize)

    # ===== POKÉMON-LADELOGIK MIT SERVICE =====
    def change_pokemon(self, slot):
        def load_data():
            name = self.name_entries[slot].get().strip()
            if not name:
                return
            try:
                level = int(self.level_entries[slot].get())
            except ValueError:
                level = 100

            try:
                pokemon_obj = self.pokemon_service.fetch_pokemon(
                    name=name,
                    level=level,
                    game_version=self.game_version
                )

                data = {
                    "name": pokemon_obj.name,
                    "types": pokemon_obj.types,
                    "moves": pokemon_obj.moves,
                    "image_path": pokemon_obj.image_path,
                    "strengths": pokemon_obj.strengths,
                    "weaknesses": pokemon_obj.weaknesses,
                }
                self.team_data[slot] = data
                self.root.after(0, self.update_team_display)

            except ValueError as e:
                self.root.after(0, lambda: self._show_error(slot, str(e)))

        threading.Thread(target=load_data, daemon=True).start()

    def _show_error(self, slot, message):
        self.stats_labels[slot].config(text=f"❌ {message}", fg="red")
        self.img_labels[slot].configure(image="")
        self.img_labels[slot].image = None

    # ===== ANZEIGE AKTUALISIEREN =====
    def update_team_display(self):
        for idx, frame in enumerate(self.team_frames):
            data = self.team_data[idx]
            img_label = self.img_labels[idx]
            stats_label = self.stats_labels[idx]

            if data:
                if "img_pil" not in data:
                    image_path = data.get("image_path")
                    if image_path and os.path.exists(image_path):
                        data["img_pil"] = Image.open(image_path).convert("RGBA")
                    else:
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

                strengths = data.get("strengths", [])
                weaknesses = data.get("weaknesses", [])
                stats_text = (
                    f"Typen: {', '.join(data['types'])}\n"
                    f"Moves: {', '.join(data['moves'])}\n"
                    f"Strengths: {', '.join(strengths) if strengths else '-'}\n"
                    f"Weaknesses: {', '.join(weaknesses) if weaknesses else '-'}"
                )
                stats_label.config(text=stats_text)
                self.update_text_font(stats_label, frame)
            else:
                img_label.configure(image="")
                img_label.image = None
                stats_label.config(text="")

    def update_text_font(self, label, frame):
        text_height = int(frame.winfo_height() * 0.55)
        size = max(8, min(12, int(text_height / 20)))
        font = tkFont.Font(family="Helvetica", size=size)
        label.config(font=font)

    def actually_resize(self):
        for idx, frame in enumerate(self.team_frames):
            stats_label = self.stats_labels[idx]
            stats_label.config(wraplength=int(frame.winfo_width() * 0.9))
        self.update_team_display()

    def on_resize(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(150, self.actually_resize)

    # ===== TEAM SPEICHERN =====
    def save_team(self):
        team_name = tkinter.simpledialog.askstring("Team speichern", "Name des Teams:")
        if not team_name:
            return

        team_data = {
            "name": team_name,
            "game_version": self.game_version,
            "pokemon": []
        }

        for i, p in enumerate(self.team_data):
            if p:
                level = 100
                try:
                    level = int(self.level_entries[i].get())
                except ValueError:
                    pass
                team_data["pokemon"].append({
                    "name": p["name"],
                    "level": level,
                    "types": p["types"],
                    "moves": p["moves"],
                    "strengths": p["strengths"],
                    "weaknesses": p["weaknesses"],
                    "image_path": p["image_path"]
                })

        try:
            with open(f"{team_name}.json", "w", encoding="utf-8") as f:
                json.dump(team_data, f, indent=2, ensure_ascii=False)
            tkinter.messagebox.showinfo("Gespeichert", f"Team '{team_name}' wurde gespeichert!")
        except Exception as e:
            tkinter.messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{e}")