# team_editor.py
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import threading
import os
import json
import tkinter.simpledialog
import tkinter.messagebox
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext
from core.ai_advisor import AIAdvisor
from models.team import Team, Pokemon
from core.pokemon_service import PokemonService

class TeamEditor:
    def __init__(self, root, game_version, pokemon_service, db, team=None):
        self.root = root
        self.db = db
        self.pokemon_service = pokemon_service

        # Team setzen: Entweder das geladene Team oder ein neues
        if team:
            self.team = team
            self.game_version = team.game_version
            # Teamdaten für die Anzeige vorbereiten
            self.team_data = [p.to_dict() if p else None for p in team.pokemon]
            while len(self.team_data) < 6:
                self.team_data.append(None)
        else:
            self.game_version = game_version
            self.team = Team(name="Unbenanntes Team", game_version=self.game_version)
            self.team_data = [None] * 6

        # Liste aller Pokémon-Namen für Autocomplete
        self.all_pokemon_names = [
            name.lower() for name in self.pokemon_service.get_all_pokemon_names()
        ]

        self.resize_job = None

        # UI aufbauen
        self.setup_ui()

        # Fenster schließen Event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Anzeige updaten
        self.root.after(100, self.update_team_display)
        self.root.after(150, self.actually_resize)

    def setup_ui(self):
        self.root.title(f"Pokémon Team – {self.game_version.title()}")
        self.root.geometry("1400x900")
        self.root.configure(bg="#333333")

        # Layout Rows/Columns
        self.root.rowconfigure(0, weight=1)  # Pokémon-Felder
        self.root.rowconfigure(1, weight=0)  # Eingabezeile (AI)
        self.root.rowconfigure(2, weight=0)  # Antwortfeld (AI)
        self.root.columnconfigure(0, weight=1)

        # Team-Grid Container
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
        self.save_buttons = []

        # Pokémon Slots (2x3)
        for i in range(2):
            for j in range(3):
                idx = i * 3 + j
                frame = tk.Frame(team_container, bg="#333333", bd=2, relief="raised")
                frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                frame.grid_propagate(False)
                self.team_frames.append(frame)

                # Internes Grid: 3 Zeilen, 2 Spalten
                frame.rowconfigure(0, weight=1)  # Obere Zeile (Name/Level + Bild)
                frame.rowconfigure(1, weight=0)  # Trennlinie (klein)
                frame.rowconfigure(2, weight=2)  # Untere Zeile (Stats)
                frame.columnconfigure(0, weight=7)  # Linke Spalte: 70%
                frame.columnconfigure(1, weight=3)  # Rechte Spalte: 30%

                # --- ZEILE 0: NAME/LEVEL + BILD ---
                # ---- LINKE SPALTE: Name/Level + Buttons ----
                input_frame = tk.Frame(frame, bg="#333333")
                input_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

                # Name-Zeile
                name_row = tk.Frame(input_frame, bg="#333333")
                name_row.pack(anchor="w", pady=1)

                tk.Label(name_row, text="Name:", bg="#333333", fg="white", font=("Helvetica", 9)).pack(side="left",
                                                                                                       padx=(2, 4))
                name_entry = tk.Entry(name_row, width=18, font=("Helvetica", 9))
                name_entry.pack(side="left")

                AutocompleteEntry(
                    entry=name_entry,
                    all_names=self.all_pokemon_names,
                    on_select=lambda name, s=idx: self._on_pokemon_selected(s, name)
                )

                # Level-Zeile
                level_row = tk.Frame(input_frame, bg="#333333")
                level_row.pack(anchor="w", pady=1)

                tk.Label(level_row, text="Level:  ", bg="#333333", fg="white", font=("Helvetica", 9)).pack(side="left",
                                                                                                         padx=(2, 4))
                level_entry = tk.Entry(level_row, width=5, font=("Helvetica", 9))
                level_entry.pack(side="left", padx=(0, 4))

                tk.Button(
                    level_row, text="Suchen",
                    command=lambda s=idx: self.change_pokemon(s),
                    font=("Helvetica", 8)
                ).pack(side="left",anchor="w", pady=1, padx=(0, 4))

                save_btn = tk.Button(
                    level_row, text="💾",
                    command=lambda s=idx: self.save_single_pokemon(s),
                    bg="#447744", fg="white", font=("Helvetica", 8), width=3
                )
                save_btn.pack(side="left")
                self.save_buttons.append(save_btn)

                self.name_entries.append(name_entry)
                self.level_entries.append(level_entry)

                # ---- RECHTE SPALTE: BILD ----
                img_label = tk.Label(frame, bg="#333333")
                img_label.grid(row=0, column=1, sticky="ne", padx=5, pady=5)
                self.img_labels.append(img_label)

                # --- ZEILE 1: Trennlinie (leer, aber mit Höhe) ---
                separator = tk.Frame(frame, bg="#222222", height=2)
                separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

                # --- ZEILE 2: STATS (Moves, Strengths, Weaknesses) ---
                stats_label = tk.Label(
                    frame,
                    text="",
                    bg="#333333",
                    fg="lightgray",
                    justify="left",
                    anchor="nw",
                    font=("Helvetica", 9),
                    wraplength=250
                )
                stats_label.grid(row=2, column=0, columnspan=2, sticky="nw", padx=5, pady=5)
                self.stats_labels.append(stats_label)

        # AI-Advisor Input Frame
        self.advice_input_frame = tk.Frame(self.root, bg="#333333", height=30)
        self.advice_input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=0)
        self.advice_input_frame.grid_propagate(False)
        self.advice_input_frame.pack_propagate(False)
        self.advice_input_frame.grid_remove()

        self.advice_entry = tk.Entry(self.advice_input_frame, font=("Arial", 12), bg="#333333", fg="white")
        self.advice_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Enter-Taste binden
        def on_enter(event):
            if not (event.state & 0x0001):  # Shift nicht gedrückt
                self.ask_ai_advisor()
                return "break"

        self.advice_entry.bind("<Return>", on_enter)

        # Antwortfeld (ScrolledText)
        self.advice_frame = tk.Frame(self.root, bg="#222222", height=50)
        self.advice_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.advice_frame.pack_propagate(False)
        self.advice_frame.grid_propagate(False)
        self.advice_frame.grid_remove()

        self.advice_text = scrolledtext.ScrolledText(
            self.advice_frame,
            wrap="word",
            bg="#222222",
            fg="white",
            font=("Helvetica", 13),
            state="disabled"
        )
        self.advice_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Toggle-Button für AI
        self.toggle_advisor_btn = tk.Button(
            self.root, text="🔍 Prof. Eich (Tipps)",
            command=self.toggle_advisor,
            bg="#4455AA", fg="white", font=("Helvetica", 10),
            padx=10, pady=5
        )
        self.toggle_advisor_btn.place(relx=0.85, rely=1.0, x=-20, y=-20, anchor="se")

        # Team speichern Button
        tk.Button(
            self.root, text="💾 Team speichern",
            command=self.save_team,
            bg="#447744", fg="white", font=("Helvetica", 10),
            padx=10, pady=5
        ).place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

        self.root.bind("<Configure>", self.on_resize)

    # Toggle Advisor-Leiste
    def toggle_advisor(self):
        if self.advice_input_frame.winfo_ismapped():
            self.advice_input_frame.grid_remove()
            self.advice_frame.grid_remove()
            self.set_answer("Team Tipps werden hier angezeigt")

            self.root.rowconfigure(0, weight=1)
            self.root.rowconfigure(1, weight=0)
            self.root.rowconfigure(2, weight=0)
        else:
            self.advice_input_frame.grid()
            self.advice_frame.grid()
            self.set_answer("Stelle eine Frage an Prof. Eich...")
            self.advice_entry.focus_set()

            self.root.rowconfigure(0, weight=3)
            self.root.rowconfigure(1, weight=0)
            self.root.rowconfigure(2, weight=1)

            self.root.update_idletasks()
            self.on_resize(None)

    # AI-Frage stellen
    def ask_ai_advisor(self):
        question = self.advice_entry.get().strip()
        if not question:
            messagebox.showwarning("Leere Frage", "Bitte gib eine Frage ein.")
            return

        self.advice_entry.delete(0, tk.END)

        self.set_answer("💡 Denke nach...")

        def query_ai():
            try:
                team = Team.from_dict_list(self.team_data) if isinstance(self.team_data, list) else self.team_data
                advisor = AIAdvisor(db=self.db, game_version=self.game_version)
                answer = advisor.ask_question(team, question)
            except Exception as e:
                answer = f"Fehler: {e}"

            self.root.after(0, lambda: self.set_answer(answer))

        threading.Thread(target=query_ai, daemon=True).start()

    # Antwort setzen
    def set_answer(self, answer):
        self.advice_text.config(state="normal")
        self.advice_text.delete("1.0", tk.END)
        self.advice_text.insert(tk.END, answer)
        self.advice_text.config(state="disabled")
        self.advice_text.see(tk.END)

    # Pokémon speichern
    def save_single_pokemon(self, slot):
        data = self.team_data[slot]
        if not data:
            messagebox.showwarning("Kein Pokémon", "Es ist kein Pokémon in diesem Slot.")
            return

        name = self.name_entries[slot].get().strip()
        if not name:
            messagebox.showwarning("Name fehlt", "Bitte gib einen Namen ein.")
            return

        try:
            level = int(self.level_entries[slot].get())
        except ValueError:
            level = 100

        data["name"] = name
        data["level"] = level

        messagebox.showinfo("Gespeichert", f" Pokémon '{name}' gespeichert!")

    # Pokémon laden
    def change_pokemon(self, slot):
        def load_data():
            name = self.name_entries[slot].get().strip()
            if not name:
                return
            try:
                level = int(self.level_entries[slot].get())
            except ValueError:
                level = 1

            try:
                pokemon_obj = self.pokemon_service.fetch_pokemon(
                    name=name,
                    level=level,
                    game_version=self.game_version
                )

                # Team-Objekt aktualisieren
                team_pokemon = Pokemon(
                    name=pokemon_obj.name,
                    level=pokemon_obj.level,
                    types=pokemon_obj.types,
                    moves=pokemon_obj.moves,
                    strengths=pokemon_obj.strengths,
                    weaknesses=pokemon_obj.weaknesses,
                    image_path=pokemon_obj.image_path,
                    locations=pokemon_obj.locations
                )

                self.team_data[slot] = team_pokemon.to_dict()

                if len(self.team.pokemon) > slot:
                    self.team.pokemon[slot] = team_pokemon
                else:
                    while len(self.team.pokemon) <= slot:
                        self.team.pokemon.append(None)
                    self.team.pokemon[slot] = team_pokemon

                self.root.after(0, self.update_team_display)

            except ValueError as e:
                self.root.after(0, lambda e=e: self._show_error(slot, str(e)))

        threading.Thread(target=load_data, daemon=True).start()

    def _show_error(self, slot, message):
        self.stats_labels[slot].config(text=f"❌ {message}", fg="red")
        self.img_labels[slot].configure(image="")
        self.img_labels[slot].image = None

    # Update Anzeige
    def update_team_display(self):
        for idx, frame in enumerate(self.team_frames):
            if frame.winfo_width() <= 1 or frame.winfo_height() <= 1:
                continue

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
                frame_height = frame.winfo_height()

                # --- SKALIERUNG FÜR BILD ---
                max_img_width = int(frame_width * 0.3 * 0.8)  # 30% Breite * 80%
                max_img_height = int(frame_height * 0.3)  # 30% der Gesamthöhe für Zeile 0

                img_ratio = img.width / img.height

                # Berechne neue Größe
                if img_ratio > 1:  # Breitformat → begrenze Breite
                    new_width = min(max_img_width, img.width)
                    new_height = int(new_width / img_ratio)
                else:  # Hochformat → begrenze Höhe
                    new_height = min(max_img_height, img.height)
                    new_width = int(new_height * img_ratio)

                # Falls zu hoch → korrigiere
                if new_height > max_img_height:
                    new_height = max_img_height
                    new_width = int(new_height * img_ratio)

                # Skalieren
                img_resized = img.resize((new_width, new_height), Image.LANCZOS)

                # Optional: Kleiner Rand
                img_padded = Image.new("RGBA", (new_width + 10, new_height + 10), (0, 0, 0, 0))
                img_padded.paste(img_resized, (5, 5))
                img_resized = img_padded

                img_tk = ImageTk.PhotoImage(img_resized)
                img_label = self.img_labels[idx]
                img_label.configure(image=img_tk)
                img_label.image = img_tk

                strengths = data.get("strengths", [])
                weaknesses = data.get("weaknesses", [])
                stats_text = (
                    f"Level: {data.get('level', 100)}\n"
                    f"Typen: {', '.join(data['types'])}\n"
                    f"Moves: {', '.join(data['moves'])}\n"
                    f"Strengths: {', '.join(strengths) if strengths else '-'}\n"
                    f"Weaknesses: {', '.join(weaknesses) if weaknesses else '-'}"
                )
                stats_label.config(text=stats_text, anchor="nw", justify="left")
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

    def on_close(self):
        """Wird beim Schließen des Fensters aufgerufen."""
        if any(self.team_data):
            if tk.messagebox.askyesno("Team speichern?", "Möchtest du dein aktuelles Team speichern, bevor das Fenster geschlossen wird?"):
                self.save_team()
        self.root.destroy()

    def switch_team(self, new_team):
        """Wechselt zu einem neuen Team und fragt vorher, ob das aktuelle Team gespeichert werden soll."""
        if any(self.team_data):
            if tk.messagebox.askyesno("Team speichern", "Möchtest du dein aktuelles Team speichern, bevor das Team gewechselt wird?"):
                self.save_team()
        self.load_team_data(new_team)
        self.update_team_display()

    def load_team_data(self, team):
        """Füllt die Team-Slots mit einem geladenen Team_Objekt."""
        for idx, p in enumerate(team.pokemon):
            if p:
                self.team_data[idx] = {
                    "name": p.name,
                    "level": p.level,
                    "types": p.types,
                    "moves": p.moves,
                    "image_path": p.image_path,
                    "strengths": getattr(p, "strengths", []),
                    "weaknesses": getattr(p, "weaknesses", []),
                }
                self.name_entries[idx].delete(0, tk.END)
                self.name_entries[idx].insert(0, p.name)
                self.level_entries[idx].delete(0, tk.END)
                self.level_entries[idx].insert(0, str(p.level))

    # Team speichern
    def save_team(self):
        team_name = tkinter.simpledialog.askstring("Team speichern", "Name des Teams:")
        if not team_name:
            return

        self.team.name = team_name
        success = self.team.save_to_file(team_name)
        if success:
            tkinter.messagebox.showinfo("Gespeichert", f"Team '{team_name}' wurde gespeichert!")
        else:
            tkinter.messagebox.showerror("Fehler", f"Speichern fehlgeschlagen für Team '{team_name}'!")

    def _on_pokemon_selected(self, slot, name):
        """Wird aufgerufen, wenn ein Name per Autocomplete ausgewählt wurde."""
        self.name_entries[slot].delete(0, "end")
        self.name_entries[slot].insert(0, name)



class AutocompleteEntry:
    def __init__(self, entry, all_names, on_select=None):
        self.entry = entry
        self.all_names = all_names
        self.on_select = on_select
        self.listbox = None
        self.window = None

        self.entry.bind("<KeyRelease>", self.on_keyrelease)
        self.entry.bind("<FocusOut>", self.on_focusout)
        self.entry.bind("<Return>", self.on_return)

    def on_keyrelease(self, event):
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return

        value = self.entry.get().strip().lower()
        if len(value) < 1:  # Mindestens 1 Buchstabe
            self.hide_list()
            return

        matches = [name for name in self.all_names if name.startswith(value)]
        if matches:
            self.show_list(matches[:10])
        else:
            self.hide_list()

    def show_list(self, matches):
        self.hide_list()

        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = max(self.entry.winfo_width(), 120)  # Mindestbreite

        self.window = tk.Toplevel(self.entry)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"{width}x{min(len(matches) * 20, 200)}+{x}+{y}")
        self.window.wm_attributes("-topmost", True)
        # Wichtig: Kein Fokus auf das Fenster!
        self.window.bind("<FocusOut>", self.on_list_focusout)

        self.listbox = tk.Listbox(
            self.window,
            bg="#333333",
            fg="white",
            selectbackground="#5555AA",
            activestyle="none",
            font=("Helvetica", 10),
            takefocus=False  # ← verhindert Fokus-Diebstahl
        )
        self.listbox.pack(fill="both", expand=True)

        for name in matches:
            self.listbox.insert("end", name.title())

        self.listbox.bind("<ButtonRelease-1>", self.on_list_click)
        self.listbox.bind("<Return>", self.on_list_select)
        self.listbox.bind("<Up>", self.on_arrow_key)
        self.listbox.bind("<Down>", self.on_arrow_key)
        self.listbox.selection_set(0)
        # NICHT: self.listbox.focus() ← das stiehlt den Fokus!

    def hide_list(self):
        if self.window:
            self.window.destroy()
            self.window = None
            self.listbox = None

    def on_list_click(self, event):
        self.select_item()

    def on_return(self, event):
        if self.listbox and self.listbox.curselection():
            self.select_item()
            return "break"

    def on_list_select(self, event):
        self.select_item()

    def on_arrow_key(self, event):
        if not self.listbox:
            return
        sel = self.listbox.curselection()
        index = sel[0] if sel else 0
        if event.keysym == "Up" and index > 0:
            index -= 1
        elif event.keysym == "Down" and index < self.listbox.size() - 1:
            index += 1
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        return "break"

    def select_item(self):
        if self.listbox and self.listbox.curselection():
            selection = self.listbox.get(self.listbox.curselection())
            self.entry.delete(0, "end")
            self.entry.insert(0, selection)
            if self.on_select:
                self.on_select(selection)
        self.hide_list()
        self.entry.focus_set()  # Fokus zurück zum Entry

    def on_focusout(self, event):
        # Verzögerung, um Klick auf Listbox zu erkennen
        self.entry.after(150, self.check_focus)

    def on_list_focusout(self, event):
        # Wenn das Dropdown den Fokus verliert, prüfen
        self.entry.after(150, self.check_focus)

    def check_focus(self):
        if not self.window:
            return
        # Prüfe, ob Fokus noch im Entry oder im Dropdown ist
        current_focus = self.entry.focus_get()
        if current_focus == self.entry or (self.listbox and current_focus == self.listbox):
            return  # Alles gut – nicht schließen
        # Sonst: schließen
        self.hide_list()