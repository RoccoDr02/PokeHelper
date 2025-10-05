import tkinter as tk
from tkinter import messagebox, simpledialog
from core.database import Database
from models.team import Team

class StartScreen:
    def __init__(self, root, on_create_team, on_load_team):
        self.root = root
        self.db = Database("all_pokedex.db")
        self.on_create_team = on_create_team
        self.setup_ui()
        self.on_load_team = on_load_team

        self.versions = self.db.get_all_game_versions()

        self.create_version_selector()

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


        tk.Button(
            self.root, text="✨ Neues Team erstellen",
            command=self._create_new_team,
            bg="#558855", fg="white", font=("Helvetica", 12, "bold"),
            padx=20, pady=8
        ).pack(pady=20)

        tk.Button(
            self.root, text="Team laden",
            command=self._load_existing_team,
            bg="#558855", fg="white", font=("Helvetica", 12, "bold"),
            padx=20, pady=8
        ).pack(pady=20)

    def create_version_selector(self):
        tk.Label(self.root, text="Wähle eine Spielversion:").pack(pady=10)

        self.version_var = tk.StringVar(value=self.versions[0] if self.versions else "platinum")
        versions_menu = tk.OptionMenu(self.root, self.version_var, *self.versions)
        versions_menu.pack(pady=5)

    def _create_new_team(self):
        version = self.version_var.get()
        self.on_create_team(version)

    def _load_existing_team(self):
        version = self.version_var.get()

        # Liste aller gespeicherten Teams abrufen
        saved_teams = Team.list_saved_teams()
        if not saved_teams:
            messagebox.showinfo("Keine Teams", "Es sind keine gespeicherten Teams vorhanden.")
            return

        # Auswahldialog
        selected_team = simpledialog.askstring(
            "Team laden",
            "Welches Team möchtest du laden?\n" + "\n".join(saved_teams)
        )

        if not selected_team:
            return  # Abbruch

        if selected_team not in saved_teams:
            messagebox.showerror("Fehler", f"Team '{selected_team}' existiert nicht.")
            return

        try:
            team_obj = Team.load_from_file(selected_team)
            self.on_load_team(team_obj, version)
        except Exception as e:
            messagebox.showerror("Fehler beim Laden", str(e))