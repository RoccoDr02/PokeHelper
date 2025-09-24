# start_screen.py
import tkinter as tk
from tkinter import messagebox

class StartScreen:
    def __init__(self, root, on_create_team):
        """
        :param root: Haupt-Tk-Fenster
        :param on_create_team: Callback-Funktion, die aufgerufen wird, wenn ein neues Team erstellt wird
        """
        self.root = root
        self.on_create_team = on_create_team
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Pokémon Team Builder")
        self.root.geometry("600x450")
        self.root.configure(bg="#222222")
        self.root.resizable(True, True)

        # Titel
        title_label = tk.Label(
            self.root,
            text="Willkommen zum Pokémon Team Builder!",
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#222222"
        )
        title_label.pack(pady=30)

        # Spielversion-Auswahl
        version_frame = tk.Frame(self.root, bg="#222222")
        version_frame.pack(pady=10)

        tk.Label(
            version_frame,
            text="Wähle deine Spielversion:",
            font=("Helvetica", 12),
            fg="white",
            bg="#222222"
        ).pack()

        self.version_var = tk.StringVar(value="platinum")
        versions = [
            "platinum", "diamond", "pearl",
            "scarlet", "violet",
            "sword", "shield",
            "brilliant-diamond", "shining-pearl"
        ]
        version_menu = tk.OptionMenu(version_frame, self.version_var, *versions)
        version_menu.config(
            width=20,
            bg="#444444",
            fg="white",
            activebackground="#555555",
            activeforeground="white"
        )
        version_menu.pack(pady=10)

        # Buttons
        button_frame = tk.Frame(self.root, bg="#222222")
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="✨ Neues Team erstellen",
            command=self._create_new_team,
            bg="#558855",
            fg="white",
            font=("Helvetica", 12, "bold"),
            padx=20,
            pady=8,
            relief="flat"
        ).pack(pady=8)

        tk.Button(
            button_frame,
            text="📂 Team laden",
            command=self._load_team,
            bg="#555588",
            fg="white",
            font=("Helvetica", 12),
            padx=20,
            pady=8,
            relief="flat",
            state="disabled"  # Aktiviere später, wenn DB fertig ist
        ).pack(pady=8)

        # Hinweis
        hint = tk.Label(
            self.root,
            text="Hinweis: Die Spielversion beeinflusst verfügbare Moves und Fundorte.",
            font=("Helvetica", 9),
            fg="#aaaaaa",
            bg="#222222",
            wraplength=500
        )
        hint.pack(pady=20)

    def _create_new_team(self):
        version = self.version_var.get()
        self.on_create_team(version)

    def _load_team(self):
        messagebox.showinfo("Hinweis", "Team-Laden wird in Kürze verfügbar sein.")
        # Später: Öffne Dropdown mit gespeicherten Teams aus DB