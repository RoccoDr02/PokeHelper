# main.py
import tkinter as tk
from core.database import Database
from core.pokemon_service import PokemonService
from start_screen import StartScreen
from team_editor import TeamEditor

def main():
    # Initialisiere DB und Service
    db = Database("all_pokedex.db")
    pokemon_service = PokemonService(db)

    root = tk.Tk()

    def start_new_team(game_version):
        for widget in root.winfo_children():
            widget.destroy()
        # Übergib den Service an den Editor!
        TeamEditor(root, game_version, pokemon_service, db=db)

    def load_existing_team(team_obj, game_version):
        for widget in root.winfo_children():
            widget.destroy()
        # Übergibt das geladene Team an den Editor
        TeamEditor(root, game_version, pokemon_service, db=db, team=team_obj)

    StartScreen(
        root,
        on_create_team=start_new_team,
        on_load_team=load_existing_team
    )
    root.mainloop()

if __name__ == "__main__":
    main()