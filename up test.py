import customtkinter as ctk
import random
import time

# Windows audio control
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )
    volume_control = interface.QueryInterface(IAudioEndpointVolume)

    AUDIO_AVAILABLE = True

except Exception as e:
    print("Audio control unavailable:", e)
    AUDIO_AVAILABLE = False


# ---------------------------------------------------------
# APP SETTINGS
# ---------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 720

MAX_VOLUME = 100
START_VOLUME = 50

GRAVITY_START = 1.0
GRAVITY_INCREASE = 0.15

PUSH_AMOUNT = 8

GAME_UPDATE_MS = 100


# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------

class InconvenientVolumeSlider(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("VOLUNTEER — Inconvenient Volume Controller")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Game variables
        self.volume_level = START_VOLUME
        self.score = 0
        self.high_score = 0
        self.combo = 0

        self.gravity_speed = GRAVITY_START

        self.game_running = True
        self.last_push_time = time.time()

        self.event_text = "⚠ Gravity is active."
        self.event_timer = 0

        # -------------------------
        # HEADER
        # -------------------------

        self.title_label = ctk.CTkLabel(
            self,
            text="🔊 CRITICAL SYSTEM VOLUME",
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.title_label.pack(pady=(20, 3))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="The volume wants to escape.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle_label.pack()

        # -------------------------
        # STATS
        # -------------------------

        self.stats_frame = ctk.CTkFrame(
            self,
            corner_radius=15
        )
        self.stats_frame.pack(
            fill="x",
            padx=25,
            pady=15
        )

        self.score_label = ctk.CTkLabel(
            self.stats_frame,
            text="SCORE\n0",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        self.score_label.pack(side="left", expand=True, pady=12)

        self.combo_label = ctk.CTkLabel(
            self.stats_frame,
            text="COMBO\nx0",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        self.combo_label.pack(side="left", expand=True)

        self.highscore_label = ctk.CTkLabel(
            self.stats_frame,
            text="HIGH SCORE\n0",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        self.highscore_label.pack(side="left", expand=True)

        # -------------------------
        # VOLUME DISPLAY
        # -------------------------

        self.volume_label = ctk.CTkLabel(
            self,
            text="VOLUME: 50%",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.volume_label.pack(pady=(5, 5))

        self.volume_bar = ctk.CTkProgressBar(
            self,
            width=430,
            height=22,
            corner_radius=10
        )
        self.volume_bar.pack(pady=5)
        self.volume_bar.set(self.volume_level / 100)

        # -------------------------
        # BOULDER AREA
        # -------------------------

        self.canvas = ctk.CTkCanvas(
            self,
            width=430,
            height=250,
            bg="#151515",
            highlightthickness=0
        )
        self.canvas.pack(pady=15)

        self.draw_hill()

        self.boulder = self.canvas.create_oval(
            0, 0, 45, 45,
            fill="#3498db",
            outline="#5dade2",
            width=3
        )

        self.update_boulder()

        # -------------------------
        # STATUS
        # -------------------------

        self.status_label = ctk.CTkLabel(
            self,
            text=self.event_text,
            font=ctk.CTkFont(size=14),
            text_color="#bbbbbb"
        )
        self.status_label.pack(pady=5)

        # -------------------------
        # PUSH BUTTON
        # -------------------------

        self.push_button = ctk.CTkButton(
            self,
            text="🏋️ PUSH BOULDER UP!",
            width=400,
            height=55,
            corner_radius=15,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.push_up
        )
        self.push_button.pack(pady=10)

        # -------------------------
        # RESTART BUTTON
        # -------------------------

        self.restart_button = ctk.CTkButton(
            self,
            text="🔄 RESTART",
            width=180,
            height=35,
            corner_radius=10,
            fg_color="transparent",
            border_width=1,
            command=self.restart_game
        )
        self.restart_button.pack(pady=5)

        # -------------------------
        # FOOTER
        # -------------------------

        audio_status = (
            "🟢 Windows audio control ENABLED"
            if AUDIO_AVAILABLE
            else "🟡 Simulation mode"
        )

        self.audio_label = ctk.CTkLabel(
            self,
            text=audio_status,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.audio_label.pack(pady=(5, 0))

        # Start game loop
        self.after(GAME_UPDATE_MS, self.game_loop)

    # -----------------------------------------------------
    # DRAW HILL
    # -----------------------------------------------------

    def draw_hill(self):

        self.canvas.delete("hill")

        # Hill
        self.canvas.create_polygon(
            0, 250,
            0, 210,
            80, 190,
            160, 160,
            240, 130,
            320, 90,
            430, 40,
            430, 250,
            fill="#242424",
            outline="#444444",
            tags="hill"
        )

        # Ground line
        self.canvas.create_line(
            0, 250,
            430, 40,
            fill="#555555",
            width=4,
            tags="hill"
        )

    # -----------------------------------------------------
    # BOULDER POSITION
    # -----------------------------------------------------

    def update_boulder(self):

        # Convert volume to position
        progress = self.volume_level / 100

        x = 20 + progress * 360
        y = 205 - progress * 165

        self.canvas.coords(
            self.boulder,
            x,
            y,
            x + 45,
            y + 45
        )

    # -----------------------------------------------------
    # PUSH BOULDER
    # -----------------------------------------------------

    def push_up(self):

        if not self.game_running:
            return

        old_volume = self.volume_level

        self.volume_level = min(
            MAX_VOLUME,
            self.volume_level + PUSH_AMOUNT
        )

        self.apply_system_volume()

        # Combo
        current_time = time.time()

        if current_time - self.last_push_time < 1.2:
            self.combo += 1
        else:
            self.combo = 1

        self.last_push_time = current_time

        # Score
        multiplier = max(1, self.combo)

        self.score += 10 * multiplier

        # Random event
        if random.random() < 0.15:
            self.random_event()

        self.update_ui()
        self.update_boulder()

    # -----------------------------------------------------
    # GRAVITY
    # -----------------------------------------------------

    def apply_gravity(self):

        if not self.game_running:
            return

        # Gravity gets stronger as the game continues
        self.gravity_speed += GRAVITY_INCREASE / 10

        self.volume_level -= self.gravity_speed

        if self.volume_level < 0:
            self.volume_level = 0

        self.apply_system_volume()

        # Score for surviving above 50%
        if self.volume_level >= 50:
            self.score += 1

        # Game over
        if self.volume_level <= 0:
            self.game_over()

        self.update_ui()
        self.update_boulder()

    # -----------------------------------------------------
    # RANDOM EVENTS
    # -----------------------------------------------------

    def random_event(self):

        events = [
            ("💀 GRAVITY SPIKE!", 2.5),
            ("😈 THE BOULDER IS ANGRY!", 3.0),
            ("🤡 WHY ARE YOU STILL PLAYING?", 2.0),
            ("📢 YOUR SPEAKERS ARE JUDGING YOU.", 1.5),
            ("🧠 PRODUCTIVITY HAS DECREASED.", 2.0),
            ("⚠ SYSTEM ADMINISTRATION HAS BEEN NOTIFIED.", 2.5)
        ]

        message, extra_gravity = random.choice(events)

        self.event_text = message
        self.gravity_speed += extra_gravity

        self.status_label.configure(
            text=message
        )

        self.after(
            2500,
            lambda: self.status_label.configure(
                text="⚠ Gravity is active."
            )
        )

    # -----------------------------------------------------
    # GAME LOOP
    # -----------------------------------------------------

    def game_loop(self):

        if self.game_running:
            self.apply_gravity()

        self.after(
            GAME_UPDATE_MS,
            self.game_loop
        )

    # -----------------------------------------------------
    # SYSTEM VOLUME
    # -----------------------------------------------------

    def apply_system_volume(self):

        if AUDIO_AVAILABLE:

            try:
                volume_control.SetMasterVolumeLevelScalar(
                    self.volume_level / 100,
                    None
                )

            except Exception as e:
                print("Volume error:", e)

    # -----------------------------------------------------
    # UPDATE UI
    # -----------------------------------------------------

    def update_ui(self):

        volume = int(self.volume_level)

        self.volume_label.configure(
            text=f"VOLUME: {volume}%"
        )

        self.volume_bar.set(
            self.volume_level / 100
        )

        self.score_label.configure(
            text=f"SCORE\n{self.score}"
        )

        self.combo_label.configure(
            text=f"COMBO\nx{self.combo}"
        )

        self.highscore_label.configure(
            text=f"HIGH SCORE\n{self.high_score}"
        )

        # Dynamic messages
        if volume >= 90:
            self.status_label.configure(
                text="🔥 DANGER: YOUR EARS ARE IN DANGER."
            )

        elif volume >= 70:
            self.status_label.configure(
                text="😎 Loud enough to annoy the neighbors."
            )

        elif volume >= 50:
            self.status_label.configure(
                text="⚠ Keep pushing!"
            )

        elif volume >= 25:
            self.status_label.configure(
                text="😰 THE BOULDER IS LOSING."
            )

        else:
            self.status_label.configure(
                text="💀 VOLUME CRITICAL."
            )

    # -----------------------------------------------------
    # GAME OVER
    # -----------------------------------------------------

    def game_over(self):

        if not self.game_running:
            return

        self.game_running = False

        # High score
        if self.score > self.high_score:
            self.high_score = self.score

        self.push_button.configure(
            text="💀 GAME OVER",
            state="disabled"
        )

        self.status_label.configure(
            text=f"💀 BOULDER LOST! Final Score: {self.score}"
        )

        self.volume_label.configure(
            text="VOLUME: 0%"
        )

    # -----------------------------------------------------
    # RESTART
    # -----------------------------------------------------

    def restart_game(self):

        self.volume_level = START_VOLUME
        self.score = 0
        self.combo = 0

        self.gravity_speed = GRAVITY_START

        self.game_running = True

        self.push_button.configure(
            text="🏋️ PUSH BOULDER UP!",
            state="normal"
        )

        self.status_label.configure(
            text="⚠ Gravity is active."
        )

        self.apply_system_volume()

        self.update_ui()
        self.update_boulder()


# ---------------------------------------------------------
# START
# ---------------------------------------------------------

if __name__ == "__main__":

    app = InconvenientVolumeSlider()

    app.mainloop()
