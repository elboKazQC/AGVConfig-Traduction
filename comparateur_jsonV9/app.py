import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import json
import subprocess
from functools import partial
from translate import traduire
import re
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('logs/app_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Définition des constantes (couleurs, polices, largeur minimale, etc.)
COL_BG_MAIN      = "#2a2a2a"  # Fond principal plus foncé
COL_BG_TOPBAR    = "#1c1c1c"  # Barre supérieure plus foncée
COL_BG_COLUMN    = "#2a2a2a"  # Colonnes plus foncées
COL_BG_ROW       = "#333333"  # Lignes plus foncées
COL_BG_ROW_ALT   = "#3a3a3a"  # Lignes alternées plus foncées
COL_BG_ROW_HOVER = "#404040"  # Survol plus foncé
COL_FG_TEXT      = "#ffffff"  # Texte blanc
COL_EDIT_BG      = "#404040"  # Fond d'édition plus foncé
COL_EDIT_FG      = "#ffffff"  # Texte d'édition blanc
COL_EDIT_BG_FOCUS = "#505050"  # Fond d'édition avec focus
COL_GREEN        = "#4caf50"  # Vert pour les éléments extensibles
COL_RED          = "#f44336"  # Rouge pour les alertes
COL_AMBER        = "#ffc107"  # Ambre pour les avertissements
COL_HIGHLIGHT    = "#505050"  # Contour de survol plus visible
COL_SEARCH_HIGHLIGHT = "#ffab00"  # Couleur de surbrillance pour la recherche
COL_SEARCH_BG = "#3a3a3a"  # Fond pour la barre de recherche

FONT_DEFAULT = ("Segoe UI", 11)
FONT_TOPBAR  = ("Segoe UI", 12, "bold")
FONT_TITLE   = ("Segoe UI", 14, "bold")

MIN_COL_WIDTH = 400

# Styles pour les alarmes
ALARM_STYLES = {
    "error": {"bg": "#f44336", "fg": "#ffffff"},
    "warning": {"bg": "#ffc107", "fg": "#000000"},
    "info": {"bg": "#2196f3", "fg": "#ffffff"},
    "success": {"bg": "#4caf50", "fg": "#ffffff"}
}

class FaultEditor:
    def __init__(self, root):
        # Créer le dossier logs s'il n'existe pas
        os.makedirs('logs', exist_ok=True)
        logger.info("Démarrage de l'application Fault Editor")
        self.root = root
        self.root.title("Fault Editor - Auto Reload")
        self.root.geometry("1400x800")
        self.lang = "fr"
        self.file_map = {}
        self.data_map = {}
        self.path_map = {}
        self.columns = []  # Liste des colonnes créées
        self.current_path = [0, 255, 255, 255]  # Chemin courant
        self.editing_info = None  # Dictionnaire contenant les infos de l'édition en cours
        self.base_dir = None  # Dossier courant pour les fichiers JSON
        self.search_results = []  # Pour stocker les résultats de recherche
        self.current_search_index = -1  # Index actuel dans les résultats
        self.search_mode = "hierarchical"  # Mode de recherche (hierarchical ou flat)
        self.search_frame = None  # Frame pour la barre de recherche
        self.current_file_path = None  # Chemin du fichier actuellement sélectionné
        # Ne pas charger de dossier par défaut, attendre que l'utilisateur ouvre un dossier
        self.setup_ui()

    def initialize_file_map(self, folder):
        logger.info(f"Initialisation du file_map pour le dossier: {folder}")
        self.file_map.clear()
        for root_dir, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".json"):
                    self.file_map[file] = os.path.join(root_dir, file)
        logger.info(f"Total : {len(self.file_map)} fichiers JSON trouvés dans {folder}")

    def setup_ui(self):
        style = ttk.Style()
        style.configure('TRadiobutton', font=FONT_TOPBAR)
        style.configure('TButton', font=FONT_TOPBAR)

        # Barre supérieure avec logo
        topbar = tk.Frame(self.root, bg=COL_BG_TOPBAR, height=60)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Logo Noovelia
        logo_frame = tk.Frame(topbar, bg=COL_BG_TOPBAR)
        logo_frame.pack(side="left", padx=10)
        logo_label = tk.Label(logo_frame, text="noovelia", font=("Segoe UI", 16), bg=COL_BG_TOPBAR, fg="white")
        logo_label.pack(side="left")

        # Boutons de la barre supérieure
        buttons_frame = tk.Frame(topbar, bg=COL_BG_TOPBAR)
        buttons_frame.pack(side="right", padx=10)

        # Bouton de recherche
        search_btn = tk.Button(buttons_frame, text="🔍 Rechercher",
                              command=lambda: self.show_search(),
                              bg=COL_BG_TOPBAR, fg="white",
                              font=FONT_DEFAULT,
                              relief="flat", padx=10, pady=5)
        search_btn.pack(side="right", padx=(10, 2))

        # Boutons d'ouverture de fichiers
        open_btn = ttk.Button(buttons_frame, text="📂 Ouvrir un dossier", command=self.open_folder)
        open_btn.pack(side="right", padx=2)

        load_flat_btn = ttk.Button(buttons_frame, text="📄 Charger JSON plat", command=self.load_flat_json)
        load_flat_btn.pack(side="right", padx=2)

        # Sélecteur de langue
        lang_frame = tk.Frame(buttons_frame, bg=COL_BG_TOPBAR)
        lang_frame.pack(side="right", padx=10)

        self.lang_var = tk.StringVar(value="fr")
        ttk.Radiobutton(lang_frame, text="FR", value="fr", variable=self.lang_var, command=self.reload_lang).pack(side="left", padx=2)
        ttk.Radiobutton(lang_frame, text="EN", value="en", variable=self.lang_var, command=self.reload_lang).pack(side="left", padx=2)
        ttk.Radiobutton(lang_frame, text="ES", value="es", variable=self.lang_var, command=self.reload_lang).pack(side="left", padx=2)

        # Cadre des outils (pour pouvoir désactiver/activer les boutons)
        self.tools_frame = tk.Frame(self.root, bg="#2a2a2a", height=50)
        self.tools_frame.pack(fill="x", side="top", pady=(0, 5))
        self.tools_frame.pack_propagate(False)

        btn_sync_all = ttk.Button(self.tools_frame, text="Synchroniser tous les fichiers", command=self.run_sync_all)
        btn_sync_all.pack(side="left", padx=5)

        self.sync_one_var = tk.StringVar()
        tk.Label(self.tools_frame, text="Fichier à synchroniser:", bg="#2a2a2a", fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.sync_one_var, width=25).pack(side="left")
        btn_sync_one = ttk.Button(self.tools_frame, text="Synchroniser ce fichier", command=self.run_sync_one)
        btn_sync_one.pack(side="left", padx=5)

        self.genfichier_file_var = tk.StringVar()
        self.genfichier_src_var  = tk.StringVar(value="fr")
        self.genfichier_tgt_var  = tk.StringVar(value="en")
        tk.Label(self.tools_frame, text="gen_fichier:", bg="#2a2a2a", fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.genfichier_file_var, width=20).pack(side="left")
        tk.Label(self.tools_frame, text="src:", bg="#2a2a2a", fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.genfichier_src_var, width=5).pack(side="left")
        tk.Label(self.tools_frame, text="tgt:", bg="#2a2a2a", fg="white").pack(side="left", padx=(10,1))
        ttk.Entry(self.tools_frame, textvariable=self.genfichier_tgt_var, width=5).pack(side="left")
        btn_genfichier = ttk.Button(self.tools_frame, text="Générer fichier", command=self.run_generer_fichier)
        btn_genfichier.pack(side="left", padx=5)

        btn_gen_manquant = ttk.Button(self.tools_frame, text="Générer les fichiers manquants", command=self.run_generer_manquant)
        btn_gen_manquant.pack(side="left", padx=5)

        btn_check = ttk.Button(self.tools_frame, text="Vérifier la cohérence", command=self.run_check_coherence)
        btn_check.pack(side="left", padx=5)

        self.selected_file_label = tk.Label(self.tools_frame, text="Fichier sélectionné :", bg="#2a2a2a", fg="white", font=FONT_DEFAULT)
        self.selected_file_label.pack(side="left", padx=10)

        # Barre d'état
        self.status = tk.Label(self.root, text="Prêt", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=COL_BG_TOPBAR, fg="white")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Style des scrollbars
        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar",
                       background=COL_BG_MAIN,
                       troughcolor=COL_BG_MAIN,
                       arrowcolor="white")
        style.configure("Custom.Horizontal.TScrollbar",
                       background=COL_BG_MAIN,
                       troughcolor=COL_BG_MAIN,
                       arrowcolor="white")

        # Conteneur pour le canvas et les scrollbars
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Canvas principal pour les colonnes avec nouveaux styles de scrollbar
        self.main_canvas = tk.Canvas(container, bg=COL_BG_MAIN)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar verticale avec nouveau style
        scrollbar_y = ttk.Scrollbar(container, orient="vertical",
                                  command=self.main_canvas.yview,
                                  style="Custom.Vertical.TScrollbar")
        scrollbar_y.pack(side="right", fill="y")
        self.main_canvas.configure(yscrollcommand=scrollbar_y.set)

        # Scrollbar horizontale avec nouveau style
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal",
                                  command=self.main_canvas.xview,
                                  style="Custom.Horizontal.TScrollbar")
        scrollbar_x.pack(side="bottom", fill="x")
        self.main_canvas.configure(xscrollcommand=scrollbar_x.set)
        self.scrollbar_x = scrollbar_x

        # Frame interne contenant les colonnes
        self.columns_frame = tk.Frame(self.main_canvas, bg=COL_BG_MAIN)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.columns_frame, anchor="nw")

        # Met à jour la zone scrollable en fonction du contenu
        self.columns_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.columns_frame.bind("<Configure>", lambda e: self.main_canvas.itemconfig(self.canvas_window, width=self.columns_frame.winfo_reqwidth()))
        # Gère la visibilité dynamique de la scrollbar horizontale
        self.main_canvas.bind("<Configure>", self.update_xscroll_visibility)
        self.columns_frame.bind("<Configure>", self.update_xscroll_visibility)

        # On ajuste seulement la hauteur pour que le canvas prenne toute la hauteur de la fenêtre
        self.root.bind("<Configure>", lambda e: self.main_canvas.config(height=self.root.winfo_height()))

        # Binding de la molette pour le scroll vertical
        def on_mousewheel(event):
            if event.state & 0x4:  # Ctrl est pressé
                # Zoom ou dézoom (à implémenter si nécessaire)
                return
            elif event.state & 0x1:  # Shift est pressé
                self.main_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.root.unbind_all("<MouseWheel>")
        self.root.bind_all("<MouseWheel>", on_mousewheel)

        # Améliore la gestion du focus
        def on_focus_in(event):
            if isinstance(event.widget, tk.Entry):
                event.widget.config(bg=COL_EDIT_BG_FOCUS)

        def on_focus_out(event):
            if isinstance(event.widget, tk.Entry):
                event.widget.config(bg=COL_EDIT_BG)

        self.root.bind_class("Entry", "<FocusIn>", on_focus_in)
        self.root.bind_class("Entry", "<FocusOut>", on_focus_out)

        # Binding des événements pour une meilleure gestion de la navigation
        self.root.bind("<Control-r>", lambda e: self.reload_root())
        self.root.bind("<Escape>", lambda e: self.unmake_editable())
        self.root.bind("<Control-f>", lambda e: self.show_search())  # Raccourci Ctrl+F pour la recherche

    def reload_root(self, event=None):
        """Recharge complètement l'interface depuis la racine"""
        try:
            # Sauvegarde de l'état
            old_lang = self.lang
            old_path = self.current_path[:]

            # Recharge depuis la racine
            self.load_root()

            # Essaie de restaurer le chemin précédent
            try:
                self.rebuild_columns_for_path()
                self.status.config(text="✅ Interface rechargée")
            except Exception as e:
                print(f"❌ Erreur lors de la restauration du chemin : {e}")
                # On reste à la racine en cas d'erreur
                self.status.config(text="✅ Interface rechargée (racine)")
        except Exception as e:
            print(f"❌ Erreur lors du rechargement : {e}")
            self.status.config(text="❌ Erreur de rechargement")

    def update_xscroll_visibility(self, event=None):
        # Affiche ou masque la scrollbar horizontale selon la largeur du contenu
        canvas_width = self.main_canvas.winfo_width()
        content_width = self.columns_frame.winfo_reqwidth()
        if content_width > canvas_width:
            self.scrollbar_x.pack(side="bottom", fill="x")
        else:
            self.scrollbar_x.pack_forget()

    def on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Méthode pour afficher un popup de chargement
    def afficher_popup_chargement(self, message="Traitement en cours..."):
        popup = tk.Toplevel(self.root)
        popup.title("Veuillez patienter")
        popup.geometry("300x100")
        popup.transient(self.root)
        popup.grab_set()  # Bloque les interactions avec la fenêtre principale
        popup.resizable(False, False)
        tk.Label(popup, text=message, font=("Segoe UI", 11)).pack(pady=20)
        self.root.update_idletasks()
        return popup

    # Méthode pour activer/désactiver les widgets de la barre d'outils
    def set_tools_enabled(self, state):
        for widget in self.tools_frame.winfo_children():
            try:
                # Vérifier que le widget a bien un attribut config avant de l'utiliser
                if hasattr(widget, 'config'):
                    widget.config(state=state)  # type: ignore
            except tk.TclError:
                pass

    # --- Fonctions pour lancer les scripts externes ---
    def run_sync_all(self):
        cmd = ["python", "sync_all.py"]
        self.run_command(cmd, desc="Synchroniser tous les fichiers")

    def run_sync_one(self):
        arg = self.sync_one_var.get().strip()
        if not arg:
            self.status.config(text="❌ Argument sync_one manquant")
            print("❌ Aucun argument fourni pour sync_one")
            return

        # Valider que le fichier existe
        file_path = self.file_map.get(arg)
        if not file_path or not os.path.exists(file_path):
            self.status.config(text=f"❌ Fichier introuvable : {arg}")
            print(f"❌ Fichier introuvable : {arg}")
            return

        print(f"🔄 Lancement de sync_one pour : {file_path}")
        cmd = ["python", "sync_one.py", file_path]
        self.run_command(cmd, desc=f"Synchroniser {arg}")

    def run_generer_fichier(self):
        if not self.base_dir:
            self.status.config(text="❌ Aucun dossier ouvert")
            return

        f_arg = self.genfichier_file_var.get().strip()
        src = self.genfichier_src_var.get().strip()
        tgt = self.genfichier_tgt_var.get().strip()

        if not (f_arg and src and tgt):
            self.status.config(text="❌ Arguments generer_fichier manquants")
            return

        cmd = ["python", "generer_fichier.py", self.base_dir, f_arg, src, tgt]
        self.run_command(cmd, desc=f"Générer fichier {f_arg} {src}->{tgt}")

    def run_generer_manquant(self):
        if not self.base_dir:
            self.status.config(text="❌ Aucun dossier ouvert")
            return

        cmd = ["python", "generer_manquant.py", self.base_dir]
        self.run_command(cmd, desc="Générer les fichiers manquants")

    def run_check_coherence(self):
        if not hasattr(self, 'file_map') or not self.file_map:
            self.status.config(text="❌ Aucun dossier ouvert")
            return

        # Obtenir le dossier parent du premier fichier trouvé
        premier_fichier = next(iter(self.file_map.values()))
        dossier_base = os.path.dirname(premier_fichier)

        print(f"🔍 Vérification de cohérence dans : {dossier_base}")
        cmd = ["python", "check_coherence.py", dossier_base]
        self.run_command(cmd, desc="Vérifier la cohérence")

    def run_command(self, cmd, desc=""):
        logger.info(f"Exécution de la commande: {' '.join(cmd)}")
        self.set_tools_enabled("disabled")
        popup = self.afficher_popup_chargement(f"{desc} en cours...")
        try:
            # Obtenir le chemin du dossier contenant app.py
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Modifier la commande pour inclure le chemin complet du script
            if cmd[0] == "python":
                cmd[1] = os.path.join(script_dir, cmd[1])

            self.status.config(text=f"⏳ Exécution : {desc} ...")
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            logger.info(f"Exécution dans le dossier: {script_dir}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=script_dir  # Utiliser le dossier du script comme dossier de travail
            )

            if result.returncode == 0:
                logger.info(f"Commande terminée avec succès: {desc}")
                logger.debug(f"Sortie de la commande:\n{result.stdout}")
                self.status.config(text=f"✅ Terminé : {desc}")
            else:
                logger.error(f"Erreur lors de l'exécution de {desc}: {result.stderr}")
                self.status.config(text=f"❌ Erreur : {desc}")
        except Exception as e:
            logger.error(f"Exception lors de l'exécution de {desc}: {str(e)}")
            self.status.config(text=f"❌ Exception : {desc}")
        finally:
            popup.destroy()
            self.set_tools_enabled("normal")

    def run_sync_script(self, file_path):
        try:
            if not file_path:
                self.status.config(text="❌ Aucun fichier sélectionné")
                print("❌ Aucun fichier sélectionné pour la synchronisation")
                return

            # Utiliser le chemin complet du fichier source
            source_file = file_path

            if not os.path.exists(source_file):
                error_msg = f"❌ Fichier introuvable : {source_file}"
                self.status.config(text="❌ Fichier introuvable")
                print(error_msg)
                return

            source_dir = os.path.dirname(source_file)
            print(f"📂 Répertoire de travail pour la synchronisation : {source_dir}")

            # Appeler sync_one.py avec le chemin complet du fichier source
            script_dir = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                ["python", os.path.join(script_dir, "sync_one.py"), source_file],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=source_dir
            )

            if result.returncode == 0:
                self.status.config(text="✅ Synchronisation réussie")
                print("\nSortie du script :")
                print(result.stdout)
            else:
                self.status.config(text="❌ Erreur lors de la synchronisation")
                print("\nErreur lors de la synchronisation :")
                print(result.stderr)

        except Exception as e:
            self.status.config(text="❌ Erreur de synchronisation")
            print(f"\n❌ Erreur lors de la synchronisation : {e}")

    def reload_data(self):
        """Recharge les données des fichiers JSON en mémoire"""
        for filename, filepath in self.path_map.items():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.data_map[filename] = json.load(f)
            except Exception as e:
                print(f"Erreur lors du rechargement de {filename}: {e}")

    def sync_files(self):
        if not self.check_required_files():
            self.status.config(text="❌ Fichiers requis manquants")
            return

        try:
            self.run_sync_script(self.current_file_path)
        except Exception as e:
            self.status.config(text="❌ Erreur lors de la synchronisation")
            print(f"Erreur : {e}")

    def check_required_files(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        required_files = ["sync_one.py", "generer_fichier.py", "translate.py"]

        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(script_dir, file)):
                missing_files.append(file)

        if missing_files:
            print(f"❌ Fichiers manquants : {', '.join(missing_files)}")
            print(f"📁 Dossier recherché : {script_dir}")
            return False
        return True

    # --- Navigation et chargement des colonnes ---
    def reload_lang(self):
        self.lang = self.lang_var.get()
        print(f"Changement de langue : {self.lang}")
        # Réinitialise le chemin courant pour éviter les erreurs
        self.current_path = [0, 255, 255, 255]
        self.clear_columns_from(0)
        self.rebuild_columns_for_path()

    def rebuild_columns_for_path(self):
        partial_path = [0, 255, 255, 255]
        self.load_level(partial_path, 0)
        if self.current_path[1] != 255:
            partial_path[1] = self.current_path[1]
            partial_path[2] = 255
            partial_path[3] = 255
            self.load_level(partial_path, 1)
            if self.current_path[2] != 255:
                partial_path[2] = self.current_path[2]
                partial_path[3] = 255
                self.load_level(partial_path, 2)
                if self.current_path[3] != 255:
                    partial_path[3] = self.current_path[3]
                    self.load_level(partial_path, 3)
        self.main_canvas.yview_moveto(0.0)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.base_dir = folder
        self.initialize_file_map(self.base_dir)
        print("Dossier ouvert :", folder)
        print("Fichiers trouvés :", list(self.file_map.keys()))
        self.current_path = [0, 255, 255, 255]
        self.load_root()

    def load_root(self):
        self.current_path = [0, 255, 255, 255]
        self.clear_columns_from(0)
        self.load_level(self.current_path, 0)

    def load_level(self, path, level):
        filename = self.path_to_filename(path)
        logger.info(f"Chargement du niveau {level} avec le fichier : {filename}")
        filepath = self.file_map.get(filename)
        if not filepath:
            logger.error(f"Fichier introuvable : {filename}")
            self.status.config(text=f"❌ Introuvable : {filename}")
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
            logger.info(f"Fichier {filename} chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de {filename}: {str(e)}")
            self.status.config(text=f"❌ Erreur lecture {filename}")
            return
        self.data_map[filename] = content
        self.path_map[filename] = filepath
        self.clear_columns_from(level)
        fault_list = content.get("FaultDetailList", [])
        print(f"Nombre d'items dans FaultDetailList : {len(fault_list)}")
        self.display_column(fault_list, path, filename, level)
        self.root.after(100, lambda: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.yview_moveto(0.0)

    def path_to_filename(self, path):
        return f"faults_{'_'.join(str(p).zfill(3) for p in path)}_{self.lang}.json"

    # --- Gestion des clics sur les items ---
    def update_selected_file(self, fn):
        self.selected_file_label.config(text=f"Fichier sélectionné : {fn}")
        self.sync_one_var.set(fn)
        self.genfichier_file_var.set(fn)

    def handle_single_click(self, fault, i, path, level, fn, event):
        widget = event.widget
        widget._click_job = widget.after(300, lambda: self.single_click_action(fault, i, path, level, fn))

    def single_click_action(self, fault, i, path, level, fn):
        self.update_selected_file(fn)
        print(f"Clic sur l'item {i} (Expandable={fault.get('IsExpandable')})")
        if fault.get("IsExpandable"):
            new_path = path[:]
            try:
                insert_idx = new_path.index(255)
            except ValueError:
                print("Erreur : 255 non trouvé dans", new_path)
                # Réinitialise le chemin si une erreur survient
                self.current_path = [0, 255, 255, 255]
                self.clear_columns_from(0)
                self.rebuild_columns_for_path()
                return
            new_path[insert_idx] = i
            if insert_idx + 1 < len(new_path):
                new_path[insert_idx + 1] = 255
            self.current_path = new_path
            print(f"Navigation vers {self.path_to_filename(new_path)}")
            self.load_level(new_path, level + 1)

    def handle_double_click(self, fault, i, path, level, fn, row, event):
        if self.editing_info and self.editing_info["row"] != row:
            self.unmake_editable()
        self.editing_info = {"row": row, "fault": fault, "idx": i, "filename": fn, "path": path, "level": level}
        self.update_selected_file(fn)
        print(f"🛠️ Double-clic sur {i} dans {fn}")
        self.make_editable(row, fault, i, fn, path, level)

    def display_column(self, fault_list, path, filename, level):
        col_index = len(self.columns)
        frame = tk.Frame(self.columns_frame, bg=COL_BG_COLUMN)
        frame.grid(row=0, column=col_index, padx=5, pady=10, sticky="nsew")
        self.columns_frame.grid_columnconfigure(col_index, minsize=MIN_COL_WIDTH)
        self.columns.append(frame)
        for idx, fault in enumerate(fault_list):
            row = tk.Frame(frame, bg=COL_BG_ROW, highlightthickness=0, highlightbackground=COL_HIGHLIGHT)
            row.pack(fill="x", padx=4, pady=3)
            row.bind("<Enter>", lambda e, r=row: r.configure(highlightthickness=1))
            row.bind("<Leave>", lambda e, r=row: r.configure(highlightthickness=0))
            color = COL_GREEN if fault.get("IsExpandable") else COL_RED
            dot = tk.Canvas(row, width=14, height=14, bg=COL_BG_ROW, highlightthickness=0)
            dot.create_oval(2, 2, 12, 12, fill=color, outline=color)
            dot.pack(side="left", padx=(6, 8))
            label_text = f"{idx}: {fault.get('Description', '(vide)')}"
            label = tk.Label(row, text=label_text, fg=COL_FG_TEXT, bg=COL_BG_ROW,
                             anchor="w", font=FONT_DEFAULT)
            label.pack(side="left", fill="x", expand=True)
            label.bind("<Button-1>", partial(self.handle_single_click, fault, idx, path, level, filename))
            label.bind("<Double-1>", partial(self.handle_double_click, fault, idx, path, level, filename, row))
        self.root.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        self.main_canvas.yview_moveto(0.0)

    def render_row(self, row, fault, idx, path, level, filename):
        """Rend un row en mode lecture seule (utile pour annuler l'édition)"""
        for w in row.winfo_children():
            w.destroy()
        color = COL_GREEN if fault.get("IsExpandable") else COL_RED
        dot = tk.Canvas(row, width=14, height=14, bg=COL_BG_ROW, highlightthickness=0)
        dot.create_oval(2, 2, 12, 12, fill=color, outline=color)
        dot.pack(side="left", padx=(6,8))
        label_text = f"{idx}: {fault.get('Description', '(vide)')}"
        label = tk.Label(row, text=label_text, fg=COL_FG_TEXT, bg=COL_BG_ROW, anchor="w", font=FONT_DEFAULT)
        label.pack(side="left", fill="x", expand=True)
        label.bind("<Button-1>", partial(self.handle_single_click, fault, idx, path, level, filename))
        label.bind("<Double-1>", partial(self.handle_double_click, fault, idx, path, level, filename, row))

    def unmake_editable(self):
        """Rétablit l'ancien row en mode lecture seule."""
        if not self.editing_info:
            return
        row  = self.editing_info["row"]
        fault = self.editing_info["fault"]
        idx   = self.editing_info["idx"]
        filename = self.editing_info["filename"]
        path = self.editing_info["path"]
        level = self.editing_info["level"]
        self.render_row(row, fault, idx, path, level, filename)
        self.editing_info = None

    def make_editable(self, row, fault, idx, filename, path, level):
        print(f"✏️ Modification déclenchée sur l'item {idx} dans {filename}")
        for widget in row.winfo_children():
            widget.destroy()
        desc_var = tk.StringVar(value=fault.get("Description", ""))
        desc_entry = tk.Entry(row, textvariable=desc_var, bg=COL_EDIT_BG, fg=COL_EDIT_FG,
                              highlightthickness=0, relief="flat", font=FONT_DEFAULT)
        desc_entry.pack(side="left", padx=5, fill="both", expand=True, ipady=4)
        desc_entry.focus_set()
        def save_edit(event=None):
            fault["Description"] = desc_var.get()
            fault["IsExpandable"] = exp_var.get()
            self.save_file(filename)
            self.unmake_editable()
        desc_entry.bind("<Return>", save_edit)
        exp_var = tk.BooleanVar(value=fault.get("IsExpandable", False))
        exp_check = tk.Checkbutton(row, text="Expandable", variable=exp_var,
                                   bg=COL_BG_ROW, fg=COL_FG_TEXT, selectcolor=COL_BG_ROW,
                                   activebackground=COL_BG_ROW, highlightthickness=0, bd=0,
                                   font=FONT_DEFAULT)
        exp_check.pack(side="left", padx=5)
        tk.Button(row, text="✅", command=save_edit,
                  bg=COL_BG_ROW, fg=COL_FG_TEXT, relief="flat", font=FONT_DEFAULT).pack(side="left", padx=5)
        row.update_idletasks()
        self.columns_frame.event_generate("<Configure>")

    def save_file(self, rel_path):
        logger.info(f"Sauvegarde du fichier: {rel_path}")
        try:
            with open(self.file_map[rel_path], "w", encoding="utf-8") as f:
                json.dump(self.data_map[os.path.basename(rel_path)], f, indent=2, ensure_ascii=False)
            logger.info(f"Fichier {rel_path} sauvegardé avec succès")
            self.status.config(text=f"✅ {rel_path} sauvegardé")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de {rel_path}: {str(e)}")
            self.status.config(text=f"❌ Échec de la sauvegarde {rel_path}")

    def clear_columns_from(self, level):
        for frame in self.columns[level:]:
            frame.destroy()
        self.columns = self.columns[:level]
        self.root.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def load_flat_json(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier JSON plat (fr.json, en.json, es.json)",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        if not file_path:
            return

        # On force l'utilisation de fr.json, en.json, es.json dans le même dossier
        base_dir = os.path.dirname(file_path)
        fr_path = os.path.join(base_dir, "fr.json")
        en_path = os.path.join(base_dir, "en.json")
        es_path = os.path.join(base_dir, "es.json")

        # Afficher les chemins exacts pour le débogage
        print(f"\n-------- DÉBOGUE CHEMINS DE FICHIERS --------")
        print(f"Fichier sélectionné : {file_path}")
        print(f"Chemin fr.json : {fr_path} (Existe: {os.path.exists(fr_path)})")
        print(f"Chemin en.json : {en_path} (Existe: {os.path.exists(en_path)})")
        print(f"Chemin es.json : {es_path} (Existe: {os.path.exists(es_path)})")

        # Charger ou créer les fichiers
        def load_or_create(path):
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if not content.strip():
                            print(f"⚠️ Fichier {os.path.basename(path)} est vide")
                            return {}

                        try:
                            data = json.loads(content)
                            if not isinstance(data, dict):
                                print(f"⚠️ Fichier {os.path.basename(path)} n'est pas un dictionnaire JSON valide")
                                return {}
                            print(f"Fichier {os.path.basename(path)} chargé avec {len(data)} clés")
                            return data
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur de décodage JSON pour {path}: {e}")
                            print(f"Contenu problématique: {content[:100]}...")
                            if self.ask_yes_no(f"Le fichier {os.path.basename(path)} contient du JSON invalide. Voulez-vous le recréer vide?"):
                                with open(path, "w", encoding="utf-8") as f:
                                    json.dump({}, f, indent=2, ensure_ascii=False)
                                return {}
                            else:
                                return {}
                except Exception as e:
                    print(f"❌ Erreur lors de la lecture de {path}: {e}")
                    return {}
            else:
                print(f"Fichier {os.path.basename(path)} n'existe pas, création...")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=2, ensure_ascii=False)
                return {}

        # Charger les données des fichiers
        fr_data = load_or_create(fr_path)
        en_data = load_or_create(en_path)
        es_data = load_or_create(es_path)

        # Afficher clairement les données chargées
        print(f"\n-------- DÉBOGUE DONNÉES CHARGÉES --------")
        print(f"Clés fr.json : {len(fr_data)} clés")
        if len(fr_data) > 0:
            print(f"Premières 3 clés fr.json : {list(fr_data.keys())[:3]}")
        print(f"Clés en.json : {len(en_data)} clés")
        print(f"Clés es.json : {len(es_data)} clés")

        # Vérifier que fr.json contient des données, sinon prendre toutes les clés
        if fr_data:
            all_keys = list(fr_data.keys())
            print(f"Utilisation des {len(all_keys)} clés de fr.json")
        else:
            # Si fr.json est vide, utiliser la combinaison de toutes les clés
            all_keys = sorted(set(list(fr_data.keys()) + list(en_data.keys()) + list(es_data.keys())))
            print(f"fr.json vide, utilisation de l'union de toutes les clés: {len(all_keys)} clés")

        print("----------------------------------------")

        # Si aucune clé n'est trouvée, ne pas afficher la clé "nouvelle_cle"
        translations = {"fr": fr_data, "en": en_data, "es": es_data}
        self.show_flat_json_editor(all_keys, translations, fr_path, en_path, es_path)
        self.status.config(text=f"✅ Fichiers chargés : {len(all_keys)} clés trouvées")

    def show_flat_json_editor(self, all_keys, translations, fr_path, en_path, es_path):
        """Affiche l'éditeur de fichiers JSON plats"""
        # Si aucune clé n'est trouvée, ajouter une clé par défaut
        if not all_keys:
            all_keys = ["nouvelle_cle"]
            for lang in ["fr", "en", "es"]:
                translations[lang]["nouvelle_cle"] = ""

        # Créer la fenêtre d'édition
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Éditeur JSON")
        editor_window.geometry("1200x800")
        editor_window.configure(bg=COL_BG_TOPBAR)

        # Stocker les chemins des fichiers dans editor_window pour pouvoir y accéder plus tard
        # type: ignore - Pylance ne reconnaît pas qu'on ajoute des attributs dynamiques aux widgets Tkinter
        editor_window.fr_path = fr_path  # type: ignore
        editor_window.en_path = en_path  # type: ignore
        editor_window.es_path = es_path  # type: ignore

        # Désactiver temporairement le raccourci Ctrl+F global pour éviter les conflits
        self.root.unbind("<Control-f>")

        # Cadre principal avec barre d'outils
        main_container = tk.Frame(editor_window, bg=COL_BG_TOPBAR)
        main_container.pack(fill="both", expand=True)

        # Barre d'outils en haut
        toolbar = tk.Frame(main_container, bg=COL_BG_TOPBAR, height=40)
        toolbar.pack(fill="x", side="top")

        # Configuration de la barre d'outils avec le bouton de recherche
        self.setup_flat_editor_toolbar(editor_window, toolbar)

        # Conteneur pour la table d'édition
        table_container = tk.Frame(main_container, bg=COL_BG_TOPBAR)
        table_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(table_container, bg=COL_BG_TOPBAR, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)

        # Configuration de la mise en page
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Frame pour contenir la grille
        grid_frame = tk.Frame(canvas, bg=COL_BG_TOPBAR)
        canvas_window = canvas.create_window((0, 0), window=grid_frame, anchor="nw")

        # Stocker les références importantes pour la recherche
        # type: ignore - Pylance ne reconnaît pas qu'on ajoute des attributs dynamiques aux widgets Tkinter
        editor_window.grid_frame = grid_frame  # type: ignore
        editor_window.canvas = canvas  # type: ignore
        editor_window.all_keys = all_keys  # type: ignore
        editor_window.entry_vars = {}  # type: ignore

        # En-têtes
        headers = ["Clé", "Français", "Anglais", "Espagnol", ""]
        header_bg = COL_BG_TOPBAR
        header_fg = "white"

        # Configuration des colonnes
        for col in range(5):
            grid_frame.grid_columnconfigure(col, weight=1, minsize=200 if col < 4 else 50)

        # Création des en-têtes
        for col, header in enumerate(headers):
            tk.Label(grid_frame, text=header, bg=header_bg, fg=header_fg,
                    font=FONT_TITLE, anchor="w", padx=5).grid(
                    row=0, column=col, sticky="ew", padx=2, pady=5)

        # Créer les lignes pour chaque clé
        row_colors = [COL_BG_ROW, COL_BG_ROW_ALT]
        for row_idx, key in enumerate(all_keys, start=1):
            row_color = row_colors[row_idx % 2]

            # Colonne clé
            key_label = tk.Label(grid_frame, text=key, bg=row_color, fg=COL_FG_TEXT,
                               font=FONT_DEFAULT, anchor="w", padx=5)
            key_label.grid(row=row_idx, column=0, sticky="ew", padx=2, pady=3)

            # Colonnes traductions
            for col_idx, lang in enumerate(["fr", "en", "es"], start=1):
                var = tk.StringVar(value=translations[lang].get(key, ""))
                entry = tk.Entry(grid_frame, textvariable=var, bg=COL_EDIT_BG,
                               fg=COL_EDIT_FG, font=FONT_DEFAULT)
                entry.grid(row=row_idx, column=col_idx, sticky="ew", padx=2, pady=3)
                editor_window.entry_vars[(row_idx, lang)] = var  # type: ignore

            # Bouton traduction par ligne
            translate_btn = tk.Button(grid_frame, text="🌐", font=FONT_DEFAULT,
                                   command=lambda r=row_idx: self.translate_row(editor_window, r))
            translate_btn.grid(row=row_idx, column=4, padx=2, pady=3)

        # Configuration du scroll et des événements
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        grid_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # Raccourci clavier pour la recherche
        editor_window.bind("<Control-f>", lambda event: self.show_flat_search(editor_window))

        # Configuration de la fermeture
        def on_editor_close():
            self.root.bind("<Control-f>", lambda e: self.show_search())
            editor_window.destroy()
        editor_window.protocol("WM_DELETE_WINDOW", on_editor_close)

    def translate_row(self, editor_window, row):
        """Traduit une ligne spécifique du français vers l'anglais et l'espagnol"""
        fr_text = editor_window.entry_vars.get((row, "fr"))
        if fr_text and fr_text.get().strip():
            try:
                # Effet visuel de début de traduction
                for widget in editor_window.grid_frame.grid_slaves(row=row):
                    widget.config(bg=COL_AMBER)
                editor_window.update_idletasks()

                # Traduire vers l'anglais
                en_trad = self.translate_text(fr_text.get(), "en")
                editor_window.entry_vars[(row, "en")].set(en_trad)

                # Traduire vers l'espagnol
                es_trad = self.translate_text(fr_text.get(), "es")
                editor_window.entry_vars[(row, "es")].set(es_trad)

                # Effet visuel de succès
                for widget in editor_window.grid_frame.grid_slaves(row=row):
                    widget.config(bg=COL_GREEN)
                    editor_window.after(500, lambda w=widget: w.config(
                        bg=COL_BG_ROW if row % 2 == 1 else COL_BG_ROW_ALT))

                # Mettre à jour le statut
                if hasattr(editor_window, 'status_bar'):
                    editor_window.status_bar.config(text=f"✅ Ligne {row} traduite avec succès")

            except Exception as e:
                print(f"Erreur lors de la traduction de la ligne {row}: {e}")
                # Effet visuel d'erreur
                for widget in editor_window.grid_frame.grid_slaves(row=row):
                    widget.config(bg=COL_RED)
                    editor_window.after(500, lambda w=widget: w.config(
                        bg=COL_BG_ROW if row % 2 == 1 else COL_BG_ROW_ALT))

                if hasattr(editor_window, 'status_bar'):
                    editor_window.status_bar.config(text=f"❌ Erreur de traduction ligne {row}")

    def setup_flat_editor_toolbar(self, editor_window, toolbar):
        # Bouton pour sauvegarder les fichiers
        save_btn = tk.Button(toolbar,
                            text="💾 Sauvegarder",
                            command=lambda: self.save_flat_files(editor_window),
                            bg=COL_BG_TOPBAR,
                            fg="white",
                            font=FONT_DEFAULT,
                            relief="flat",
                            padx=10,
                            pady=5)
        save_btn.pack(side="left", padx=15, pady=5)

        # Bouton de recherche avec style cohérent
        search_btn = tk.Button(toolbar,
                              text="🔍 Rechercher",
                              command=lambda: self.show_flat_search(editor_window),
                              bg=COL_BG_TOPBAR,
                              fg="white",
                              font=FONT_DEFAULT,
                              relief="flat",
                              padx=10,
                              pady=5)
        search_btn.pack(side="left", padx=15, pady=5)

        # Bouton pour traduire toutes les entrées
        translate_all_btn = tk.Button(toolbar,
                                    text="🌐 Traduire tout",
                                    command=lambda: self.translate_all(editor_window),
                                    bg=COL_BG_TOPBAR,
                                    fg="white",
                                    font=FONT_DEFAULT,
                                    relief="flat",
                                    padx=10,
                                    pady=5)
        translate_all_btn.pack(side="left", padx=15, pady=5)

    def show_flat_search(self, editor_window):
        """Affiche la barre de recherche pour l'éditeur de fichiers plats"""
        # Fermer la barre de recherche existante si elle existe
        if hasattr(editor_window, 'search_frame') and editor_window.search_frame:
            editor_window.search_frame.destroy()
            editor_window.search_frame = None

        # Créer la barre de recherche
        editor_window.search_frame = tk.Frame(editor_window, bg=COL_BG_TOPBAR)
        editor_window.search_frame.pack(fill="x", after=editor_window.winfo_children()[0])

        # Container gauche pour le champ de recherche
        search_container = tk.Frame(editor_window.search_frame, bg=COL_BG_TOPBAR)
        search_container.pack(side="left", fill="x", expand=True)

        # Container droit pour les boutons
        buttons_container = tk.Frame(editor_window.search_frame, bg=COL_BG_TOPBAR)
        buttons_container.pack(side="right", fill="x")

        # Icône et champ de recherche
        search_label = tk.Label(search_container, text="🔍", bg=COL_BG_TOPBAR, fg="white",
                             font=("Segoe UI", 12))
        search_label.pack(side="left", padx=(10, 0))

        editor_window.search_var = tk.StringVar()
        search_entry = tk.Entry(search_container, textvariable=editor_window.search_var, width=40,
                             bg=COL_EDIT_BG, fg=COL_EDIT_FG, font=FONT_DEFAULT,
                             insertbackground="white")
        search_entry.pack(side="left", padx=10)

        # Compteur de résultats
        editor_window.results_label = tk.Label(search_container, text="", bg=COL_BG_TOPBAR,
                                   fg="white", font=FONT_DEFAULT)
        editor_window.results_label.pack(side="left", padx=10)

        # Style commun pour les boutons
        button_style = {
            "bg": COL_BG_TOPBAR,
            "fg": "white",
            "font": FONT_DEFAULT,
            "relief": "flat",
            "padx": 10,
            "pady": 5
        }

        # Boutons de navigation
        tk.Button(buttons_container, text="◀", command=lambda: self.prev_flat_search_result(editor_window),
                 **button_style).pack(side="left", padx=2)
        tk.Button(buttons_container, text="▶", command=lambda: self.next_flat_search_result(editor_window),
                 **button_style).pack(side="left", padx=2)

        # Bouton fermer
        tk.Button(buttons_container, text="✖", command=lambda: self.close_flat_search(editor_window),
                 **button_style).pack(side="left", padx=(10, 5))

        # Configuration de la recherche en temps réel
        editor_window.search_var.trace_add("write", lambda *args: self.flat_search_as_you_type(editor_window))
        search_entry.bind("<Return>", lambda e: self.next_flat_search_result(editor_window))
        search_entry.bind("<Escape>", lambda e: self.close_flat_search(editor_window))

        # Initialiser les variables de recherche
        editor_window.search_results = []
        editor_window.current_search_index = -1

        # Focus sur le champ de recherche
        search_entry.focus_set()
        print("Barre de recherche plate affichée")

    def close_flat_search(self, editor_window):
        """Ferme la barre de recherche pour l'éditeur de fichiers plats."""
        if hasattr(editor_window, 'search_frame') and editor_window.search_frame:
            editor_window.search_frame.destroy()
            editor_window.search_frame = None
        editor_window.search_results = []
        editor_window.current_search_index = -1
        self.clear_flat_search_highlights(editor_window)

    def clear_flat_search_highlights(self, editor_window):
        """Réinitialise les surlignages de recherche dans l'éditeur de fichiers plats."""
        for row_idx in range(1, len(editor_window.all_keys) + 1):
            for widget in editor_window.grid_frame.grid_slaves(row=row_idx):
                widget.config(bg=COL_BG_ROW if row_idx % 2 == 1 else COL_BG_ROW_ALT)

    def flat_search_as_you_type(self, editor_window):
        """Recherche en temps réel dans l'éditeur de fichiers plats"""
        search_text = editor_window.search_var.get().strip()
        if not search_text:
            editor_window.search_results = []
            editor_window.current_search_index = -1
            self.clear_flat_search_highlights(editor_window)
            return

        # Effectuer la recherche dans les clés et les valeurs
        results = []
        for row_idx, key in enumerate(editor_window.all_keys, start=1):
            if search_text.lower() in key.lower():
                results.append(row_idx)

        editor_window.search_results = results
        if results:
            editor_window.current_search_index = 0
            self.highlight_flat_search_result(editor_window, results[0])
        else:
            self.clear_flat_search_highlights(editor_window)

    def highlight_flat_search_result(self, editor_window, row_idx):
        """Met en évidence un résultat de recherche spécifique et défile jusqu'à lui si nécessaire."""
        self.clear_flat_search_highlights(editor_window)

        # Mettre en surbrillance la ligne trouvée
        for widget in editor_window.grid_frame.grid_slaves(row=row_idx):
            if isinstance(widget, (tk.Label, tk.Canvas)):
                widget.config(bg=COL_SEARCH_HIGHLIGHT)

        # Mettre à jour le compteur de résultats
        total_results = len(editor_window.search_results)
        current_index = editor_window.current_search_index + 1
        if total_results > 0:
            editor_window.results_label.config(text=f"{current_index}/{total_results}")

        # Calculer les coordonnées de la ligne dans le canvas
        widget = editor_window.grid_frame.grid_slaves(row=row_idx)[0]
        widget_y = widget.winfo_y()
        canvas_height = editor_window.canvas.winfo_height()

        # Obtenir les coordonnées actuelles de la vue
        current_view_top = editor_window.canvas.yview()[0] * editor_window.grid_frame.winfo_height()
        current_view_bottom = editor_window.canvas.yview()[1] * editor_window.grid_frame.winfo_height()

        # Si le widget n'est pas complètement visible, défiler jusqu'à lui
        if widget_y < current_view_top or widget_y + widget.winfo_height() > current_view_bottom:
            # Calculer la nouvelle position de défilement pour centrer le résultat
            new_y = (widget_y - (canvas_height / 2)) / editor_window.grid_frame.winfo_height()
            # Limiter la position entre 0 et 1
            new_y = max(0, min(1, new_y))
            editor_window.canvas.yview_moveto(new_y)

        editor_window.update_idletasks()  # Assurer que l'interface est mise à jour

    def next_flat_search_result(self, editor_window):
        """Passe au résultat de recherche suivant dans l'éditeur plat."""
        if not editor_window.search_results:
            return

        editor_window.current_search_index = (editor_window.current_search_index + 1) % len(editor_window.search_results)
        self.highlight_flat_search_result(editor_window, editor_window.search_results[editor_window.current_search_index])

    def prev_flat_search_result(self, editor_window):
        """Passe au résultat de recherche précédent dans l'éditeur plat."""
        if not editor_window.search_results:
            return

        editor_window.current_search_index = (editor_window.current_search_index - 1) % len(editor_window.search_results)
        self.highlight_flat_search_result(editor_window, editor_window.search_results[editor_window.current_search_index])

    def translate_text(self, text, target_lang):
        """Traduit un texte français vers la langue cible"""
        try:
            # Appeler la fonction de traduction importée
            translated = traduire(text, target_lang)
            return translated
        except Exception as e:
            print(f"Erreur lors de la traduction: {e}")
            return text

    def ask_yes_no(self, question):
        """Affiche une boîte de dialogue oui/non et retourne True si l'utilisateur clique sur Oui"""
        return messagebox.askyesno("Question", question)

    def translate_all(self, editor_window):
        """Traduit toutes les valeurs françaises vers l'anglais et l'espagnol"""
        if not hasattr(editor_window, 'all_keys') or not editor_window.all_keys:
            return

        # Confirmer l'opération
        if not messagebox.askyesno("Confirmation", "Voulez-vous traduire toutes les entrées françaises vers l'anglais et l'espagnol?"):
            return

        # Afficher un popup de chargement
        popup = tk.Toplevel(editor_window)
        popup.title("Traduction en cours")
        popup.geometry("300x100")
        popup.transient(editor_window)
        popup.grab_set()

        # Ajouter une barre de progression
        progress_var = tk.DoubleVar()
        progress_label = tk.Label(popup, text="Traduction en cours...", font=FONT_DEFAULT)
        progress_label.pack(pady=(10, 5))
        progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=100)
        progress_bar.pack(fill="x", padx=20)

        try:
            # Nombre de clés à traduire et compteur
            total = len(editor_window.all_keys)
            translated = 0

            # Pour chaque clé
            for row_idx, key in enumerate(editor_window.all_keys, start=1):
                # Obtenir le texte français
                fr_text = editor_window.entry_vars.get((row_idx, "fr"))
                if fr_text and fr_text.get().strip():
                    try:
                        # Traduire vers l'anglais
                        en_trad = self.translate_text(fr_text.get(), "en")
                        editor_window.entry_vars[(row_idx, "en")].set(en_trad)

                        # Traduire vers l'espagnol
                        es_trad = self.translate_text(fr_text.get(), "es")
                        editor_window.entry_vars[(row_idx, "es")].set(es_trad)

                        translated += 1

                        # Mettre à jour la barre de progression
                        progress = (translated / total) * 100
                        progress_var.set(progress)
                        progress_label.config(text=f"Traduction en cours... ({translated}/{total})")
                        popup.update()

                    except Exception as e:
                        print(f"Erreur lors de la traduction de '{fr_text.get()}': {e}")

            # Mettre à jour le statut final
            editor_window.status_bar.config(text=f"✅ {translated} sur {total} entrées traduites")

        except Exception as e:
            editor_window.status_bar.config(text=f"❌ Erreur lors de la traduction: {e}")
            print(f"Erreur lors de la traduction: {e}")
        finally:
            # Fermer le popup
            popup.destroy()

    def show_search(self):
        """Affiche la barre de recherche pour la vue hiérarchique"""
        # Fermer la barre de recherche existante si elle existe
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None

        # Créer la barre de recherche
        self.search_frame = tk.Frame(self.root, bg=COL_BG_TOPBAR)
        self.search_frame.pack(fill="x", after=self.tools_frame)

        # Container gauche pour le champ de recherche
        search_container = tk.Frame(self.search_frame, bg=COL_BG_TOPBAR)
        search_container.pack(side="left", fill="x", expand=True)

        # Container droit pour les boutons
        buttons_container = tk.Frame(self.search_frame, bg=COL_BG_TOPBAR)
        buttons_container.pack(side="right", fill="x")

        # Icône et champ de recherche
        search_label = tk.Label(search_container, text="🔍", bg=COL_BG_TOPBAR, fg="white", font=("Segoe UI", 12))
        search_label.pack(side="left", padx=(10, 0))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_container, textvariable=self.search_var, width=40,
                            bg=COL_EDIT_BG, fg=COL_EDIT_FG, font=FONT_DEFAULT,
                            insertbackground="white")
        search_entry.pack(side="left", padx=10)

        # Compteur de résultats
        self.results_label = tk.Label(search_container, text="", bg=COL_BG_TOPBAR, fg="white", font=FONT_DEFAULT)
        self.results_label.pack(side="left", padx=10)

        # Style commun pour les boutons
        button_style = {
            "bg": COL_BG_TOPBAR,
            "fg": "white",
            "font": FONT_DEFAULT,
            "relief": "flat",
            "padx": 10,
            "pady": 5
        }

        # Boutons de navigation
        tk.Button(buttons_container, text="◀", command=self.prev_search_result, **button_style).pack(side="left", padx=2)
        tk.Button(buttons_container, text="▶", command=self.next_search_result, **button_style).pack(side="left", padx=2)

        # Bouton fermer
        tk.Button(buttons_container, text="✖", command=self.close_search, **button_style).pack(side="left", padx=(10, 5))

        # Configuration de la recherche en temps réel
        self.search_var.trace_add("write", lambda *args: self.search_as_you_type())
        search_entry.bind("<Return>", lambda e: self.next_search_result())
        search_entry.bind("<Escape>", lambda e: self.close_search())

        # Initialiser les variables de recherche
        self.search_results = []
        self.current_search_index = -1

        # Focus sur le champ de recherche
        search_entry.focus_set()

    def close_search(self):
        """Ferme la barre de recherche hiérarchique"""
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None
        self.search_results = []
        self.current_search_index = -1
        self.clear_search_highlights()

    def clear_search_highlights(self):
        """Réinitialise les surlignages de recherche dans la vue hiérarchique"""
        for column in self.columns:
            # Utiliser enumerate pour obtenir l'index de chaque ligne
            for idx, row in enumerate(column.winfo_children()):
                if isinstance(row, tk.Frame):
                    bg_color = COL_BG_ROW if idx % 2 == 1 else COL_BG_ROW_ALT
                    row.configure(bg=bg_color)  # Configurer le bg du frame parent
                    for widget in row.winfo_children():
                        if isinstance(widget, (tk.Label, tk.Canvas)):
                            widget.configure(bg=bg_color)

    def search_as_you_type(self):
        """Recherche en temps réel dans la vue hiérarchique"""
        search_text = self.search_var.get().strip().lower()
        if not search_text:
            self.search_results = []
            self.current_search_index = -1
            self.clear_search_highlights()
            self.results_label.config(text="")
            return

        # Effectuer la recherche dans toutes les colonnes
        results = []
        for column in self.columns:
            for row in column.winfo_children():
                if isinstance(row, tk.Frame):
                    for widget in row.winfo_children():
                        if isinstance(widget, tk.Label) and search_text in widget.cget("text").lower():
                            results.append((column, row))
                            break

        self.search_results = results
        if results:
            self.current_search_index = 0
            self.highlight_search_result(results[0])
        else:
            self.clear_search_highlights()
            self.results_label.config(text="0/0")

    def highlight_search_result(self, result):
        """Met en évidence un résultat de recherche spécifique"""
        self.clear_search_highlights()
        column, row = result

        # Mettre en surbrillance la ligne trouvée
        row.configure(bg=COL_SEARCH_HIGHLIGHT)  # Configurer le bg du frame parent
        for widget in row.winfo_children():
            if isinstance(widget, (tk.Label, tk.Canvas)):
                widget.configure(bg=COL_SEARCH_HIGHLIGHT)

        # Mettre à jour le compteur de résultats
        if self.search_results:
            current_index = self.current_search_index + 1
            total_results = len(self.search_results)
            self.results_label.config(text=f"{current_index}/{total_results}")

        # S'assurer que le résultat est visible
        self.ensure_result_visible(column, row)

    def ensure_result_visible(self, column, row):
        """S'assure qu'un résultat de recherche est visible à l'écran"""
        # Calculer les coordonnées de la ligne dans le canvas
        bbox = self.main_canvas.bbox("all")
        if not bbox:
            return

        widget_y = row.winfo_y()
        canvas_height = self.main_canvas.winfo_height()

        # Obtenir les coordonnées actuelles de la vue
        current_view_top = self.main_canvas.yview()[0] * bbox[3]
        current_view_bottom = self.main_canvas.yview()[1] * bbox[3]

        # Si le widget n'est pas complètement visible, défiler jusqu'à lui
        if widget_y < current_view_top or widget_y + row.winfo_height() > current_view_bottom:
            # Calculer la nouvelle position de défilement pour centrer le résultat
            new_y = (widget_y - (canvas_height / 2)) / bbox[3]
            # Limiter la position entre 0 et 1
            new_y = max(0, min(1, new_y))
            self.main_canvas.yview_moveto(new_y)

    def next_search_result(self):
        """Passe au résultat de recherche suivant dans la vue hiérarchique"""
        if not self.search_results:
            return
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.highlight_search_result(self.search_results[self.current_search_index])

    def prev_search_result(self):
        """Passe au résultat de recherche précédent dans la vue hiérarchique"""
        if not self.search_results:
            return
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self.highlight_search_result(self.search_results[self.current_search_index])

    def save_flat_files(self, editor_window):
        """Sauvegarde les fichiers JSON plats"""
        try:
            # Récupérer les données
            fr_data = {}
            en_data = {}
            es_data = {}

            for key in editor_window.all_keys:
                for row_idx, k in enumerate(editor_window.all_keys, start=1):
                    if k == key:
                        fr_data[key] = editor_window.entry_vars[(row_idx, "fr")].get()
                        en_data[key] = editor_window.entry_vars[(row_idx, "en")].get()
                        es_data[key] = editor_window.entry_vars[(row_idx, "es")].get()
                        break

            # Sauvegarder les fichiers
            files_to_save = [
                (editor_window.fr_path, fr_data),
                (editor_window.en_path, en_data),
                (editor_window.es_path, es_data)
            ]

            for path, data in files_to_save:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            self.status.config(text="✅ Fichiers plats sauvegardés")
        except Exception as e:
            self.status.config(text=f"❌ Erreur lors de la sauvegarde: {str(e)}")
            print(f"Erreur lors de la sauvegarde des fichiers plats: {e}")

def launch_app():
    root = tk.Tk()
    app = FaultEditor(root)
    root.mainloop()

if __name__ == "__main__":
    launch_app()
