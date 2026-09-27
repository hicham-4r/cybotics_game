import math

import pygame

from settings import (
    WIDTH,
    HEIGHT,
    CYAN,
    CYAN_LIGHT,
    PURPLE,
    WHITE,
)


class TransitionManager:

    def __init__(
        self,
        width=WIDTH,
        height=HEIGHT
    ):
        self.width = width
        self.height = height

        # Fade state:
        #
        # None
        # OUT
        # HOLD
        # IN
        self.mode = None

        self.alpha = 0

        self.fade_elapsed = 0.0
        self.fade_duration = 0.0

        self.pending_action = None

        # Level intro card.
        self.intro_level = None
        self.intro_name = ""

        self.intro_duration = 0.0
        self.intro_remaining = 0.0

        self.queued_intro = None

        self.level_font = pygame.font.SysFont(
            "consolas",
            19,
            bold=True
        )

        self.name_font = pygame.font.SysFont(
            "consolas",
            30,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "consolas",
            14
        )

    # ========================================================
    # STATE
    # ========================================================

    @property
    def busy(self):
        return self.mode is not None

    @property
    def blocks_input(self):
        return self.mode is not None

    @property
    def blocks_gameplay(self):
        # Timers and physics stop while the screen transitions.
        #
        # This prevents the player losing time while the screen
        # is black.
        return self.mode is not None

    # ========================================================
    # FADE OUT
    # ========================================================

    def start_fade_out(
        self,
        action,
        duration=0.22
    ):
        if self.mode is not None:
            return False

        self.mode = "OUT"

        self.fade_elapsed = 0.0
        self.fade_duration = max(
            0.05,
            float(duration)
        )

        self.alpha = 0

        self.pending_action = action

        return True

    # ========================================================
    # FADE IN
    # ========================================================

    def start_fade_in(
        self,
        duration=0.32,
        level_number=None,
        level_name=None
    ):
        self.mode = "IN"

        self.fade_elapsed = 0.0
        self.fade_duration = max(
            0.05,
            float(duration)
        )

        self.alpha = 255

        if (
            level_number is not None
            and level_name is not None
        ):
            self.queued_intro = (
                int(level_number),
                str(level_name)
            )
        else:
            self.queued_intro = None

    # ========================================================
    # LEVEL INTRO
    # ========================================================

    def start_level_intro(
        self,
        level_number,
        level_name,
        duration=1.35
    ):
        self.intro_level = int(
            level_number
        )

        self.intro_name = str(
            level_name
        ).upper()

        self.intro_duration = max(
            0.2,
            float(duration)
        )

        self.intro_remaining = (
            self.intro_duration
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):
        dt = min(
            max(
                0.0,
                float(dt)
            ),
            0.05
        )

        transition_action = None

        # ----------------------------------------------------
        # INTRO TIMER
        # ----------------------------------------------------

        if self.intro_remaining > 0:
            self.intro_remaining = max(
                0.0,
                self.intro_remaining - dt
            )

        # ----------------------------------------------------
        # NO FADE ACTIVE
        # ----------------------------------------------------

        if self.mode is None:
            return None

        # ----------------------------------------------------
        # FADE OUT
        # ----------------------------------------------------

        if self.mode == "OUT":
            self.fade_elapsed += dt

            progress = min(
                1.0,
                self.fade_elapsed
                / self.fade_duration
            )

            # Smooth ease-in.
            eased = progress * progress

            self.alpha = int(
                255 * eased
            )

            if progress >= 1.0:
                self.alpha = 255

                self.mode = "HOLD"

                transition_action = (
                    self.pending_action
                )

                self.pending_action = None

        # ----------------------------------------------------
        # FADE IN
        # ----------------------------------------------------

        elif self.mode == "IN":
            self.fade_elapsed += dt

            progress = min(
                1.0,
                self.fade_elapsed
                / self.fade_duration
            )

            # Smooth ease-out.
            eased = (
                1.0
                - (
                    1.0 - progress
                )
                * (
                    1.0 - progress
                )
            )

            self.alpha = int(
                255
                * (
                    1.0 - eased
                )
            )

            if progress >= 1.0:
                self.alpha = 0

                self.mode = None

                if self.queued_intro is not None:
                    level_number, level_name = (
                        self.queued_intro
                    )

                    self.start_level_intro(
                        level_number,
                        level_name
                    )

                    self.queued_intro = None

        return transition_action

    # ========================================================
    # DRAW INTRO CARD
    # ========================================================

    def _draw_intro(
        self,
        surface
    ):
        if (
            self.intro_remaining <= 0
            or self.intro_duration <= 0
            or self.intro_level is None
        ):
            return

        elapsed = (
            self.intro_duration
            - self.intro_remaining
        )

        # ----------------------------------------------------
        # FADE IN/OUT OF CARD
        # ----------------------------------------------------

        fade_in = min(
            1.0,
            elapsed / 0.18
        )

        fade_out = min(
            1.0,
            self.intro_remaining / 0.25
        )

        visibility = min(
            fade_in,
            fade_out
        )

        visibility = max(
            0.0,
            min(
                1.0,
                visibility
            )
        )

        if visibility <= 0:
            return

        # ----------------------------------------------------
        # SLIDE ANIMATION
        # ----------------------------------------------------

        eased = (
            1.0
            - (
                1.0 - fade_in
            )
            * (
                1.0 - fade_in
            )
        )

        center_y = int(
            120
            - 18
            * (
                1.0 - eased
            )
        )

        panel_width = 530
        panel_height = 92

        panel = pygame.Surface(
            (
                panel_width,
                panel_height
            ),
            pygame.SRCALPHA
        )

        alpha = int(
            235
            * visibility
        )

        pygame.draw.rect(
            panel,
            (
                5,
                13,
                25,
                alpha
            ),
            panel.get_rect(),
            border_radius=10
        )

        pygame.draw.rect(
            panel,
            (
                CYAN[0],
                CYAN[1],
                CYAN[2],
                int(
                    210 * visibility
                )
            ),
            panel.get_rect(),
            width=2,
            border_radius=10
        )

        # Left accent.
        pygame.draw.rect(
            panel,
            (
                PURPLE[0],
                PURPLE[1],
                PURPLE[2],
                int(
                    230 * visibility
                )
            ),
            pygame.Rect(
                0,
                12,
                5,
                panel_height - 24
            ),
            border_radius=3
        )

        level_text = self.level_font.render(
            f"LEVEL {self.intro_level:02d}",
            True,
            CYAN
        )

        level_text.set_alpha(
            int(
                255 * visibility
            )
        )

        name_text = self.name_font.render(
            self.intro_name,
            True,
            WHITE
        )

        name_text.set_alpha(
            int(
                255 * visibility
            )
        )

        system_text = self.small_font.render(
            "CYBOTICS // GRAVITY PROTOCOL",
            True,
            PURPLE
        )

        system_text.set_alpha(
            int(
                255 * visibility
            )
        )

        panel.blit(
            level_text,
            (
                28,
                13
            )
        )

        panel.blit(
            name_text,
            (
                28,
                36
            )
        )

        panel.blit(
            system_text,
            (
                300,
                17
            )
        )

        # Animated scan line.
        scan_x = int(
            (
                elapsed
                * 360
            )
            % (
                panel_width + 80
            )
        ) - 40

        pygame.draw.line(
            panel,
            (
                150,
                240,
                255,
                int(
                    80 * visibility
                )
            ),
            (
                scan_x,
                0
            ),
            (
                scan_x - 35,
                panel_height
            ),
            width=2
        )

        surface.blit(
            panel,
            panel.get_rect(
                center=(
                    self.width // 2,
                    center_y
                )
            )
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface
    ):
        # Intro is underneath the black fade so that a new
        # level naturally emerges from darkness.
        self._draw_intro(
            surface
        )

        if self.alpha <= 0:
            return

        fade_surface = pygame.Surface(
            (
                self.width,
                self.height
            ),
            pygame.SRCALPHA
        )

        fade_surface.fill(
            (
                2,
                4,
                10,
                self.alpha
            )
        )

        surface.blit(
            fade_surface,
            (
                0,
                0
            )
        )