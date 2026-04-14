import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_handler import DatabaseHandler
from core.smart_assistant import SmartAssistant
import core.history_handler as history


DARK = {
    "primary":        "#4f9cf9",
    "primary_hover":  "#3b82f6",
    "bg_window":      "#0f1117",
    "bg_panel":       "#1a1d27",
    "bg_card":        "#22263a",
    "bg_input":       "#2a2f45",
    "text_primary":   "#e8eaf0",
    "text_secondary": "#8b92a8",
    "text_muted":     "#555d7a",
    "border":         "#2e3350",
    "success":        "#4ade80",
    "error":          "#f87171",
    "user_bubble":    "#4f9cf9",
    "ai_bubble":      "#22263a",
}

LIGHT = {
    "primary":        "#2563eb",
    "primary_hover":  "#1d4ed8",
    "bg_window":      "#f1f5f9",
    "bg_panel":       "#ffffff",
    "bg_card":        "#f8fafc",
    "bg_input":       "#f1f5f9",
    "text_primary":   "#0f172a",
    "text_secondary": "#475569",
    "text_muted":     "#94a3b8",
    "border":         "#e2e8f0",
    "success":        "#16a34a",
    "error":          "#dc2626",
    "user_bubble":    "#2563eb",
    "ai_bubble":      "#f8fafc",
}


class LoginScreen:
    def __init__(self, parent, on_login_success, theme_mode="light"):
        self.parent = parent
        self.on_login_success = on_login_success
        self.theme_mode = theme_mode

        self.login_frame = ctk.CTkFrame(parent, fg_color=self._bg())
        self.login_frame.pack(fill="both", expand=True)
        self._build()

    # ── helpers ────────────────────────────────────────────────────────────────

    def _c(self):
        return DARK if self.theme_mode == "dark" else LIGHT

    def _bg(self):
        return self._c()["bg_window"]

    def _build(self):
        c = self._c()

        bg = ctk.CTkFrame(self.login_frame, fg_color=c["bg_window"], corner_radius=0)
        bg.pack(fill="both", expand=True)

        center = ctk.CTkFrame(bg, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(
            center,
            fg_color=c["bg_panel"],
            corner_radius=24,
            border_width=1,
            border_color=c["border"],
            width=460,
            height=620,
        )
        card.pack(padx=20, pady=20)
        card.pack_propagate(False)

        # ── theme toggle ──────────────────────────────────────────────────────
        self.theme_btn = ctk.CTkButton(
            card,
            text="🌙" if self.theme_mode == "dark" else "☀️",
            command=self._toggle_theme,
            width=40, height=40,
            corner_radius=20,
            fg_color="transparent",
            hover_color=c["bg_card"],
            border_width=1,
            border_color=c["border"],
            font=ctk.CTkFont(size=16),
        )
        self.theme_btn.place(relx=1.0, x=-16, y=16, anchor="ne")

        # ── logo ──────────────────────────────────────────────────────────────
        logo_bg = ctk.CTkFrame(card, fg_color=c["bg_card"], corner_radius=60, width=120, height=120)
        logo_bg.pack(pady=(50, 0))
        logo_bg.pack_propagate(False)
        try:
            img = Image.open(os.path.join("Img", "Logo.png")).resize((80, 80), Image.Resampling.LANCZOS)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
            lbl = ctk.CTkLabel(logo_bg, image=photo, text="")
            lbl.image = photo
            lbl.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            ctk.CTkLabel(logo_bg, text="S", font=ctk.CTkFont(size=48, weight="bold"),
                         text_color=c["primary"]).place(relx=0.5, rely=0.5, anchor="center")

        # ── title ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(card, text="SOUGUI AI",
                     font=ctk.CTkFont(size=36, weight="bold"),
                     text_color=c["primary"]).pack(pady=(16, 2))
        ctk.CTkLabel(card, text="Artisanat Tunisien",
                     font=ctk.CTkFont(size=12),
                     text_color=c["text_secondary"]).pack()
        ctk.CTkFrame(card, height=1, fg_color=c["border"]).pack(fill="x", padx=40, pady=16)

        # ── inputs ────────────────────────────────────────────────────────────
        inputs = ctk.CTkFrame(card, fg_color="transparent")
        inputs.pack(fill="x", padx=44)

        ctk.CTkLabel(inputs, text="NOM D'UTILISATEUR",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=c["primary"], anchor="w").pack(fill="x", pady=(0, 4))
        self.username_entry = ctk.CTkEntry(
            inputs,
            placeholder_text="Entrez votre nom d'utilisateur",
            height=48, corner_radius=14, border_width=1,
            border_color=c["border"], fg_color=c["bg_input"],
            text_color=c["text_primary"],
            placeholder_text_color=c["text_muted"],
            font=ctk.CTkFont(size=14),
        )
        self.username_entry.pack(fill="x", pady=(0, 14))
        self.username_entry.bind("<FocusIn>",  lambda e: self.username_entry.configure(border_color=c["primary"]))
        self.username_entry.bind("<FocusOut>", lambda e: self.username_entry.configure(border_color=c["border"]))

        ctk.CTkLabel(inputs, text="MOT DE PASSE",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=c["primary"], anchor="w").pack(fill="x", pady=(0, 4))
        self.password_entry = ctk.CTkEntry(
            inputs,
            placeholder_text="Entrez votre mot de passe",
            show="●", height=48, corner_radius=14, border_width=1,
            border_color=c["border"], fg_color=c["bg_input"],
            text_color=c["text_primary"],
            placeholder_text_color=c["text_muted"],
            font=ctk.CTkFont(size=14),
        )
        self.password_entry.pack(fill="x")
        self.password_entry.bind("<Return>", lambda e: self._login())
        self.password_entry.bind("<FocusIn>",  lambda e: self.password_entry.configure(border_color=c["primary"]))
        self.password_entry.bind("<FocusOut>", lambda e: self.password_entry.configure(border_color=c["border"]))

        # ── login button ──────────────────────────────────────────────────────
        ctk.CTkButton(
            card,
            text="ACCÉDER AU SYSTÈME",
            command=self._login,
            height=52, corner_radius=20,
            fg_color=c["primary"], hover_color=c["primary_hover"],
            text_color="#ffffff",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(fill="x", padx=44, pady=24)

        ctk.CTkLabel(card, text="Version 2.0 • Sougui AI",
                     font=ctk.CTkFont(size=10),
                     text_color=c["text_muted"]).pack()

        try:
            self.username_entry.focus_set()
        except Exception:
            pass

    def _toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        ctk.set_appearance_mode(self.theme_mode)
        self.login_frame.configure(fg_color=self._bg())
        # Unbind focus events before destroying to prevent stale callbacks
        try:
            self.username_entry.unbind("<FocusIn>")
            self.username_entry.unbind("<FocusOut>")
            self.password_entry.unbind("<FocusIn>")
            self.password_entry.unbind("<FocusOut>")
        except Exception:
            pass
        for w in self.login_frame.winfo_children():
            w.destroy()
        self._build()

    def _login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if u == "sougui" and p == "sougui":
            self.login_frame.destroy()
            self.on_login_success(self.theme_mode)
        else:
            messagebox.showerror("Accès refusé", "Identifiants incorrects")
            self.password_entry.delete(0, "end")
            try:
                self.username_entry.focus_set()
            except Exception:
                pass


class ChatbotUI:
    def __init__(self):
        self.smart_assistant = SmartAssistant()
        self.theme_mode = "light"
        self.colors = LIGHT.copy()
        self.current_session = None
        self._msg_count = 0
        self._stream_label = None
        self._stream_container = None
        self._sidebar_visible = True
        self._tw = []  # list of (widget, dark_cfg, light_cfg)

        ctk.set_appearance_mode("light")

        self.window = ctk.CTk()
        self.window.title("Sougui AI")
        self.window.geometry("1440x900")
        self.window.minsize(1100, 700)

        try:
            icon_path = os.path.join("Img", "Logo.png")
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path).resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.window.iconphoto(True, icon_photo)
                self.window.icon_photo = icon_photo
        except Exception:
            pass

        LoginScreen(self.window, self.on_login)

    # ── Theme ──────────────────────────────────────────────────────────────────

    def on_login(self, theme_mode):
        self.theme_mode = theme_mode
        self.colors = DARK.copy() if theme_mode == "dark" else LIGHT.copy()
        ctk.set_appearance_mode(theme_mode)
        self._build_main_ui()

    def toggle_theme(self):
        """In-place theme update — no widget destruction."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.colors = DARK.copy() if self.theme_mode == "dark" else LIGHT.copy()
        ctk.set_appearance_mode(self.theme_mode)
        self._apply_theme()

    def _apply_theme(self):
        for widget, dark_cfg, light_cfg in self._tw:
            try:
                cfg = dark_cfg if self.theme_mode == "dark" else light_cfg
                widget.configure(**cfg)
            except Exception:
                pass
        # Update theme button icon
        try:
            icon = "☀️" if self.theme_mode == "dark" else "🌙"
            self.theme_button.configure(text=icon)
        except Exception:
            pass

    def _reg(self, widget, dark_cfg: dict, light_cfg: dict):
        """Register a widget for in-place theme updates."""
        self._tw.append((widget, dark_cfg, light_cfg))
        return widget

    # ── Build UI ───────────────────────────────────────────────────────────────

    def _build_main_ui(self):
        c = self.colors
        self._tw = []

        # ── Root container ────────────────────────────────────────────────────
        root = ctk.CTkFrame(self.window, fg_color=c["bg_window"])
        root.pack(fill="both", expand=True)
        self._reg(root, {"fg_color": DARK["bg_window"]}, {"fg_color": LIGHT["bg_window"]})

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(root, height=64, corner_radius=0,
                              fg_color=c["bg_panel"], border_width=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        self._reg(header, {"fg_color": DARK["bg_panel"]}, {"fg_color": LIGHT["bg_panel"]})

        hcontent = ctk.CTkFrame(header, fg_color="transparent")
        hcontent.pack(fill="both", expand=True, padx=24)

        # Left: logo + title
        left_h = ctk.CTkFrame(hcontent, fg_color="transparent")
        left_h.pack(side="left", pady=10)
        try:
            img = Image.open(os.path.join("Img", "Logo.png")).resize((44, 44), Image.Resampling.LANCZOS)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(44, 44))
            lbl = ctk.CTkLabel(left_h, image=photo, text="")
            lbl.image = photo
            lbl.pack(side="left", padx=(0, 12))
        except Exception:
            pass

        tf = ctk.CTkFrame(left_h, fg_color="transparent")
        tf.pack(side="left")
        title_lbl = ctk.CTkLabel(tf, text="SOUGUI AI",
                                 font=ctk.CTkFont(size=20, weight="bold"),
                                 text_color=c["primary"])
        title_lbl.pack(anchor="w")
        self._reg(title_lbl, {"text_color": DARK["primary"]}, {"text_color": LIGHT["primary"]})
        sub_lbl = ctk.CTkLabel(tf, text="Chatbot Assistant",
                               font=ctk.CTkFont(size=10),
                               text_color=c["text_secondary"])
        sub_lbl.pack(anchor="w")
        self._reg(sub_lbl, {"text_color": DARK["text_secondary"]}, {"text_color": LIGHT["text_secondary"]})

        # Right: controls
        right_h = ctk.CTkFrame(hcontent, fg_color="transparent")
        right_h.pack(side="right", pady=10)

        self.disconnect_button = ctk.CTkButton(
            right_h, text="DÉCONNEXION", command=self.disconnect,
            width=120, height=36, corner_radius=12,
            fg_color=c["error"], hover_color="#b91c1c",
            text_color="#ffffff", font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.disconnect_button.pack(side="right", padx=(8, 0))
        self._reg(self.disconnect_button, {"fg_color": DARK["error"]}, {"fg_color": LIGHT["error"]})

        self.clear_button = ctk.CTkButton(
            right_h, text="EFFACER", command=self.clear_chat,
            width=90, height=36, corner_radius=12,
            fg_color=c["bg_card"], hover_color=c["bg_input"],
            text_color=c["text_secondary"], border_width=1, border_color=c["border"],
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.clear_button.pack(side="right", padx=(8, 0))
        self._reg(self.clear_button,
                  {"fg_color": DARK["bg_card"], "hover_color": DARK["bg_input"],
                   "text_color": DARK["text_secondary"], "border_color": DARK["border"]},
                  {"fg_color": LIGHT["bg_card"], "hover_color": LIGHT["bg_input"],
                   "text_color": LIGHT["text_secondary"], "border_color": LIGHT["border"]})

        self.theme_button = ctk.CTkButton(
            right_h,
            text="☀️" if self.theme_mode == "dark" else "🌙",
            command=self.toggle_theme,
            width=40, height=36, corner_radius=12,
            fg_color=c["bg_card"], hover_color=c["bg_input"],
            border_width=1, border_color=c["border"],
            font=ctk.CTkFont(size=15),
        )
        self.theme_button.pack(side="right", padx=(8, 0))
        self._reg(self.theme_button,
                  {"fg_color": DARK["bg_card"], "hover_color": DARK["bg_input"], "border_color": DARK["border"]},
                  {"fg_color": LIGHT["bg_card"], "hover_color": LIGHT["bg_input"], "border_color": LIGHT["border"]})

        # ── Body (sidebar + chat) ─────────────────────────────────────────────
        body = ctk.CTkFrame(root, fg_color=c["bg_window"])
        body.pack(fill="both", expand=True)
        self._reg(body, {"fg_color": DARK["bg_window"]}, {"fg_color": LIGHT["bg_window"]})
        self._body_ref = body

        self._build_sidebar(body)
        self._build_chat_panel(body)

        # ── Status bar ────────────────────────────────────────────────────────
        status_bar = ctk.CTkFrame(root, height=30, corner_radius=0,
                                  fg_color=c["bg_panel"], border_width=0)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        self._reg(status_bar, {"fg_color": DARK["bg_panel"]}, {"fg_color": LIGHT["bg_panel"]})

        self.status_label = ctk.CTkLabel(
            status_bar, text="SYSTÈME PRÊT",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=c["success"],
        )
        self.status_label.pack(side="left", padx=20)
        self._reg(self.status_label, {"text_color": DARK["success"]}, {"text_color": LIGHT["success"]})

        self.clock_label = ctk.CTkLabel(
            status_bar, text="",
            font=ctk.CTkFont(size=10),
            text_color=c["text_muted"],
        )
        self.clock_label.pack(side="right", padx=20)
        self._reg(self.clock_label, {"text_color": DARK["text_muted"]}, {"text_color": LIGHT["text_muted"]})
        self._update_clock()

        self.connect_database()

    def _build_sidebar(self, parent):
        c = self.colors

        self.sidebar = ctk.CTkFrame(
            parent, width=260,
            fg_color=c["bg_panel"], corner_radius=12,
            border_width=1, border_color=c["border"],
        )
        self.sidebar.pack(side="left", fill="y", padx=(10, 0), pady=10)
        self.sidebar.pack_propagate(False)
        self._reg(self.sidebar,
                  {"fg_color": DARK["bg_panel"], "border_color": DARK["border"]},
                  {"fg_color": LIGHT["bg_panel"], "border_color": LIGHT["border"]})

        # Top bar
        topbar = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=44)
        topbar.pack(fill="x", padx=10, pady=(10, 4))
        topbar.pack_propagate(False)

        hist_lbl = ctk.CTkLabel(topbar, text="HISTORIQUE",
                                font=ctk.CTkFont(size=11, weight="bold"),
                                text_color=c["primary"])
        hist_lbl.pack(side="left", pady=8)
        self._reg(hist_lbl, {"text_color": DARK["primary"]}, {"text_color": LIGHT["primary"]})

        new_btn = ctk.CTkButton(
            topbar, text="+", command=self._new_session,
            width=28, height=28, corner_radius=8,
            fg_color=c["primary"], hover_color=c["primary_hover"],
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff",
        )
        new_btn.pack(side="right", pady=8)
        self._reg(new_btn,
                  {"fg_color": DARK["primary"], "hover_color": DARK["primary_hover"]},
                  {"fg_color": LIGHT["primary"], "hover_color": LIGHT["primary_hover"]})

        self._collapse_btn = ctk.CTkButton(
            topbar, text="◀", command=self._toggle_sidebar,
            width=28, height=28, corner_radius=8,
            fg_color="transparent", hover_color=c["bg_card"],
            text_color=c["text_muted"], border_width=1, border_color=c["border"],
            font=ctk.CTkFont(size=11),
        )
        self._collapse_btn.pack(side="right", padx=(0, 4), pady=8)
        self._reg(self._collapse_btn,
                  {"hover_color": DARK["bg_card"], "text_color": DARK["text_muted"], "border_color": DARK["border"]},
                  {"hover_color": LIGHT["bg_card"], "text_color": LIGHT["text_muted"], "border_color": LIGHT["border"]})

        # Search
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_history_list())
        search_entry = ctk.CTkEntry(
            self.sidebar, textvariable=self._search_var,
            placeholder_text="Rechercher...",
            height=30, corner_radius=10, border_width=1,
            border_color=c["border"], fg_color=c["bg_card"],
            text_color=c["text_primary"],
            placeholder_text_color=c["text_muted"],
            font=ctk.CTkFont(size=11),
        )
        search_entry.pack(fill="x", padx=10, pady=(0, 6))
        self._reg(search_entry,
                  {"border_color": DARK["border"], "fg_color": DARK["bg_card"],
                   "text_color": DARK["text_primary"], "placeholder_text_color": DARK["text_muted"]},
                  {"border_color": LIGHT["border"], "fg_color": LIGHT["bg_card"],
                   "text_color": LIGHT["text_primary"], "placeholder_text_color": LIGHT["text_muted"]})

        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=c["border"])
        sep.pack(fill="x", padx=10)
        self._reg(sep, {"fg_color": DARK["border"]}, {"fg_color": LIGHT["border"]})

        # Session list
        self.history_list_frame = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", corner_radius=0)
        self.history_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Export button
        sep2 = ctk.CTkFrame(self.sidebar, height=1, fg_color=c["border"])
        sep2.pack(fill="x", padx=10)
        self._reg(sep2, {"fg_color": DARK["border"]}, {"fg_color": LIGHT["border"]})

        export_btn = ctk.CTkButton(
            self.sidebar, text="Exporter session", command=self._export_session,
            height=30, corner_radius=8,
            fg_color="transparent", hover_color=c["bg_card"],
            text_color=c["text_secondary"], border_width=1, border_color=c["border"],
            font=ctk.CTkFont(size=11),
        )
        export_btn.pack(fill="x", padx=10, pady=8)
        self._reg(export_btn,
                  {"hover_color": DARK["bg_card"], "text_color": DARK["text_secondary"], "border_color": DARK["border"]},
                  {"hover_color": LIGHT["bg_card"], "text_color": LIGHT["text_secondary"], "border_color": LIGHT["border"]})

    def _build_chat_panel(self, parent):
        c = self.colors

        self._main_panel = ctk.CTkFrame(parent, fg_color=c["bg_window"])
        self._main_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self._reg(self._main_panel, {"fg_color": DARK["bg_window"]}, {"fg_color": LIGHT["bg_window"]})

        # Messages area
        self.messages_frame = ctk.CTkScrollableFrame(
            self._main_panel,
            fg_color=c["bg_panel"], corner_radius=16,
            border_width=1, border_color=c["border"],
        )
        self.messages_frame.pack(fill="both", expand=True, pady=(0, 10))
        self._reg(self.messages_frame,
                  {"fg_color": DARK["bg_panel"], "border_color": DARK["border"]},
                  {"fg_color": LIGHT["bg_panel"], "border_color": LIGHT["border"]})

        # Quick actions
        quick_wrap = ctk.CTkFrame(self._main_panel, fg_color=c["bg_panel"],
                                  corner_radius=12, height=52,
                                  border_width=1, border_color=c["border"])
        quick_wrap.pack(fill="x", pady=(0, 10))
        quick_wrap.pack_propagate(False)
        self._reg(quick_wrap,
                  {"fg_color": DARK["bg_panel"], "border_color": DARK["border"]},
                  {"fg_color": LIGHT["bg_panel"], "border_color": LIGHT["border"]})

        quick_scroll = ctk.CTkScrollableFrame(
            quick_wrap, orientation="horizontal", height=42, fg_color="transparent")
        quick_scroll.pack(fill="both", expand=True, padx=8, pady=5)

        quick_questions = [
            ("REVENUS",      "Quel est mon chiffre d'affaires total et analyse de performance?"),
            ("CLIENTS",      "Montre-moi l'analyse détaillée de l'intelligence client"),
            ("PRODUITS",     "Fournis les métriques complètes de performance produits"),
            ("DASHBOARD",    "Génère le tableau de bord complet d'intelligence business"),
            ("INSIGHTS",     "Donne-moi des insights business avancés propulsés par l'IA"),
            ("ENTREPRISE",   "Parle-moi de l'expertise et des services de Sougui"),
            ("PERFORMANCE",  "Montre les statistiques de performance et d'analytique système"),
            ("AIDE",         "Quelles capacités avancées offres-tu?"),
        ]
        for label, question in quick_questions:
            btn = ctk.CTkButton(
                quick_scroll, text=label,
                command=lambda q=question: self.quick_question(q),
                height=32, corner_radius=16,
                fg_color="transparent", hover_color=c["bg_card"],
                text_color=c["primary"], border_width=1, border_color=c["primary"],
                font=ctk.CTkFont(size=10, weight="bold"),
            )
            btn.pack(side="left", padx=4)

        # Input area
        input_wrap = ctk.CTkFrame(self._main_panel, fg_color=c["bg_panel"],
                                  corner_radius=16, height=60,
                                  border_width=1, border_color=c["border"])
        input_wrap.pack(fill="x")
        input_wrap.pack_propagate(False)
        self._reg(input_wrap,
                  {"fg_color": DARK["bg_panel"], "border_color": DARK["border"]},
                  {"fg_color": LIGHT["bg_panel"], "border_color": LIGHT["border"]})

        self.input_field = ctk.CTkEntry(
            input_wrap,
            placeholder_text="Posez votre question...",
            font=ctk.CTkFont(size=13), height=44,
            corner_radius=12, border_width=0,
            fg_color=c["bg_input"],
            text_color=c["text_primary"],
            placeholder_text_color=c["text_muted"],
        )
        self.input_field.pack(side="left", fill="both", expand=True, padx=(12, 8), pady=8)
        self.input_field.bind("<Return>", lambda e: self.send_message())
        self.input_field.bind("<Escape>", lambda e: self.input_field.delete(0, "end"))
        self._reg(self.input_field,
                  {"fg_color": DARK["bg_input"], "text_color": DARK["text_primary"],
                   "placeholder_text_color": DARK["text_muted"]},
                  {"fg_color": LIGHT["bg_input"], "text_color": LIGHT["text_primary"],
                   "placeholder_text_color": LIGHT["text_muted"]})

        self.send_button = ctk.CTkButton(
            input_wrap, text="➤",
            command=self.send_message,
            width=44, height=44, corner_radius=12,
            fg_color=c["primary"], hover_color=c["primary_hover"],
            text_color="#ffffff", font=ctk.CTkFont(size=18),
        )
        self.send_button.pack(side="right", padx=(0, 10), pady=8)
        self._reg(self.send_button,
                  {"fg_color": DARK["primary"], "hover_color": DARK["primary_hover"]},
                  {"fg_color": LIGHT["primary"], "hover_color": LIGHT["primary_hover"]})

        try:
            self.input_field.focus_set()
        except Exception:
            pass

    # ── Clock ──────────────────────────────────────────────────────────────────

    def _update_clock(self):
        try:
            self.clock_label.configure(text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
            self.window.after(1000, self._update_clock)
        except Exception:
            pass

    # ── Clear chat ─────────────────────────────────────────────────────────────

    def clear_chat(self):
        for w in self.messages_frame.winfo_children():
            w.destroy()
        self.current_session = None
        self._msg_count = 0
        self.smart_assistant.reset_conversation()
        self.connect_database()

    # ── Disconnect ─────────────────────────────────────────────────────────────

    def disconnect(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter?"):
            self.window.destroy()
            import subprocess
            subprocess.Popen(["py.exe", "main.py"])

    # ── History management ─────────────────────────────────────────────────────

    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self.sidebar.pack_forget()
            self._sidebar_visible = False
            try:
                self._collapse_btn.configure(text="▶")
            except Exception:
                pass
        else:
            self.sidebar.pack(side="left", fill="y", padx=(10, 0), pady=10,
                              before=self._main_panel)
            self._sidebar_visible = True
            try:
                self._collapse_btn.configure(text="◀")
            except Exception:
                pass

    def _export_session(self):
        if not self.current_session or not self.current_session.get("messages"):
            messagebox.showinfo("Export", "Aucun message à exporter.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt"), ("Tous les fichiers", "*.*")],
            initialfile=f"sougui_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            title="Exporter la session",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("=== Sougui AI — Session exportée ===\n")
                f.write(f"Titre : {self.current_session.get('title', '')}\n")
                f.write(f"Date  : {self.current_session.get('date', '')}\n")
                f.write("=" * 50 + "\n\n")
                for msg in self.current_session["messages"]:
                    role = "Vous" if msg["role"] == "user" else "Sougui AI"
                    ts = msg.get("timestamp", "")
                    f.write(f"[{ts}] {role}:\n{msg['content']}\n\n")
            self.update_status(f"Session exportée → {os.path.basename(path)}")
            self.window.after(3000, lambda: self.update_status("SYSTÈME OPÉRATIONNEL"))
        except Exception as e:
            messagebox.showerror("Erreur", f"Export échoué: {e}")

    def _new_session(self):
        self.current_session = history.new_session()
        self._msg_count = 0
        for w in self.messages_frame.winfo_children():
            w.destroy()
        self.smart_assistant.reset_conversation()
        self._refresh_history_list()
        self.connect_database()

    def _refresh_history_list(self):
        for w in self.history_list_frame.winfo_children():
            w.destroy()
        query = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        sessions = history.load_all()
        filtered = [s for s in sessions if query in s.get("title", "").lower()] if query else sessions
        if not filtered:
            ctk.CTkLabel(
                self.history_list_frame, text="Aucune session",
                font=ctk.CTkFont(size=11), text_color=self.colors["text_muted"],
            ).pack(pady=20)
            return
        for s in filtered:
            self._add_session_row(s)

    def _add_session_row(self, session: dict):
        c = self.colors
        is_active = self.current_session and session["id"] == self.current_session["id"]
        msg_count = len(session.get("messages", []))

        row = ctk.CTkFrame(
            self.history_list_frame,
            fg_color=c["primary"] if is_active else c["bg_card"],
            corner_radius=10, height=60,
        )
        row.pack(fill="x", pady=2, padx=3)
        row.pack_propagate(False)

        meta = ctk.CTkFrame(row, fg_color="transparent")
        meta.pack(fill="x", padx=10, pady=(6, 0))

        try:
            dt = datetime.fromisoformat(session["date"])
            date_str = dt.strftime("%d/%m %H:%M")
        except Exception:
            date_str = ""

        ctk.CTkLabel(meta, text=date_str, font=ctk.CTkFont(size=9),
                     text_color="#cccccc" if is_active else c["text_muted"]).pack(side="left")
        ctk.CTkLabel(meta, text=f"{msg_count} msg", font=ctk.CTkFont(size=9),
                     text_color="#cccccc" if is_active else c["text_muted"]).pack(side="right")

        title = session.get("title", "Session")[:30]
        title_lbl = ctk.CTkLabel(
            row, text=title,
            font=ctk.CTkFont(size=11, weight="bold" if is_active else "normal"),
            text_color="#ffffff" if is_active else c["text_primary"],
            anchor="w",
        )
        title_lbl.pack(anchor="w", padx=10, pady=(2, 6))

        for widget in (row, title_lbl, meta):
            widget.bind("<Button-1>",        lambda e, sid=session["id"]: self._load_session(sid))
            widget.bind("<Double-Button-1>", lambda e, sid=session["id"]: self._rename_session(sid))
            widget.bind("<Button-3>",        lambda e, sid=session["id"]: self._confirm_delete_session(sid))

    def _rename_session(self, session_id: str):
        s = history.get_session(session_id)
        if not s:
            return
        new_title = simpledialog.askstring("Renommer", "Nouveau titre:", initialvalue=s.get("title", ""))
        if new_title and new_title.strip():
            sessions = history.load_all()
            for sess in sessions:
                if sess["id"] == session_id:
                    sess["title"] = new_title.strip()
                    break
            history._save_all(sessions)
            if self.current_session and self.current_session["id"] == session_id:
                self.current_session["title"] = new_title.strip()
            self._refresh_history_list()

    def _load_session(self, session_id: str):
        s = history.get_session(session_id)
        if not s:
            return
        self.current_session = s
        self._msg_count = len(s.get("messages", []))
        for w in self.messages_frame.winfo_children():
            w.destroy()
        for msg in s["messages"]:
            sender = "USER" if msg["role"] == "user" else "SOUGUI AI"
            self.add_message(sender, msg["content"], msg["role"], persist=False)
        self._refresh_history_list()
        self.update_status(f"Session chargée — {s['title'][:40]}")

    def _confirm_delete_session(self, session_id: str):
        if messagebox.askyesno("Supprimer", "Supprimer cette session?"):
            history.delete_session(session_id)
            if self.current_session and self.current_session["id"] == session_id:
                self.current_session = None
                self._msg_count = 0
                for w in self.messages_frame.winfo_children():
                    w.destroy()
                self.connect_database()
            else:
                self._refresh_history_list()

    # ── Database / welcome ─────────────────────────────────────────────────────

    def connect_database(self):
        self.update_status("INITIALISATION DU SYSTÈME...")

        if self.current_session is None:
            self.current_session = history.new_session()
            self._refresh_history_list()

        welcome_text = (
            "Bienvenue sur Sougui AI — votre plateforme d'intelligence business.\n\n"
            "Posez vos questions en français ou en anglais. Exemples:\n"
            "  • Quel est mon chiffre d'affaires total?\n"
            "  • Montre-moi les meilleurs clients\n"
            "  • Analyse les performances produits\n\n"
            "Utilisez les boutons rapides ci-dessus pour démarrer."
        )
        self.add_message("SOUGUI AI", welcome_text, "assistant", persist=False)
        self.update_status("SYSTÈME OPÉRATIONNEL")

    # ── Quick question ─────────────────────────────────────────────────────────

    def quick_question(self, question):
        self.input_field.delete(0, "end")
        self.input_field.insert(0, question)
        self.send_message()

    # ── Send message ───────────────────────────────────────────────────────────

    def send_message(self):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.input_field.delete(0, "end")
        self.add_message("USER", user_input, "user")

        if self.current_session:
            history.append_message(self.current_session["id"], "user", user_input)
            self._refresh_history_list()

        self._show_typing_indicator()
        self._start_loading()
        self.input_field.configure(state="disabled")
        self.update_status("Analyse en cours...")

        self._stream_label = None

        def on_response(text, streaming=True):
            def _update():
                if streaming:
                    if self._stream_label is None:
                        self._remove_typing_indicator()
                        self._stream_label = self._create_stream_bubble()
                    try:
                        if self._stream_label and self._stream_label.winfo_exists():
                            self._stream_label.configure(text=text)
                            self.messages_frame._parent_canvas.yview_moveto(1.0)
                    except Exception:
                        pass
                else:
                    try:
                        if hasattr(self, "_stream_container") and self._stream_container.winfo_exists():
                            self._stream_container.destroy()
                    except Exception:
                        pass
                    self._stream_label = None
                    self._remove_typing_indicator()
                    self.add_message("SOUGUI AI", text, "assistant")
                    if self.current_session:
                        history.append_message(self.current_session["id"], "assistant", text)
                    self._enable_input()
                    self.update_status("SYSTÈME OPÉRATIONNEL")
            self.window.after(0, _update)

        self.smart_assistant.answer_question(user_input, on_response)

    def _start_loading(self):
        self.send_button.configure(state="disabled")
        self._loading_active = True
        self._loading_dots = 0
        self._animate_loading()

    def _animate_loading(self):
        if not getattr(self, "_loading_active", False):
            return
        try:
            if self.send_button.winfo_exists():
                dots = "." * (self._loading_dots % 4)
                self.send_button.configure(text=f"•{dots}")
                self._loading_dots += 1
                self.window.after(300, self._animate_loading)
        except Exception:
            pass

    def _enable_input(self):
        self._loading_active = False
        try:
            self.send_button.configure(state="normal", text="➤")
        except Exception:
            pass
        try:
            self.input_field.configure(state="normal")
            self.input_field.focus_set()
        except Exception:
            pass

    # ── Streaming bubbles ──────────────────────────────────────────────────────

    def _create_stream_bubble(self):
        c = self.colors
        self._stream_container = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        self._stream_container.pack(fill="x", padx=16, pady=6)

        header = ctk.CTkFrame(self._stream_container, fg_color="transparent")
        header.pack(side="top", anchor="w", fill="x")
        ctk.CTkLabel(header, text="SOUGUI AI",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=c["primary"]).pack(side="left")
        ctk.CTkLabel(header, text=datetime.now().strftime("%H:%M"),
                     font=ctk.CTkFont(size=9),
                     text_color=c["text_muted"]).pack(side="left", padx=(8, 0))

        bubble = ctk.CTkFrame(self._stream_container,
                              fg_color=c["ai_bubble"], corner_radius=16,
                              border_width=1, border_color=c["border"])
        bubble.pack(side="top", anchor="w", padx=(0, 120), fill="x", expand=True)

        label = ctk.CTkLabel(bubble, text="",
                             font=ctk.CTkFont(size=13),
                             text_color=c["text_primary"],
                             wraplength=620, justify="left", anchor="w")
        label.pack(padx=16, pady=12, anchor="w")
        self.messages_frame._parent_canvas.yview_moveto(1.0)
        return label

    def _show_typing_indicator(self):
        c = self.colors
        self._typing_container = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        self._typing_container.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(self._typing_container, text="SOUGUI AI",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=c["primary"]).pack(side="left", anchor="w")

        bubble = ctk.CTkFrame(self._typing_container,
                              fg_color=c["ai_bubble"], corner_radius=16,
                              border_width=1, border_color=c["border"])
        bubble.pack(side="left", anchor="w", padx=(10, 0))

        self._typing_label = ctk.CTkLabel(bubble, text="  •  •  •  ",
                                          font=ctk.CTkFont(size=16),
                                          text_color=c["primary"])
        self._typing_label.pack(padx=14, pady=10)
        self._typing_dot_state = 0
        self._animate_typing()
        self.window.after(100, lambda: self.messages_frame._parent_canvas.yview_moveto(1.0))

    def _animate_typing(self):
        if not hasattr(self, "_typing_label") or not self._typing_label.winfo_exists():
            return
        frames = ["  •        ", "     •     ", "        •  "]
        self._typing_label.configure(text=frames[self._typing_dot_state % 3])
        self._typing_dot_state += 1
        self._typing_anim_id = self.window.after(400, self._animate_typing)

    def _remove_typing_indicator(self):
        try:
            if hasattr(self, "_typing_anim_id"):
                self.window.after_cancel(self._typing_anim_id)
            if hasattr(self, "_typing_container") and self._typing_container.winfo_exists():
                self._typing_container.destroy()
        except Exception:
            pass

    # ── Add message ────────────────────────────────────────────────────────────

    def add_message(self, sender, message, msg_type="user", persist=True):
        c = self.colors
        timestamp = datetime.now().strftime("%H:%M")

        if persist:
            self._msg_count += 1

        container = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        container.pack(fill="x", padx=16, pady=6)

        if msg_type == "user":
            ctk.CTkLabel(container, text=timestamp,
                         font=ctk.CTkFont(size=9),
                         text_color=c["text_muted"]).pack(side="right", anchor="e", padx=(0, 8))

            bubble = ctk.CTkFrame(container, fg_color=c["user_bubble"], corner_radius=16)
            bubble.pack(side="right", anchor="e", padx=(120, 0))

            ctk.CTkLabel(bubble, text=message,
                         font=ctk.CTkFont(size=13),
                         text_color="#ffffff",
                         wraplength=500, justify="left").pack(padx=16, pady=12)
        else:
            header_row = ctk.CTkFrame(container, fg_color="transparent")
            header_row.pack(side="top", anchor="w", fill="x")
            ctk.CTkLabel(header_row, text=sender,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=c["primary"]).pack(side="left", anchor="w")
            ctk.CTkLabel(header_row, text=timestamp,
                         font=ctk.CTkFont(size=9),
                         text_color=c["text_muted"]).pack(side="left", anchor="w", padx=(8, 0))

            bubble = ctk.CTkFrame(container, fg_color=c["ai_bubble"],
                                  corner_radius=16, border_width=1, border_color=c["border"])
            bubble.pack(side="top", anchor="w", padx=(0, 120), fill="x", expand=True)

            self._render_markdown(bubble, message)

            action_row = ctk.CTkFrame(bubble, fg_color="transparent")
            action_row.pack(anchor="e", padx=12, pady=(0, 6))
            ctk.CTkButton(
                action_row, text="Copier",
                command=lambda m=message: self._copy_to_clipboard(m),
                width=60, height=22,
                font=ctk.CTkFont(size=10), corner_radius=8,
                fg_color="transparent", hover_color=c["bg_card"],
                text_color=c["text_muted"], border_width=1, border_color=c["border"],
            ).pack(side="right")

        self.window.after(100, lambda: self.messages_frame._parent_canvas.yview_moveto(1.0))

    # ── Markdown renderer ──────────────────────────────────────────────────────

    def _render_markdown(self, parent, text):
        """Render markdown: ## headers, **bold**, ``` code, - lists, numbered lists, tables."""
        c = self.colors
        lines = text.split("\n")
        in_code = False
        code_lines = []
        in_table = False
        table_rows = []

        def flush_table():
            nonlocal table_rows, in_table
            if not table_rows:
                return
            tframe = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=8)
            tframe.pack(fill="x", padx=16, pady=6)
            for ri, row_cells in enumerate(table_rows):
                rframe = ctk.CTkFrame(tframe, fg_color="transparent")
                rframe.pack(fill="x", padx=4, pady=1)
                for cell in row_cells:
                    is_header = ri == 0
                    ctk.CTkLabel(
                        rframe, text=cell.strip(),
                        font=ctk.CTkFont(size=11, weight="bold" if is_header else "normal"),
                        text_color=c["primary"] if is_header else c["text_primary"],
                        anchor="w", width=140,
                    ).pack(side="left", padx=4)
            table_rows.clear()
            in_table = False

        def render_inline(parent_frame, text_line):
            parts = re.split(r'(\*\*[^*]+\*\*)', text_line)
            if len(parts) == 1:
                ctk.CTkLabel(
                    parent_frame, text=text_line,
                    font=ctk.CTkFont(size=13),
                    text_color=c["text_primary"],
                    justify="left", anchor="w", wraplength=580,
                ).pack(padx=16, pady=1, anchor="w")
                return
            row = ctk.CTkFrame(parent_frame, fg_color="transparent")
            row.pack(padx=16, pady=1, anchor="w", fill="x")
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    ctk.CTkLabel(row, text=part[2:-2],
                                 font=ctk.CTkFont(size=13, weight="bold"),
                                 text_color=c["text_primary"],
                                 justify="left", anchor="w").pack(side="left")
                elif part:
                    ctk.CTkLabel(row, text=part,
                                 font=ctk.CTkFont(size=13),
                                 text_color=c["text_primary"],
                                 justify="left", anchor="w").pack(side="left")

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                if in_code:
                    cf = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=8)
                    cf.pack(fill="x", padx=16, pady=6)
                    ctk.CTkLabel(cf, text="\n".join(code_lines),
                                 font=ctk.CTkFont(size=11, family="Courier New"),
                                 text_color=c["success"],
                                 justify="left", anchor="w", wraplength=560).pack(padx=12, pady=8, anchor="w")
                    code_lines.clear()
                    in_code = False
                else:
                    in_code = True
                continue

            if in_code:
                code_lines.append(line)
                continue

            if stripped.startswith("|") and stripped.endswith("|"):
                cells = [c2 for c2 in stripped.split("|") if c2.strip() not in ("", "---", ":---", "---:")]
                if cells:
                    if all(set(c2.strip()) <= set("-: ") for c2 in cells):
                        continue
                    in_table = True
                    table_rows.append(cells)
                continue
            elif in_table:
                flush_table()

            if stripped == "":
                ctk.CTkFrame(parent, height=4, fg_color="transparent").pack()
                continue

            if stripped.startswith("# ") and not stripped.startswith("## "):
                ctk.CTkLabel(parent, text=stripped[2:],
                             font=ctk.CTkFont(size=16, weight="bold"),
                             text_color=c["primary"],
                             justify="left", anchor="w", wraplength=580).pack(padx=16, pady=(8, 2), anchor="w")
            elif stripped.startswith("## "):
                ctk.CTkLabel(parent, text=stripped[3:],
                             font=ctk.CTkFont(size=14, weight="bold"),
                             text_color=c["primary"],
                             justify="left", anchor="w", wraplength=580).pack(padx=16, pady=(6, 2), anchor="w")
            elif stripped.startswith("### "):
                ctk.CTkLabel(parent, text=stripped[4:],
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=c["primary"],
                             justify="left", anchor="w", wraplength=580).pack(padx=16, pady=(4, 2), anchor="w")
            elif stripped in ("---", "***", "___"):
                ctk.CTkFrame(parent, height=1, fg_color=c["border"]).pack(fill="x", padx=16, pady=4)
            elif stripped.startswith(("- ", "* ", "• ", "▸ ")):
                content = stripped[2:]
                row = ctk.CTkFrame(parent, fg_color="transparent")
                row.pack(padx=16, pady=1, anchor="w", fill="x")
                ctk.CTkLabel(row, text="•", font=ctk.CTkFont(size=13),
                             text_color=c["primary"], width=16).pack(side="left", anchor="nw", padx=(0, 4))
                render_inline(row, content)
            elif re.match(r'^\d+\.\s', stripped):
                num, content = stripped.split(". ", 1)
                row = ctk.CTkFrame(parent, fg_color="transparent")
                row.pack(padx=16, pady=1, anchor="w", fill="x")
                ctk.CTkLabel(row, text=f"{num}.", font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=c["primary"], width=28).pack(side="left", anchor="nw")
                render_inline(row, content)
            else:
                render_inline(parent, stripped)

        if in_table:
            flush_table()
        if in_code and code_lines:
            cf = ctk.CTkFrame(parent, fg_color=c["bg_card"], corner_radius=8)
            cf.pack(fill="x", padx=16, pady=6)
            ctk.CTkLabel(cf, text="\n".join(code_lines),
                         font=ctk.CTkFont(size=11, family="Courier New"),
                         text_color=c["success"],
                         justify="left", anchor="w", wraplength=560).pack(padx=12, pady=8, anchor="w")

    # ── Utilities ──────────────────────────────────────────────────────────────

    def _copy_to_clipboard(self, text):
        try:
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            self.update_status("Copié dans le presse-papiers")
            self.window.after(2000, lambda: self.update_status("SYSTÈME OPÉRATIONNEL"))
        except Exception:
            pass

    def update_status(self, status):
        try:
            self.status_label.configure(text=status)
        except Exception:
            pass

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = ChatbotUI()
    app.run()
