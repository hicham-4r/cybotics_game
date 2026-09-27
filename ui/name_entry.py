import pygame

from settings import (
    WIDTH,
    HEIGHT,
    BACKGROUND,
    GRID_COLOR,
    CYAN,
    PURPLE,
    WHITE,
)


class NameEntryScreen:

    MIN_LENGTH = 3
    MAX_LENGTH = 12


    def __init__(self):

        self.value = ""
        self.error_message = ""


        self.title_font = pygame.font.SysFont(
            "consolas",
            48,
            bold=True
        )


        self.input_font = pygame.font.SysFont(
            "consolas",
            34,
            bold=True
        )


        self.normal_font = pygame.font.SysFont(
            "consolas",
            20
        )


        self.small_font = pygame.font.SysFont(
            "consolas",
            16
        )


    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.value = ""
        self.error_message = ""


    # ========================================================
    # EXTERNAL ERROR
    # ========================================================

    def set_error(
        self,
        message
    ):

        self.error_message = str(
            message
        )


    # ========================================================
    # VALID CHARACTER
    # ========================================================

    def _is_valid_character(
        self,
        character
    ):

        return (
            character.isalnum()
            or character in "_-"
        )


    # ========================================================
    # HANDLE EVENT
    # ========================================================

    def handle_event(
        self,
        event
    ):

        if event.type != pygame.KEYDOWN:

            return None


        # ----------------------------------------------------
        # BACK
        # ----------------------------------------------------

        if event.key == pygame.K_ESCAPE:

            return "BACK"


        # ----------------------------------------------------
        # BACKSPACE
        # ----------------------------------------------------

        if event.key == pygame.K_BACKSPACE:

            self.value = (
                self.value[:-1]
            )

            self.error_message = ""

            return None


        # ----------------------------------------------------
        # CONFIRM
        # ----------------------------------------------------

        if event.key == pygame.K_RETURN:

            clean_name = (
                self.value
                .strip()
                .upper()
            )


            if len(
                clean_name
            ) < self.MIN_LENGTH:

                self.error_message = (
                    "NAME MUST CONTAIN AT LEAST 3 CHARACTERS"
                )

                return None


            if len(
                clean_name
            ) > self.MAX_LENGTH:

                self.error_message = (
                    "NAME CANNOT EXCEED 12 CHARACTERS"
                )

                return None


            self.value = (
                clean_name
            )

            self.error_message = ""

            return "SUBMIT"


        # ----------------------------------------------------
        # TYPE CHARACTER
        # ----------------------------------------------------

        character = (
            event.unicode
        )


        if (
            character
            and len(
                self.value
            ) < self.MAX_LENGTH
            and self._is_valid_character(
                character
            )
        ):

            self.value += (
                character.upper()
            )

            self.error_message = ""


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
                (x, 0),
                (x, HEIGHT)
            )


        for y in range(
            0,
            HEIGHT,
            spacing
        ):

            pygame.draw.line(
                surface,
                GRID_COLOR,
                (0, y),
                (WIDTH, y)
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
        # TITLE
        # ----------------------------------------------------

        title = self.title_font.render(
            "IDENTIFY PLAYER",
            True,
            CYAN
        )


        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                160
            )
        )


        surface.blit(
            title,
            title_rect
        )


        # ----------------------------------------------------
        # SUBTITLE
        # ----------------------------------------------------

        subtitle = self.normal_font.render(
            "CYBOTICS // ENTER UNIQUE PLAYER NAME",
            True,
            PURPLE
        )


        subtitle_rect = subtitle.get_rect(
            center=(
                WIDTH // 2,
                215
            )
        )


        surface.blit(
            subtitle,
            subtitle_rect
        )


        # ----------------------------------------------------
        # INPUT BOX
        # ----------------------------------------------------

        input_rect = pygame.Rect(
            WIDTH // 2 - 260,
            295,
            520,
            75
        )


        pygame.draw.rect(
            surface,
            (10, 20, 32),
            input_rect,
            border_radius=7
        )


        pygame.draw.rect(
            surface,
            CYAN,
            input_rect,
            width=2,
            border_radius=7
        )


        # ----------------------------------------------------
        # CURSOR
        # ----------------------------------------------------

        cursor_visible = (
            pygame.time.get_ticks()
            // 500
        ) % 2 == 0


        display_value = (
            self.value
        )


        if cursor_visible:

            display_value += "_"


        if not self.value:

            if cursor_visible:

                display_value = "_"

            else:

                display_value = ""


        input_text = (
            self.input_font.render(
                display_value,
                True,
                WHITE
            )
        )


        input_text_rect = (
            input_text.get_rect(
                center=input_rect.center
            )
        )


        surface.blit(
            input_text,
            input_text_rect
        )


        # ----------------------------------------------------
        # LENGTH
        # ----------------------------------------------------

        length_text = self.small_font.render(
            (
                f"{len(self.value)}"
                f"/{self.MAX_LENGTH}"
            ),
            True,
            PURPLE
        )


        surface.blit(
            length_text,
            (
                input_rect.right - 55,
                input_rect.bottom + 10
            )
        )


        # ----------------------------------------------------
        # RULES
        # ----------------------------------------------------

        rules = self.small_font.render(
            (
                "3-12 CHARACTERS // "
                "A-Z 0-9 _ - // NAME MUST BE UNIQUE"
            ),
            True,
            PURPLE
        )


        rules_rect = rules.get_rect(
            center=(
                WIDTH // 2,
                415
            )
        )


        surface.blit(
            rules,
            rules_rect
        )


        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        if self.error_message:

            error = self.small_font.render(
                self.error_message,
                True,
                (255, 90, 100)
            )


            error_rect = error.get_rect(
                center=(
                    WIDTH // 2,
                    465
                )
            )


            surface.blit(
                error,
                error_rect
            )


        # ----------------------------------------------------
        # CONFIRM
        # ----------------------------------------------------

        confirm = self.normal_font.render(
            "[ENTER] INITIALIZE RUN",
            True,
            CYAN
        )


        confirm_rect = confirm.get_rect(
            center=(
                WIDTH // 2,
                535
            )
        )


        surface.blit(
            confirm,
            confirm_rect
        )


        # ----------------------------------------------------
        # BACK
        # ----------------------------------------------------

        back = self.small_font.render(
            "[ESC] RETURN TO MAIN MENU",
            True,
            PURPLE
        )


        back_rect = back.get_rect(
            center=(
                WIDTH // 2,
                585
            )
        )


        surface.blit(
            back,
            back_rect
        )