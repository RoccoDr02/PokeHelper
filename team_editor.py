# ===== TEAM-EDITOR (dein alter Code, jetzt als Klasse) =====
class TeamEditor:
    def __init__(self, root, game_version):
        self.root = root
        self.game_version = game_version  # ← wird später für Moves genutzt!
        self.team_data = [None] * 6
        self.resize_job = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title(f"Pokémon Team – {self.game_version.title()}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#333333")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # ... (hier kommt dein gesamter UI-Code ab "team_container = tk.Frame..." bis zum Ende der Schleife)
        # WICHTIG: überall "root" → "self.root", "team_data" → "self.team_data"
        # Und bei Buttons: command=lambda s=idx: self.change_pokemon(s)

        self.root.bind("<Configure>", self.on_resize)

    # Alle deine Funktionen hierhin – mit "self" als erstem Parameter
    def get_pokemon_data(self, name, level=100):
        data = self._get_pokemon_from_db(name)
        if not data:
            return None

        # Typen extrahieren
        types = [t["type"]["name"] for t in data["types"]]

        # 🔥 Lokaler Bildpfad statt API
        image_path = os.path.join("pokemon_images", f"{name.lower()}.png")
        if not os.path.exists(image_path):
            image_path = None  # Fallback: kein Bild

            # Moves wie zuvor aus raw_data extrahieren (mit self.game_version)
            moves = []
            for move_entry in data["moves"]:
                for detail in move_entry["version_group_details"]:
                    if (detail["version_group"]["name"] == self.game_version and
                            detail["move_learn_method"]["name"] == "level-up" and
                            detail["level_learned_at"] <= level):
                        moves.append(move_entry["move"]["name"])
                        break

        return {
            "name": data["name"],
            "types": types,
            "moves": moves,
            "image": img_path
        }

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
                strengths, weaknesses = self.get_type_relations(data['types'])
                data['strengths'] = strengths
                data['weaknesses'] = weaknesses
                self.team_data[slot] = data
                self.root.after(0, self.update_team_display)
        threading.Thread(target=load_data).start()

    # ... (alle anderen Methoden: update_team_display, on_resize, etc. – mit self.)