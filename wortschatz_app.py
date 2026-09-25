"""
wortschatz_app.py - Windows 11 German Flashcards Learning Application

Features:
- Two Distinct, Non-Convoluted Modes:
    1. 📖 Explore Mode:
       - Casual reading, browsing, and vocabulary discovery at your own pace.
       - Standard navigation: Previous (← / 1), Flip (Space), Next (→ / 2).
       - Zero test pressure: No ratings, no mastery badges cluttering the card, pure study.
       - Features: Reverse (DE ⇄ EN), Shuffle, Audio speech, Search (Ctrl+F), Add (Ctrl+N).
    2. 🎯 Quiz Mode:
       - Structured active recall testing and memory retention.
       - Workflow: Prompt -> Reveal Answer (Space) -> Rate: [1] Needs Practice or [2] Mastered.
       - In-session score tracking (e.g. Session: 8/10 • 80% accuracy).
       - Retention Filters: Review 'Needs Practice Only', 'Mastered Only', or 'Unseen Only'.
       - Card Mastery Status Badges (🟢 Mastered / 🔴 Needs Practice / ⚪ Unseen).
       - Deck progress persistence in user_progress.json with study streak tracking.
- Smart In-line Grammar: Automatically parses plurals ('das Buch, die Bücher', '-¨er') and parenthetical notes.
- High-Quality Neural German TTS: 100% offline-ready cached speech via Edge-TTS & Windows MCI.
- Global Search (Ctrl + F) & In-App Quick-Add (Ctrl + N).
"""

import os
import random
import subprocess
import tkinter as tk
from typing import List, Dict, Optional

import customtkinter as ctk
from deck_loader import scan_decks, Flashcard
from audio_service import get_audio_service
from progress_manager import ProgressManager, STATUS_NEW, STATUS_LEARNING, STATUS_MASTERED


class WortschatzApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App Configuration
        self.title("Wortschatz — German Flashcards")
        self.geometry("980x760")
        self.minsize(840, 680)

        # Set Modern Windows 11 appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Working Directory & Services
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_svc = get_audio_service()
        self.progress_mgr = ProgressManager()

        # State Variables
        self.decks: Dict[str, List[Flashcard]] = {}
        self.current_category: str = ""
        self.active_cards: List[Flashcard] = []
        self.current_card_index: int = 0
        self.is_flipped: bool = False

        # Modes & Settings
        self.study_mode: str = "explore"      # "explore" vs "quiz"
        self.card_filter: str = "all"         # "all", "needs_practice", "mastered", "unseen"
        self.selected_level: str = "ALL"      # "ALL", "B1", "B2", "C1"
        self.shuffle_mode: bool = False
        self.reverse_mode: bool = False       # False: German->English, True: English->German
        self.auto_speak: bool = False         # Pronounce automatically on card reveal

        # Quiz Session Metrics
        self.quiz_session_reviewed: int = 0
        self.quiz_session_correct: int = 0
        self.quiz_session_practice: int = 0

        # Active Modal References
        self._search_window = None
        self._add_window = None
        self._preload_window = None
        self._preload_cancel = None
        self._reset_window = None

        # Build UI
        self._build_header()
        self._build_toolbar()
        self._build_stats_bar()
        self._build_card_area()
        self._build_action_buttons()
        self._build_footer()

        # Keyboard Bindings
        self._setup_keybindings()

        # Initial Load
        self.load_all_decks()

    # ================= UI BUILDERS =================

    def _build_header(self):
        """Top main bar: Brand, Category, Search, Add, Refresh, Theme."""
        self.header_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=("gray90", "#1e2229"))
        self.header_frame.pack(fill="x", padx=20, pady=(14, 6))

        # Brand Label
        brand_label = ctk.CTkLabel(
            self.header_frame,
            text="🇩🇪 Wortschatz",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=("gray10", "#f3f4f6"),
        )
        brand_label.pack(side="left", padx=(16, 12), pady=10)

        # CEFR Level Filter Segmented Button: [ All | B1 | B2 | C1 ]
        self.level_segment = ctk.CTkSegmentedButton(
            self.header_frame,
            values=["All", "B1", "B2", "C1"],
            command=self._on_level_filter_changed,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            width=180,
            dynamic_resizing=False,
        )
        self.level_segment.set("All")
        self.level_segment.pack(side="left", padx=(0, 8), pady=10)

        # Category Dropdown
        self.cat_var = tk.StringVar(value="Loading...")
        self.cat_menu = ctk.CTkOptionMenu(
            self.header_frame,
            variable=self.cat_var,
            values=["Loading..."],
            command=self._on_category_selected,
            width=210,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            dynamic_resizing=False,
        )
        self.cat_menu.pack(side="left", padx=4, pady=10)

        # Search Button (Ctrl+F)
        self.search_btn = ctk.CTkButton(
            self.header_frame,
            text="🔍 Search",
            width=75,
            command=self.open_search_modal,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.search_btn.pack(side="left", padx=4, pady=10)

        # Quick Add Button (Ctrl+N)
        self.add_btn = ctk.CTkButton(
            self.header_frame,
            text="➕ Add",
            width=65,
            command=self.open_add_modal,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.add_btn.pack(side="left", padx=4, pady=10)

        # Reload Button
        self.reload_btn = ctk.CTkButton(
            self.header_frame,
            text="🔄 Refresh",
            width=75,
            command=self.load_all_decks,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.reload_btn.pack(side="left", padx=4, pady=10)

        # Open Folder Button
        self.folder_btn = ctk.CTkButton(
            self.header_frame,
            text="📂 Decks",
            width=70,
            command=self._open_folder_in_explorer,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.folder_btn.pack(side="left", padx=4, pady=10)

        # Right side: Theme toggle
        self.theme_btn = ctk.CTkButton(
            self.header_frame,
            text="☀️ Theme",
            width=70,
            command=self._toggle_theme,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.theme_btn.pack(side="right", padx=(4, 14), pady=10)

        # Reset Metrics Button
        self.reset_metrics_btn = ctk.CTkButton(
            self.header_frame,
            text="↺ Reset Metrics",
            width=110,
            command=self.open_reset_metrics_modal,
            fg_color=("gray80", "#2d333b"),
            hover_color=("#ef4444", "#dc2626"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.reset_metrics_btn.pack(side="right", padx=4, pady=10)
        self.reset_btn = self.reset_metrics_btn

    def _build_toolbar(self):
        """Mode Switcher and Mode-Specific Control Row."""
        self.toolbar_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray95", "#161b22"))
        self.toolbar_frame.pack(fill="x", padx=20, pady=(2, 6))

        # Mode Selector: [ 📖 Explore | 🎯 Quiz ]
        self.mode_segment = ctk.CTkSegmentedButton(
            self.toolbar_frame,
            values=["📖 Explore", "🎯 Quiz"],
            command=self._on_study_mode_changed,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=200,
            dynamic_resizing=False,
        )
        self.mode_segment.set("📖 Explore")
        self.mode_segment.pack(side="left", padx=12, pady=6)

        # ============ Explore-Specific Widgets ============
        self.explore_tools_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        self.explore_tools_frame.pack(side="left", padx=8, pady=4)

        self.reverse_btn = ctk.CTkButton(
            self.explore_tools_frame,
            text="⇄ DE ➔ EN",
            width=95,
            command=self._toggle_reverse_mode,
            fg_color=("gray85", "#21262d"),
            hover_color=("gray75", "#30363d"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.reverse_btn.pack(side="left", padx=4)

        self.shuffle_btn = ctk.CTkButton(
            self.explore_tools_frame,
            text="🔀 Shuffle: Off",
            width=105,
            command=self._toggle_shuffle,
            fg_color=("gray85", "#21262d"),
            hover_color=("gray75", "#30363d"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.shuffle_btn.pack(side="left", padx=4)

        self.restart_btn = ctk.CTkButton(
            self.explore_tools_frame,
            text="↺ Restart",
            width=80,
            command=self.restart_current_category,
            fg_color=("gray85", "#21262d"),
            hover_color=("gray75", "#30363d"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.restart_btn.pack(side="left", padx=4)

        # ============ Quiz-Specific Widgets ============
        self.quiz_tools_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        # Hidden initially in explore mode

        self.filter_var = tk.StringVar(value="All Cards")
        self.filter_menu = ctk.CTkOptionMenu(
            self.quiz_tools_frame,
            variable=self.filter_var,
            values=["All Cards", "🔴 Needs Practice Only", "🟢 Mastered Only", "⚪ Unseen Only"],
            command=self._on_filter_changed,
            width=190,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=("#2563eb", "#1d4ed8"),
            button_color=("#1d4ed8", "#1e40af"),
        )
        self.filter_menu.pack(side="left", padx=4)

        self.quiz_session_label = ctk.CTkLabel(
            self.quiz_tools_frame,
            text="Session: Ready to quiz",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#15803d", "#86efac"),
            fg_color=("#dcfce7", "#064e3b"),
            corner_radius=8,
            padx=10,
            pady=4,
        )
        self.quiz_session_label.pack(side="left", padx=8)

        # ============ Common Right Tools ============
        self.stats_chip = ctk.CTkLabel(
            self.toolbar_frame,
            text="🔥 0 Days  •  🔴 Practice: 0  •  🟢 Mastered: 0  •  Today: 0",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#1d4ed8", "#60a5fa"),
            fg_color=("#eff6ff", "#172554"),
            corner_radius=8,
            padx=12,
            pady=4,
        )
        self.stats_chip.pack(side="right", padx=(8, 12), pady=6)

        # Toolbar Inline Preload Progress Frame (Displays live loading progress bar in toolbar)
        self.toolbar_preload_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        
        self.toolbar_preload_bar = ctk.CTkProgressBar(
            self.toolbar_preload_frame,
            width=100,
            height=8,
            corner_radius=4,
            progress_color=("#2563eb", "#1d4ed8"),
        )
        self.toolbar_preload_bar.set(0.0)
        self.toolbar_preload_bar.pack(side="left", padx=(0, 6))

        self.toolbar_preload_lbl = ctk.CTkLabel(
            self.toolbar_preload_frame,
            text="0%",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#2563eb", "#60a5fa"),
        )
        self.toolbar_preload_lbl.pack(side="left")

        self.preload_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="⬇ Preload Audio",
            width=120,
            command=self.open_preload_modal,
            fg_color=("gray85", "#21262d"),
            hover_color=("gray75", "#30363d"),
            text_color=("gray20", "#c9d1d9"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
        )
        self.preload_btn.pack(side="right", padx=4, pady=6)

        self.auto_speak_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="🔊 Auto-Audio: Off",
            width=125,
            command=self._toggle_auto_speak,
            fg_color=("gray85", "#21262d"),
            hover_color=("gray75", "#30363d"),
            text_color=("gray20", "#c9d1d9"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
        )
        self.auto_speak_btn.pack(side="right", padx=4, pady=6)

    def _build_stats_bar(self):
        """Card counter, mode indicator, and progress bar."""
        self.stats_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=(2, 4))

        # Counter Label
        self.progress_label = ctk.CTkLabel(
            self.stats_frame,
            text="Card 0 / 0",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("gray20", "#e5e7eb"),
        )
        self.progress_label.pack(side="left", padx=8)

        # Mode Indicator
        self.mode_label = ctk.CTkLabel(
            self.stats_frame,
            text="📖 Explore Mode",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("gray40", "#9ca3af"),
        )
        self.mode_label.pack(side="right", padx=8)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, height=8, corner_radius=4)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=20, pady=(2, 8))

    def _build_card_area(self):
        """Interactive flashcard container."""
        self.card_container = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color=("white", "#1f242c"),
            border_width=2,
            border_color=("#e2e8f0", "#333d4b"),
            cursor="hand2",
        )
        self.card_container.pack(fill="both", expand=True, padx=20, pady=4)
        self.card_container.bind("<Button-1>", lambda e: self.flip_card())

        # Card Top Meta Bar
        self.card_meta_frame = ctk.CTkFrame(self.card_container, fg_color="transparent")
        self.card_meta_frame.pack(fill="x", padx=24, pady=(20, 0))
        self.card_meta_frame.bind("<Button-1>", lambda e: self.flip_card())

        # CEFR Level Badge (B1, B2, C1)
        self.card_level_badge = ctk.CTkLabel(
            self.card_meta_frame,
            text="B1",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=("#0ea5e9", "#0284c7"),
            text_color="white",
            corner_radius=8,
            padx=10,
            pady=4,
        )
        self.card_level_badge.pack(side="left", padx=(0, 6))
        self.card_level_badge.bind("<Button-1>", lambda e: self.flip_card())

        # Category Badge
        self.card_category_badge = ctk.CTkLabel(
            self.card_meta_frame,
            text="CATEGORY",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=("#e0e7ff", "#2e3856"),
            text_color=("#3730a3", "#a5b4fc"),
            corner_radius=8,
            padx=12,
            pady=4,
        )
        self.card_category_badge.pack(side="left")
        self.card_category_badge.bind("<Button-1>", lambda e: self.flip_card())

        # Article Badge (der / die / das)
        self.article_badge = ctk.CTkLabel(
            self.card_meta_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=8,
            padx=10,
            pady=4,
        )
        self.article_badge.pack(side="left", padx=8)
        self.article_badge.bind("<Button-1>", lambda e: self.flip_card())

        # Audio Pronunciation Button (🔊 Speaker)
        self.audio_btn = ctk.CTkButton(
            self.card_meta_frame,
            text="🔊 Listen (V)",
            width=95,
            height=28,
            command=self.play_current_audio,
            fg_color=("#f3f4f6", "#2d333b"),
            hover_color=("#e5e7eb", "#374151"),
            text_color=("gray20", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=8,
        )
        self.audio_btn.pack(side="left", padx=8)

        # Card Mastery Status Badge (Only shown in Quiz Mode)
        self.card_status_badge = ctk.CTkLabel(
            self.card_meta_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=8,
            padx=10,
            pady=4,
        )
        self.card_status_badge.pack(side="right", padx=(8, 0))
        self.card_status_badge.bind("<Button-1>", lambda e: self.flip_card())
        self.card_status_badge.pack_forget()

        # Side Badge (Front / Answer)
        self.side_badge = ctk.CTkLabel(
            self.card_meta_frame,
            text="🇩🇪 FRONT",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=("gray90", "#2d333b"),
            text_color=("gray40", "#9ca3af"),
            corner_radius=8,
            padx=12,
            pady=4,
        )
        self.side_badge.pack(side="right")
        self.side_badge.bind("<Button-1>", lambda e: self.flip_card())

        # Card Center Content Frame
        self.content_frame = ctk.CTkFrame(self.card_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=28, pady=10)
        self.content_frame.bind("<Button-1>", lambda e: self.flip_card())

        # Subtext prompt
        self.card_subtext = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color=("gray50", "#9ca3af"),
            wraplength=720,
            justify="center",
        )
        self.card_subtext.pack(pady=(10, 4))
        self.card_subtext.bind("<Button-1>", lambda e: self.flip_card())

        # Main Word / Text
        self.card_main_text = ctk.CTkLabel(
            self.content_frame,
            text="No cards loaded",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color=("gray10", "#f9fafb"),
            wraplength=720,
            justify="center",
        )
        self.card_main_text.pack(expand=True, pady=8)
        self.card_main_text.bind("<Button-1>", lambda e: self.flip_card())

        # Plural Badge / Subtitle (In-line grammar)
        self.card_plural_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#2563eb", "#60a5fa"),
            fg_color=("#eff6ff", "#172554"),
            corner_radius=8,
            padx=14,
            pady=4,
        )
        self.card_plural_label.pack(pady=(0, 4))
        self.card_plural_label.bind("<Button-1>", lambda e: self.flip_card())
        self.card_plural_label.pack_forget()

        # Grammar Note / Hint
        self.card_grammar_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"),
            text_color=("gray45", "#9ca3af"),
            wraplength=700,
            justify="center",
        )
        self.card_grammar_label.pack(pady=(0, 6))
        self.card_grammar_label.bind("<Button-1>", lambda e: self.flip_card())
        self.card_grammar_label.pack_forget()

        # Card Footer Hint
        self.card_hint = ctk.CTkLabel(
            self.card_container,
            text="👆 Click card or press [Space] to flip",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray50", "#6b7280"),
        )
        self.card_hint.pack(side="bottom", pady=(0, 16))
        self.card_hint.bind("<Button-1>", lambda e: self.flip_card())

    def _build_action_buttons(self):
        """Action button bar: configured dynamically by active mode."""
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=20, pady=(6, 4))

        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        self.action_frame.grid_columnconfigure(2, weight=1)

        # Button 0 (Left)
        self.btn_left = ctk.CTkButton(
            self.action_frame,
            text="◀ Previous (← / 1)",
            command=self._on_btn_left_clicked,
            height=50,
            corner_radius=14,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        )
        self.btn_left.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        # Button 1 (Center)
        self.btn_center = ctk.CTkButton(
            self.action_frame,
            text="🔄 Flip (Space)",
            command=self._on_btn_center_clicked,
            height=50,
            corner_radius=14,
            fg_color=("#2563eb", "#1d4ed8"),
            hover_color=("#1d4ed8", "#1e40af"),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="white",
        )
        self.btn_center.grid(row=0, column=1, padx=8, sticky="ew")

        # Button 2 (Right)
        self.btn_right = ctk.CTkButton(
            self.action_frame,
            text="Next (→ / 2) ▶",
            command=self._on_btn_right_clicked,
            height=50,
            corner_radius=14,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        )
        self.btn_right.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        # Backward compatibility aliases for tests
        self.prev_btn = self.btn_left
        self.flip_btn = self.btn_center
        self.next_btn = self.btn_right

    def _build_footer(self):
        """Dynamic keyboard shortcut hints at bottom."""
        self.footer_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "#6b7280"),
        )
        self.footer_label.pack(side="bottom", pady=(0, 8))
        self._update_footer_text()

    # ================= KEYBOARD BINDINGS =================

    def _setup_keybindings(self):
        """Attach global keyboard controls routed cleanly to active mode."""
        self.bind("<Left>", lambda e: self._on_key_left())
        self.bind("<Right>", lambda e: self._on_key_right())
        self.bind("<space>", lambda e: self.flip_card())
        self.bind("<Return>", lambda e: self.flip_card())
        self.bind("<Up>", lambda e: self.flip_card())
        self.bind("<Down>", lambda e: self.flip_card())

        # Keys 1 & 2
        self.bind("1", lambda e: self.on_key_1())
        self.bind("2", lambda e: self.on_key_2())

        # Audio Pronunciation
        self.bind("v", lambda e: self.play_current_audio())
        self.bind("V", lambda e: self.play_current_audio())
        self.bind("a", lambda e: self.play_current_audio())
        self.bind("A", lambda e: self.play_current_audio())

        # Shortcuts
        self.bind("r", lambda e: self.restart_current_category())
        self.bind("R", lambda e: self.restart_current_category())
        self.bind("s", lambda e: self._toggle_shuffle())
        self.bind("S", lambda e: self._toggle_shuffle())

        # Modals
        self.bind("<Control-f>", lambda e: self.open_search_modal())
        self.bind("<Control-F>", lambda e: self.open_search_modal())
        self.bind("<Control-n>", lambda e: self.open_add_modal())
        self.bind("<Control-N>", lambda e: self.open_add_modal())

    # ================= DECK LOADING & LOGIC =================

    def _on_level_filter_changed(self, choice: str):
        """Called when CEFR level filter is switched: All, B1, B2, or C1."""
        self.selected_level = choice.upper()
        self.load_all_decks()

    def load_all_decks(self):
        """Scans the directory for category files and populates menu respecting CEFR level."""
        self.decks = scan_decks(self.app_dir)

        if not self.decks:
            self.cat_menu.configure(values=["No decks found (.txt, .csv)"])
            self.cat_var.set("No decks found")
            self.active_cards = []
            self._render_empty_state()
            return

        # Filter categories by selected level if not ALL
        if self.selected_level != "ALL":
            filtered_decks = {}
            for cat, cards in self.decks.items():
                matching_cards = [c for c in cards if getattr(c, "level", None) == self.selected_level or getattr(c.level, "value", "") == self.selected_level or f"_{self.selected_level}_" in cat or cat.startswith(f"{self.selected_level}_")]
                if matching_cards:
                    filtered_decks[cat] = matching_cards
            visible_decks = filtered_decks
        else:
            visible_decks = self.decks

        categories = sorted(visible_decks.keys())
        total_cards = sum(len(cards) for cards in visible_decks.values())

        if not categories:
            menu_items = [f"No {self.selected_level} decks found"]
            self.cat_menu.configure(values=menu_items)
            self.cat_var.set(menu_items[0])
            self.active_cards = []
            self._render_empty_state()
            return

        menu_items = [f"★ All ({self.selected_level}) ({total_cards})"]
        for cat in categories:
            menu_items.append(f"{cat} ({len(visible_decks[cat])})")

        self.cat_menu.configure(values=menu_items)

        selected = menu_items[0]
        for item in menu_items:
            if item.startswith(f"{self.current_category} ("):
                selected = item
                break

        self.cat_var.set(selected)
        self._on_category_selected(selected)
        self._update_stats_chip()
        self._update_filter_menu_counts()

    def _on_category_selected(self, choice: str):
        """Called when a category is selected."""
        if not self.decks:
            return

        if choice.startswith("★ All Categories"):
            self.current_category = "All Categories"
            aggregated = []
            for cards in self.decks.values():
                aggregated.extend(cards)
            raw_cards = list(aggregated)
        else:
            cat_name = choice.rsplit(" (", 1)[0].strip()
            self.current_category = cat_name
            raw_cards = list(self.decks.get(cat_name, []))

        # Apply study filter if active in Quiz mode
        if self.study_mode == "quiz" and self.card_filter != "all":
            self.active_cards = self.progress_mgr.filter_cards(raw_cards, self.card_filter)
        else:
            self.active_cards = list(raw_cards)

        self.restart_current_category(maintain_filter=True)
        self._update_filter_menu_counts()

    def restart_current_category(self, maintain_filter: bool = False):
        """Reset index and prepare cards for the active mode."""
        if not maintain_filter:
            if self.current_category == "All Categories":
                aggregated = []
                for cards in self.decks.values():
                    aggregated.extend(cards)
                raw_cards = list(aggregated)
            else:
                raw_cards = list(self.decks.get(self.current_category, []))

            if self.study_mode == "quiz" and self.card_filter != "all":
                self.active_cards = self.progress_mgr.filter_cards(raw_cards, self.card_filter)
            else:
                self.active_cards = list(raw_cards)

        if self.shuffle_mode:
            random.shuffle(self.active_cards)

        self.current_card_index = 0
        self.is_flipped = False

        self._update_stats_display()
        self._display_current_card()
        self._update_action_buttons()

    # ================= MODE MANAGEMENT (EXPLORE VS QUIZ) =================

    def _on_study_mode_changed(self, value: str):
        """Switches between 📖 Explore Mode and 🎯 Quiz Mode cleanly."""
        if "Explore" in value:
            self.study_mode = "explore"
            # Show Explore tools, hide Quiz tools
            self.quiz_tools_frame.pack_forget()
            self.explore_tools_frame.pack(side="left", padx=8, pady=4)
            self.mode_label.configure(text="📖 Explore Mode")
        else:
            self.study_mode = "quiz"
            # Show Quiz tools, hide Explore tools
            self.explore_tools_frame.pack_forget()
            self.quiz_tools_frame.pack(side="left", padx=8, pady=4)
            self.mode_label.configure(text=f"🎯 Quiz Mode ({self.filter_var.get()})")
            # Reset session score on entering quiz mode
            self.quiz_session_reviewed = 0
            self.quiz_session_correct = 0
            self.quiz_session_practice = 0
            self._update_quiz_session_label()
            self._update_filter_menu_counts()

        self._update_footer_text()
        self.restart_current_category()

    def _on_filter_changed(self, choice: str):
        """Filter cards in Quiz mode by retention status."""
        if "Needs Practice" in choice:
            self.card_filter = "needs_practice"
        elif "Mastered" in choice:
            self.card_filter = "mastered"
        elif "Unseen" in choice:
            self.card_filter = "unseen"
        else:
            self.card_filter = "all"

        self.mode_label.configure(text=f"🎯 Quiz Mode ({choice})")
        self.restart_current_category()

    def _update_footer_text(self):
        """Shows relevant shortcuts for the active mode."""
        if self.study_mode == "explore":
            self.footer_label.configure(
                text="📖 Explore Controls:   [Space] Flip   •   [← / 1] Previous   •   [→ / 2] Next   •   [V] Listen   •   [S] Shuffle   •   [Ctrl+F] Search   •   [Ctrl+N] Add Card"
            )
        else:
            self.footer_label.configure(
                text="🎯 Quiz Controls:   [Space] Reveal Answer   •   [← / 1] Needs Practice   •   [→ / 2] Mastered   •   [V] Listen   •   [← / → before reveal] Skip"
            )

    # ================= DISPATCHED BUTTON & KEY ACTIONS =================

    def _on_btn_left_clicked(self):
        """Left button action depending on mode."""
        if self.study_mode == "explore":
            self.explore_prev()
        else:
            if self.is_flipped:
                self.quiz_rate_practice()
            else:
                self.quiz_skip_prev()

    def _on_btn_center_clicked(self):
        """Center button action depending on mode."""
        self.flip_card()

    def _on_btn_right_clicked(self):
        """Right button action depending on mode."""
        if self.study_mode == "explore":
            self.explore_next()
        else:
            if self.is_flipped:
                self.quiz_rate_mastered()
            else:
                self.quiz_skip_next()

    def _on_key_left(self):
        """Left arrow key handler: Previous in Explore; Needs Practice in Quiz (when revealed), or Skip."""
        if self.study_mode == "explore":
            self.explore_prev()
        else:
            if self.is_flipped:
                self.quiz_rate_practice()
            else:
                self.quiz_skip_prev()

    def _on_key_right(self):
        """Right arrow key handler: Next in Explore; Mastered in Quiz (when revealed), or Skip."""
        if self.study_mode == "explore":
            self.explore_next()
        else:
            if self.is_flipped:
                self.quiz_rate_mastered()
            else:
                self.quiz_skip_next()

    def on_key_1(self):
        """Key '1' handler: Previous in Explore; Needs Practice in Quiz (when revealed)."""
        if self.study_mode == "explore":
            self.explore_prev()
        else:
            if self.is_flipped:
                self.quiz_rate_practice()
            else:
                self.card_hint.configure(text="⚠️ Press [Space] to reveal answer before rating!")

    def on_key_2(self):
        """Key '2' handler: Next in Explore; Mastered in Quiz (when revealed)."""
        if self.study_mode == "explore":
            self.explore_next()
        else:
            if self.is_flipped:
                self.quiz_rate_mastered()
            else:
                self.card_hint.configure(text="⚠️ Press [Space] to reveal answer before rating!")

    # ================= EXPLORE MODE IMPLEMENTATION =================

    def explore_prev(self):
        """Navigate to previous card in Explore Mode."""
        if not self.active_cards:
            return
        self.current_card_index = (self.current_card_index - 1) % len(self.active_cards)
        self.is_flipped = False
        self._update_stats_display()
        self._display_current_card()
        self._update_action_buttons()

    def explore_next(self):
        """Navigate to next card in Explore Mode."""
        if not self.active_cards:
            return
        self.current_card_index = (self.current_card_index + 1) % len(self.active_cards)
        self.is_flipped = False
        self._update_stats_display()
        self._display_current_card()
        self._update_action_buttons()

    # Aliases for tests
    def prev_card(self):
        if self.study_mode == "explore":
            self.explore_prev()
        else:
            self.quiz_skip_prev()

    def next_card(self):
        if self.study_mode == "explore":
            self.explore_next()
        else:
            self.quiz_skip_next()

    # ================= QUIZ MODE IMPLEMENTATION =================

    def quiz_skip_prev(self):
        """Skip to previous question in Quiz Mode without rating."""
        self.explore_prev()

    def quiz_skip_next(self):
        """Skip to next question in Quiz Mode without rating."""
        self.explore_next()

    def quiz_rate_practice(self):
        """Rate card as Needs Practice (1), record session stat, and advance."""
        if not self.active_cards:
            return
        card = self.active_cards[self.current_card_index]
        self.progress_mgr.mark_card(card.category, card.german, STATUS_LEARNING)

        self.quiz_session_reviewed += 1
        self.quiz_session_practice += 1
        self._update_quiz_session_label()
        self._update_stats_chip()
        self._update_filter_menu_counts()

        # Advance to next quiz card
        self.next_card()

    def quiz_rate_mastered(self):
        """Rate card as Mastered (2), record session stat, and advance."""
        if not self.active_cards:
            return
        card = self.active_cards[self.current_card_index]
        self.progress_mgr.mark_card(card.category, card.german, STATUS_MASTERED)

        self.quiz_session_reviewed += 1
        self.quiz_session_correct += 1
        self._update_quiz_session_label()
        self._update_stats_chip()
        self._update_filter_menu_counts()

        # Advance to next quiz card
        self.next_card()

    def mark_current_card(self, status: str):
        """Helper for test backward compatibility."""
        if status == STATUS_MASTERED:
            self.quiz_rate_mastered()
        else:
            self.quiz_rate_practice()

    def _update_quiz_session_label(self):
        """Updates the quiz session score badge."""
        if self.quiz_session_reviewed == 0:
            self.quiz_session_label.configure(text="Session: Ready to quiz")
        else:
            pct = int((self.quiz_session_correct / self.quiz_session_reviewed) * 100)
            self.quiz_session_label.configure(
                text=f"Session: 🟢 {self.quiz_session_correct}  🔴 {self.quiz_session_practice} ({pct}%)"
            )

    # ================= CARD FLIPPING & RENDERING =================

    def flip_card(self):
        """Toggles front and back of current card."""
        if not self.active_cards:
            return

        self.is_flipped = not self.is_flipped
        self._display_current_card()
        self._update_action_buttons()

        if self.is_flipped and self.auto_speak:
            self.play_current_audio()

    def _display_current_card(self):
        """Renders card front or back cleanly according to active mode."""
        if not self.active_cards:
            self._render_empty_filtered_state()
            return

        card = self.active_cards[self.current_card_index]

        # Front / Back texts
        if not self.reverse_mode:
            front_text = card.clean_prompt or card.german
            back_text = card.english
            front_lang = "🇩🇪 GERMAN"
            back_lang = "🇬🇧 ENGLISH"
        else:
            front_text = card.english
            back_text = card.clean_prompt or card.german
            front_lang = "🇬🇧 ENGLISH"
            back_lang = "🇩🇪 GERMAN"

        # 1. CEFR Level Badge & Category Badge
        card_lvl = getattr(card, "level", "ALL")
        lvl_str = getattr(card_lvl, "value", str(card_lvl)).upper()
        if lvl_str in ("B1", "B2", "C1"):
            self.card_level_badge.pack(side="left", padx=(0, 6))
            self.card_level_badge.configure(text=lvl_str)
            if lvl_str == "B1":
                self.card_level_badge.configure(fg_color=("#0ea5e9", "#0284c7"))  # Sky/Teal
            elif lvl_str == "B2":
                self.card_level_badge.configure(fg_color=("#3b82f6", "#1d4ed8"))  # Vibrant Blue
            elif lvl_str == "C1":
                self.card_level_badge.configure(fg_color=("#8b5cf6", "#6d28d9"))  # Royal Purple
        else:
            self.card_level_badge.pack_forget()

        self.card_category_badge.configure(text=card.category.upper())

        # 2. Article Badge (der / die / das)
        article = card.get_article()
        if article and not self.reverse_mode:
            self.article_badge.pack(side="left", padx=8)
            if article == "der":
                self.article_badge.configure(text="der", fg_color=("#dbeafe", "#1e3a8a"), text_color=("#1d4ed8", "#93c5fd"))
            elif article == "die":
                self.article_badge.configure(text="die", fg_color=("#ffe4e6", "#881337"), text_color=("#be123c", "#fda4af"))
            elif article == "das":
                self.article_badge.configure(text="das", fg_color=("#d1fae5", "#064e3b"), text_color=("#047857", "#6ee7b7"))
        else:
            self.article_badge.pack_forget()

        # 3. Quiz Mastery Badge: Strictly ONLY shown in Quiz Mode
        if self.study_mode == "quiz":
            st = self.progress_mgr.get_card_status(card.category, card.german)
            self.card_status_badge.pack(side="right", padx=(8, 0))
            if st == STATUS_MASTERED:
                self.card_status_badge.configure(text="🟢 Mastered", fg_color=("#dcfce7", "#064e3b"), text_color=("#15803d", "#86efac"))
            elif st == STATUS_LEARNING:
                self.card_status_badge.configure(text="🔴 Needs Practice", fg_color=("#fee2e2", "#7f1d1d"), text_color=("#b91c1c", "#fca5a5"))
            else:
                self.card_status_badge.configure(text="⚪ Unseen", fg_color=("gray90", "#2d333b"), text_color=("gray50", "#9ca3af"))
        else:
            self.card_status_badge.pack_forget()

        # 4. Front vs Back Rendering
        if not self.is_flipped:
            # FRONT (Question / Prompt)
            side_text = f"{front_lang} (FRONT)" if self.study_mode == "explore" else "🎯 QUESTION"
            self.side_badge.configure(
                text=side_text,
                fg_color=("gray90", "#2d333b"),
                text_color=("gray40", "#9ca3af"),
            )
            self.card_subtext.configure(text="")
            self.card_main_text.configure(
                text=front_text,
                font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                text_color=("gray10", "#f9fafb"),
            )

            # Plural Badge
            if card.plural and not self.reverse_mode:
                self.card_plural_label.configure(text=f"📖 Plural: {card.plural}")
                self.card_plural_label.pack(pady=(0, 4))
            else:
                self.card_plural_label.pack_forget()

            # Grammar Note / Hint
            if card.grammar_note:
                self.card_grammar_label.configure(text=f"💡 Note: {card.grammar_note}")
                self.card_grammar_label.pack(pady=(0, 6))
            else:
                self.card_grammar_label.pack_forget()

            # Hint text
            if self.study_mode == "explore":
                self.card_hint.configure(text="👆 Click card or press [Space] to flip • [← / 1] Prev • [→ / 2] Next")
            else:
                self.card_hint.configure(text="👆 Click card or press [Space] to reveal answer • [V] Listen")

            self.card_container.configure(fg_color=("white", "#1f242c"))

        else:
            # BACK (Answer Revealed)
            side_text = f"{back_lang} (ANSWER)" if self.study_mode == "explore" else "🎯 ANSWER REVEALED"
            self.side_badge.configure(
                text=side_text,
                fg_color=("#dbeafe", "#172554"),
                text_color=("#1d4ed8", "#60a5fa"),
            )
            self.card_subtext.configure(text=front_text)
            self.card_main_text.configure(
                text=back_text,
                font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                text_color=("#1d4ed8", "#60a5fa"),
            )

            if card.plural:
                self.card_plural_label.configure(text=f"📖 Plural: {card.plural}")
                self.card_plural_label.pack(pady=(0, 4))
            else:
                self.card_plural_label.pack_forget()

            if card.grammar_note:
                self.card_grammar_label.configure(text=f"💡 Note: {card.grammar_note}")
                self.card_grammar_label.pack(pady=(0, 6))
            else:
                self.card_grammar_label.pack_forget()

            if self.study_mode == "explore":
                self.card_hint.configure(text="👆 Click card or press [Space] to flip back • [← / 1] Prev • [→ / 2] Next")
            else:
                self.card_hint.configure(text="Rate your recall: [← / 1] Needs Practice  •  [→ / 2] Mastered  •  [Space] Flip back")

            self.card_container.configure(fg_color=("#f8fafc", "#161b22"))

    def _update_action_buttons(self):
        """Update button labels and colors strictly based on active mode."""
        if self.study_mode == "explore":
            # EXPLORE MODE: Always Clean Navigation & Flipping
            self.btn_left.configure(
                text="◀ Previous (← / 1)",
                fg_color=("gray80", "#2d333b"),
                hover_color=("gray70", "#374151"),
                text_color=("gray10", "#e5e7eb"),
            )
            flip_text = "🔄 Flip Card (Space)" if not self.is_flipped else "🔄 Flip Back (Space)"
            self.btn_center.configure(
                text=flip_text,
                fg_color=("#2563eb", "#1d4ed8"),
                hover_color=("#1d4ed8", "#1e40af"),
                text_color="white",
            )
            self.btn_right.configure(
                text="Next (→ / 2) ▶",
                fg_color=("gray80", "#2d333b"),
                hover_color=("gray70", "#374151"),
                text_color=("gray10", "#e5e7eb"),
            )
        else:
            # QUIZ MODE: Testing & Rating Flow
            if not self.is_flipped:
                # Unrevealed (Prompt shown): Focus on Reveal
                self.btn_left.configure(
                    text="⏭ Skip (←)",
                    fg_color=("gray80", "#2d333b"),
                    hover_color=("gray70", "#374151"),
                    text_color=("gray10", "#e5e7eb"),
                )
                self.btn_center.configure(
                    text="👁 Reveal Answer (Space)",
                    fg_color=("#2563eb", "#1d4ed8"),
                    hover_color=("#1d4ed8", "#1e40af"),
                    text_color="white",
                )
                self.btn_right.configure(
                    text="⏭ Skip (→)",
                    fg_color=("gray80", "#2d333b"),
                    hover_color=("gray70", "#374151"),
                    text_color=("gray10", "#e5e7eb"),
                )
            else:
                # Revealed (Answer shown): Focus on Recall Rating
                self.btn_left.configure(
                    text="🔴 Needs Practice (← / 1)",
                    fg_color=("#ef4444", "#dc2626"),
                    hover_color=("#dc2626", "#b91c1c"),
                    text_color="white",
                )
                self.btn_center.configure(
                    text="🔄 Flip Back (Space)",
                    fg_color=("gray80", "#2d333b"),
                    hover_color=("gray70", "#374151"),
                    text_color=("gray10", "#e5e7eb"),
                )
                self.btn_right.configure(
                    text="🟢 Mastered (→ / 2) ▶",
                    fg_color=("#10b981", "#059669"),
                    hover_color=("#059669", "#047857"),
                    text_color="white",
                )

    def _update_stats_display(self):
        """Updates progress counter and progress bar."""
        total = len(self.active_cards)
        current = (self.current_card_index + 1) if total > 0 else 0

        prefix = "Card" if self.study_mode == "explore" else "Quiz Question"
        self.progress_label.configure(text=f"{prefix} {current} / {total}")
        ratio = (current / total) if total > 0 else 0.0
        self.progress_bar.set(ratio)

    def _update_stats_chip(self):
        """Updates the streak and review statistics badge."""
        stats = self.progress_mgr.get_stats_summary()
        self.stats_chip.configure(
            text=f"🔥 {stats['streak']} Days  •  🔴 Practice: {stats['learning_total']}  •  🟢 Mastered: {stats['mastered_total']}  •  Today: {stats['today_reviews']}"
        )

    def _get_current_deck_raw_cards(self) -> List[Flashcard]:
        """Returns the raw un-filtered list of cards for the active deck."""
        if not self.decks:
            return []
        if self.current_category == "All Categories":
            all_c = []
            for cards in self.decks.values():
                all_c.extend(cards)
            return all_c
        return self.decks.get(self.current_category, [])

    def get_needs_practice_count(self) -> int:
        """Returns the total count of cards needing practice across all decks."""
        return self.progress_mgr.get_needs_practice_count()

    def get_mastered_count(self) -> int:
        """Returns the total count of mastered cards across all decks."""
        return self.progress_mgr.get_mastered_count()

    def get_deck_needs_practice_count(self) -> int:
        """Returns the count of cards needing practice in the currently active deck."""
        raw_cards = self._get_current_deck_raw_cards()
        return self.progress_mgr.get_category_needs_practice_count(self.current_category, raw_cards)

    def get_deck_mastered_count(self) -> int:
        """Returns the count of mastered cards in the currently active deck."""
        raw_cards = self._get_current_deck_raw_cards()
        return self.progress_mgr.get_category_mastered_count(self.current_category, raw_cards)

    def _update_filter_menu_counts(self):
        """Updates the Quiz filter dropdown options with dynamic card counts for the active deck."""
        if not hasattr(self, "filter_menu"):
            return
        raw_cards = self._get_current_deck_raw_cards()
        counts = self.progress_mgr.get_deck_counts(self.current_category, raw_cards)

        all_text = f"All Cards ({counts['total']})"
        practice_text = f"🔴 Needs Practice ({counts[STATUS_LEARNING]})"
        mastered_text = f"🟢 Mastered ({counts[STATUS_MASTERED]})"
        unseen_text = f"⚪ Unseen ({counts[STATUS_NEW]})"

        filter_options = [all_text, practice_text, mastered_text, unseen_text]
        self.filter_menu.configure(values=filter_options)

        if self.card_filter == "needs_practice":
            self.filter_var.set(practice_text)
        elif self.card_filter == "mastered":
            self.filter_var.set(mastered_text)
        elif self.card_filter == "unseen":
            self.filter_var.set(unseen_text)
        else:
            self.filter_var.set(all_text)

    def _render_empty_filtered_state(self):
        """Shows message when current filter has no matching cards."""
        self.card_main_text.configure(
            text=f"No cards matching '{self.filter_var.get()}'!\n\nSwitch filter to 'All Cards' to see cards.",
            font=ctk.CTkFont(family="Segoe UI", size=18),
        )
        self.card_subtext.configure(text="")
        self.card_plural_label.pack_forget()
        self.card_grammar_label.pack_forget()
        self.article_badge.pack_forget()
        self.card_status_badge.pack_forget()
        self.card_category_badge.configure(text="EMPTY")
        self.card_hint.configure(text="Select 'All Cards' in toolbar above")

    def _render_empty_state(self):
        """Display helpful instructions if no decks are found."""
        self.card_main_text.configure(
            text="No flashcard files found in folder!\n\nAdd a .txt or .csv file with 2 columns:\nGerman;English",
            font=ctk.CTkFont(family="Segoe UI", size=18),
        )
        self.card_subtext.configure(text="")
        self.card_category_badge.configure(text="EMPTY")
        self.card_hint.configure(text="Click [📂 Decks] to add cards and [🔄 Refresh]")

    # ================= AUDIO PRONUNCIATION =================

    def play_current_audio(self):
        """Plays German speech synthesis for current card asynchronously."""
        if not self.active_cards:
            return

        card = self.active_cards[self.current_card_index]
        text_to_speak = card.clean_prompt or card.german

        orig_text = self.audio_btn.cget("text")
        self.audio_btn.configure(text="🔊 Playing...")

        def _on_done(success: bool):
            try:
                self.after(0, lambda: self.audio_btn.configure(text=orig_text))
            except Exception:
                pass

        self.audio_svc.play_german(text_to_speak, _on_done)

    # ================= CONTROLS & TOGGLES =================

    def _toggle_theme(self):
        """Toggles Dark and Light mode."""
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        icon = "🌙 Theme" if new_mode == "Light" else "☀️ Theme"
        self.theme_btn.configure(text=icon)

    def _toggle_shuffle(self):
        """Toggles shuffling of cards in Explore mode."""
        self.shuffle_mode = not self.shuffle_mode
        self.shuffle_btn.configure(
            text="🔀 Shuffle: On" if self.shuffle_mode else "🔀 Shuffle: Off",
            fg_color=("#2563eb", "#1d4ed8") if self.shuffle_mode else ("gray85", "#21262d"),
            text_color="white" if self.shuffle_mode else ("gray10", "#e5e7eb"),
        )
        if self.shuffle_mode:
            random.shuffle(self.active_cards)
            self._display_current_card()

    def _toggle_reverse_mode(self):
        """Toggles between German -> English and English -> German."""
        self.reverse_mode = not self.reverse_mode
        if self.reverse_mode:
            self.reverse_btn.configure(
                text="⇄ EN ➔ DE",
                fg_color=("#7c3aed", "#6d28d9"),
                text_color="white",
            )
        else:
            self.reverse_btn.configure(
                text="⇄ DE ➔ EN",
                fg_color=("gray85", "#21262d"),
                text_color=("gray10", "#e5e7eb"),
            )
        self._display_current_card()

    def _toggle_auto_speak(self):
        """Toggles auto-pronunciation on card reveal."""
        self.auto_speak = not self.auto_speak
        if self.auto_speak:
            self.auto_speak_btn.configure(
                text="🔊 Auto-Audio: On",
                fg_color=("#2563eb", "#1d4ed8"),
                text_color="white",
            )
        else:
            self.auto_speak_btn.configure(
                text="🔊 Auto-Audio: Off",
                fg_color=("gray85", "#21262d"),
                text_color=("gray20", "#c9d1d9"),
            )

    def _open_folder_in_explorer(self):
        """Opens decks folder in Windows Explorer."""
        target_dir = os.path.join(self.app_dir, "decks")
        if not os.path.isdir(target_dir):
            target_dir = self.app_dir
        try:
            os.startfile(target_dir)
        except AttributeError:
            subprocess.Popen(["explorer", target_dir])

    # ================= MODALS: SEARCH, QUICK ADD, PRELOAD =================

    def open_search_modal(self):
        """Opens live search popup across all decks (Ctrl+F)."""
        if self._search_window is not None and self._search_window.winfo_exists():
            self._search_window.lift()
            self._search_window.focus_force()
            return

        self._search_window = ctk.CTkToplevel(self)
        self._search_window.title("Search Flashcards (Ctrl+F)")
        self._search_window.geometry("640x500")
        self._search_window.minsize(500, 380)
        self._center_window(self._search_window, 640, 500)

        entry_frame = ctk.CTkFrame(self._search_window, fg_color="transparent")
        entry_frame.pack(fill="x", padx=16, pady=12)

        search_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Type German or English word / phrase...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            height=40,
        )
        search_entry.pack(fill="x", side="left", expand=True, padx=(0, 8))
        search_entry.focus_set()

        results_frame = ctk.CTkScrollableFrame(self._search_window, corner_radius=10)
        results_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        def _do_search(*args):
            for w in results_frame.winfo_children():
                w.destroy()

            query = search_entry.get().strip().lower()
            if not query:
                lbl = ctk.CTkLabel(results_frame, text="Type above to search across all decks...", text_color="gray50")
                lbl.pack(pady=20)
                return

            matches = []
            for cat_name, cards in self.decks.items():
                for idx, c in enumerate(cards):
                    if query in c.german.lower() or query in c.english.lower():
                        matches.append((cat_name, c, idx))

            if not matches:
                lbl = ctk.CTkLabel(results_frame, text=f"No flashcards matching '{query}'", text_color="gray50")
                lbl.pack(pady=20)
                return

            for cat_name, card, idx in matches[:40]:
                row = ctk.CTkFrame(results_frame, fg_color=("gray90", "#21262d"), corner_radius=8, cursor="hand2")
                row.pack(fill="x", pady=4, padx=4)

                cat_badge = ctk.CTkLabel(
                    row,
                    text=cat_name,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    fg_color=("#e0e7ff", "#2e3856"),
                    text_color=("#3730a3", "#a5b4fc"),
                    corner_radius=6,
                    padx=8,
                    pady=2,
                )
                cat_badge.pack(side="left", padx=8, pady=8)

                txt = f"{card.german}  ➔  {card.english}"
                txt_lbl = ctk.CTkLabel(
                    row,
                    text=txt,
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    anchor="w",
                )
                txt_lbl.pack(side="left", padx=8, fill="x", expand=True)

                def _jump(c_name=cat_name, card_obj=card):
                    self._jump_to_card(c_name, card_obj)
                    self._search_window.destroy()

                row.bind("<Button-1>", lambda e, c_name=cat_name, card_obj=card: _jump(c_name, card_obj))
                txt_lbl.bind("<Button-1>", lambda e, c_name=cat_name, card_obj=card: _jump(c_name, card_obj))

        search_entry.bind("<KeyRelease>", _do_search)
        _do_search()

    def _jump_to_card(self, category: str, target_card: Flashcard):
        """Switches to category and sets current index to target card."""
        menu_items = self.cat_menu.cget("values")
        for item in menu_items:
            if item.startswith(f"{category} ("):
                self.cat_var.set(item)
                self._on_category_selected(item)
                break

        for idx, c in enumerate(self.active_cards):
            if c.german == target_card.german and c.english == target_card.english:
                self.current_card_index = idx
                self.is_flipped = False
                self._update_stats_display()
                self._display_current_card()
                self._update_action_buttons()
                break

    def open_add_modal(self):
        """Opens quick-add dialog to append a card directly to a deck file (Ctrl+N)."""
        if self._add_window is not None and self._add_window.winfo_exists():
            self._add_window.lift()
            self._add_window.focus_force()
            return

        self._add_window = ctk.CTkToplevel(self)
        self._add_window.title("Quick Add Flashcard (Ctrl+N)")
        self._add_window.geometry("540x440")
        self._add_window.minsize(480, 400)
        self._center_window(self._add_window, 540, 440)

        frame = ctk.CTkFrame(self._add_window, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=20)

        title_lbl = ctk.CTkLabel(
            frame,
            text="Add New Flashcard",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        )
        title_lbl.pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(frame, text="Select Category / Deck:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w")
        cat_options = sorted([k for k in self.decks.keys()])
        if not cat_options:
            cat_options = ["Wortschatz - Allgemeine"]

        default_cat = self.current_category if self.current_category in self.decks else cat_options[0]
        cat_var = tk.StringVar(value=default_cat)
        cat_select = ctk.CTkOptionMenu(frame, variable=cat_var, values=cat_options, height=36)
        cat_select.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(frame, text="German (e.g. 'das Fahrrad, die Fahrräder'):", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w")
        de_entry = ctk.CTkEntry(frame, placeholder_text="e.g. das Fahrrad, die Fahrräder", height=38)
        de_entry.pack(fill="x", pady=(4, 12))
        de_entry.focus_set()

        ctk.CTkLabel(frame, text="English Meaning:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(anchor="w")
        en_entry = ctk.CTkEntry(frame, placeholder_text="e.g. the bicycle", height=38)
        en_entry.pack(fill="x", pady=(4, 18))

        feedback_lbl = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(family="Segoe UI", size=12))
        feedback_lbl.pack(pady=(0, 8))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        def _save_card():
            de = de_entry.get().strip()
            en = en_entry.get().strip()
            cat = cat_var.get().strip()

            if not de or not en:
                feedback_lbl.configure(text="⚠️ Please enter both German and English text.", text_color="#ef4444")
                return

            decks_dir = os.path.join(self.app_dir, "decks")
            os.makedirs(decks_dir, exist_ok=True)
            target_path = os.path.join(decks_dir, f"{cat}.txt")

            try:
                with open(target_path, "a", encoding="utf-8") as f:
                    f.write(f"\n{de};{en}")

                feedback_lbl.configure(text=f"✅ Added to '{cat}' successfully!", text_color="#10b981")
                self.load_all_decks()
                de_entry.delete(0, "end")
                en_entry.delete(0, "end")
                de_entry.focus_set()
            except Exception as e:
                feedback_lbl.configure(text=f"Error saving: {e}", text_color="#ef4444")

        add_submit_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Save Card",
            command=_save_card,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=("#2563eb", "#1d4ed8"),
        )
        add_submit_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            command=self._add_window.destroy,
            height=42,
            fg_color=("gray80", "#2d333b"),
            text_color=("gray10", "#e5e7eb"),
        )
        cancel_btn.pack(side="right", padx=(6, 0))

    def open_preload_modal(self):
        """Opens dialog to batch download/cache all German audio for 100% offline study."""
        import threading

        if self._preload_window is not None and self._preload_window.winfo_exists():
            self._preload_window.lift()
            self._preload_window.focus_force()
            return

        self._preload_window = ctk.CTkToplevel(self)
        self._preload_window.title("Preload All Audio (100% Offline Study)")
        self._preload_window.geometry("560x360")
        self._preload_window.minsize(500, 320)
        self._center_window(self._preload_window, 560, 360)

        frame = ctk.CTkFrame(self._preload_window, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=20)

        title_lbl = ctk.CTkLabel(
            frame,
            text="⬇ Preload German Audio",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        )
        title_lbl.pack(anchor="w", pady=(0, 6))

        desc_lbl = ctk.CTkLabel(
            frame,
            text="Downloads and caches natural German speech for all flashcards across your decks so you can study completely offline anywhere with zero internet connection.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            wraplength=500,
            justify="left",
            text_color=("gray40", "#9ca3af"),
        )
        desc_lbl.pack(anchor="w", pady=(0, 16))

        # Fresh scan all deck files directly from disk
        self.decks = scan_decks(self.app_dir)

        unique_texts = []
        seen = set()
        for cards in self.decks.values():
            for c in cards:
                t = (c.clean_prompt or c.german).strip()
                if t and t not in seen:
                    seen.add(t)
                    unique_texts.append(t)

        # Gather unique phrases
        total_unique = len(unique_texts)
        cached_initial = sum(1 for t in unique_texts if self.audio_svc.is_cached(t))
        ratio_init = (cached_initial / total_unique) if total_unique > 0 else 0.0
        pct_init = int(ratio_init * 100)

        count_lbl = ctk.CTkLabel(
            frame,
            text=f"Cache Status: {pct_init}%  •  {cached_initial} / {total_unique} cards ready offline",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#1d4ed8", "#60a5fa"),
        )
        count_lbl.pack(anchor="w", pady=(0, 6))

        bar = ctk.CTkProgressBar(
            frame,
            height=14,
            corner_radius=7,
            progress_color=("#2563eb", "#1d4ed8"),
        )
        bar.set(ratio_init)
        bar.pack(fill="x", pady=(2, 8))

        detail_lbl = ctk.CTkLabel(
            frame,
            text=f"Ready to cache {total_unique - cached_initial} missing audio clips." if total_unique > cached_initial else "All cards are already cached and ready for 100% offline study!",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray50", "#9ca3af"),
        )
        detail_lbl.pack(anchor="w", pady=(0, 16))

        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        self._preload_cancel = threading.Event()

        def _on_progress(completed, total, current_word):
            ratio = (completed / total) if total > 0 else 0.0
            pct = int(ratio * 100)

            # 1. Update toolbar inline progress bar on main window
            self.after(0, lambda: self._update_toolbar_preload_progress(completed, total, current_word))

            # 2. Update modal progress bar if open
            if self._preload_window and self._preload_window.winfo_exists():
                self.after(0, lambda: [
                    bar.set(ratio),
                    count_lbl.configure(text=f"⚡ Caching Audio: {pct}%  •  {completed} / {total} cards"),
                    detail_lbl.configure(text=f"Downloading: {current_word[:42]}..."),
                ])

        def _on_finish(newly_cached, total):
            # 1. Finish toolbar progress bar
            self.after(0, lambda: self._finish_toolbar_preload_progress(newly_cached, total))

            # 2. Finish modal progress bar if open
            if self._preload_window and self._preload_window.winfo_exists():
                self.after(0, lambda: [
                    bar.set(1.0),
                    count_lbl.configure(text=f"✅ Done! 100%  •  {total} / {total} cards cached locally"),
                    detail_lbl.configure(text=f"Cached {newly_cached} new audio clips. App is 100% offline ready!"),
                    start_btn.configure(text="✅ All Audio Cached", state="disabled", fg_color=("#10b981", "#059669")),
                    close_btn.configure(text="Close"),
                ])

        def _start_download():
            start_btn.configure(text="⏳ Downloading...", state="disabled")
            close_btn.configure(text="Stop / Cancel")
            self._preload_cancel.clear()
            self.audio_svc.preload_all(unique_texts, _on_progress, _on_finish, self._preload_cancel)

        def _on_close():
            if self._preload_cancel:
                self._preload_cancel.set()
            if self._preload_window:
                self._preload_window.destroy()

        start_btn = ctk.CTkButton(
            btn_box,
            text="▶ Start Preload",
            command=_start_download,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=("#2563eb", "#1d4ed8"),
        )
        start_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        if total_unique == cached_initial and total_unique > 0:
            start_btn.configure(text="✅ All Audio Cached", state="disabled", fg_color=("#10b981", "#059669"))

        close_btn = ctk.CTkButton(
            btn_box,
            text="Close",
            command=_on_close,
            height=40,
            fg_color=("gray80", "#2d333b"),
            text_color=("gray10", "#e5e7eb"),
        )
        close_btn.pack(side="right", padx=(6, 0))

    def _update_toolbar_preload_progress(self, completed: int, total: int, current_word: str):
        """Updates the inline progress bar on the main window toolbar."""
        try:
            if not self.toolbar_preload_frame.winfo_ismapped():
                self.toolbar_preload_frame.pack(side="right", padx=6, pady=6)
                self.toolbar_preload_frame.pack_configure(before=self.preload_btn)

            ratio = (completed / total) if total > 0 else 0.0
            pct = int(ratio * 100)
            self.toolbar_preload_bar.set(ratio)
            self.toolbar_preload_lbl.configure(text=f"{pct}%")
            self.preload_btn.configure(text=f"⏳ {completed}/{total}")
        except Exception:
            pass

    def _finish_toolbar_preload_progress(self, newly_cached: int, total: int):
        """Completes and smoothly auto-hides the inline toolbar progress bar."""
        try:
            self.toolbar_preload_bar.set(1.0)
            self.toolbar_preload_lbl.configure(text="100%")
            self.preload_btn.configure(
                text="✅ All Audio Cached",
                fg_color=("#10b981", "#059669"),
                text_color="white",
            )

            def _reset_btn():
                try:
                    self.toolbar_preload_frame.pack_forget()
                    self.preload_btn.configure(
                        text="⬇ Preload Audio",
                        fg_color=("gray85", "#21262d"),
                        text_color=("gray20", "#c9d1d9"),
                    )
                except Exception:
                    pass

            self.after(4000, _reset_btn)
        except Exception:
            pass

    def _center_window(self, win, w: int, h: int):
        """Center a toplevel window relative to parent."""
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")

    def open_reset_metrics_modal(self):
        """Opens a confirmation modal asking 'Are you sure?' with Yes and No buttons to reset metrics."""
        if self._reset_window is not None and self._reset_window.winfo_exists():
            self._reset_window.lift()
            self._reset_window.focus_force()
            return

        self._reset_window = ctk.CTkToplevel(self)
        self._reset_window.title("Reset Metrics?")
        self._reset_window.resizable(False, False)
        self._reset_window.transient(self)
        self._reset_window.grab_set()

        self._center_window(self._reset_window, 450, 270)

        # Modal content container
        content = ctk.CTkFrame(self._reset_window, corner_radius=14, fg_color=("gray95", "#1e2229"))
        content.pack(fill="both", expand=True, padx=16, pady=16)

        # Warning Icon & Title
        self.reset_confirm_title_lbl = ctk.CTkLabel(
            content,
            text="⚠️ Reset All Metrics?",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=("#b91c1c", "#f87171"),
        )
        self.reset_confirm_title_lbl.pack(pady=(16, 8), padx=16)

        # Description text
        self.reset_confirm_desc_lbl = ctk.CTkLabel(
            content,
            text="Are you sure you want to reset all metrics and progress?\n\n"
                 "• Study streak and today's reviews will be reset to 0\n"
                 "• All Mastered (🟢) and Needs Practice (🔴) statuses will be cleared\n"
                 "• Current quiz session scores will be reset\n\n"
                 "This action cannot be undone.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray30", "#cbd5e1"),
            justify="center",
        )
        self.reset_confirm_desc_lbl.pack(pady=(0, 18), padx=16)

        # Button Frame (No / Cancel and Yes / Confirm)
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 10))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        def _on_cancel():
            if self._reset_window and self._reset_window.winfo_exists():
                self._reset_window.destroy()
                self._reset_window = None

        def _on_confirm():
            self.reset_all_metrics()
            if self._reset_window and self._reset_window.winfo_exists():
                self._reset_window.destroy()
                self._reset_window = None

        # No / Cancel Button
        self.reset_confirm_no_btn = ctk.CTkButton(
            btn_frame,
            text="No, Cancel",
            command=_on_cancel,
            height=40,
            fg_color=("gray80", "#2d333b"),
            hover_color=("gray70", "#374151"),
            text_color=("gray10", "#e5e7eb"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        self.reset_confirm_no_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        # Yes / Reset Button
        self.reset_confirm_yes_btn = ctk.CTkButton(
            btn_frame,
            text="Yes, Reset Metrics",
            command=_on_confirm,
            height=40,
            fg_color=("#ef4444", "#dc2626"),
            hover_color=("#dc2626", "#b91c1c"),
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        self.reset_confirm_yes_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        # Accessibility bindings
        self._reset_window.bind("<Escape>", lambda e: _on_cancel())
        self._reset_window.protocol("WM_DELETE_WINDOW", _on_cancel)

    def reset_all_metrics(self):
        """Resets all metrics in progress manager and active session, updating the UI."""
        self.progress_mgr.reset_metrics()
        self.quiz_session_reviewed = 0
        self.quiz_session_correct = 0
        self.quiz_session_practice = 0

        self._update_stats_chip()
        self._update_quiz_session_label()
        self._update_filter_menu_counts()
        self.restart_current_category(maintain_filter=False)


def main():
    app = WortschatzApp()
    app.mainloop()


if __name__ == "__main__":
    main()
