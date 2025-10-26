# team_editor.py
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import threading
import os
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
from tkinter import ttk
from core.ai_advisor import AIAdvisor
from models.team import Team, Pokemon
from core.pokemon_service import PokemonService


class TeamEditor:
    def __init__(self, root, game_version, pokemon_service: PokemonService, db, team=None, ai_advisor=None):
        self.root = root
        self.db = db
        self.pokemon_service = pokemon_service
        self.menu_width = 180
        self.menu_open = False

        # Team setzen
        if team:
            self.team = team
            self.game_version = team.game_version
            self.team_data = [p.to_dict() if p else None for p in team.pokemon]
            while len(self.team_data) < 6:
                self.team_data.append(None)
        else:
            self.game_version = game_version
            self.team = Team(name="Unbenanntes Team", game_version=self.game_version)
            self.team_data = [None] * 6

        self.all_pokemon_names = [
            name.lower() for name in self.pokemon_service.get_all_pokemon_names()
        ]

        self.resize_job = None
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.update_team_display)
        self.root.after(150, self.actually_resize)

    def setup_ui(self):
        self.root.title(f"Pokémon Team – {self.game_version.title()}")
        self.root.geometry("1400x900")
        self.root.configure(bg="#333333")

        # === GRID: Zwei Spalten (Menü + Team) ===
        self.root.columnconfigure(0, weight=0)  # Menü: feste Breite
        self.root.columnconfigure(1, weight=1)  # Team: dehnbar
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)  # AI-Eingabe
        self.root.rowconfigure(2, weight=0)  # AI-Antwort

        # === MENÜ-TOGGLE-BUTTON (oben links im Menü-Bereich) ===
        self.toggle_menu_btn = tk.Button(
            self.root,
            text="☰ Menü",
            command=self.toggle_menu,
            bg="#2a2a2a",
            fg="white",
            font=("Helvetica", 10, "bold"),
            padx=10,
            pady=5
        )
        self.toggle_menu_btn.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        # === MENÜFRAME (Spalte 0, unter dem Button) ===
        self.menu_frame = tk.Frame(self.root, bg="#2a2a2a", width=self.menu_width)
        self.menu_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=(50, 10))
        self.menu_frame.grid_propagate(False)
        self.menu_frame.grid_remove()  # Versteckt bis geöffnet

        # === TEAM CONTAINER (Spalte 1) ===
        self.team_container = tk.Frame(self.root, bg="#333333", height=820)
        self.team_container.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.team_container.grid_propagate(False)
        for r in range(2):
            self.team_container.rowconfigure(r, weight=1)
        for c in range(3):
            self.team_container.columnconfigure(c, weight=1)

        self.team_frames = []
        self.img_labels = []
        self.name_entries = []
        self.level_entries = []
        self.stats_labels = []

        for i in range(2):
            for j in range(3):
                idx = i * 3 + j
                frame = tk.Frame(self.team_container, bg="#333333", bd=2, relief="raised")
                frame.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                frame.grid_propagate(False)
                frame.rowconfigure(0, weight=1)
                frame.rowconfigure(1, weight=0)
                frame.rowconfigure(2, weight=2)
                frame.columnconfigure(0, weight=7)
                frame.columnconfigure(1, weight=3)

                self.team_frames.append(frame)

                input_frame = tk.Frame(frame, bg="#333333")
                input_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

                name_row = tk.Frame(input_frame, bg="#333333")
                name_row.pack(anchor="w", pady=1)
                tk.Label(name_row, text="Name:", bg="#333333", fg="white", font=("Helvetica", 9)).pack(side="left", padx=(2, 4))
                name_entry = tk.Entry(name_row, width=12, font=("Helvetica", 10))
                name_entry.pack(side="left")
                AutocompleteEntry(
                    entry=name_entry,
                    all_names=self.all_pokemon_names,
                    on_select=lambda name, s=idx: self._on_pokemon_selected(s, name)
                )

                level_row = tk.Frame(input_frame, bg="#333333")
                level_row.pack(anchor="w", pady=1)
                tk.Label(level_row, text="Level: ", bg="#333333", fg="white", font=("Helvetica", 10)).pack(side="left", padx=(2, 4))
                level_entry = tk.Entry(level_row, width=5, font=("Helvetica", 9))
                level_entry.pack(side="left", padx=(0, 4))
                tk.Button(
                    level_row, text="Suchen",
                    command=lambda s=idx: self.change_pokemon(s),
                    font=("Helvetica", 8)
                ).pack(side="left", padx=(0, 4))

                tk.Button(
                    input_frame,
                    text="Details",
                    font=("Helvetica", 8),
                    command=lambda s=idx: self.show_pokemon_details(s)
                ).pack(side="left", padx=(0, 4))

                self.name_entries.append(name_entry)
                self.level_entries.append(level_entry)

                img_label = tk.Label(frame, bg="#333333")
                img_label.grid(row=0, column=1, sticky="ne", padx=5, pady=5)
                self.img_labels.append(img_label)

                separator = tk.Frame(frame, bg="#222222", height=2)
                separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

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

        # === AI ADVISOR BEREICH (nur in Spalte 1) ===
        self.advice_input_frame = tk.Frame(self.root, bg="#333333", height=40)
        self.advice_input_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=(10, 5))
        self.advice_input_frame.grid_propagate(False)
        self.advice_input_frame.grid_remove()

        self.advice_entry = tk.Entry(self.advice_input_frame, font=("Arial", 12), bg="#333333", fg="white")
        self.advice_entry.pack(side="left", fill="x", expand=True, padx=5)

        def on_enter(event):
            if not (event.state & 0x0001):
                self.ask_ai_advisor()
                return "break"
        self.advice_entry.bind("<Return>", on_enter)

        self.advice_frame = tk.Frame(self.root, bg="#222222", height=160)
        self.advice_frame.grid(row=2, column=1, sticky="sew", padx=10, pady=(5, 15))
        self.advice_frame.grid_propagate(False)
        self.advice_frame.grid_remove()

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("Dark.Vertical.TScrollbar", background="#444444", troughcolor="#222222", darkcolor="#333333", lightcolor="#555555", arrowcolor="#FFFFFF", bordercolor="#222222", width=12)
        style.map("Dark.Vertical.TScrollbar", background=[("active", "#555555"), ("pressed", "#666666")], arrowcolor=[("active", "#FFFFFF"), ("pressed", "#CCCCCC")])

        self.advice_frame.columnconfigure(0, weight=1)
        self.advice_frame.rowconfigure(0, weight=1)

        self.advice_text = tk.Text(
            self.advice_frame, wrap="word", bg="#222222", fg="white", font=("Helvetica", 13),
            bd=0, padx=12, pady=12, insertbackground="white", state="disabled"
        )
        scrollbar = ttk.Scrollbar(self.advice_frame, orient="vertical", command=self.advice_text.yview, style="Dark.Vertical.TScrollbar")
        self.advice_text.configure(yscrollcommand=scrollbar.set)
        self.advice_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.root.bind("<Configure>", self.on_resize)

    # === MENÜ-FUNKTIONEN ===
    def toggle_menu(self):
        if self.menu_open:
            self.menu_frame.grid_remove()
            self.menu_open = False
            self.toggle_menu_btn.config(text="☰ Menü")
        else:
            self.menu_frame.grid()
            self.menu_open = True
            self.toggle_menu_btn.config(text="✕ Schließen")

        if not hasattr(self, '_menu_buttons_created'):
            tk.Button(self.menu_frame, text="➕ Neues Team", command=self.new_team, bg="#555555", fg="white", font=("Helvetica", 10), pady=5).pack(fill="x", pady=2)
            tk.Button(self.menu_frame, text="📂 Team laden", command=self.load_team, bg="#555555", fg="white", font=("Helvetica", 10), pady=5).pack(fill="x", pady=2)
            tk.Button(self.menu_frame, text="💾 Team speichern", command=self.save_team, bg="#555555", fg="white", font=("Helvetica", 10), pady=5).pack(fill="x", pady=2)
            tk.Button(self.menu_frame, text="🔍 Prof. Eich", command=self.toggle_advisor, bg="#555555", fg="white", font=("Helvetica", 10), pady=5).pack(fill="x", pady=2)
            tk.Button(self.menu_frame, text="⚙️ Einstellungen", command=self.open_settings, bg="#555555", fg="white", font=("Helvetica", 10), pady=5).pack(fill="x", pady=2)
            tk.Label(self.menu_frame, text="", bg="#2a2a2a").pack(expand=True)
            tk.Button(self.menu_frame, text="❓ Hilfe", command=self.show_help, bg="#444444", fg="lightgray", font=("Helvetica", 9), pady=3).pack(side="bottom", fill="x", pady=5)
            self._menu_buttons_created = True

    def new_team(self):
        # Optional: Aktuelles Team speichern?
        if any(p is not None for p in self.team_data):
            if not messagebox.askyesno("Neues Team", "Möchtest du das aktuelle Team verwerfen?"):
                return

        # Lade die Versionen AUS DER DATENBANK
        try:
            versions = self.db.get_all_game_versions()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Spielversionen nicht laden:\n{e}")
            return

        # Sicherstellen, dass mindestens eine Version vorhanden ist
        if not versions:
            versions = ["platinum"]

        # Erstelle ein neues Fenster für die Versionsauswahl
        dialog = tk.Toplevel(self.root)
        dialog.title("Neues Team – Spielversion")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.configure(bg="#333333")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Wähle eine Spielversion:",
            bg="#333333",
            fg="white",
            font=("Helvetica", 10)
        ).pack(pady=10)

        version_var = tk.StringVar(value=versions[0])

        version_menu = tk.OptionMenu(dialog, version_var, *versions)
        version_menu.config(bg="#444444", fg="white", width=20)
        version_menu.pack(pady=5)

        def confirm():
            selected_version = version_var.get()
            dialog.destroy()
            self._create_new_team_with_version(selected_version)

        tk.Button(
            dialog,
            text="OK",
            command=confirm,
            bg="#447744",
            fg="white",
            font=("Helvetica", 10),
            padx=10,
            pady=5
        ).pack(pady=10)

    def load_team(self):
        """Lädt ein gespeichertes Team und übernimmt dessen Spielversion."""
        saved_teams = Team.list_saved_teams()
        if not saved_teams:
            messagebox.showinfo("Keine Teams", "Es sind keine gespeicherten Teams vorhanden.")
            return

        team_list_text = "\n".join(saved_teams)
        selected_team = simpledialog.askstring(
            "Team laden",
            f"Welches Team möchtest du laden?\n\nGespeicherte Teams:\n{team_list_text}"
        )

        if not selected_team:
            return

        if selected_team not in saved_teams:
            messagebox.showerror("Fehler", f"Team '{selected_team}' existiert nicht.")
            return

        try:
            team_obj = Team.load_from_file(selected_team)
            self.switch_team(team_obj)
        except Exception as e:
            messagebox.showerror("Fehler beim Laden", str(e))

    def open_settings(self):
        messagebox.showinfo("Einstellungen", "Keine Einstellungen verfügbar.")

    def show_help(self):
        messagebox.showinfo("Hilfe", (
            "• Gib einen Pokémon-Namen ein und drücke 'Suchen'\n"
            "• Nutze Prof. Eich für Tipps zu deinem Team\n"
        ))

    # === BESTEHENDE METHODEN ===
    def toggle_advisor(self):
        if self.advice_input_frame.winfo_ismapped():
            self.advice_input_frame.grid_remove()
            self.advice_frame.grid_remove()
            self.root.rowconfigure(0, weight=1)
            self.root.rowconfigure(1, weight=0)
            self.root.rowconfigure(2, weight=0)
            self.set_answer("Team Tipps werden hier angezeigt")
        else:
            self.advice_input_frame.grid()
            self.advice_frame.grid()
            self.set_answer("Stelle eine Frage an Prof. Eich...")
            self.advice_entry.focus_set()
            self.root.rowconfigure(0, weight=2)
            self.root.rowconfigure(1, weight=0)
            self.root.rowconfigure(2, weight=1)
            self.root.update_idletasks()
            self.on_resize(None)

    def ask_ai_advisor(self):
        question = self.advice_entry.get().strip()
        if not question:
            messagebox.showwarning("Leere Frage", "Bitte gib eine Frage ein.")
            return
        self.advice_entry.delete(0, tk.END)
        self.set_answer("💡 Denke nach...")

        def query_ai():
            try:
                team = Team.from_dict_list(self.team_data)
                advisor = AIAdvisor(db=self.db, game_version=self.game_version)
                answer = advisor.ask_question(team, question)
            except Exception as e:
                answer = f"Fehler: {e}"
            self.root.after(0, lambda: self.set_answer(answer))

        threading.Thread(target=query_ai, daemon=True).start()

    def set_answer(self, response: str):
        self.advice_text.configure(state="normal")
        self.advice_text.delete("1.0", tk.END)
        self.advice_text.insert(tk.END, response)
        self.advice_text.yview_moveto(0.0)
        self.advice_text.configure(state="disabled")

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
                # Pokémon vom Service holen (berechnet alles: types, strengths, weaknesses)
                pokemon_obj = self.pokemon_service.fetch_pokemon(
                    name=name, level=level, game_version=self.game_version
                )

                # Team-Daten speichern
                self.team_data[slot] = pokemon_obj.to_dict()

                # Team-Objekt aktualisieren
                if len(self.team.pokemon) > slot:
                    self.team.pokemon[slot] = pokemon_obj
                else:
                    while len(self.team.pokemon) <= slot:
                        self.team.pokemon.append(None)
                    self.team.pokemon[slot] = pokemon_obj

                self.root.after(0, self.update_team_display)
                self.root.after(500, lambda: self.team.auto_save())

            except Exception as e:
                self.root.after(0, lambda e=e: self._show_error(slot, str(e)))

        threading.Thread(target=load_data, daemon=True).start()

    def _show_error(self, slot, message):
        self.stats_labels[slot].config(text=f"❌ {message}", fg="red")
        self.img_labels[slot].configure(image="")
        self.img_labels[slot].image = None

    # === Anzeige aktualisieren ===
    def update_team_display(self):
        for idx, frame in enumerate(self.team_frames):
            if frame.winfo_width() <= 1 or frame.winfo_height() <= 1:
                continue
            data = self.team_data[idx]
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
                max_img_width = int(frame_width * 0.3 * 0.8)
                max_img_height = int(frame_height * 0.5)
                img_ratio = img.width / img.height
                if img_ratio > 1:
                    new_width = min(max_img_width, img.width)
                    new_height = int(new_width / img_ratio)
                else:
                    new_height = min(max_img_height, img.height)
                    new_width = int(new_height * img_ratio)
                if new_height > max_img_height:
                    new_height = max_img_height
                    new_width = int(new_height * img_ratio)
                img_resized = img.resize((new_width, new_height), Image.LANCZOS)
                img_padded = Image.new("RGBA", (new_width + 10, new_height + 10), (0, 0, 0, 0))
                img_padded.paste(img_resized, (5, 5))
                img_tk = ImageTk.PhotoImage(img_padded)
                self.img_labels[idx].configure(image=img_tk)
                self.img_labels[idx].image = img_tk

                # Typen, Stärken, Schwächen direkt aus dem Dictionary
                types = [t.title() for t in data.get("types", [])]
                strengths = [s.title() for s in data.get("strengths", [])]
                weaknesses = [w.title() for w in data.get("weaknesses", [])]
                moves = [str(m).title() for m in data.get("moves", [])]
                stats_text = (
                    f"Level: {data.get('level', 100)}\n"
                    f"Typen: {', '.join(types)}\n"
                    f"Moves: {', '.join(moves)}\n"
                    f"Strengths: {', '.join(strengths) if strengths else '-'}\n"
                    f"Weaknesses: {', '.join(weaknesses) if weaknesses else '-'}"
                )
                self.stats_labels[idx].config(text=stats_text, anchor="nw", justify="left")
                self.update_text_font(self.stats_labels[idx], frame)
            else:
                self.img_labels[idx].configure(image="")
                self.img_labels[idx].image = None
                self.stats_labels[idx].config(text="")

    def update_text_font(self, label, frame):
        text_height = int(frame.winfo_height() * 0.55)
        size = max(8, min(12, int(text_height / 20)))
        font = tkFont.Font(family="Helvetica", size=size)
        label.config(font=font)

    def actually_resize(self):
        for idx, frame in enumerate(self.team_frames):
            self.stats_labels[idx].config(wraplength=int(frame.winfo_width() * 0.9))
        self.update_team_display()

    def on_resize(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(150, self.actually_resize)

    def on_close(self):
        if any(self.team_data):
            if tk.messagebox.askyesno("Team speichern?", "Möchtest du dein aktuelles Team speichern, bevor das Fenster geschlossen wird?"):
                try:
                    self.team.auto_save()
                except Exception as e:
                    tk.messagebox.showerror("Fehler beim Speichern", str(e))
        self.root.destroy()

    def show_pokemon_details(self, slot):
        data = self.team_data[slot]
        if not data:
            tk.messagebox.showinfo("Keine Daten", "Dieses Pokémon ist noch leer.")
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"{data.get('name', 'Unbekannt').title()} – Details")
        popup.geometry("400x500")
        popup.configure(bg="#333333")
        popup.transient(self.root)

        # Typen
        types = [t.title() for t in data.get("types", [])]
        tk.Label(popup, text=f"Typen: {', '.join(types)}", bg="#333333", fg="white",
                 font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        # Stärken / Schwächen
        strengths = [s.title() for s in data.get("strengths", [])]
        weaknesses = [w.title() for w in data.get("weaknesses", [])]
        tk.Label(popup, text=f"Stärken: {', '.join(strengths) if strengths else '-'}", bg="#333333", fg="lightgreen",
                 font=("Helvetica", 10)).pack(anchor="w", padx=10, pady=2)
        tk.Label(popup, text=f"Schwächen: {', '.join(weaknesses) if weaknesses else '-'}", bg="#333333", fg="red",
                 font=("Helvetica", 10)).pack(anchor="w", padx=10, pady=2)

        # Level-Up Moves
        tk.Label(popup, text="Nächste Level-Up Moves:", bg="#333333", fg="white", font=("Helvetica", 12, "bold")).pack(
            anchor="w", padx=10, pady=(10, 0))

        level_up_moves = data.get("level_up_moves", [])
        current_level = data.get("level", 1)

        # Sortiere nach Level
        sorted_moves = sorted(level_up_moves, key=lambda m: m["level"])

        # Nächste 5 Moves, die noch nicht gelernt wurden
        future_moves = [m for m in sorted(level_up_moves, key=lambda x: x["level"]) if m["level"] > current_level][:5]

        if future_moves:
            moves_text = "\n".join([f"{m['name'].title()} – Level {m['level']}" for m in future_moves])
        else:
            moves_text = "Keine Level-Up-Moves mehr verfügbar."

        tk.Label(popup, text=moves_text, bg="#333333", fg="lightgray", justify="left", font=("Helvetica", 10)).pack(
            anchor="w", padx=20)

        # Fundorte
        locations = data.get("locations", [])
        tk.Label(popup, text=f"Fundorte: {', '.join(locations) if locations else '-'}", bg="#333333", fg="lightblue",
                 justify="left", font=("Helvetica", 10)).pack(anchor="w", padx=10, pady=10)


    def switch_team(self, new_team):
        """Wechselt zu einem neuen Team und übernimmt dessen Spielversion."""
        if any(p is not None for p in self.team_data):
            if messagebox.askyesno("Team speichern",
                                   "Möchtest du dein aktuelles Team speichern, bevor das Team gewechselt wird?"):
                self.team.auto_save()

        # 🔥 Spielversion sofort aktualisieren
        self.game_version = new_team.game_version
        self.team = new_team
        self.load_team_data(new_team)
        self.update_team_display()

        # Optional: Fenstertitel aktualisieren
        self.root.title(f"Pokémon Team – {self.game_version.title()}")

    def load_team_data(self, team):
        for idx, p in enumerate(team.pokemon):
            if p:
                self.team_data[idx] = {
                    "name": p.name,
                    "level": p.level,
                    "types": p.types,
                    "strengths": p.strengths,
                    "weaknesses": p.weaknesses
                }
                self.name_entries[idx].delete(0, tk.END)
                self.name_entries[idx].insert(0, p.name)
                self.level_entries[idx].delete(0, tk.END)
                self.level_entries[idx].insert(0, str(p.level))

    def save_team(self):
        team_name = simpledialog.askstring("Team speichern", "Name des Teams:")
        if not team_name:
            return
        self.team.name = team_name
        success = self.team.save_to_file(team_name)
        if success:
            messagebox.showinfo("Gespeichert", f"Team '{team_name}' wurde gespeichert!")
        else:
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen für Team '{team_name}'!")

    def _on_pokemon_selected(self, slot, name):
        self.name_entries[slot].delete(0, "end")
        self.name_entries[slot].insert(0, name)

    def _create_new_team_with_version(self, version):
        """Erstellt ein neues Team mit der gewählten Version."""
        self.team = Team(name="Unbenanntes Team", game_version=version)
        self.game_version = version
        self.team_data = [None] * 6

        # UI leeren
        for entry in self.name_entries:
            entry.delete(0, tk.END)
        for entry in self.level_entries:
            entry.delete(0, tk.END)

        # Fenstertitel aktualisieren
        self.root.title(f"Pokémon Team – {self.game_version.title()}")

        self.update_team_display()


# === AUTOCOMPLETE (unverändert) ===
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
        if len(value) < 1:
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
        width = max(self.entry.winfo_width(), 120)
        self.window = tk.Toplevel(self.entry)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"{width}x{min(len(matches) * 20, 200)}+{x}+{y}")
        self.window.wm_attributes("-topmost", True)
        self.window.bind("<FocusOut>", self.on_list_focusout)
        self.listbox = tk.Listbox(
            self.window,
            bg="#333333",
            fg="white",
            selectbackground="#5555AA",
            activestyle="none",
            font=("Helvetica", 10),
            takefocus=False
        )
        self.listbox.pack(fill="both", expand=True)
        for name in matches:
            self.listbox.insert("end", name.title())
        self.listbox.bind("<ButtonRelease-1>", self.on_list_click)
        self.listbox.bind("<Return>", self.on_list_select)
        self.listbox.bind("<Up>", self.on_arrow_key)
        self.listbox.bind("<Down>", self.on_arrow_key)
        self.listbox.selection_set(0)

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
        self.entry.focus_set()

    def on_focusout(self, event):
        self.entry.after(150, self.check_focus)

    def on_list_focusout(self, event):
        self.entry.after(150, self.check_focus)

    def check_focus(self):
        if not self.window:
            return
        current_focus = self.entry.focus_get()
        if current_focus == self.entry or (self.listbox and current_focus == self.listbox):
            return
        self.hide_list()