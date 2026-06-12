import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import random
import threading
import datetime
from PIL import Image, ImageTk

# 1. BASE DE DATOS COMPLETA DE GRUPOS
grupos_equipos = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "Rep. Checa"],
    "Grupo B": ["Canadá", "Qatar", "Suiza", "Bosnia"],
    "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "Grupo D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "Grupo E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "Grupo F": ["Países Bajos", "Japón", "Túnez", "Suecia"],
    "Grupo G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "Grupo H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "Grupo I": ["Francia", "Irak", "Senegal", "Noruega"],
    "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "Grupo K": ["Congo", "Portugal", "Uzbekistán", "Colombia"],
    "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
}

class FixtureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fixture Mundial 2026 🏆")
        self.root.geometry("950x850") 
        self.root.configure(bg="#1e3d2f") 
        
        # --- MENÚ SUPERIOR ---
        self.menubar = tk.Menu(self.root)
        self.acerca_menu = tk.Menu(self.menubar, tearoff=0)
        self.acerca_menu.add_command(label="Info", command=self.mostrar_info)
        self.menubar.add_cascade(label="Acerca de", menu=self.acerca_menu)
        self.root.config(menu=self.menubar)

        # --- RUTAS ---
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))

        self.archivo_guardado = os.path.join(self.script_dir, "progreso_fixture.json")
        self.carpeta_banderas = os.path.join(self.script_dir, "banderas")
        self.ruta_icono = os.path.join(self.script_dir, "icono.ico")
        
        if os.path.exists(self.ruta_icono):
            try: self.root.iconbitmap(self.ruta_icono)
            except Exception: pass
        
        if not os.path.exists(self.carpeta_banderas):
            try: os.makedirs(self.carpeta_banderas)
            except Exception: pass
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # --- GENERACIÓN INICIAL DE PARTIDOS ---
        self.partidos_grupos = {}
        for g, equipos in grupos_equipos.items():
            # Cruces base de un grupo de 4 equipos
            partidos_base = [
                {"l": equipos[0], "v": equipos[1], "res_l": "", "res_v": ""},
                {"l": equipos[2], "v": equipos[3], "res_l": "", "res_v": ""},
                {"l": equipos[0], "v": equipos[2], "res_l": "", "res_v": ""},
                {"l": equipos[1], "v": equipos[3], "res_l": "", "res_v": ""},
                {"l": equipos[3], "v": equipos[0], "res_l": "", "res_v": ""},
                {"l": equipos[1], "v": equipos[2], "res_l": "", "res_v": ""},
            ]
            self.partidos_grupos[g] = partidos_base
            
        self.llaves = {
            "16avos": [{"l": "Por Definir", "v": "Por Definir", "res_l": "", "res_v": "", "pen_l": "", "pen_v": ""} for _ in range(16)],
            "octavos": [{"l": "Por Definir", "v": "Por Definir", "res_l": "", "res_v": "", "pen_l": "", "pen_v": ""} for _ in range(8)],
            "cuartos": [{"l": "Por Definir", "v": "Por Definir", "res_l": "", "res_v": "", "pen_l": "", "pen_v": ""} for _ in range(4)],
            "semis": [{"l": "Por Definir", "v": "Por Definir", "res_l": "", "res_v": "", "pen_l": "", "pen_v": ""} for _ in range(2)],
            "final": [{"l": "Por Definir", "v": "Por Definir", "res_l": "", "res_v": "", "pen_l": "", "pen_v": ""} for _ in range(1)]
        }

        self.dict_banderas = {}
        self.cargar_imagenes_banderas()
        self.cargar_progreso_disco() # Aquí se fuerzan a guardar tus fechas exactas

        # Estilos visuales generales
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background="#1e3d2f", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#2e7d32", foreground="white", font=("Arial", 10, "bold"), padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#4caf50")], foreground=[("selected", "black")])
        
        self.style.configure("Treeview", background="#264d3b", foreground="white", fieldbackground="#264d3b", font=("Arial", 10, "bold"), borderwidth=0)
        self.style.configure("Treeview.Heading", background="#2e7d32", foreground="white", font=("Arial", 10, "bold"), borderwidth=1)
        self.style.map("Treeview", background=[("selected", "#4caf50")])

        # Notebook / Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_grupos = tk.Frame(self.notebook, bg="#264d3b")
        self.tab_16avos = tk.Frame(self.notebook, bg="#264d3b")
        self.tab_octavos = tk.Frame(self.notebook, bg="#264d3b")
        self.tab_cuartos = tk.Frame(self.notebook, bg="#264d3b")
        self.tab_semis = tk.Frame(self.notebook, bg="#264d3b")
        self.tab_final = tk.Frame(self.notebook, bg="#264d3b")
        
        self.notebook.add(self.tab_grupos, text="Fase de Grupos")
        self.notebook.add(self.tab_16avos, text="16°avos")
        self.notebook.add(self.tab_octavos, text="Octavos")
        self.notebook.add(self.tab_cuartos, text="Cuartos")
        self.notebook.add(self.tab_semis, text="Semis")
        self.notebook.add(self.tab_final, text="Final")

        self.setup_tab_grupos()
        self.setup_tab_eliminatorias("16avos", self.tab_16avos, "octavos")
        self.setup_tab_eliminatorias("octavos", self.tab_octavos, "cuartos")
        self.setup_tab_eliminatorias("cuartos", self.tab_cuartos, "semis")
        self.setup_tab_eliminatorias("semis", self.tab_semis, "final")
        self.setup_tab_eliminatorias("final", self.tab_final, None)
        
        # INICIAR EL BUCLE DE REVISIÓN DE HORA (ACTUALIZACIÓN A LAS 00:00Hs)
        self.ultima_fecha_revisada = datetime.datetime.now().strftime("%d/%m")
        self.loop_actualizar_fecha()

    def mostrar_info(self):
        messagebox.showinfo("Información", "App para el mundial actualizada con reloj dinámico")

    def calcular_calendario_defecto(self, l, v):
        # Mapeo usando frozenset para encontrar el partido sin importar el orden Local o Visitante
        calendario_real = {
            # Viernes 12 de junio
            frozenset(["Canadá", "Bosnia"]): ("12/06", "16:00"),
            frozenset(["Estados Unidos", "Paraguay"]): ("12/06", "22:00"),
            # Sábado 13 de junio
            frozenset(["Qatar", "Suiza"]): ("13/06", "16:00"),
            frozenset(["Brasil", "Marruecos"]): ("13/06", "19:00"),
            frozenset(["Haití", "Escocia"]): ("13/06", "22:00"),
            # Domingo 14 de junio
            frozenset(["Australia", "Turquía"]): ("14/06", "01:00"),
            frozenset(["Alemania", "Curazao"]): ("14/06", "14:00"),
            frozenset(["Países Bajos", "Japón"]): ("14/06", "17:00"),
            frozenset(["Costa de Marfil", "Ecuador"]): ("14/06", "20:00"),
            frozenset(["Suecia", "Túnez"]): ("14/06", "23:00"),
            # Lunes 15 de junio
            frozenset(["España", "Cabo Verde"]): ("15/06", "13:00"),
            frozenset(["Bélgica", "Egipto"]): ("15/06", "16:00"),
            frozenset(["Arabia Saudita", "Uruguay"]): ("15/06", "19:00"),
            frozenset(["Irán", "Nueva Zelanda"]): ("15/06", "22:00"),
            # Martes 16 de junio
            frozenset(["Francia", "Senegal"]): ("16/06", "16:00"),
            frozenset(["Irak", "Noruega"]): ("16/06", "19:00"),
            frozenset(["Argentina", "Argelia"]): ("16/06", "22:00"),
            # Miércoles 17 de junio
            frozenset(["Austria", "Jordania"]): ("17/06", "01:00"),
            frozenset(["Portugal", "Congo"]): ("17/06", "14:00"), # RD Congo adaptado al diccionario original
            frozenset(["Inglaterra", "Croacia"]): ("17/06", "17:00"),
            frozenset(["Ghana", "Panamá"]): ("17/06", "20:00"),
            frozenset(["Uzbekistán", "Colombia"]): ("17/06", "23:00"),
            # Jueves 18 de junio
            frozenset(["Rep. Checa", "Sudáfrica"]): ("18/06", "13:00"),
            frozenset(["Suiza", "Bosnia"]): ("18/06", "16:00"),
            frozenset(["Canadá", "Qatar"]): ("18/06", "19:00"),
            frozenset(["México", "Corea del Sur"]): ("18/06", "22:00"),
            # Viernes 19 de junio
            frozenset(["Estados Unidos", "Australia"]): ("19/06", "16:00"),
            frozenset(["Escocia", "Marruecos"]): ("19/06", "19:00"),
            frozenset(["Brasil", "Haití"]): ("19/06", "22:00"),
            # Sábado 20 de junio
            frozenset(["Turquía", "Paraguay"]): ("20/06", "01:00"),
            frozenset(["Países Bajos", "Suecia"]): ("20/06", "14:00"),
            frozenset(["Alemania", "Costa de Marfil"]): ("20/06", "17:00"),
            frozenset(["Ecuador", "Curazao"]): ("20/06", "21:00"),
            # Domingo 21 de junio
            frozenset(["Túnez", "Japón"]): ("21/06", "01:00"),
            frozenset(["España", "Arabia Saudita"]): ("21/06", "13:00"),
            frozenset(["Bélgica", "Irán"]): ("21/06", "16:00"),
            frozenset(["Uruguay", "Cabo Verde"]): ("21/06", "19:00"),
            frozenset(["Nueva Zelanda", "Egipto"]): ("21/06", "22:00"),
            # Lunes 22 de junio
            frozenset(["Argentina", "Austria"]): ("22/06", "14:00"),
            frozenset(["Francia", "Irak"]): ("22/06", "18:00"),
            frozenset(["Noruega", "Senegal"]): ("22/06", "21:00"),
            # Martes 23 de junio
            frozenset(["Jordania", "Argelia"]): ("23/06", "00:00"),
            frozenset(["Portugal", "Uzbekistán"]): ("23/06", "14:00"),
            frozenset(["Inglaterra", "Ghana"]): ("23/06", "17:00"),
            frozenset(["Panamá", "Croacia"]): ("23/06", "20:00"),
            frozenset(["Colombia", "Congo"]): ("23/06", "23:00"),
            # Miércoles 24 de junio
            frozenset(["Suiza", "Canadá"]): ("24/06", "16:00"),
            frozenset(["Bosnia", "Qatar"]): ("24/06", "16:00"),
            frozenset(["Marruecos", "Haití"]): ("24/06", "19:00"),
            frozenset(["Rep. Checa", "México"]): ("24/06", "22:00"),
            frozenset(["Sudáfrica", "Corea del Sur"]): ("24/06", "22:00"),
            # Jueves 25 de junio
            frozenset(["Ecuador", "Alemania"]): ("25/06", "17:00"),
            frozenset(["Curazao", "Costa de Marfil"]): ("25/06", "17:00"),
            frozenset(["Túnez", "Países Bajos"]): ("25/06", "20:00"),
            frozenset(["Japón", "Suecia"]): ("25/06", "20:00"),
            frozenset(["Turquía", "Estados Unidos"]): ("25/06", "23:00"),
            frozenset(["Paraguay", "Australia"]): ("25/06", "23:00"),
            # Viernes 26 de junio
            frozenset(["Noruega", "Francia"]): ("26/06", "16:00"),
            frozenset(["Senegal", "Irak"]): ("26/06", "16:00"),
            frozenset(["Uruguay", "España"]): ("26/06", "21:00"),
            frozenset(["Cabo Verde", "Arabia Saudita"]): ("26/06", "21:00"),
            # Sábado 27 de junio
            frozenset(["Nueva Zelanda", "Bélgica"]): ("27/06", "00:00"),
            frozenset(["Egipto", "Irán"]): ("27/06", "00:00"),
            frozenset(["Panamá", "Inglaterra"]): ("27/06", "18:00"),
            frozenset(["Croacia", "Ghana"]): ("27/06", "18:00"),
            frozenset(["Colombia", "Portugal"]): ("27/06", "20:30"),
            frozenset(["Congo", "Uzbekistán"]): ("27/06", "20:30"),
            frozenset(["Jordania", "Argentina"]): ("27/06", "23:00"),
            frozenset(["Argelia", "Austria"]): ("27/06", "23:00")
        }
        pareja = frozenset([l, v])
        # Si el partido no está en tu lista del 12 en adelante, se asume que pertenece a un día previo como el 11/06.
        return calendario_real.get(pareja, ("11/06", "12:00"))

    def cargar_imagenes_banderas(self):
        for grupo, equipos in grupos_equipos.items():
            for equipo in equipos:
                ruta_img = os.path.join(self.carpeta_banderas, f"{equipo}.png")
                if os.path.exists(ruta_img):
                    try: self.dict_banderas[equipo] = tk.PhotoImage(file=ruta_img)
                    except Exception: pass

    def setup_tab_grupos(self):
        top_frame = tk.Frame(self.tab_grupos, bg="#264d3b")
        top_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(top_frame, text="Selecciona Grupo:", bg="#264d3b", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        self.combo_grupo = ttk.Combobox(top_frame, values=list(grupos_equipos.keys()), state="readonly", font=("Arial", 11))
        self.combo_grupo.pack(side="left", padx=5)
        self.combo_grupo.current(0)
        self.combo_grupo.bind("<<ComboboxSelected>>", self.cargar_partidos_grupo)
        
        self.frame_partidos = tk.LabelFrame(self.tab_grupos, text="Partidos del Grupo", bg="#1a3327", fg="gold", font=("Arial", 12, "bold"), padx=15, pady=10)
        self.frame_partidos.pack(fill="x", padx=20, pady=(5, 10))
        
        self.frame_tabla = tk.LabelFrame(self.tab_grupos, text="Tabla de Posiciones", bg="#1a3327", fg="cyan", font=("Arial", 12, "bold"), padx=15, pady=10)
        self.frame_tabla.pack(fill="x", padx=20, pady=(5, 10))
        
        columnas = ("pos", "equipo", "pts", "pj", "pg", "pe", "pp", "gf", "gc", "dif")
        self.tree_tabla = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings", height=4)
        
        anchos = {"pos": 30, "equipo": 150, "pts": 45, "pj": 40, "pg": 40, "pe": 40, "pp": 40, "gf": 40, "gc": 40, "dif": 40}
        titulos = {"pos": "#", "equipo": "Equipo", "pts": "PTS", "pj": "PJ", "pg": "G", "pe": "E", "pp": "P", "gf": "GF", "gc": "GC", "dif": "DIF"}
        
        for col in columnas:
            self.tree_tabla.heading(col, text=titulos[col])
            align = "w" if col == "equipo" else "center"
            self.tree_tabla.column(col, width=anchos[col], anchor=align)
            
        self.tree_tabla.pack(fill="x")
        
        self.frame_proximos_root = tk.LabelFrame(
            self.tab_grupos, 
            text=" ENCUENTROS DEL DÍA ",
            font=("Arial", 12, "bold"),
            bg="#1a3327", 
            fg="white",
            bd=2,
            relief="groove"
        )
        self.frame_proximos_root.pack(fill="x", padx=20, pady=10)
        
        self.cargar_partidos_grupo(None)

    def cargar_partidos_grupo(self, event):
        for widget in self.frame_partidos.winfo_children():
            widget.destroy()
            
        grupo_sel = self.combo_grupo.get()
        partidos = self.partidos_grupos[grupo_sel]
        
        center_grid = tk.Frame(self.frame_partidos, bg="#1a3327")
        center_grid.pack(anchor="center", pady=5)
        
        for i, p in enumerate(partidos):
            py = 4 
            
            lbl_l = tk.Label(center_grid, text=p["l"], bg="#1a3327", fg="white", width=16, anchor="e", font=("Arial", 11, "bold"))
            lbl_l.grid(row=i, column=0, padx=(0, 6), pady=py)
            
            flag_l_frame = tk.Frame(center_grid, bg="#1a3327", width=35, height=20)
            flag_l_frame.grid(row=i, column=1, padx=(0, 10), pady=py)
            flag_l_frame.pack_propagate(False) 
            if p["l"] in self.dict_banderas:
                tk.Label(flag_l_frame, image=self.dict_banderas[p["l"]], bg="#1a3327").pack()
            
            ent_l = tk.Entry(center_grid, width=4, justify="center", font=("Arial", 11, "bold"))
            ent_l.insert(0, str(p["res_l"]))
            ent_l.grid(row=i, column=2, padx=5, pady=py)
            
            tk.Label(center_grid, text=" - ", bg="#1a3327", fg="gold", font=("Arial", 12, "bold")).grid(row=i, column=3, padx=5, pady=py)
            
            ent_v = tk.Entry(center_grid, width=4, justify="center", font=("Arial", 11, "bold"))
            ent_v.insert(0, str(p["res_v"]))
            ent_v.grid(row=i, column=4, padx=5, pady=py)
            
            flag_v_frame = tk.Frame(center_grid, bg="#1a3327", width=35, height=20)
            flag_v_frame.grid(row=i, column=5, padx=(10, 0), pady=py)
            flag_v_frame.pack_propagate(False) 
            if p["v"] in self.dict_banderas:
                tk.Label(flag_v_frame, image=self.dict_banderas[p["v"]], bg="#1a3327").pack()
            
            lbl_v = tk.Label(center_grid, text=p["v"], bg="#1a3327", fg="white", width=16, anchor="w", font=("Arial", 11, "bold"))
            lbl_v.grid(row=i, column=6, padx=(6, 0), pady=py)
            
            ent_l.bind("<FocusOut>", lambda e, g=grupo_sel, idx=i, el=ent_l, ev=ent_v: self.auto_guardar_grupo(g, idx, el, ev))
            ent_l.bind("<Return>", lambda e, g=grupo_sel, idx=i, el=ent_l, ev=ent_v: self.auto_guardar_grupo(g, idx, el, ev))
            ent_v.bind("<FocusOut>", lambda e, g=grupo_sel, idx=i, el=ent_l, ev=ent_v: self.auto_guardar_grupo(g, idx, el, ev))
            ent_v.bind("<Return>", lambda e, g=grupo_sel, idx=i, el=ent_l, ev=ent_v: self.auto_guardar_grupo(g, idx, el, ev))
            
        self.actualizar_tabla_ui()
        self.actualizar_proximos_encuentros()

    def obtener_estadisticas_grupo(self, grupo):
        stats = {e: {"pts": 0, "pj": 0, "pg": 0, "pe": 0, "pp": 0, "gf": 0, "gc": 0, "dg": 0, "nombre": e} for e in grupos_equipos[grupo]}
        for p in self.partidos_grupos[grupo]:
            if p["res_l"] != "" and p["res_v"] != "":
                gl, gv = int(p["res_l"]), int(p["res_v"])
                stats[p["l"]]["pj"] += 1
                stats[p["v"]]["pj"] += 1
                stats[p["l"]]["gf"] += gl
                stats[p["v"]]["gf"] += gv
                stats[p["l"]]["gc"] += gv
                stats[p["v"]]["gc"] += gl
                stats[p["l"]]["dg"] += (gl - gv)
                stats[p["v"]]["dg"] += (gv - gl)
                
                if gl > gv:
                    stats[p["l"]]["pts"] += 3
                    stats[p["l"]]["pg"] += 1
                    stats[p["v"]]["pp"] += 1
                elif gv > gl:
                    stats[p["v"]]["pts"] += 3
                    stats[p["v"]]["pg"] += 1
                    stats[p["l"]]["pp"] += 1
                else:
                    stats[p["l"]]["pts"] += 1
                    stats[p["v"]]["pts"] += 1
                    stats[p["l"]]["pe"] += 1
                    stats[p["v"]]["pe"] += 1
                    
        return sorted(stats.values(), key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)

    def loop_actualizar_fecha(self):
        # Cada minuto, revisamos si la fecha actual del sistema cruzó las 00:00 hs.
        fecha_actual_sistema = datetime.datetime.now().strftime("%d/%m")
        if self.ultima_fecha_revisada != fecha_actual_sistema:
            self.ultima_fecha_revisada = fecha_actual_sistema
            self.actualizar_proximos_encuentros()
            
        self.root.after(60000, self.loop_actualizar_fecha)

    def actualizar_proximos_encuentros(self):
        for widget in self.frame_proximos_root.winfo_children():
            widget.destroy()

        fecha_hoy = datetime.datetime.now().strftime("%d/%m")
        
        partidos_dia = []
        for grupo, lista_p in self.partidos_grupos.items():
            for p in lista_p:
                if p.get("fecha") == fecha_hoy and (p["res_l"] == "" or p["res_v"] == ""):
                    partidos_dia.append(p)
                    
        if not partidos_dia:
            lbl = tk.Label(self.frame_proximos_root, text=f"🏆 No hay partidos pendientes para la fecha {fecha_hoy}.", bg="#1a3327", fg="gold", font=("Arial", 11, "bold"))
            lbl.pack(pady=15)
            return

        partidos_dia = sorted(partidos_dia, key=lambda x: x.get("hora", "00:00"))

        frame_cabecera = tk.Frame(self.frame_proximos_root, bg="#2e7d32")
        frame_cabecera.pack(fill="x")
        
        lbl_cabecera = tk.Label(frame_cabecera, text=f"PARTIDOS PENDIENTES DEL DÍA: {fecha_hoy}", bg="#2e7d32", fg="white", font=("Arial", 12, "bold"), pady=4)
        lbl_cabecera.pack()

        frame_tabla_encuentros = tk.Frame(self.frame_proximos_root, bg="#11291e")
        frame_tabla_encuentros.pack(fill="x")

        for p in partidos_dia:
            fila = tk.Frame(frame_tabla_encuentros, bg="#11291e", highlightbackground="#1e3d2f", highlightthickness=1)
            fila.pack(fill="x", ipady=6)
            
            grid_interno = tk.Frame(fila, bg="#11291e")
            grid_interno.pack(anchor="center")
            
            lbl_hora = tk.Label(grid_interno, text=p.get("hora", "00:00"), bg="#11291e", fg="white", font=("Arial", 11, "bold"), width=8, anchor="center")
            lbl_hora.grid(row=0, column=0, padx=(10, 30))
            
            lbl_e1 = tk.Label(grid_interno, text=p["l"], bg="#11291e", fg="white", font=("Arial", 11, "bold"), width=15, anchor="e")
            lbl_e1.grid(row=0, column=1, padx=5)
            
            flag_l_frame = tk.Frame(grid_interno, bg="#11291e", width=30, height=20)
            flag_l_frame.grid(row=0, column=2, padx=5)
            flag_l_frame.pack_propagate(False)
            if p["l"] in self.dict_banderas:
                tk.Label(flag_l_frame, image=self.dict_banderas[p["l"]], bg="#11291e").pack()
                
            lbl_separador = tk.Label(grid_interno, text="-", bg="#11291e", fg="white", font=("Arial", 12, "bold"))
            lbl_separador.grid(row=0, column=3, padx=15)
            
            flag_v_frame = tk.Frame(grid_interno, bg="#11291e", width=30, height=20)
            flag_v_frame.grid(row=0, column=4, padx=5)
            flag_v_frame.pack_propagate(False)
            if p["v"] in self.dict_banderas:
                tk.Label(flag_v_frame, image=self.dict_banderas[p["v"]], bg="#11291e").pack()
                
            lbl_e2 = tk.Label(grid_interno, text=p["v"], bg="#11291e", fg="white", font=("Arial", 11, "bold"), width=15, anchor="w")
            lbl_e2.grid(row=0, column=5, padx=5)

    def actualizar_tabla_ui(self):
        for item in self.tree_tabla.get_children():
            self.tree_tabla.delete(item)
            
        grupo_sel = self.combo_grupo.get()
        stats = self.obtener_estadisticas_grupo(grupo_sel)
        
        for i, st in enumerate(stats):
            self.tree_tabla.insert("", "end", values=(
                i + 1, st["nombre"], st["pts"], st["pj"], st["pg"], st["pe"], st["pp"], st["gf"], st["gc"], st["dg"]
            ))

    def auto_guardar_grupo(self, grupo, idx, el, ev):
        val_l = el.get().strip()
        val_v = ev.get().strip()
        nuevo_l = int(val_l) if val_l.isdigit() else ""
        nuevo_v = int(val_v) if val_v.isdigit() else ""
        
        if self.partidos_grupos[grupo][idx]["res_l"] != nuevo_l or self.partidos_grupos[grupo][idx]["res_v"] != nuevo_v:
            self.partidos_grupos[grupo][idx]["res_l"] = nuevo_l
            self.partidos_grupos[grupo][idx]["res_v"] = nuevo_v
            self.guardar_progreso_disco()
            self.actualizar_tabla_ui() 
            self.actualizar_proximos_encuentros() 
            
            if nuevo_l != "" and nuevo_v != "":
                if self.verificar_todos_grupos_completos():
                    self.calcular_clasificados(silencioso=True)

    def verificar_todos_grupos_completos(self):
        for g in self.partidos_grupos.values():
            for p in g:
                if p["res_l"] == "" or p["res_v"] == "":
                    return False
        return True

    def calcular_clasificados(self, silencioso=False):
        clasificados = []
        terceros = []
        
        for g in self.partidos_grupos.keys():
            stats = self.obtener_estadisticas_grupo(g)
            clasificados.append(stats[0]["nombre"]) 
            clasificados.append(stats[1]["nombre"]) 
            terceros.append(stats[2])               

        mejores_terceros = sorted(terceros, key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)[:8]
        for t in mejores_terceros:
            clasificados.append(t["nombre"])

        for i in range(16):
            self.llaves["16avos"][i]["l"] = clasificados[i]
            self.llaves["16avos"][i]["v"] = clasificados[31 - i]
            
        self.guardar_progreso_disco()
        self.refresh_eliminatoria_ui("16avos")
        if not silencioso:
            messagebox.showinfo("Torneo Actualizado", "¡Fase de grupos procesada! Revisa los 16°avos.")

    def setup_tab_eliminatorias(self, fase_actual, frame_tab, fase_siguiente):
        canvas = tk.Canvas(frame_tab, bg="#264d3b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_tab, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#264d3b")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        frame_tab.scroll_frame = scroll_frame
        self.refresh_eliminatoria_ui(fase_actual)

    def refresh_eliminatoria_ui(self, fase_actual):
        frame = getattr(self, f"tab_{fase_actual}").scroll_frame
        for widget in frame.winfo_children():
            widget.destroy()
            
        tk.Label(frame, text=f"LLAVE DE {fase_actual.upper()}", bg="#264d3b", fg="gold", font=("Arial", 14, "bold")).pack(pady=10)
        
        for i, p in enumerate(self.llaves[fase_actual]):
            frame_match = tk.LabelFrame(frame, text=f"Partido {i+1}", bg="#1a3327", fg="white", padx=10, pady=5)
            frame_match.pack(fill="x", pady=5, padx=50)
            
            center_grid = tk.Frame(frame_match, bg="#1a3327")
            center_grid.pack(anchor="center")
            
            lbl_l = tk.Label(center_grid, text=p["l"], bg="#1a3327", fg="cyan" if p["l"] != "Por Definir" else "gray", width=20, anchor="e", font=("Arial", 10, "bold"))
            lbl_l.grid(row=0, column=0, padx=(0, 6))
            
            flag_l_frame = tk.Frame(center_grid, bg="#1a3327", width=35, height=20)
            flag_l_frame.grid(row=0, column=1, padx=(0, 5))
            flag_l_frame.pack_propagate(False)
            if p["l"] in self.dict_banderas:
                tk.Label(flag_l_frame, image=self.dict_banderas[p["l"]], bg="#1a3327").pack()
                
            is_tie = (str(p.get("res_l", "")) == str(p.get("res_v", "")) and str(p.get("res_l", "")) != "")

            e_pl = tk.Entry(center_grid, width=3, justify="center", font=("Arial", 9, "bold"), bg="#ffcc00", fg="black")
            if is_tie:
                tk.Label(center_grid, text="(", bg="#1a3327", fg="#ffcc00", font=("Arial", 10, "bold")).grid(row=0, column=2)
                e_pl.insert(0, str(p.get("pen_l", "")))
                e_pl.grid(row=0, column=3)
                tk.Label(center_grid, text=")", bg="#1a3327", fg="#ffcc00", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=(0, 5))

            el = tk.Entry(center_grid, width=4, justify="center", font=("Arial", 10, "bold"))
            el.insert(0, str(p["res_l"]))
            el.grid(row=0, column=5, padx=5)
            
            tk.Label(center_grid, text="vs", bg="#1a3327", fg="white").grid(row=0, column=6, padx=5)
            
            ev = tk.Entry(center_grid, width=4, justify="center", font=("Arial", 10, "bold"))
            ev.insert(0, str(p["res_v"]))
            ev.grid(row=0, column=7, padx=5)
            
            e_pv = tk.Entry(center_grid, width=3, justify="center", font=("Arial", 9, "bold"), bg="#ffcc00", fg="black")
            if is_tie:
                tk.Label(center_grid, text="(", bg="#1a3327", fg="#ffcc00", font=("Arial", 10, "bold")).grid(row=0, column=8, padx=(5, 0))
                e_pv.insert(0, str(p.get("pen_v", "")))
                e_pv.grid(row=0, column=9)
                tk.Label(center_grid, text=")", bg="#1a3327", fg="#ffcc00", font=("Arial", 10, "bold")).grid(row=0, column=10)
            
            flag_v_frame = tk.Frame(center_grid, bg="#1a3327", width=35, height=20)
            flag_v_frame.grid(row=0, column=11, padx=(5, 0))
            flag_v_frame.pack_propagate(False)
            if p["v"] in self.dict_banderas:
                tk.Label(flag_v_frame, image=self.dict_banderas[p["v"]], bg="#1a3327").pack()
            
            lbl_v = tk.Label(center_grid, text=p["v"], bg="#1a3327", fg="cyan" if p["v"] != "Por Definir" else "gray", width=20, anchor="w", font=("Arial", 10, "bold"))
            lbl_v.grid(row=0, column=12, padx=(6, 0))
            
            fase_sig = "octavos" if fase_actual == "16avos" else ("cuartos" if fase_actual == "octavos" else ("semis" if fase_actual == "cuartos" else ("final" if fase_actual == "semis" else None)))
            
            def bind_events(widget):
                widget.bind("<FocusOut>", lambda e, f=fase_actual, idx=i, fs=fase_sig, ent_l=el, ent_v=ev, epl=e_pl, epv=e_pv: self.auto_avanzar_eliminatoria(f, idx, fs, ent_l, ent_v, epl, epv))
                widget.bind("<Return>", lambda e, f=fase_actual, idx=i, fs=fase_sig, ent_l=el, ent_v=ev, epl=e_pl, epv=e_pv: self.auto_avanzar_eliminatoria(f, idx, fs, ent_l, ent_v, epl, epv))

            bind_events(el)
            bind_events(ev)
            if is_tie:
                bind_events(e_pl)
                bind_events(e_pv)

    def auto_avanzar_eliminatoria(self, fase_actual, idx, fase_siguiente, el, ev, e_pl, e_pv):
        p = self.llaves[fase_actual][idx]
        if p["l"] == "Por Definir" or p["v"] == "Por Definir": return
        val_l, val_v = el.get().strip(), ev.get().strip()
        
        if val_l == "" or val_v == "" or not val_l.isdigit() or not val_v.isdigit(): return
            
        gl, gv = int(val_l), int(val_v)
        
        pen_l_val = e_pl.get().strip() if e_pl.winfo_exists() else ""
        pen_v_val = e_pv.get().strip() if e_pv.winfo_exists() else ""
        
        pl = int(pen_l_val) if pen_l_val.isdigit() else ""
        pv = int(pen_v_val) if pen_v_val.isdigit() else ""

        was_tie = (str(p.get("res_l", "")) == str(p.get("res_v", "")) and str(p.get("res_l", "")) != "")
        is_tie = (gl == gv)
        
        if p.get("res_l") == gl and p.get("res_v") == gv and p.get("pen_l") == pl and p.get("pen_v") == pv:
            return

        p["res_l"], p["res_v"] = gl, gv
        p["pen_l"], p["pen_v"] = pl, pv
        self.guardar_progreso_disco()
        
        if was_tie != is_tie:
            self.refresh_eliminatoria_ui(fase_actual)
            return  
            
        if is_tie:
            if pl == "" or pv == "" or pl == pv:
                return 
            ganador = p["l"] if pl > pv else p["v"]
        else:
            p["pen_l"], p["pen_v"] = "", ""
            self.guardar_progreso_disco()
            ganador = p["l"] if gl > gv else p["v"]
            
        if fase_siguiente:
            idx_siguiente = idx // 2
            posicion = "l" if idx % 2 == 0 else "v"
            if self.llaves[fase_siguiente][idx_siguiente][posicion] != ganador:
                self.llaves[fase_siguiente][idx_siguiente][posicion] = ganador
                self.guardar_progreso_disco()
                self.refresh_eliminatoria_ui(fase_siguiente)
        else:
            self.celebrar_campeon(ganador)

    def celebrar_campeon(self, ganador):
        def reproducir_sonido():
            try:
                import winsound
                notas = [(523, 180), (659, 180), (784, 180), (1046, 500)]
                for freq, dur in notas: winsound.Beep(freq, dur)
            except Exception: pass
                
        threading.Thread(target=reproducir_sonido, daemon=True).start()

        v_cel = tk.Toplevel(self.root)
        v_cel.title("¡FIN DEL MUNDIAL!")
        v_cel.geometry("600x420")
        v_cel.configure(bg="black")
        v_cel.resizable(False, False)
        v_cel.transient(self.root)
        v_cel.grab_set()
        
        canvas = tk.Canvas(v_cel, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(300, 130, text="🥳 ¡¡¡ TENEMOS CAMPEÓN MUNDIAL !!! 🥳", fill="gold", font=("Arial", 20, "bold"))
        canvas.create_text(300, 220, text=f"🏆 {ganador.upper()} 🏆", fill="white", font=("Arial", 26, "bold"), justify="center")
        canvas.create_text(300, 310, text="¡Felicitaciones por completar el fixture!", fill="lightgreen", font=("Arial", 12, "italic"))
        
        particulas = []
        colores = ["red", "blue", "green", "yellow", "orange", "purple", "cyan", "magenta", "gold", "pink"]
        for _ in range(70):
            x, y = random.randint(10, 590), random.randint(-300, 0)
            w, h = random.randint(6, 12), random.randint(6, 12)
            p_id = canvas.create_rectangle(x, y, x+w, y+h, fill=random.choice(colores), outline="")
            particulas.append({"id": p_id, "x": x, "y": y, "vel": random.randint(3, 7)})
            
        def animar_confetti():
            if not v_cel.winfo_exists(): return
            for p in particulas:
                p["y"] += p["vel"]
                if p["y"] > 420:
                    p["y"], p["x"] = random.randint(-40, 0), random.randint(10, 590)
                    canvas.coords(p["id"], p["x"], p["y"], p["x"]+8, p["y"]+8)
                else: canvas.move(p["id"], 0, p["vel"])
            v_cel.after(25, animar_confetti)
        animar_confetti()

    def guardar_progreso_disco(self):
        try:
            data = {"partidos_grupos": self.partidos_grupos, "llaves": self.llaves}
            with open(self.archivo_guardado, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception: pass

    def cargar_progreso_disco(self):
        # 1. Cargamos el archivo JSON de tu computadora si existe
        if os.path.exists(self.archivo_guardado):
            try:
                with open(self.archivo_guardado, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.partidos_grupos = data.get("partidos_grupos", self.partidos_grupos)
                    self.llaves = data.get("llaves", self.llaves)
            except Exception: pass

        # 2. ¡EL TRUCO AQUÍ! Reemplazamos de manera forzada cualquier fecha vieja guardada
        #    en el archivo .json para asegurarnos de que solo use tus fechas de la lista real.
        for g, partidos in self.partidos_grupos.items():
            for p in partidos:
                fecha, hora = self.calcular_calendario_defecto(p["l"], p["v"])
                p["fecha"] = fecha
                p["hora"] = hora

    def on_closing(self):
        self.guardar_progreso_disco()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FixtureApp(root)
    root.mainloop()