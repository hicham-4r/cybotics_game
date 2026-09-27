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


class SettingsScreen:

    def __init__(
        self
    ):

        self.selected_index = 0

        self.row_rects = []

        self.music_bar_rect = None
        self.sfx_bar_rect = None


        self.title_font = pygame.font.SysFont(
            "consolas",
            46,
            bold=True
        )


        self.row_font = pygame.font.SysFont(
            "consolas",
            23,
            bold=True
        )


        self.value_font = pygame.font.SysFont(
            "consolas",
            20,
            bold=True
        )


        self.small_font = pygame.font.SysFont(
            "consolas",
            15
        )


    # ========================================================
    # HANDLE EVENTS
    # ========================================================

    def handle_event(
        self,
        event
    ):

        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        if event.type == pygame.KEYDOWN:

            if event.key in (
                pygame.K_ESCAPE,
                pygame.K_BACKSPACE
            ):

                return "BACK"


            if event.key in (
                pygame.K_w,
                pygame.K_UP
            ):

                self.selected_index = (
                    self.selected_index
                    - 1
                ) % 4

                return "MOVE"


            if event.key in (
                pygame.K_s,
                pygame.K_DOWN
            ):

                self.selected_index = (
                    self.selected_index
                    + 1
                ) % 4

                return "MOVE"


            if event.key == pygame.K_f:

                return "TOGGLE_FULLSCREEN"


            if event.key == pygame.K_m:

                return "TOGGLE_MUTE"


            if event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE
            ):

                if self.selected_index == 0:

                    return "TOGGLE_FULLSCREEN"


                if self.selected_index == 3:

                    return "TOGGLE_MUTE"


            if event.key in (
                pygame.K_LEFT,
                pygame.K_a,
                pygame.K_MINUS
            ):

                if self.selected_index == 1:

                    return "MUSIC_DOWN"


                if self.selected_index == 2:

                    return "SFX_DOWN"


            if event.key in (
                pygame.K_RIGHT,
                pygame.K_d,
                pygame.K_EQUALS
            ):

                if self.selected_index == 1:

                    return "MUSIC_UP"


                if self.selected_index == 2:

                    return "SFX_UP"


        # ----------------------------------------------------
        # MOUSE MOVE
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEMOTION:

            for (
                index,
                row_rect
            ) in enumerate(
                self.row_rects
            ):

                if row_rect.collidepoint(
                    event.pos
                ):

                    if (
                        self.selected_index
                        != index
                    ):

                        self.selected_index = (
                            index
                        )

                        return "MOVE"


        # ----------------------------------------------------
        # MOUSE CLICK
        # ----------------------------------------------------

        elif (
            event.type
            == pygame.MOUSEBUTTONDOWN

            and event.button == 1
        ):

            if (
                self.music_bar_rect
                is not None

                and self.music_bar_rect.collidepoint(
                    event.pos
                )
            ):

                self.selected_index = 1

                ratio = (
                    (
                        event.pos[0]
                        - self.music_bar_rect.left
                    )
                    / self.music_bar_rect.width
                )


                ratio = max(
                    0.0,
                    min(
                        1.0,
                        ratio
                    )
                )


                return (
                    "SET_MUSIC",
                    ratio
                )


            if (
                self.sfx_bar_rect
                is not None

                and self.sfx_bar_rect.collidepoint(
                    event.pos
                )
            ):

                self.selected_index = 2

                ratio = (
                    (
                        event.pos[0]
                        - self.sfx_bar_rect.left
                    )
                    / self.sfx_bar_rect.width
                )


                ratio = max(
                    0.0,
                    min(
                        1.0,
                        ratio
                    )
                )


                return (
                    "SET_SFX",
                    ratio
                )


            for (
                index,
                row_rect
            ) in enumerate(
                self.row_rects
            ):

                if row_rect.collidepoint(
                    event.pos
                ):

                    self.selected_index = (
                        index
                    )


                    if index == 0:

                        return "TOGGLE_FULLSCREEN"


                    if index == 3:

                        return "TOGGLE_MUTE"


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


        for x in range(
            0,
            WIDTH,
            spacing
        ):

            pygame.draw.line(
                surface,
                GRID_COLOR,
                (
                    x,
                    0
                ),
                (
                    x,
                    HEIGHT
                )
            )


        for y in range(
            0,
            HEIGHT,
            spacing
        ):

            pygame.draw.line(
                surface,
                GRID_COLOR,
                (
                    0,
                    y
                ),
                (
                    WIDTH,
                    y
                )
            )


    # ========================================================
    # DRAW SLIDER
    # ========================================================

    def _draw_slider(
        self,
        surface,
        rect,
        percent
    ):

        pygame.draw.rect(
            surface,
            (
                13,
                25,
                40
            ),
            rect,
            border_radius=8
        )


        pygame.draw.rect(
            surface,
            (
                50,
                85,
                110
            ),
            rect,
            width=2,
            border_radius=8
        )


        ratio = max(
            0.0,
            min(
                1.0,
                percent / 100.0
            )
        )


        inner_rect = rect.inflate(
            -6,
            -6
        )


        fill_width = int(
            inner_rect.width
            * ratio
        )


        if fill_width > 0:

            fill_rect = pygame.Rect(
                inner_rect.left,
                inner_rect.top,
                fill_width,
                inner_rect.height
            )


            pygame.draw.rect(
                surface,
                CYAN,
                fill_rect,
                border_radius=5
            )


        knob_x = int(
            inner_rect.left
            + inner_rect.width
            * ratio
        )


        pygame.draw.circle(
            surface,
            CYAN_LIGHT,
            (
                knob_x,
                rect.centery
            ),
            8
        )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface,
        fullscreen_enabled,
        audio_available,
        music_percent,
        sfx_percent,
        muted
    ):

        self._draw_background(
            surface
        )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = self.title_font.render(
            "SYSTEM SETTINGS",
            True,
            CYAN
        )


        surface.blit(
            title,
            title.get_rect(
                center=(
                    WIDTH // 2,
                    75
                )
            )
        )


        # ----------------------------------------------------
        # SAVE STATUS
        # ----------------------------------------------------

        if audio_available:

            audio_text = (
                "AUDIO SYSTEM // ONLINE"
            )

            audio_color = CYAN

        else:

            audio_text = (
                "AUDIO SYSTEM // UNAVAILABLE"
            )

            audio_color = (
                255,
                100,
                110
            )


        subtitle = self.small_font.render(
            (
                f"{audio_text}"
                "     //     "
                "SETTINGS SAVE AUTOMATICALLY"
            ),
            True,
            audio_color
        )


        surface.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    WIDTH // 2,
                    120
                )
            )
        )


        self.row_rects = []


        start_y = 165

        row_gap = 105


        for index in range(
            4
        ):

            rect = pygame.Rect(
                210,
                start_y
                + index
                * row_gap,
                860,
                82
            )


            self.row_rects.append(
                rect
            )


            selected = (
                index
                == self.selected_index
            )


            if selected:

                pygame.draw.rect(
                    surface,
                    (
                        12,
                        35,
                        50
                    ),
                    rect,
                    border_radius=9
                )


                pygame.draw.rect(
                    surface,
                    CYAN,
                    rect,
                    width=2,
                    border_radius=9
                )


            else:

                pygame.draw.rect(
                    surface,
                    (
                        8,
                        17,
                        29
                    ),
                    rect,
                    border_radius=9
                )


                pygame.draw.rect(
                    surface,
                    (
                        35,
                        55,
                        75
                    ),
                    rect,
                    width=1,
                    border_radius=9
                )


        # ----------------------------------------------------
        # DISPLAY MODE
        # ----------------------------------------------------

        display_rect = (
            self.row_rects[0]
        )


        display_label = self.row_font.render(
            "DISPLAY MODE",
            True,
            WHITE
        )


        surface.blit(
            display_label,
            (
                display_rect.left + 30,
                display_rect.centery - 14
            )
        )


        display_value = (
            "FULLSCREEN"
            if fullscreen_enabled
            else "WINDOWED"
        )


        display_value_text = (
            self.value_font.render(
                display_value,
                True,
                CYAN
            )
        )


        display_value_rect = (
            display_value_text.get_rect(
                midright=(
                    display_rect.right - 35,
                    display_rect.centery
                )
            )
        )


        surface.blit(
            display_value_text,
            display_value_rect
        )


        # ----------------------------------------------------
        # MUSIC
        # ----------------------------------------------------

        music_rect = (
            self.row_rects[1]
        )


        music_label = self.row_font.render(
            "MUSIC",
            True,
            WHITE
        )


        surface.blit(
            music_label,
            (
                music_rect.left + 30,
                music_rect.centery - 14
            )
        )


        self.music_bar_rect = pygame.Rect(
            570,
            music_rect.centery - 12,
            330,
            24
        )


        self._draw_slider(
            surface,
            self.music_bar_rect,
            music_percent
        )


        music_value = self.value_font.render(
            f"{music_percent}%",
            True,
            CYAN
        )


        surface.blit(
            music_value,
            music_value.get_rect(
                midleft=(
                    930,
                    music_rect.centery
                )
            )
        )


        # ----------------------------------------------------
        # SFX
        # ----------------------------------------------------

        sfx_rect = (
            self.row_rects[2]
        )


        sfx_label = self.row_font.render(
            "SOUND EFFECTS",
            True,
            WHITE
        )


        surface.blit(
            sfx_label,
            (
                sfx_rect.left + 30,
                sfx_rect.centery - 14
            )
        )


        self.sfx_bar_rect = pygame.Rect(
            570,
            sfx_rect.centery - 12,
            330,
            24
        )


        self._draw_slider(
            surface,
            self.sfx_bar_rect,
            sfx_percent
        )


        sfx_value = self.value_font.render(
            f"{sfx_percent}%",
            True,
            CYAN
        )


        surface.blit(
            sfx_value,
            sfx_value.get_rect(
                midleft=(
                    930,
                    sfx_rect.centery
                )
            )
        )


        # ----------------------------------------------------
        # MUTE
        # ----------------------------------------------------

        mute_rect = (
            self.row_rects[3]
        )


        mute_label = self.row_font.render(
            "GLOBAL AUDIO",
            True,
            WHITE
        )


        surface.blit(
            mute_label,
            (
                mute_rect.left + 30,
                mute_rect.centery - 14
            )
        )


        if muted:

            mute_value = "MUTED"

            mute_color = (
                255,
                100,
                110
            )

        else:

            mute_value = "ACTIVE"

            mute_color = CYAN


        mute_text = self.value_font.render(
            mute_value,
            True,
            mute_color
        )


        surface.blit(
            mute_text,
            mute_text.get_rect(
                midright=(
                    mute_rect.right - 35,
                    mute_rect.centery
                )
            )
        )


        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        controls = self.small_font.render(
            (
                "UP/DOWN // SELECT     "
                "LEFT/RIGHT // ADJUST     "
                "ENTER // TOGGLE     "
                "F // FULLSCREEN     "
                "M // MUTE"
            ),
            True,
            PURPLE
        )


        surface.blit(
            controls,
            controls.get_rect(
                center=(
                    WIDTH // 2,
                    630
                )
            )
        )


        back = self.small_font.render(
            "[ESC] RETURN TO MAIN MENU",
            True,
            WHITE
        )


        surface.blit(
            back,
            back.get_rect(
                center=(
                    WIDTH // 2,
                    665
                )
            )
        )