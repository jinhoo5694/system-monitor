#!/usr/bin/env python3
"""
J.A.R.V.I.S. Style System Monitor
Iron Man inspired HUD interface with pre-rendered 3D model animation
"""

import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import psutil
import platform
import os
import math
import random
from datetime import datetime
from collections import deque
import glob

class JarvisMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. SYSTEM MONITOR")
        self.root.geometry("1024x768")
        self.root.configure(bg='#0a0a12')

        # JARVIS color scheme
        self.bg_color = '#0a0a12'
        self.primary = '#00d4ff'      # JARVIS cyan
        self.secondary = '#0099cc'    # Darker cyan
        self.accent = '#ff6600'       # Orange accent (arc reactor)
        self.warning = '#ffaa00'      # Warning yellow
        self.text_dim = '#4a6a7a'     # Dimmed text
        self.glow = '#00ffff'         # Glow effect

        # Initialize data
        self.last_net_io = psutil.net_io_counters()
        self.last_update = datetime.now()
        self.process = psutil.Process(os.getpid())

        # Pre-create fonts
        self.small_font = tkfont.Font(family='Helvetica', size=8)
        self.label_font = tkfont.Font(family='Helvetica', size=10)
        self.value_font = tkfont.Font(family='Helvetica', size=14, weight='bold')
        self.title_font = tkfont.Font(family='Helvetica', size=20, weight='bold')
        self.hud_font = tkfont.Font(family='Courier', size=9)
        self.loading_font = tkfont.Font(family='Helvetica', size=16)

        # Historical data
        self.max_data_points = 60
        self.cpu_history = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.mem_history = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.net_up_history = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.net_down_history = deque([0] * self.max_data_points, maxlen=self.max_data_points)

        # Pre-rendered frames
        self.frames = []
        self.current_frame = 0
        self.model_loading = True

        # Code lines for scrolling display
        self.code_lines = []
        self.code_scroll_offset_left = 0
        self.code_scroll_offset_right = 0

        # Show loading screen first
        self.show_loading_screen()

        # Load frames after UI is shown
        self.root.after(100, self.initialize_app)

    def show_loading_screen(self):
        """Show loading screen while model loads"""
        self.loading_frame = tk.Frame(self.root, bg=self.bg_color)
        self.loading_frame.pack(fill=tk.BOTH, expand=True)

        # Center container
        center = tk.Frame(self.loading_frame, bg=self.bg_color)
        center.place(relx=0.5, rely=0.5, anchor='center')

        # Title
        title = tk.Label(center, text="J.A.R.V.I.S.", font=self.title_font,
                        bg=self.bg_color, fg=self.primary)
        title.pack(pady=20)

        # Loading text
        self.loading_label = tk.Label(center, text="INITIALIZING SYSTEMS...",
                                      font=self.loading_font, bg=self.bg_color, fg=self.text_dim)
        self.loading_label.pack(pady=10)

        # Progress bar canvas
        self.progress_canvas = tk.Canvas(center, width=300, height=20,
                                         bg=self.bg_color, highlightthickness=1,
                                         highlightbackground=self.primary)
        self.progress_canvas.pack(pady=20)

        # Status text
        self.status_label = tk.Label(center, text="Loading 3D model...",
                                     font=self.hud_font, bg=self.bg_color, fg=self.text_dim)
        self.status_label.pack()

        self.root.update()

    def update_loading_progress(self, progress, status=""):
        """Update loading progress bar"""
        self.progress_canvas.delete("all")
        # Draw progress bar
        width = int(296 * progress)
        self.progress_canvas.create_rectangle(2, 2, width, 18, fill=self.primary, outline="")
        if status:
            self.status_label.config(text=status)
        self.root.update()

    def initialize_app(self):
        """Initialize the app after loading screen is shown"""
        self.update_loading_progress(0.1, "Loading pre-rendered frames...")
        self.load_frames()

        self.update_loading_progress(0.6, "Scanning code files...")
        self.load_code_lines()

        self.update_loading_progress(0.8, "Setting up interface...")
        self.root.update()

        # Destroy loading screen and setup main UI
        self.loading_frame.destroy()
        self.model_loading = False

        self.setup_ui()

        # Start updates
        self.update_stats()
        self.animate_model()
        self.scroll_code()

    def load_frames(self):
        """Load pre-rendered animation frames"""
        cache_dir = os.path.join(os.path.dirname(__file__), 'ironman', 'cache')
        frame_files = sorted(glob.glob(os.path.join(cache_dir, 'frame_*.png')))

        if not frame_files:
            print(f"No pre-rendered frames found in {cache_dir}")
            print("Run 'python3 prerender_model.py' to generate frames")
            return

        # Target size - keep original square ratio
        target_size = (300, 300)

        for i, frame_path in enumerate(frame_files):
            img = Image.open(frame_path)
            # Resize to fit the model container
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.frames.append(photo)

            # Update progress
            if i % 10 == 0:
                progress = 0.1 + (i / len(frame_files)) * 0.5
                self.update_loading_progress(progress, f"Loading frames... {i+1}/{len(frame_files)}")

        print(f"Loaded {len(self.frames)} animation frames")

    def load_code_lines(self):
        """Load code lines from cache file (fast) or generate if missing"""
        cache_file = os.path.join(os.path.dirname(__file__), 'ironman', 'cache', 'code_lines.txt')

        # Try to load from cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.code_lines = [line.rstrip() for line in f.readlines() if line.strip()]
                print(f"Loaded {len(self.code_lines)} code lines from cache")
                return
            except:
                pass

        # Generate and cache - only scan current project directory (fast)
        print("Generating code lines cache...")
        project_dir = os.path.dirname(__file__)
        code_extensions = ['*.py', '*.js', '*.ts', '*.json', '*.sh']

        all_lines = []
        for ext in code_extensions:
            for file_path in glob.glob(os.path.join(project_dir, '**', ext), recursive=True):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f.readlines()[:50]:
                            line = line.rstrip()
                            if 5 < len(line) < 60:
                                all_lines.append(line)
                except:
                    continue

        # Add some cool Iron Man themed lines
        jarvis_lines = [
            "def boot_jarvis_core():",
            "    arc_reactor.initialize()",
            "class MarkIII(IronManSuit):",
            "    def __init__(self):",
            "        self.weapons = WeaponSystem()",
            "async fn scan_threat_level() {",
            "    sensors.activate();",
            "    return analysis.run();",
            "}",
            "POWER_OUTPUT = 3_000_000_000",
            "const JARVIS_VERSION = '4.0.1';",
            "target.lock(coordinates);",
            "repulsor.charge(85);",
            "flight_systems.engage();",
            "hud.display(threat_data);",
            "armor.integrity = 98.7;",
            "reactor_temp = 347.2;",
            "altitude = 12847.5;",
            "velocity = mach_2.3;",
        ] * 50

        all_lines.extend(jarvis_lines)
        random.shuffle(all_lines)
        self.code_lines = all_lines[:1000]

        # Save to cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.code_lines))
            print(f"Cached {len(self.code_lines)} code lines")
        except Exception as e:
            print(f"Could not cache code lines: {e}")

    def setup_ui(self):
        """Setup the JARVIS-style interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top header
        self.create_header(main_frame)

        # Middle section - 3 columns
        middle_frame = tk.Frame(main_frame, bg=self.bg_color)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left panel - CPU & Memory gauges (smaller to center the model)
        left_panel = tk.Frame(middle_frame, bg=self.bg_color, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        self.create_left_panel(left_panel)

        # Center panel - 3D Model
        center_panel = tk.Frame(middle_frame, bg=self.bg_color)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.create_3d_panel(center_panel)

        # Right panel - Network & System info
        right_panel = tk.Frame(middle_frame, bg=self.bg_color, width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        self.create_right_panel(right_panel)

        # Bottom status bar
        self.create_footer(main_frame)

    def create_header(self, parent):
        """Create JARVIS header"""
        header_frame = tk.Frame(parent, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        # Left decorative line
        left_line = tk.Canvas(header_frame, width=150, height=30, bg=self.bg_color, highlightthickness=0)
        left_line.pack(side=tk.LEFT)
        left_line.create_line(0, 15, 140, 15, fill=self.primary, width=1)
        left_line.create_oval(140, 10, 150, 20, outline=self.primary, width=2)

        # Title
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side=tk.LEFT, expand=True)

        title = tk.Label(
            title_frame,
            text="J.A.R.V.I.S.",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.primary
        )
        title.pack()

        subtitle = tk.Label(
            title_frame,
            text="SYSTEM MONITORING INTERFACE v3.0",
            font=self.small_font,
            bg=self.bg_color,
            fg=self.text_dim
        )
        subtitle.pack()

        # Right decorative line
        right_line = tk.Canvas(header_frame, width=150, height=30, bg=self.bg_color, highlightthickness=0)
        right_line.pack(side=tk.RIGHT)
        right_line.create_oval(0, 10, 10, 20, outline=self.primary, width=2)
        right_line.create_line(10, 15, 150, 15, fill=self.primary, width=1)

    def create_left_panel(self, parent):
        """Create left panel with CPU and Memory arc gauges"""
        # CPU Arc Gauge
        cpu_label = tk.Label(parent, text="CPU LOAD", font=self.label_font, bg=self.bg_color, fg=self.primary)
        cpu_label.pack(pady=(10, 5))

        self.cpu_canvas = tk.Canvas(parent, width=210, height=130, bg=self.bg_color, highlightthickness=0)
        self.cpu_canvas.pack()

        self.cpu_value_label = tk.Label(parent, text="0%", font=self.value_font, bg=self.bg_color, fg=self.primary)
        self.cpu_value_label.pack()

        self.cpu_detail_label = tk.Label(parent, text="", font=self.hud_font, bg=self.bg_color, fg=self.text_dim)
        self.cpu_detail_label.pack(pady=(0, 20))

        # Memory Arc Gauge
        mem_label = tk.Label(parent, text="MEMORY USAGE", font=self.label_font, bg=self.bg_color, fg=self.accent)
        mem_label.pack(pady=(10, 5))

        self.mem_canvas = tk.Canvas(parent, width=210, height=130, bg=self.bg_color, highlightthickness=0)
        self.mem_canvas.pack()

        self.mem_value_label = tk.Label(parent, text="0%", font=self.value_font, bg=self.bg_color, fg=self.accent)
        self.mem_value_label.pack()

        self.mem_detail_label = tk.Label(parent, text="", font=self.hud_font, bg=self.bg_color, fg=self.text_dim)
        self.mem_detail_label.pack(pady=(0, 20))

        # GPU Status
        gpu_label = tk.Label(parent, text="GPU STATUS", font=self.label_font, bg=self.bg_color, fg=self.warning)
        gpu_label.pack(pady=(10, 5))

        self.gpu_value_label = tk.Label(parent, text="ACTIVE", font=self.value_font, bg=self.bg_color, fg=self.warning)
        self.gpu_value_label.pack()

        self.gpu_detail_label = tk.Label(parent, text="", font=self.hud_font, bg=self.bg_color, fg=self.text_dim)
        self.gpu_detail_label.pack()

    def create_3d_panel(self, parent):
        """Create center panel with pre-rendered 3D model animation and code displays"""
        # Main container
        main_container = tk.Frame(parent, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top HUD title
        top_hud = tk.Label(main_container, text="[ MARK III SUIT STATUS ]",
                          font=self.hud_font, bg=self.bg_color, fg=self.primary)
        top_hud.pack(pady=(0, 5))

        # Model container - centered
        model_container = tk.Frame(main_container, bg='#050810', width=320, height=300,
                                   highlightbackground=self.primary, highlightthickness=2)
        model_container.pack()
        model_container.pack_propagate(False)

        # 3D model label - centered
        self.model_label = tk.Label(model_container, bg='#050810')
        self.model_label.place(relx=0.5, rely=0.5, anchor='center')

        # Show first frame if available
        if self.frames:
            self.model_label.config(image=self.frames[0])

        # Code panels container - expand to fill
        code_outer = tk.Frame(main_container, bg=self.bg_color)
        code_outer.pack(fill=tk.BOTH, expand=True, pady=5)

        # Inner frame to hold both panels - centered
        code_frame = tk.Frame(code_outer, bg=self.bg_color)
        code_frame.place(relx=0.5, rely=0, anchor='n', relheight=1.0)

        # Left code scroll panel - SYS
        left_code_frame = tk.Frame(code_frame, bg='#0a0f14', width=155,
                                   highlightbackground=self.secondary, highlightthickness=1)
        left_code_frame.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        left_code_frame.pack_propagate(False)

        left_header = tk.Label(left_code_frame, text="< SYS.SCAN >", font=self.small_font,
                              bg='#0a0f14', fg=self.secondary)
        left_header.pack(pady=2)

        self.left_code_canvas = tk.Canvas(left_code_frame, bg='#0a0f14', highlightthickness=0)
        self.left_code_canvas.pack(fill=tk.BOTH, expand=True)

        # Right code scroll panel - DATA
        right_code_frame = tk.Frame(code_frame, bg='#0a0f14', width=155,
                                    highlightbackground=self.secondary, highlightthickness=1)
        right_code_frame.pack(side=tk.LEFT, fill=tk.Y, padx=3)
        right_code_frame.pack_propagate(False)

        right_header = tk.Label(right_code_frame, text="< DATA.STREAM >", font=self.small_font,
                               bg='#0a0f14', fg=self.secondary)
        right_header.pack(pady=2)

        self.right_code_canvas = tk.Canvas(right_code_frame, bg='#0a0f14', highlightthickness=0)
        self.right_code_canvas.pack(fill=tk.BOTH, expand=True)

        # Status indicators at bottom
        status_frame = tk.Frame(main_container, bg=self.bg_color)
        status_frame.pack(pady=5)

        self.status_labels = []
        statuses = ["POWER: ONLINE", "WEAPONS: STANDBY", "FLIGHT: READY", "J.A.R.V.I.S.: ACTIVE"]
        colors = [self.primary, self.warning, self.accent, self.primary]

        for status, color in zip(statuses, colors):
            lbl = tk.Label(status_frame, text=status, font=self.small_font, bg=self.bg_color, fg=color)
            lbl.pack(side=tk.LEFT, padx=8)
            self.status_labels.append(lbl)

    def scroll_code(self):
        """Animate scrolling code in side panels"""
        if not self.code_lines:
            self.root.after(100, self.scroll_code)
            return

        # Left panel - scroll up
        self.left_code_canvas.delete("all")
        canvas_height = self.left_code_canvas.winfo_height()
        line_height = 12
        visible_lines = canvas_height // line_height + 2

        for i in range(visible_lines):
            line_idx = int(self.code_scroll_offset_left + i) % len(self.code_lines)
            y = i * line_height - (self.code_scroll_offset_left % 1) * line_height
            line = self.code_lines[line_idx][:25]  # More characters to fill width

            # Fade effect based on position
            if i < 2:
                color = '#1a3a4a'
            elif i > visible_lines - 3:
                color = '#1a3a4a'
            else:
                color = '#00a0c0'

            self.left_code_canvas.create_text(3, y, text=line, anchor='nw',
                                              font=('Courier', 6), fill=color)

        self.code_scroll_offset_left = (self.code_scroll_offset_left + 0.5) % len(self.code_lines)

        # Right panel - scroll down (different content)
        self.right_code_canvas.delete("all")
        canvas_height = self.right_code_canvas.winfo_height()

        for i in range(visible_lines):
            line_idx = int(len(self.code_lines) - self.code_scroll_offset_right - i) % len(self.code_lines)
            y = i * line_height
            line = self.code_lines[line_idx][:25]  # More characters to fill width

            if i < 2:
                color = '#1a3a4a'
            elif i > visible_lines - 3:
                color = '#1a3a4a'
            else:
                color = '#00a0c0'

            self.right_code_canvas.create_text(3, y, text=line, anchor='nw',
                                               font=('Courier', 6), fill=color)

        self.code_scroll_offset_right = (self.code_scroll_offset_right + 0.3) % len(self.code_lines)

        self.root.after(80, self.scroll_code)

    def create_right_panel(self, parent):
        """Create right panel with network stats"""
        # Network Section
        net_label = tk.Label(parent, text="NETWORK I/O", font=self.label_font, bg=self.bg_color, fg=self.primary)
        net_label.pack(pady=(10, 5))

        # Network graph canvas
        self.net_canvas = tk.Canvas(parent, width=210, height=80, bg=self.bg_color, highlightthickness=1,
                                     highlightbackground=self.secondary)
        self.net_canvas.pack()

        # Upload stats
        up_frame = tk.Frame(parent, bg=self.bg_color)
        up_frame.pack(fill=tk.X, pady=3)
        tk.Label(up_frame, text="UP:", font=self.hud_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.net_up_label = tk.Label(up_frame, text="0 B/s", font=self.label_font, bg=self.bg_color, fg=self.accent)
        self.net_up_label.pack(side=tk.RIGHT)

        # Download stats
        down_frame = tk.Frame(parent, bg=self.bg_color)
        down_frame.pack(fill=tk.X, pady=3)
        tk.Label(down_frame, text="DOWN:", font=self.hud_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.net_down_label = tk.Label(down_frame, text="0 B/s", font=self.label_font, bg=self.bg_color, fg=self.primary)
        self.net_down_label.pack(side=tk.RIGHT)

        # Total data
        tx_frame = tk.Frame(parent, bg=self.bg_color)
        tx_frame.pack(fill=tk.X, pady=2)
        tk.Label(tx_frame, text="TOTAL TX:", font=self.small_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.total_tx_label = tk.Label(tx_frame, text="0 B", font=self.small_font, bg=self.bg_color, fg=self.accent)
        self.total_tx_label.pack(side=tk.RIGHT)

        rx_frame = tk.Frame(parent, bg=self.bg_color)
        rx_frame.pack(fill=tk.X, pady=2)
        tk.Label(rx_frame, text="TOTAL RX:", font=self.small_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.total_rx_label = tk.Label(rx_frame, text="0 B", font=self.small_font, bg=self.bg_color, fg=self.primary)
        self.total_rx_label.pack(side=tk.RIGHT)

        # Divider
        tk.Frame(parent, height=1, bg=self.secondary).pack(fill=tk.X, pady=10)

        # System Info Section
        sys_label = tk.Label(parent, text="SYSTEM INFO", font=self.label_font, bg=self.bg_color, fg=self.primary)
        sys_label.pack(pady=(0, 5))

        # System details
        self.sys_info_frame = tk.Frame(parent, bg=self.bg_color)
        self.sys_info_frame.pack(fill=tk.X)

        # Get more detailed info
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%m/%d %H:%M")
        except:
            boot_time = "N/A"

        try:
            # Cross-platform disk path
            if platform.system() == 'Windows':
                disk = psutil.disk_usage('C:\\')
            else:
                disk = psutil.disk_usage('/')
            disk_used = f"{disk.percent}%"
        except:
            disk_used = "N/A"

        info_items = [
            ("OS:", f"{platform.system()} {platform.release()[:10]}"),
            ("ARCH:", platform.machine()),
            ("CPU:", f"{psutil.cpu_count()}C / {psutil.cpu_count(logical=True)}T"),
            ("DISK:", disk_used),
            ("BOOT:", boot_time),
            ("HOST:", platform.node()[:12]),
        ]

        for label, value in info_items:
            row = tk.Frame(self.sys_info_frame, bg=self.bg_color)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=label, font=self.small_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=self.hud_font, bg=self.bg_color, fg=self.primary).pack(side=tk.RIGHT)

        # Divider
        tk.Frame(parent, height=1, bg=self.secondary).pack(fill=tk.X, pady=10)

        # Live Stats Section
        live_label = tk.Label(parent, text="LIVE STATS", font=self.label_font, bg=self.bg_color, fg=self.primary)
        live_label.pack(pady=(0, 5))

        # Swap usage
        swap_frame = tk.Frame(parent, bg=self.bg_color)
        swap_frame.pack(fill=tk.X, pady=1)
        tk.Label(swap_frame, text="SWAP:", font=self.small_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.swap_label = tk.Label(swap_frame, text="0%", font=self.small_font, bg=self.bg_color, fg=self.primary)
        self.swap_label.pack(side=tk.RIGHT)

        # Process count
        proc_frame = tk.Frame(parent, bg=self.bg_color)
        proc_frame.pack(fill=tk.X, pady=1)
        tk.Label(proc_frame, text="PROCS:", font=self.small_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.proc_count_label = tk.Label(proc_frame, text="0", font=self.small_font, bg=self.bg_color, fg=self.primary)
        self.proc_count_label.pack(side=tk.RIGHT)

        # Battery (if available)
        batt_frame = tk.Frame(parent, bg=self.bg_color)
        batt_frame.pack(fill=tk.X, pady=1)
        tk.Label(batt_frame, text="BATTERY:", font=self.small_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.battery_label = tk.Label(batt_frame, text="N/A", font=self.small_font, bg=self.bg_color, fg=self.warning)
        self.battery_label.pack(side=tk.RIGHT)

        # Top process
        top_frame = tk.Frame(parent, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=1)
        tk.Label(top_frame, text="TOP:", font=self.small_font, bg=self.bg_color, fg=self.text_dim).pack(side=tk.LEFT)
        self.top_proc_label = tk.Label(top_frame, text="...", font=self.small_font, bg=self.bg_color, fg=self.accent)
        self.top_proc_label.pack(side=tk.RIGHT)

    def create_footer(self, parent):
        """Create bottom status bar"""
        footer_frame = tk.Frame(parent, bg=self.bg_color)
        footer_frame.pack(fill=tk.X, pady=(10, 0))

        # Left side - timestamp
        self.time_label = tk.Label(
            footer_frame,
            text="",
            font=self.hud_font,
            bg=self.bg_color,
            fg=self.text_dim
        )
        self.time_label.pack(side=tk.LEFT)

        # Right side - process memory
        self.proc_mem_label = tk.Label(
            footer_frame,
            text="",
            font=self.hud_font,
            bg=self.bg_color,
            fg=self.text_dim
        )
        self.proc_mem_label.pack(side=tk.RIGHT)

        # Center - status
        self.status_label = tk.Label(
            footer_frame,
            text="ALL SYSTEMS OPERATIONAL",
            font=self.hud_font,
            bg=self.bg_color,
            fg=self.primary
        )
        self.status_label.pack()

    def draw_arc_gauge(self, canvas, value, max_value=100, color=None):
        """Draw a JARVIS-style arc gauge"""
        if color is None:
            color = self.primary

        canvas.delete("all")
        width = 210
        height = 130
        cx, cy = width // 2, height - 15
        radius = 85

        # Draw background arc
        start_angle = 180
        extent = 180
        canvas.create_arc(
            cx - radius, cy - radius, cx + radius, cy + radius,
            start=start_angle, extent=extent,
            outline=self.text_dim, width=3, style='arc'
        )

        # Draw tick marks
        for i in range(11):
            angle = math.radians(180 - i * 18)
            x1 = cx + (radius - 10) * math.cos(angle)
            y1 = cy - (radius - 10) * math.sin(angle)
            x2 = cx + (radius - 5) * math.cos(angle)
            y2 = cy - (radius - 5) * math.sin(angle)
            canvas.create_line(x1, y1, x2, y2, fill=self.text_dim, width=1)

        # Draw value arc
        value_extent = (value / max_value) * 180
        canvas.create_arc(
            cx - radius, cy - radius, cx + radius, cy + radius,
            start=start_angle, extent=value_extent,
            outline=color, width=4, style='arc'
        )

        # Draw glow effect for high values
        if value > 70:
            glow_color = self.warning if value > 90 else color
            canvas.create_arc(
                cx - radius + 5, cy - radius + 5, cx + radius - 5, cy + radius - 5,
                start=start_angle, extent=value_extent,
                outline=glow_color, width=2, style='arc'
            )

        # Draw needle
        needle_angle = math.radians(180 - (value / max_value) * 180)
        needle_x = cx + (radius - 20) * math.cos(needle_angle)
        needle_y = cy - (radius - 20) * math.sin(needle_angle)
        canvas.create_line(cx, cy, needle_x, needle_y, fill=color, width=2)
        canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=color, outline=color)

    def draw_network_graph(self):
        """Draw network activity graph with real data"""
        canvas = self.net_canvas
        canvas.delete("all")

        width = 210
        height = 80
        padding = 5
        graph_width = width - 2 * padding
        graph_height = height - 2 * padding

        # Draw grid
        for i in range(4):
            y = padding + graph_height * i / 3
            canvas.create_line(padding, y, width - padding, y, fill=self.text_dim, dash=(1, 3))

        # Get max value for scaling
        max_up = max(self.net_up_history) if max(self.net_up_history) > 0 else 1
        max_down = max(self.net_down_history) if max(self.net_down_history) > 0 else 1
        max_val = max(max_up, max_down)

        # Draw download line (cyan)
        points_down = []
        for i, val in enumerate(self.net_down_history):
            x = padding + (i / len(self.net_down_history)) * graph_width
            y = height - padding - (val / max_val) * graph_height
            points_down.append((x, y))

        if len(points_down) > 1:
            for i in range(len(points_down) - 1):
                canvas.create_line(points_down[i][0], points_down[i][1],
                                  points_down[i+1][0], points_down[i+1][1],
                                  fill=self.primary, width=1)

        # Draw upload line (orange)
        points_up = []
        for i, val in enumerate(self.net_up_history):
            x = padding + (i / len(self.net_up_history)) * graph_width
            y = height - padding - (val / max_val) * graph_height
            points_up.append((x, y))

        if len(points_up) > 1:
            for i in range(len(points_up) - 1):
                canvas.create_line(points_up[i][0], points_up[i][1],
                                  points_up[i+1][0], points_up[i+1][1],
                                  fill=self.accent, width=1)

    def animate_model(self):
        """Animate the 3D model by cycling through pre-rendered frames"""
        if self.frames:
            self.model_label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Smooth 60fps-like animation (every 50ms = 20fps, good balance)
        self.root.after(50, self.animate_model)

    def format_bytes(self, bytes_val):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"

    def format_speed(self, bytes_per_sec):
        """Format network speed"""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.0f} B/s"
        elif bytes_per_sec < 1024 * 1024:
            return f"{bytes_per_sec/1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec/(1024*1024):.1f} MB/s"

    def update_stats(self):
        """Update all system statistics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_history.append(cpu_percent)
            self.draw_arc_gauge(self.cpu_canvas, cpu_percent, color=self.primary)
            self.cpu_value_label.config(text=f"{cpu_percent:.1f}%")
            self.cpu_detail_label.config(text=f"{psutil.cpu_count()} CORES @ {psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else f"{psutil.cpu_count()} CORES")

            # Memory
            mem = psutil.virtual_memory()
            self.mem_history.append(mem.percent)
            self.draw_arc_gauge(self.mem_canvas, mem.percent, color=self.accent)
            self.mem_value_label.config(text=f"{mem.percent:.1f}%")
            self.mem_detail_label.config(text=f"{self.format_bytes(mem.used)} / {self.format_bytes(mem.total)}")

            # GPU
            gpu_status, gpu_info = self.get_gpu_usage()
            self.gpu_value_label.config(text=gpu_status)
            self.gpu_detail_label.config(text=gpu_info)

            # Network
            now = datetime.now()
            current_net_io = psutil.net_io_counters()
            time_delta = (now - self.last_update).total_seconds()

            if time_delta > 0:
                upload_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta
                download_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta

                # Record history for graph
                self.net_up_history.append(upload_speed)
                self.net_down_history.append(download_speed)

                self.net_up_label.config(text=self.format_speed(upload_speed))
                self.net_down_label.config(text=self.format_speed(download_speed))

                self.total_tx_label.config(text=f"{self.format_bytes(current_net_io.bytes_sent)}")
                self.total_rx_label.config(text=f"{self.format_bytes(current_net_io.bytes_recv)}")

                # Draw network graph
                self.draw_network_graph()

            self.last_net_io = current_net_io
            self.last_update = now

            # Live stats updates
            try:
                swap = psutil.swap_memory()
                self.swap_label.config(text=f"{swap.percent}%")
            except:
                pass

            try:
                self.proc_count_label.config(text=str(len(psutil.pids())))
            except:
                pass

            try:
                battery = psutil.sensors_battery()
                if battery:
                    status = "⚡" if battery.power_plugged else ""
                    self.battery_label.config(text=f"{battery.percent:.0f}%{status}")
                else:
                    self.battery_label.config(text="AC")
            except:
                self.battery_label.config(text="N/A")

            try:
                # Get top CPU process
                procs = [(p.info['name'][:10], p.info['cpu_percent'])
                         for p in psutil.process_iter(['name', 'cpu_percent'])]
                procs = sorted(procs, key=lambda x: x[1], reverse=True)[:1]
                if procs and procs[0][1] > 0:
                    self.top_proc_label.config(text=f"{procs[0][0]}")
            except:
                pass

            # Footer updates
            self.time_label.config(text=now.strftime("SYS.TIME: %Y-%m-%d %H:%M:%S"))
            self_mem = self.process.memory_info().rss
            self.proc_mem_label.config(text=f"PROC.MEM: {self.format_bytes(self_mem)}")

        except Exception as e:
            print(f"Error updating stats: {e}")

        self.root.after(1000, self.update_stats)

    def get_gpu_usage(self):
        """Get GPU status - cross-platform"""
        try:
            system = platform.system()
            machine = platform.machine()

            if system == 'Darwin':  # macOS
                if machine == 'arm64':
                    return "ACTIVE", "Apple Silicon"
                else:
                    return "ACTIVE", "Intel GPU"
            elif system == 'Windows':
                return "ACTIVE", "Windows GPU"
            elif system == 'Linux':
                return "ACTIVE", "Linux GPU"
            else:
                return "ACTIVE", "GPU"
        except:
            return "N/A", "Unknown"


def main():
    root = tk.Tk()
    app = JarvisMonitor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
