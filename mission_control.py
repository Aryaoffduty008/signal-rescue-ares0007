
import time
import tkinter as tk

try:
    from PIL import Image, ImageTk, ImageEnhance
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
import numpy as np
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from engine.generators import sine_wave
from engine.analysis import energy
from engine.fourier import fft_analysis

from game.missions import (
    create_mission_01,
    create_mission_02,
    create_mission_03,
    create_mission_04,
    create_mission_05,
    create_mission_06,
    create_mission_07,
    create_mission_08,
    create_mission_09,
)
from game.system_missions import (
    create_mission_10,
    create_mission_11,
    create_final_mission,
)
from game.game_state import GameState
from game.scoring import calculate_score


class MissionControl:
    """
    Final interactive Mission Control.

    Key design rule:
        target parameters != starting player controls

    Every mission starts with a deliberately imperfect configuration.
    The target is kept hidden inside mission.parameters. The graph,
    analyzer and validator all use that same target.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("SIGNAL RESCUE — ARES-7 Mission Control")
        self.root.geometry("1500x920")
        self.root.minsize(1200, 780)

        self.bg = "#091018"
        self.panel = "#111B24"
        self.panel_2 = "#1B2A33"
        self.text = "#FFF6DD"
        self.muted = "#B9C6BE"
        self.accent = "#52D0C0"
        self.success = "#87DFA5"
        self.warning = "#F3B85B"
        self.danger = "#E97867"

        self.game = GameState()
        self.current_mission = 1
        self.mission_start_time = time.time()
        self.hints_this_mission = 0

        self.control_vars = []
        self.control_types = []
        self.current_match = 0.0

        self.build_mission_set()
        self.build_interface()
        self.load_mission(1)

    # ---------------------------------------------------------
    # CAMPAIGN
    # ---------------------------------------------------------

    def build_mission_set(self):
        self.missions = {
            1: create_mission_01(),
            2: create_mission_02(),
            3: create_mission_03(),
            4: create_mission_04(),
            5: create_mission_05(),
            6: create_mission_06(),
            7: create_mission_07(),
            8: create_mission_08(),
            9: create_mission_09(),
            10: create_mission_10(),
            11: create_mission_11(),
            12: create_final_mission(),
        }

        self.operation_counts = {
            1: 1, 2: 1, 3: 1, 4: 1,
            5: 2, 6: 3, 7: 2, 8: 2,
            9: 1, 10: 2, 11: 2, 12: 5,
        }

    # ---------------------------------------------------------
    # INTERFACE
    # ---------------------------------------------------------

    def build_interface(self):
        self.root.configure(bg=self.bg)

        header = tk.Frame(self.root, bg=self.panel, height=78, highlightthickness=1, highlightbackground="#33423E")
        header.pack(fill="x")
        header.pack_propagate(False)

        status_strip = tk.Frame(self.root, bg="#D99A52", height=2)
        status_strip.pack(fill="x")
        status_strip.pack_propagate(False)

        tk.Label(
            header,
            text="🛰️ SIGNAL RESCUE",
            font=("Segoe UI", 23, "bold"),
            bg=self.panel,
            fg=self.accent,
        ).pack(side="left", padx=22)

        tk.Label(
            header,
            text="ARES-7  /  COMMUNICATIONS RECOVERY",
            font=("Consolas", 9, "bold"),
            bg=self.panel,
            fg=self.muted,
        ).pack(side="left")

        self.score_header = tk.Label(
            header,
            text="SCORE 0000",
            font=("Segoe UI", 11, "bold"),
            bg=self.panel,
            fg=self.text,
        )
        self.score_header.pack(side="right", padx=12)

        self.integrity_label = tk.Label(
            header,
            text="INTEGRITY 100%",
            font=("Segoe UI", 11, "bold"),
            bg=self.panel,
            fg=self.success,
        )
        self.integrity_label.pack(side="right", padx=22)

        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        # LEFT
        left = tk.Frame(body, bg=self.panel, width=285, highlightthickness=1, highlightbackground="#33423E")
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(
            left,
            text="ARES-7  •  CAMPAIGN",
            font=("Consolas", 11, "bold"),
            bg=self.panel,
            fg=self.accent,
        ).pack(anchor="w", padx=18, pady=(16, 7))

        names = [
            "01  Establish Contact",
            "02  Align Transmission",
            "03  Restore Strength",
            "04  Corrupted Orientation",
            "05  The Mixer",
            "06  Corrupted Transmission",
            "07  Energy Crisis",
            "08  What's Inside?",
            "09  The Channel",
            "10  Unknown System",
            "11  System Failure",
            "FINAL  Save ARES-7",
        ]

        self.mission_buttons = []
        for i, name in enumerate(names, 1):
            b = tk.Button(
                left,
                text=name,
                anchor="w",
                font=("Segoe UI", 9, "bold"),
                bg=self.panel,
                fg=self.text,
                activebackground=self.panel_2,
                activeforeground=self.accent,
                relief="flat",
                bd=0,
                padx=14,
                pady=7,
                command=lambda mission_id=i: self.select_mission(mission_id),
            )
            b.pack(fill="x", padx=8)
            self.mission_buttons.append(b)

        status_box = tk.Frame(left, bg=self.panel_2, highlightthickness=1, highlightbackground="#33423E")
        status_box.pack(side="bottom", fill="x", padx=8, pady=8)

        tk.Label(
            status_box,
            text="MISSION SCORE",
            font=("Segoe UI", 8),
            bg=self.panel_2,
            fg=self.muted,
        ).pack(anchor="w", padx=10, pady=(8, 0))

        self.score_label = tk.Label(
            status_box,
            text="0",
            font=("Segoe UI", 22, "bold"),
            bg=self.panel_2,
            fg=self.text,
        )
        self.score_label.pack(anchor="w", padx=10)

        self.progress_label = tk.Label(
            status_box,
            text="0 / 12 RECOVERED",
            font=("Segoe UI", 8),
            bg=self.panel_2,
            fg=self.muted,
        )
        self.progress_label.pack(anchor="w", padx=10, pady=(0, 8))

        # RIGHT
        right = tk.Frame(body, bg=self.bg)
        right.pack(side="left", fill="both", expand=True)

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=0)
        right.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(2, weight=0, minsize=252)

        info = tk.Frame(right, bg=self.bg)
        info.grid(row=0, column=0, sticky="ew")

        self.mission_title = tk.Label(
            info,
            text="",
            font=("Segoe UI", 21, "bold"),
            bg=self.bg,
            fg=self.text,
        )
        self.mission_title.pack(anchor="w", padx=15, pady=(4, 2))

        self.mission_badge = tk.Label(
            info,
            text="MISSION 01",
            font=("Consolas", 8, "bold"),
            bg=self.panel_2,
            fg=self.accent,
            padx=10,
            pady=4,
        )
        self.mission_badge.pack(anchor="w", padx=15, pady=(0, 4))

        self.briefing = tk.Label(
            info,
            text="",
            justify="left",
            anchor="nw",
            wraplength=1080,
            font=("Segoe UI", 10),
            bg=self.bg,
            fg=self.muted,
        )
        self.briefing.pack(fill="x", padx=15, pady=(0, 5))

        graph_frame = tk.Frame(right, bg=self.panel, highlightthickness=1, highlightbackground="#33423E")
        graph_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)

        self.figure = Figure(figsize=(9, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor(self.panel)
        self.ax.set_facecolor(self.panel)

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # CONTROL PANEL
        self.input_panel = tk.Frame(
            right,
            bg=self.panel,
            height=252,
            highlightthickness=1,
            highlightbackground="#33423E",
        )
        self.input_panel.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 5),
        )
        self.input_panel.grid_propagate(False)

        top = tk.Frame(self.input_panel, bg=self.panel)
        top.pack(fill="x", padx=15, pady=(7, 0))

        tk.Label(
            top,
            text="LIVE ENGINEERING CONSOLE  •  SIGNAL DIAGNOSTICS",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel,
            fg=self.muted,
        ).pack(side="left")

        self.match_label = tk.Label(
            top,
            text="LIVE MATCH 000.0%",
            font=("Consolas", 14, "bold"),
            bg=self.panel,
            fg=self.warning,
        )
        self.match_label.pack(side="right")

        self.analyzer = tk.Label(
            self.input_panel,
            text="",
            justify="left",
            anchor="w",
            font=("Consolas", 8),
            bg=self.panel,
            fg=self.muted,
        )
        self.analyzer.pack(fill="x", padx=15, pady=(2, 2))

        tk.Label(
            self.input_panel,
            text="CONSOLE / LIVE PARAMETERS",
            font=("Consolas", 7, "bold"),
            bg=self.panel,
            fg="#D99A52",
        ).pack(anchor="w", padx=15, pady=(0, 1))

        self.controls_frame = tk.Frame(self.input_panel, bg=self.panel)
        self.controls_frame.pack(fill="both", expand=True, padx=15, pady=2)

        bottom = tk.Frame(self.input_panel, bg=self.panel)
        bottom.pack(fill="x", padx=15, pady=(0, 6))

        self.submit_button = tk.Button(
            bottom,
            text="SUBMIT",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent,
            fg=self.bg,
            activebackground=self.accent,
            relief="flat",
            padx=24,
            pady=8,
            command=self.submit_answer,
        )
        self.submit_button.pack(side="left")

        self.hint_button = tk.Button(
            bottom,
            text="HINT",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel_2,
            fg=self.warning,
            activebackground=self.panel,
            relief="flat",
            padx=20,
            pady=8,
            command=self.show_hint,
        )
        self.hint_button.pack(side="left", padx=(8, 0))

        self.status_label = tk.Label(
            bottom,
            text="SYSTEM READY  //  SIGNAL PATH ONLINE",
            font=("Consolas", 9),
            anchor="w",
            bg=self.panel,
            fg=self.accent,
        )
        self.status_label.pack(fill="x", expand=True, side="left", padx=(12, 0))

        tk.Button(
            bottom,
            text="RESET",
            font=("Consolas", 8, "bold"),
            bg=self.panel_2,
            fg=self.muted,
            activebackground="#26383F",
            activeforeground=self.text,
            relief="flat",
            padx=12,
            pady=9,
            command=self.reset_game,
        ).pack(side="right")

    # ---------------------------------------------------------
    # CONTROL HELPERS
    # ---------------------------------------------------------

    def clear_controls(self):
        for child in self.controls_frame.winfo_children():
            child.destroy()
        self.control_vars = []
        self.control_types = []

    def add_slider(
        self, label, lo, hi, resolution, target, start, row, col,
        width=170,
    ):
        frame = tk.Frame(self.controls_frame, bg=self.panel)
        frame.grid(row=row, column=col, padx=5, pady=2, sticky="w")

        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 8, "bold"),
            bg=self.panel,
            fg=self.muted,
        ).pack(anchor="w")

        var = tk.DoubleVar(value=start)

        tk.Scale(
            frame,
            from_=lo,
            to=hi,
            resolution=resolution,
            orient="horizontal",
            variable=var,
            length=width,
            showvalue=True,
            digits=4,
            bg=self.panel,
            fg=self.text,
            troughcolor=self.panel_2,
            activebackground=self.accent,
            highlightthickness=0,
            command=lambda _: self.refresh_live(),
        ).pack()

        self.control_vars.append(var)
        self.control_types.append("float")

    def add_radio(
        self, label, options, values, target, start, row, col
    ):
        frame = tk.Frame(self.controls_frame, bg=self.panel)
        frame.grid(row=row, column=col, padx=5, pady=2, sticky="w")

        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 8, "bold"),
            bg=self.panel,
            fg=self.muted,
        ).pack(anchor="w")

        var = tk.IntVar(value=start)

        for text, value in zip(options, values):
            tk.Radiobutton(
                frame,
                text=text,
                value=value,
                variable=var,
                command=self.refresh_live,
                bg=self.panel,
                fg=self.text,
                activebackground=self.panel,
                activeforeground=self.accent,
                selectcolor=self.panel_2,
                highlightthickness=0,
                font=("Segoe UI", 8),
            ).pack(side="left", padx=(0, 7))

        self.control_vars.append(var)
        self.control_types.append("int")

    def answer(self):
        result = []
        for var, kind in zip(self.control_vars, self.control_types):
            if kind == "int":
                result.append(int(var.get()))
            else:
                result.append(float(var.get()))
        return result

    # ---------------------------------------------------------
    # DELIBERATELY IMPERFECT START VALUES
    # ---------------------------------------------------------

    def wrong_near(self, target, delta):
        start = target + delta
        return start

    def load_controls(self):
        self.clear_controls()
        p = self.missions[self.current_mission].parameters
        m = self.current_mission

        if m == 1:
            self.add_slider("AMPLITUDE", 0.5, 2.25, 0.01, p["amplitude"],
                            0.65 if p["amplitude"] > 1.0 else 1.75, 0, 0)
            self.add_slider("FREQUENCY (Hz)", 2, 9, 0.1, p["frequency"],
                            2.0 if p["frequency"] > 3 else 6.0, 0, 1)
            self.add_slider("PHASE (rad)", -1.6, 1.6, 0.01, p["phase"],
                            0.0 if abs(p["phase"]) > 0.1 else 0.6, 0, 2)

        elif m == 2:
            self.add_slider("DELAY (s)", -0.25, 0.30, 0.005, p["delay"],
                            0.0, 0, 0)

        elif m == 3:
            self.add_slider("SCALE", 0.5, 4.0, 0.01, p["scale"],
                            1.0, 0, 0)

        elif m == 4:
            self.add_radio(
                "ORIENTATION",
                ["FORWARD", "REVERSED"],
                [0, 1],
                1,
                0,
                0, 0,
            )

        elif m == 5:
            self.add_slider(
                "SIGNAL A AMPLITUDE", 0.2, 1.5, 0.01, p["amp_a"],
                0.5 if abs(p["amp_a"] - 0.5) > 0.05 else 0.9, 0, 0
            )
            self.add_slider(
                "SIGNAL B AMPLITUDE", 0.2, 1.0, 0.01, p["amp_b"],
                0.25 if abs(p["amp_b"] - 0.25) > 0.05 else 0.75, 0, 1
            )

        elif m == 6:
            self.add_slider("SCALE", 1.0, 3.0, 0.01, p["scale"],
                            1.0, 0, 0)
            self.add_slider("DELAY (s)", 0.0, 0.30, 0.005, p["delay"],
                            0.0, 0, 1)
            self.add_radio(
                "REVERSAL", ["NO", "YES"], [0, 1], 1, 0, 0, 2
            )

        elif m == 7:
            self.add_radio(
                "SELECT SIGNAL",
                [
                    f"SIGNAL 1  •  A={p['amplitudes'][0]:.2f}",
                    f"SIGNAL 2  •  A={p['amplitudes'][1]:.2f}",
                    f"SIGNAL 3  •  A={p['amplitudes'][2]:.2f}",
                ],
                [1, 2, 3],
                p["correct_index"],
                2 if p["correct_index"] != 2 else 3,
                0, 0,
            )

        elif m == 8:
            for i, freq in enumerate(p["frequencies"]):
                start = freq + (15 if i != 1 else -12)
                start = max(5, min(130, start))
                self.add_slider(
                    f"GUESS F{i+1} (Hz)", 5, 130, 1,
                    freq, start, 0, i, 170
                )

        elif m == 9:
            for i, target in enumerate(p["target"]):
                self.add_slider(
                    f"y[{i}]", -4, 8, 0.1,
                    target, 0.0, i // 3, i % 3, 145
                )

        elif m in (10, 11):
            self.add_slider(
                "ESTIMATED POLE", -3.5, 3.5, 0.05,
                p["pole"],
                -2.0 if p["pole"] > 0 else 2.0,
                0, 0, 180
            )
            self.add_radio(
                "STABILITY",
                ["UNSTABLE", "STABLE"],
                [0, 1],
                p["stable"],
                0 if p["stable"] == 1 else 1,
                0, 1,
            )

        elif m == 12:
            self.add_slider("SCALE", 1.0, 3.0, 0.01,
                            p["scale"], 1.0, 0, 0)
            self.add_slider("DELAY (s)", 0.0, 0.25, 0.005,
                            p["delay"], 0.0, 0, 1)
            self.add_radio(
                "REVERSAL", ["NO", "YES"], [0, 1], 1, 0, 0, 2
            )
            start_f = p["frequency"] + 1.5
            if start_f > 14:
                start_f = p["frequency"] - 1.5
            self.add_slider(
                "FREQUENCY (Hz)", 6, 14, 0.1,
                p["frequency"], start_f, 1, 0, 170
            )
            self.add_radio(
                "SYSTEM", ["UNSTABLE", "STABLE"], [0, 1],
                p["stable"], 0 if p["stable"] == 1 else 1, 1, 1
            )

    # ---------------------------------------------------------
    # LIVE MATCH
    # ---------------------------------------------------------

    def component_score(self, actual, target, tolerance):
        return max(
            0.0,
            min(100.0, 100.0 * (1.0 - abs(actual - target) / tolerance)),
        )

    def delay_score(self, actual, target, frequency, tolerance=0.025):
        period = 1.0 / frequency
        wrapped = ((actual - target + period / 2) % period) - period / 2
        return self.component_score(abs(wrapped), 0.0, tolerance)

    def live_match(self, a):
        p = self.missions[self.current_mission].parameters
        m = self.current_mission

        if m == 1:
            return float(np.mean([
                self.component_score(a[0], p["amplitude"], 0.25),
                self.component_score(a[1], p["frequency"], 1.0),
                self.component_score(a[2], p["phase"], 0.25),
            ]))

        if m == 2:
            return self.delay_score(a[0], p["delay"], p["frequency"])

        if m == 3:
            return self.component_score(a[0], p["scale"], 0.4)

        if m == 4:
            return 100.0 if a[0] == 1 else 0.0

        if m == 5:
            return float(np.mean([
                self.component_score(a[0], p["amp_a"], 0.25),
                self.component_score(a[1], p["amp_b"], 0.20),
            ]))

        if m == 6:
            return float(np.mean([
                self.component_score(a[0], p["scale"], 0.4),
                self.component_score(a[1], p["delay"], 0.05),
                100.0 if a[2] == 1 else 0.0,
            ]))

        if m == 7:
            return 100.0 if a[0] == p["correct_index"] else 0.0

        if m == 8:
            actual = np.sort(np.asarray(a, dtype=float))
            target = np.sort(np.asarray(p["frequencies"], dtype=float))
            return float(np.mean([
                self.component_score(x, y, 10.0)
                for x, y in zip(actual, target)
            ]))

        if m == 9:
            target = np.asarray(p["target"], dtype=float)
            return float(np.mean([
                self.component_score(x, y, 1.0)
                for x, y in zip(a, target)
            ]))

        if m in (10, 11):
            pole_score = self.component_score(a[0], p["pole"], 0.6)
            stable_score = 100.0 if a[1] == p["stable"] else 0.0
            return 0.5 * pole_score + 0.5 * stable_score

        if m == 12:
            return float(np.mean([
                self.component_score(a[0], p["scale"], 0.4),
                self.component_score(a[1], p["delay"], 0.05),
                100.0 if a[2] == p["reverse"] else 0.0,
                self.component_score(a[3], p["frequency"], 1.0),
                100.0 if a[4] == p["stable"] else 0.0,
            ]))

        return 0.0

    def refresh_live(self):
        if not self.control_vars:
            return

        a = self.answer()
        self.current_match = self.live_match(a)

        if self.current_match >= 95:
            color = self.success
        elif self.current_match >= 60:
            color = self.warning
        else:
            color = self.danger

        self.match_label.config(
            text=f"LIVE MATCH {self.current_match:05.1f}%",
            fg=color,
        )

        self.update_analyzer(a)
        self.update_live_graph(a)

    # ---------------------------------------------------------
    # ANALYZER
    # ---------------------------------------------------------

    def update_analyzer(self, a):
        p = self.missions[self.current_mission].parameters
        m = self.current_mission

        if m == 1:
            text = (
                f"A: {a[0]:.2f} / {p['amplitude']:.2f}    "
                f"f: {a[1]:.2f} / {p['frequency']:.2f} Hz    "
                f"phase: {a[2]:.2f} / {p['phase']:.2f} rad"
            )
        elif m == 2:
            text = (
                f"Current delay: {a[0]:.3f} s    "
                f"Target delay: {p['delay']:.3f} s    "
                f"|error|: {abs(a[0]-p['delay']):.3f} s"
            )
        elif m == 3:
            output = p["weak_amplitude"] * a[0]
            required = p["scale"]
            text = (
                f"Input amplitude = {p['weak_amplitude']:.2f}    "
                f"Output = A×K = {output:.2f}\n"
                f"Target amplitude = {p['target_amplitude']:.2f}    "
                f"Required K = {required:.2f}"
            )
        elif m == 4:
            text = (
                f"Current: {'x[-n]' if a[0] else 'x[n]'}    "
                f"Required: x[-n]"
            )
        elif m == 5:
            text = (
                f"y(t)=x₁+x₂    "
                f"A₁={a[0]:.2f} (target {p['amp_a']:.2f})    "
                f"A₂={a[1]:.2f} (target {p['amp_b']:.2f})"
            )
        elif m == 6:
            text = (
                f"K={a[0]:.2f}/{p['scale']:.2f}    "
                f"delay={a[1]:.3f}/{p['delay']:.3f}s    "
                f"reverse={'YES' if a[2] else 'NO'}"
            )
        elif m == 7:
            i = max(1, min(3, a[0])) - 1
            amp = p["amplitudes"][i]
            e = energy(sine_wave(np.linspace(0, 1, 1000), amp, 5, 0))
            text = (
                f"Selected Signal {i+1}    "
                f"A={amp:.2f}    E=Σ|x[n]|²≈{e:.0f}    "
                f"Minimum A={p['threshold']:.2f}"
            )
        elif m == 8:
            text = (
                f"Live frequency guesses: "
                f"{a[0]:.0f}, {a[1]:.0f}, {a[2]:.0f} Hz\n"
                f"FFT target peaks: "
                f"{p['frequencies'][0]:.0f}, {p['frequencies'][1]:.0f}, "
                f"{p['frequencies'][2]:.0f} Hz"
            )
        elif m == 9:
            text = (
                f"x[n]={p['x']}    h[n]={p['h']}\n"
                f"Live y[n]={[round(v,1) for v in a]}    "
                f"Correct y[n]={p['target']}"
            )
        elif m in (10, 11):
            response = "decaying" if a[0] < 0 else "growing"
            text = (
                f"Pole={a[0]:.2f}    response={response}    "
                f"classification={'STABLE' if a[1] else 'UNSTABLE'}"
            )
        else:
            text = (
                f"K={a[0]:.2f}    delay={a[1]:.3f}s    "
                f"reverse={'YES' if a[2] else 'NO'}    "
                f"f={a[3]:.2f}Hz    "
                f"system={'STABLE' if a[4] else 'UNSTABLE'}"
            )

        self.analyzer.config(
            text=f"LIVE ANALYZER    •    {text}"
        )

    # ---------------------------------------------------------
    # LIVE GRAPHS
    # ---------------------------------------------------------

    def clear_graph(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(self.panel)
        self.figure.patch.set_facecolor(self.panel)

    def style_graph(self, title, xlabel="", ylabel=""):
        self.ax.set_title(
            title,
            color=self.text,
            fontsize=11,
            fontweight="bold",
        )
        self.ax.set_xlabel(xlabel, color=self.muted)
        self.ax.set_ylabel(ylabel, color=self.muted)
        self.ax.tick_params(colors=self.muted)
        self.ax.grid(True, alpha=0.14, linestyle="--", linewidth=0.8)

        for spine in self.ax.spines.values():
            spine.set_color("#33405f")

        self.figure.tight_layout(pad=1.0)
        self.canvas.draw_idle()

    def update_live_graph(self, a):
        p = self.missions[self.current_mission].parameters
        m = self.current_mission

        if m == 1:
            t = np.linspace(0, 1, 1000)
            target = sine_wave(t, p["amplitude"], p["frequency"], p["phase"])
            candidate = sine_wave(t, a[0], a[1], a[2])

            self.clear_graph()
            self.ax.plot(t, target, label="REFERENCE")
            self.ax.plot(t, candidate, "--", label="LIVE CANDIDATE")
            self.ax.legend()
            self.style_graph("ESTABLISH CONTACT — LIVE", "Time (s)", "Amplitude")

        elif m == 2:
            t = np.linspace(0, 1, 1000)
            ref = sine_wave(t, 1, p["frequency"], 0)
            target = sine_wave(t - p["delay"], 1, p["frequency"], 0)
            candidate = sine_wave(t - a[0], 1, p["frequency"], 0)

            self.clear_graph()
            self.ax.plot(t, ref, label="REFERENCE")
            self.ax.plot(t, target, label="RECEIVED")
            self.ax.plot(t, candidate, "--", label="LIVE SHIFT")
            self.ax.legend()
            self.style_graph("ALIGN TRANSMISSION — LIVE", "Time (s)", "Amplitude")

        elif m == 3:
            t = np.linspace(0, 1, 1000)
            weak = sine_wave(t, p["weak_amplitude"], 5, 0)
            target = sine_wave(t, p["target_amplitude"], 5, 0)
            candidate = weak * a[0]

            self.clear_graph()
            self.ax.plot(t, weak, label="WEAK INPUT")
            self.ax.plot(t, target, label="TARGET")
            self.ax.plot(t, candidate, "--", label="LIVE OUTPUT")
            self.ax.legend()
            self.style_graph("RESTORE STRENGTH — LIVE", "Time (s)", "Amplitude")

        elif m == 4:
            original = np.asarray(p["original"], dtype=float)
            target = original[::-1]
            candidate = target if a[0] == 1 else original
            x = np.arange(len(original))

            self.clear_graph()
            self.ax.stem(
                x, target, linefmt="C0-", markerfmt="C0o", basefmt=" ",
                label="RECEIVED / TARGET"
            )
            self.ax.plot(x, candidate, "--s", label="LIVE RECONSTRUCTION")
            self.ax.legend()
            self.style_graph("TIME REVERSAL — LIVE", "Sample n", "Amplitude")

        elif m == 5:
            t = np.linspace(0, 1, 1000)
            target = (
                sine_wave(t, p["amp_a"], p["freq_a"], 0)
                + sine_wave(t, p["amp_b"], p["freq_b"], 0)
            )
            live = (
                sine_wave(t, a[0], p["freq_a"], 0)
                + sine_wave(t, a[1], p["freq_b"], 0)
            )

            self.clear_graph()
            self.ax.plot(t, target, label="ACTUAL MIX")
            self.ax.plot(t, live, "--", label="LIVE MIX")
            self.ax.legend()
            self.style_graph("THE MIXER — LIVE", "Time (s)", "Amplitude")

        elif m == 6:
            t = np.linspace(0, 1, 1000)
            original = sine_wave(t, 1, 5, 0)

            target = sine_wave(t - p["delay"], p["scale"], 5, 0)
            if p["reverse"]:
                target = target[::-1]

            live = sine_wave(t - a[1], a[0], 5, 0)
            if a[2]:
                live = live[::-1]

            self.clear_graph()
            self.ax.plot(t, original, label="ORIGINAL")
            self.ax.plot(t, target, label="CORRUPTED")
            self.ax.plot(t, live, "--", label="LIVE RECOVERY")
            self.ax.legend()
            self.style_graph("MULTI-STAGE CORRUPTION — LIVE", "Time (s)", "Amplitude")

        elif m == 7:
            amps = p["amplitudes"]
            energies = [
                energy(sine_wave(np.linspace(0, 1, 1000), amp, 5, 0))
                for amp in amps
            ]

            self.clear_graph()
            bars = self.ax.bar(
                ["SIGNAL 1", "SIGNAL 2", "SIGNAL 3"],
                energies,
            )
            selected = a[0]
            for i, bar in enumerate(bars, 1):
                bar.set_alpha(1.0 if i == selected else 0.45)
            self.style_graph("ENERGY CRISIS — LIVE", "Signal", "Energy")

        elif m == 8:
            fs = 500
            t = np.arange(0, 1, 1 / fs)

            target_signal = sum(
                amp * np.sin(2 * np.pi * freq * t)
                for freq, amp in zip(p["frequencies"], p["amplitudes"])
            )
            live_signal = sum(
                amp * np.sin(2 * np.pi * freq * t)
                for freq, amp in zip(a, p["amplitudes"])
            )

            f1, mag1, _ = fft_analysis(target_signal, fs)
            f2, mag2, _ = fft_analysis(live_signal, fs)

            keep1 = (f1 >= 0) & (f1 <= 150)
            keep2 = (f2 >= 0) & (f2 <= 150)

            self.clear_graph()
            self.ax.plot(f1[keep1], mag1[keep1], label="TARGET FFT")
            self.ax.plot(f2[keep2], mag2[keep2], "--", label="LIVE FFT")
            self.ax.legend()
            self.style_graph("FFT — LIVE FREQUENCY RECOVERY", "Frequency (Hz)", "Magnitude")

        elif m == 9:
            target = np.asarray(p["target"], dtype=float)
            live = np.asarray(a, dtype=float)
            x = np.arange(len(target))

            self.clear_graph()
            self.ax.stem(
                x, target, linefmt="C0-", markerfmt="C0o", basefmt=" ",
                label="CORRECT y[n]"
            )
            self.ax.plot(x, live, "--s", label="LIVE y[n]")
            self.ax.legend()
            self.style_graph("CONVOLUTION — LIVE", "Sample n", "Amplitude")

        elif m in (10, 11):
            t = np.linspace(0, 4, 500)
            impulse = np.exp(a[0] * t)

            self.clear_graph()
            self.ax.plot(t, impulse, label="LIVE IMPULSE RESPONSE")
            self.ax.legend()
            self.style_graph("SYSTEM RESPONSE — LIVE POLE", "Time (s)", "Response")

        elif m == 12:
            t = np.linspace(0, 1, 1000)
            original = np.sin(2 * np.pi * p["frequency"] * t)

            target = (
                p["scale"]
                * np.sin(2 * np.pi * p["frequency"] * (t - p["delay"]))
            )
            if p["reverse"]:
                target = target[::-1]

            live = (
                a[0]
                * np.sin(2 * np.pi * a[3] * (t - a[1]))
            )
            if a[2]:
                live = live[::-1]

            self.clear_graph()
            self.ax.plot(t, original, label="ORIGINAL")
            self.ax.plot(t, target, label="CORRUPTED")
            self.ax.plot(t, live, "--", label="LIVE RECOVERY")
            self.ax.legend()
            self.style_graph("FINAL ARES-7 TELEMETRY — LIVE", "Time (s)", "Amplitude")

    # ---------------------------------------------------------
    # MISSION FLOW
    # ---------------------------------------------------------

    def load_mission(self, mission_id):
        self.current_mission = mission_id
        self.game.start_mission(mission_id)
        self.mission_start_time = time.time()
        self.hints_this_mission = 0

        mission = self.missions[mission_id]
        display_id = "FINAL" if mission_id == 12 else f"{mission_id:02d}"

        self.mission_title.config(
            text=f"MISSION {display_id} — {mission.title}"
        )
        self.mission_badge.config(
            text="FINAL" if mission_id == 12 else f"MISSION {mission_id:02d}"
        )
        self.briefing.config(
            text=mission.briefing
            + "\n\nOBJECTIVE\n"
            + mission.objective
        )

        self.submit_button.config(
            state="normal",
            text="SUBMIT",
            command=self.submit_answer,
        )
        self.hint_button.config(state="normal")

        self.status_label.config(
            text=f"MISSION {display_id} READY  //  CALIBRATE TRANSMISSION",
            fg=self.accent,
        )

        self.load_controls()
        self.refresh_live()
        self.update_ui()

    def select_mission(self, mission_id):
        if mission_id not in self.game.unlocked_missions:
            self.status_label.config(
                text="🔒 MISSION LOCKED — COMPLETE THE PREVIOUS MISSION",
                fg=self.warning,
            )
            return
        self.load_mission(mission_id)

    def submit_answer(self):
        a = self.answer()
        mission = self.missions[self.current_mission]

        self.game.record_attempt()
        success, error = mission.check_answer(a)

        if success:
            self.complete_mission(error)
        else:
            self.game.wrong_attempt()
            self.update_ui()
            self.status_label.config(
                text=f"✗ NOT YET — LIVE MATCH {self.current_match:.1f}%",
                fg=self.danger,
            )

    def show_hint(self):
        mission = self.missions[self.current_mission]
        self.hints_this_mission += 1
        self.game.use_hint()
        self.update_ui()
        self.status_label.config(
            text="💡 " + mission.hint,
            fg=self.warning,
        )

    def complete_mission(self, error):
        elapsed = time.time() - self.mission_start_time
        score = calculate_score(
            error=error,
            time_taken=elapsed,
            hints_used=self.hints_this_mission,
            operations_used=self.operation_counts[self.current_mission],
        )

        self.game.complete_mission(
            self.current_mission,
            score,
        )

        self.show_results(score, error, elapsed)

    def calculate_stars(self, score):
        if score >= 1100:
            return "★★★"
        if score >= 850:
            return "★★☆"
        return "★☆☆"

    def show_results(self, score, error, elapsed):
        mission_id = self.current_mission

        self.clear_graph()
        self.ax.text(
            0.5, 0.75,
            "MISSION COMPLETE",
            ha="center", va="center",
            fontsize=24, fontweight="bold",
            color=self.success, transform=self.ax.transAxes,
        )
        self.ax.text(
            0.5, 0.60,
            self.calculate_stars(score),
            ha="center", va="center",
            fontsize=28, color=self.warning,
            transform=self.ax.transAxes,
        )
        self.ax.text(
            0.5, 0.47,
            f"+{score} POINTS",
            ha="center", va="center",
            fontsize=19, color=self.accent,
            transform=self.ax.transAxes,
        )
        self.ax.text(
            0.5, 0.36,
            f"Time: {elapsed:.2f}s",
            ha="center", va="center",
            fontsize=11, color=self.text,
            transform=self.ax.transAxes,
        )
        self.ax.text(
            0.5, 0.29,
            f"Final error: {error:.4f}",
            ha="center", va="center",
            fontsize=11, color=self.muted,
            transform=self.ax.transAxes,
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw_idle()

        self.match_label.config(
            text="LIVE MATCH 100.0%",
            fg=self.success,
        )
        self.status_label.config(
            text=f"✓ MISSION {mission_id:02d} COMPLETE",
            fg=self.success,
        )

        self.hint_button.config(state="disabled")
        self.submit_button.config(
            state="normal",
            text="NEXT MISSION",
            command=self.next_mission,
        )

        self.update_ui()

    def next_mission(self):
        if self.current_mission >= 12:
            return
        self.load_mission(self.current_mission + 1)

    def show_final_results(self, elapsed):
        self.clear_graph()
        self.ax.text(
            0.5, 0.70,
            "🛰️ ARES-7 RECOVERED",
            ha="center", va="center",
            fontsize=25, fontweight="bold",
            color=self.accent, transform=self.ax.transAxes,
        )
        self.ax.text(
            0.5, 0.55,
            "SIGNAL RESCUE COMPLETE",
            ha="center", va="center",
            fontsize=19, fontweight="bold",
            color=self.success, transform=self.ax.transAxes,
        )
        self.ax.text(
            0.5, 0.43,
            f"FINAL SCORE: {self.game.total_score}",
            ha="center", va="center",
            fontsize=15, color=self.text,
            transform=self.ax.transAxes,
        )
        self.ax.text(
            0.5, 0.34,
            f"Final Mission Time: {elapsed:.2f}s",
            ha="center", va="center",
            fontsize=11, color=self.muted,
            transform=self.ax.transAxes,
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw_idle()

        self.status_label.config(
            text="🏆 ARES-7 RECOVERED — MISSION ACCOMPLISHED",
            fg=self.success,
        )
        self.match_label.config(
            text="LIVE MATCH 100.0%",
            fg=self.success,
        )
        self.submit_button.config(state="disabled")
        self.hint_button.config(state="disabled")

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def update_ui(self):
        self.score_label.config(text=str(self.game.total_score))
        self.score_header.config(
            text=f"SCORE {self.game.total_score:04d}"
        )
        self.progress_label.config(
            text=f"{self.game.missions_completed} / 12 COMPLETE"
        )

        integrity = self.game.signal_integrity
        color = (
            self.success if integrity > 50
            else self.warning if integrity > 20
            else self.danger
        )
        self.integrity_label.config(
            text=f"INTEGRITY {integrity}%",
            fg=color,
        )

        for i, button in enumerate(self.mission_buttons, 1):
            if i in self.game.completed_missions:
                button.config(bg=self.panel_2, fg=self.success)
            elif i == self.current_mission:
                button.config(bg=self.panel_2, fg=self.accent)
            elif i in self.game.unlocked_missions:
                button.config(bg=self.panel, fg=self.text)
            else:
                button.config(bg=self.panel, fg="#59647d")


def launch():
    root = tk.Tk()
    MissionControl(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
