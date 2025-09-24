import tkinter as tk
from start_screen import StartScreen
from team_editor import TeamEditor  # dein umgebauter Team-Editor als Klasse

def main():
    root = tk.Tk()

    def start_new_team(game_version):
        # Alles im Fenster löschen
        for widget in root.winfo_children():
            widget.destroy()
        # TeamEditor starten
        TeamEditor(root, game_version)

    # StartScreen mit Callback
    StartScreen(root, on_create_team=lambda version: print("Starte Team mit:", version))
    root.mainloop()

if __name__ == "__main__":
    main()