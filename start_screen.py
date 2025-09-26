import tkinter as tk

class StartScreen:
    def __init__(self, root, on_create_team, on_load_team):
        self.root = root
        self.on_create_team = on_create_team
        self.setup_ui()
        self.on_load_team = on_load_team

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
        versions = ["platinum", "diamond", "pearl", "scarlet", "violet", "sword", "shield", "black-2-white-2"]
        tk.OptionMenu(self.root, self.version_var, *versions).pack(pady=10)

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

    def _create_new_team(self):
        version = self.version_var.get()
        self.on_create_team(version)

    def _load_existing_team(self):
        version = self.version_var.get()
        self.on_load_team(version)