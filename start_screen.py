
import math
import time
import tkinter as tk
from pathlib import Path

try:
    from PIL import Image, ImageTk, ImageEnhance, ImageOps
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


BG = "#070D12"
PANEL = "#111B20"
TEAL = "#52D0C0"
CREAM = "#FFF2D0"
MUTED = "#AEBDB5"
AMBER = "#D99A52"
GREEN = "#87DFA5"


class StartScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("SIGNAL RESCUE — ARES-7")
        self.root.geometry("1280x760")
        self.root.minsize(1050, 650)
        self.root.configure(bg=BG)
        self.loading = 0

        self.art_photo = None

        self.build()
        self.animate()

    def build(self):
        self.main = tk.Frame(
            self.root,
            bg=BG,
            highlightthickness=1,
            highlightbackground="#33423E",
        )
        self.main.pack(fill="both", expand=True, padx=18, pady=18)

        # Header strip
        header = tk.Frame(self.main, bg=PANEL, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="ARES-7  //  COMMUNICATIONS RECOVERY UNIT",
            font=("Consolas", 10, "bold"),
            bg=PANEL,
            fg=TEAL,
        ).pack(side="left", padx=18)

        tk.Label(
            header,
            text="SYSTEM 2087",
            font=("Consolas", 9, "bold"),
            bg=PANEL,
            fg=AMBER,
        ).pack(side="right", padx=18)

        tk.Frame(self.main, bg=AMBER, height=2).pack(fill="x")

        body = tk.Frame(self.main, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=22)

        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left: title and boot information
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        tk.Label(
            left,
            text="SIGNAL",
            font=("Segoe UI", 38, "bold"),
            bg=BG,
            fg=CREAM,
        ).pack(anchor="w", pady=(32, 0))

        tk.Label(
            left,
            text="RESCUE",
            font=("Segoe UI", 38, "bold"),
            bg=BG,
            fg=TEAL,
        ).pack(anchor="w", pady=(0, 18))

        tk.Label(
            left,
            text="ARES-7 DEEP-SPACE TELEMETRY RECOVERY",
            font=("Consolas", 10, "bold"),
            bg=BG,
            fg=MUTED,
        ).pack(anchor="w")

        tk.Frame(left, bg="#33423E", height=1).pack(
            fill="x", pady=18
        )

        self.boot_title = tk.Label(
            left,
            text="INITIALIZING SIGNAL SYSTEMS",
            font=("Consolas", 11, "bold"),
            bg=BG,
            fg=AMBER,
        )
        self.boot_title.pack(anchor="w")

        self.boot_log = tk.Label(
            left,
            text="",
            justify="left",
            anchor="nw",
            font=("Consolas", 9),
            bg=BG,
            fg=MUTED,
        )
        self.boot_log.pack(anchor="w", pady=(10, 0))

        self.bar_frame = tk.Frame(left, bg="#19272C", height=16)
        self.bar_frame.pack(fill="x", pady=(24, 8))
        self.bar_frame.pack_propagate(False)

        self.bar = tk.Frame(self.bar_frame, bg=TEAL, width=0)
        self.bar.pack(side="left", fill="y")

        self.percent = tk.Label(
            left,
            text="0%",
            font=("Consolas", 9, "bold"),
            bg=BG,
            fg=TEAL,
        )
        self.percent.pack(anchor="w")

        self.start_button = tk.Button(
            left,
            text="ENTER MISSION CONTROL",
            font=("Segoe UI", 11, "bold"),
            bg=TEAL,
            fg=BG,
            activebackground=CREAM,
            activeforeground=BG,
            relief="flat",
            padx=24,
            pady=12,
            command=self.start_game,
        )

        # Right: retro artwork
        art = tk.Frame(
            body,
            bg="#0B1318",
            highlightthickness=1,
            highlightbackground="#33423E",
        )
        art.grid(row=0, column=1, sticky="nsew")
        art.pack_propagate(False)

        self.art_label = tk.Label(
            art,
            bg="#0B1318",
            fg=TEAL,
            text="NO VISUAL FEED",
            font=("Consolas", 11, "bold"),
        )
        self.art_label.pack(fill="both", expand=True)

        if PIL_AVAILABLE:
            try:
                art_path = (
                    Path(__file__).resolve().parent.parent
                    / "assets"
                    / "retro_space_art.png"
                )
                if art_path.exists():
                    img = Image.open(art_path).convert("RGB")
                    img = ImageOps.fit(
                        img,
                        (900, 610),
                        method=Image.Resampling.LANCZOS,
                        centering=(0.5, 0.42),
                    )
                    img = ImageEnhance.Contrast(img).enhance(0.90)
                    img = ImageEnhance.Color(img).enhance(0.76)
                    img = ImageEnhance.Brightness(img).enhance(0.64)
                    self.art_photo = ImageTk.PhotoImage(img)
                    self.art_label.config(image=self.art_photo, text="")
            except Exception:
                pass

        # Footer
        footer = tk.Frame(self.main, bg=PANEL, height=34)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="SIGNAL RESCUE  •  SIGNALS & SYSTEMS TRAINING SIMULATION",
            font=("Consolas", 8),
            bg=PANEL,
            fg=MUTED,
        ).pack(side="left", padx=14)

        self.connection = tk.Label(
            footer,
            text="● LOCAL SIGNAL LINK",
            font=("Consolas", 8, "bold"),
            bg=PANEL,
            fg=GREEN,
        )
        self.connection.pack(side="right", padx=14)

        self.start_button.pack(anchor="w", pady=(28, 0))

    def animate(self):
        self.loading += 2
        stages = [
            (10, "CALIBRATING SIGNAL ARRAY"),
            (25, "LOADING ARES-7 TELEMETRY"),
            (42, "INITIALIZING FOURIER MODULE"),
            (59, "INITIALIZING CONVOLUTION ENGINE"),
            (76, "INITIALIZING SYSTEM ANALYSIS"),
            (90, "CHECKING RECOVERY CHANNEL"),
            (100, "SYSTEM READY"),
        ]

        message = stages[-1][1]
        for limit, text in stages:
            if self.loading <= limit:
                message = text
                break

        width = max(0, int(self.loading * 4.7))
        self.bar.config(width=width)
        self.percent.config(text=f"{min(self.loading,100)}%")
        self.boot_title.config(text=message)

        log = [
            "[ OK ] signal generators",
            "[ OK ] transformation engine",
            "[ OK ] frequency analyzer",
            "[ OK ] channel model",
            "[ OK ] stability monitor",
        ]
        visible = min(len(log), max(1, self.loading // 20))
        self.boot_log.config(text="\n".join(log[:visible]))

        if self.loading < 100:
            self.root.after(45, self.animate)
        else:
            self.connection.config(text="● LINK ESTABLISHED", fg=GREEN)

    def start_game(self):
        self.start_button.config(state="disabled", text="OPENING MISSION CONTROL...")
        self.root.after(180, self.launch_mission_control)

    def launch_mission_control(self):
        self.root.destroy()

        from ui.mission_control import MissionControl

        app_root = tk.Tk()
        MissionControl(app_root)
        app_root.mainloop()


def launch():
    root = tk.Tk()
    StartScreen(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
