from pathlib import Path
import math

import pygame

from settings import (
    WIDTH,
    HEIGHT,
    BACKGROUND,
    GRID_COLOR,
    CYAN,
    CYAN_LIGHT,
    PURPLE,
    WHITE,
)


class MainMenu:

    def __init__(
        self,
        logo_path,
        sound_manager=None
    ):
        self.logo_path = Path(
            logo_path
        )

        self.sound_manager = (
            sound_manager
        )

        self.options = [
            ("START RUN", "START"),
            ("LEADERBOARD", "LEADERBOARD"),
            ("SETTINGS", "SETTINGS"),
            ("EXIT", "EXIT"),
        ]

        self.selected_index = 0

        self.option_rects = []

        self.elapsed_time = 0.0

        self.selection_amounts = [
            0.0
            for _ in self.options
        ]

        self.selection_amounts[0] = 1.0

        self.title_font = pygame.font.SysFont(
            "consolas",
            48,
            bold=True
        )

        self.subtitle_font = pygame.font.SysFont(
            "consolas",
            20,
            bold=True
        )

        self.option_font = pygame.font.SysFont(
            "consolas",
            25,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "consolas",
            15
        )

        self.logo = (
            self._load_logo()
        )

        # Decorative digital nodes.
        self.nodes = []

        for index in range(
            24
        ):
            x = (
                45
                + (
                    index * 167
                )
                % (
                    WIDTH - 90
                )
            )

            y = (
                60
                + (
                    index * 103
                )
                % (
                    HEIGHT - 120
                )
            )

            phase = (
                index * 0.63
            )

            self.nodes.append(
                (
                    x,
                    y,
                    phase
                )
            )

    # ========================================================
    # SOUND
    # ========================================================

    def _play_sound(
        self,
        sound_name
    ):
        if self.sound_manager is None:
            return

        self.sound_manager.play(
            sound_name
        )

    # ========================================================
    # LOGO
    # ========================================================

    def _load_logo(
        self
    ):
        if not self.logo_path.exists():
            return None

        try:
            logo = pygame.image.load(
                str(
                    self.logo_path
                )
            ).convert_alpha()

            max_width = 175
            max_height = 175

            width = logo.get_width()
            height = logo.get_height()

            scale = min(
                max_width / width,
                max_height / height
            )

            return pygame.transform.smoothscale(
                logo,
                (
                    int(
                        width * scale
                    ),
                    int(
                        height * scale
                    )
                )
            )

        except pygame.error:
            return None

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

        self.elapsed_time += dt

        # Smoothly animate button selection.
        animation_speed = 9.0

        for index in range(
            len(
                self.selection_amounts
            )
        ):
            target = (
                1.0
                if index == self.selected_index
                else 0.0
            )

            current = (
                self.selection_amounts[
                    index
                ]
            )

            difference = (
                target - current
            )

            step = min(
                1.0,
                animation_speed * dt
            )

            self.selection_amounts[
                index
            ] += (
                difference * step
            )

    # ========================================================
    # EVENTS
    # ========================================================

    def handle_event(
        self,
        event
    ):
        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_w,
                pygame.K_UP
            ):
                self.selected_index -= 1
                self.selected_index %= len(
                    self.options
                )

                self._play_sound(
                    "menu_move"
                )

            elif event.key in (
                pygame.K_s,
                pygame.K_DOWN
            ):
                self.selected_index += 1
                self.selected_index %= len(
                    self.options
                )

                self._play_sound(
                    "menu_move"
                )

            elif event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE
            ):
                self._play_sound(
                    "menu_click"
                )

                return self.options[
                    self.selected_index
                ][1]

            elif event.key == pygame.K_ESCAPE:
                self._play_sound(
                    "menu_click"
                )

                return "EXIT"

        elif event.type == pygame.MOUSEMOTION:
            for index, rect in enumerate(
                self.option_rects
            ):
                if rect.collidepoint(
                    event.pos
                ):
                    if (
                        self.selected_index
                        != index
                    ):
                        self.selected_index = (
                            index
                        )

                        self._play_sound(
                            "menu_move"
                        )

                    break

        elif (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            for index, rect in enumerate(
                self.option_rects
            ):
                if rect.collidepoint(
                    event.pos
                ):
                    self.selected_index = (
                        index
                    )

                    self._play_sound(
                        "menu_click"
                    )

                    return self.options[
                        index
                    ][1]

        return None

    # ========================================================
    # BACKGROUND
    # ========================================================

    def _draw_background(
        self,
        surface
    ):
        surface.fill(
            BACKGROUND
        )

        spacing = 40

        # Slow movement makes the grid feel alive without
        # distracting from menu text.
        offset_x = int(
            (
                self.elapsed_time
                * 7
            )
            % spacing
        )

        offset_y = int(
            (
                self.elapsed_time
                * 4
            )
            % spacing
        )

        for x in range(
            -spacing,
            WIDTH + spacing,
            spacing
        ):
            actual_x = (
                x + offset_x
            )

            pygame.draw.line(
                surface,
                GRID_COLOR,
                (
                    actual_x,
                    0
                ),
                (
                    actual_x,
                    HEIGHT
                )
            )

        for y in range(
            -spacing,
            HEIGHT + spacing,
            spacing
        ):
            actual_y = (
                y + offset_y
            )

            pygame.draw.line(
                surface,
                GRID_COLOR,
                (
                    0,
                    actual_y
                ),
                (
                    WIDTH,
                    actual_y
                )
            )

        # ----------------------------------------------------
        # DIGITAL NODES
        # ----------------------------------------------------

        node_surface = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        for (
            x,
            y,
            phase
        ) in self.nodes:
            pulse = (
                math.sin(
                    self.elapsed_time
                    * 1.8
                    + phase
                )
                + 1
            ) / 2

            alpha = int(
                25
                + pulse * 55
            )

            radius = (
                1
                if pulse < 0.55
                else 2
            )

            pygame.draw.circle(
                node_surface,
                (
                    CYAN[0],
                    CYAN[1],
                    CYAN[2],
                    alpha
                ),
                (
                    x,
                    y
                ),
                radius
            )

        surface.blit(
            node_surface,
            (
                0,
                0
            )
        )

        # ----------------------------------------------------
        # CENTRAL ENERGY LINE
        # ----------------------------------------------------

        line_alpha = int(
            55
            + 35
            * (
                math.sin(
                    self.elapsed_time
                    * 1.4
                )
                + 1
            )
            / 2
        )

        line_surface = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        pygame.draw.line(
            line_surface,
            (
                30,
                160,
                220,
                line_alpha
            ),
            (
                WIDTH // 2,
                0
            ),
            (
                WIDTH // 2,
                HEIGHT
            ),
            width=1
        )

        surface.blit(
            line_surface,
            (
                0,
                0
            )
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface
    ):
        self._draw_background(
            surface
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo_y = int(
            125
            + math.sin(
                self.elapsed_time
                * 1.35
            )
            * 4
        )

        if self.logo is not None:
            glow_surface = pygame.Surface(
                (
                    250,
                    250
                ),
                pygame.SRCALPHA
            )

            pulse = (
                math.sin(
                    self.elapsed_time
                    * 2.0
                )
                + 1
            ) / 2

            pygame.draw.circle(
                glow_surface,
                (
                    50,
                    190,
                    255,
                    int(
                        18
                        + pulse * 18
                    )
                ),
                (
                    125,
                    125
                ),
                95
            )

            surface.blit(
                glow_surface,
                (
                    WIDTH // 2 - 125,
                    logo_y - 125
                )
            )

            logo_rect = self.logo.get_rect(
                center=(
                    WIDTH // 2,
                    logo_y
                )
            )

            surface.blit(
                self.logo,
                logo_rect
            )

        # ----------------------------------------------------
        # TITLES
        # ----------------------------------------------------

        system_text = self.subtitle_font.render(
            "CYBOTICS // INTERACTIVE SYSTEM",
            True,
            PURPLE
        )

        surface.blit(
            system_text,
            system_text.get_rect(
                center=(
                    WIDTH // 2,
                    230
                )
            )
        )

        title_pulse = (
            math.sin(
                self.elapsed_time
                * 2.2
            )
            + 1
        ) / 2

        title_color = (
            int(
                70
                + 40 * title_pulse
            ),
            int(
                210
                + 30 * title_pulse
            ),
            255
        )

        title = self.title_font.render(
            "GRAVITY SHIFT",
            True,
            title_color
        )

        surface.blit(
            title,
            title.get_rect(
                center=(
                    WIDTH // 2,
                    280
                )
            )
        )

        subtitle = self.small_font.render(
            (
                "GRAVITY CONTROL PROTOCOL "
                "// SYSTEM READY"
            ),
            True,
            CYAN_LIGHT
        )

        surface.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    WIDTH // 2,
                    320
                )
            )
        )

        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        self.option_rects = []

        start_y = 390
        spacing = 62

        for index, option in enumerate(
            self.options
        ):
            option_name = option[0]

            amount = (
                self.selection_amounts[
                    index
                ]
            )

            selected = (
                index == self.selected_index
            )

            width = int(
                400
                + 22 * amount
            )

            x = (
                WIDTH // 2
                - width // 2
            )

            y = (
                start_y
                + index * spacing
            )

            button_rect = pygame.Rect(
                x,
                y,
                width,
                46
            )

            if amount > 0.02:
                glow_surface = pygame.Surface(
                    (
                        width + 30,
                        66
                    ),
                    pygame.SRCALPHA
                )

                pygame.draw.rect(
                    glow_surface,
                    (
                        40,
                        190,
                        255,
                        int(
                            35 * amount
                        )
                    ),
                    pygame.Rect(
                        5,
                        5,
                        width + 20,
                        56
                    ),
                    border_radius=10
                )

                surface.blit(
                    glow_surface,
                    (
                        button_rect.x - 15,
                        button_rect.y - 10
                    )
                )

            if selected:
                fill_color = (
                    13,
                    35,
                    52
                )

                border_color = CYAN
                text_color = CYAN

            else:
                fill_color = (
                    10,
                    18,
                    30
                )

                border_color = (
                    int(
                        35
                        + 25 * amount
                    ),
                    int(
                        55
                        + 70 * amount
                    ),
                    int(
                        75
                        + 80 * amount
                    )
                )

                text_color = WHITE

            pygame.draw.rect(
                surface,
                fill_color,
                button_rect,
                border_radius=6
            )

            pygame.draw.rect(
                surface,
                border_color,
                button_rect,
                width=(
                    2
                    if selected
                    else 1
                ),
                border_radius=6
            )

            marker = (
                ">"
                if selected
                else " "
            )

            text = self.option_font.render(
                f"{marker} {option_name}",
                True,
                text_color
            )

            surface.blit(
                text,
                text.get_rect(
                    center=button_rect.center
                )
            )

            if selected:
                # Animated accent on the right.
                accent_length = int(
                    20
                    + 12
                    * (
                        math.sin(
                            self.elapsed_time
                            * 5
                        )
                        + 1
                    )
                    / 2
                )

                pygame.draw.line(
                    surface,
                    PURPLE,
                    (
                        button_rect.right
                        + 10,
                        button_rect.centery
                    ),
                    (
                        button_rect.right
                        + 10
                        + accent_length,
                        button_rect.centery
                    ),
                    width=2
                )

            self.option_rects.append(
                button_rect
            )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        instructions = self.small_font.render(
            (
                "W/S OR ARROWS // NAVIGATE"
                "     ENTER // SELECT"
                "     F11 // FULLSCREEN"
            ),
            True,
            PURPLE
        )

        surface.blit(
            instructions,
            instructions.get_rect(
                center=(
                    WIDTH // 2,
                    655
                )
            )
        )

        version = self.small_font.render(
            (
                "CYBOTICS // GRAVITY SHIFT "
                "// CORE SYSTEM"
            ),
            True,
            (
                80,
                100,
                120
            )
        )

        surface.blit(
            version,
            (
                20,
                HEIGHT - 25
            )
        )