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


class LeaderboardScreen:
    def __init__(
        self,
        database
    ):

        self.database = database

        self.entries = []

        self.highlight_run_id = None
        self.highlight_rank = None

        self.confirm_clear = False
        self.status_message = ""

        self.title_font = pygame.font.SysFont(
            "consolas",
            42,
            bold=True
        )

        self.header_font = pygame.font.SysFont(
            "consolas",
            17,
            bold=True
        )

        self.row_font = pygame.font.SysFont(
            "consolas",
            18,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "consolas",
            15
        )

        self.confirm_font = pygame.font.SysFont(
            "consolas",
            25,
            bold=True
        )

        self.refresh()


    # ========================================================
    # FORMAT SCORE
    # ========================================================

    @staticmethod
    def format_score(
        score
    ):

        return f"{int(score):,}"


    # ========================================================
    # FORMAT TIME
    # ========================================================

    @staticmethod
    def format_time(
        seconds
    ):

        minutes = int(
            seconds // 60
        )

        remaining = (
            seconds % 60
        )

        return (
            f"{minutes:02d}:"
            f"{remaining:05.2f}"
        )


    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(
        self,
        highlight_run_id=None
    ):

        self.entries = (
            self.database.get_top_runs(
                limit=10
            )
        )

        self.highlight_run_id = (
            highlight_run_id
        )


        if highlight_run_id is None:

            self.highlight_rank = None

        else:

            self.highlight_rank = (
                self.database.get_rank(
                    highlight_run_id
                )
            )


        self.confirm_clear = False


    # ========================================================
    # HANDLE EVENTS
    # ========================================================

    def handle_event(
        self,
        event
    ):

        if event.type != pygame.KEYDOWN:

            return None


        # ====================================================
        # CLEAR CONFIRMATION IS OPEN
        # ====================================================

        if self.confirm_clear:

            # ------------------------------------------------
            # CONFIRM
            # ------------------------------------------------

            if event.key == pygame.K_y:

                self.database.clear_all_runs()

                self.entries = []

                self.highlight_run_id = None
                self.highlight_rank = None

                self.confirm_clear = False

                self.status_message = (
                    "LEADERBOARD CLEARED"
                )

                return "CLEARED"


            # ------------------------------------------------
            # CANCEL
            # ------------------------------------------------

            if event.key in (
                pygame.K_n,
                pygame.K_ESCAPE,
                pygame.K_BACKSPACE
            ):

                self.confirm_clear = False

                self.status_message = (
                    "CLEAR CANCELLED"
                )

                return "CANCEL_CLEAR"


            # Block other leaderboard controls
            # while confirmation is visible.
            return None


        # ====================================================
        # NORMAL LEADERBOARD
        # ====================================================

        if event.key in (
            pygame.K_ESCAPE,
            pygame.K_BACKSPACE
        ):

            return "BACK"


        # ----------------------------------------------------
        # REFRESH
        # ----------------------------------------------------

        if event.key == pygame.K_r:

            self.refresh(
                self.highlight_run_id
            )

            self.status_message = (
                "LEADERBOARD REFRESHED"
            )

            return "REFRESH"


        # ----------------------------------------------------
        # CLEAR
        # ----------------------------------------------------

        if event.key == pygame.K_c:

            self.confirm_clear = True

            self.status_message = ""

            return "CONFIRM_CLEAR"


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
    # CLEAR CONFIRMATION OVERLAY
    # ========================================================

    def _draw_clear_confirmation(
        self,
        surface
    ):

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )


        overlay.fill(
            (
                3,
                6,
                15,
                225
            )
        )


        surface.blit(
            overlay,
            (
                0,
                0
            )
        )


        panel = pygame.Rect(
            WIDTH // 2 - 330,
            HEIGHT // 2 - 130,
            660,
            260
        )


        pygame.draw.rect(
            surface,
            (
                12,
                20,
                34
            ),
            panel,
            border_radius=10
        )


        pygame.draw.rect(
            surface,
            (
                255,
                80,
                90
            ),
            panel,
            width=2,
            border_radius=10
        )


        title = self.confirm_font.render(
            "CLEAR ENTIRE LEADERBOARD?",
            True,
            (
                255,
                90,
                100
            )
        )


        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 70
            )
        )


        surface.blit(
            title,
            title_rect
        )


        warning = self.small_font.render(
            (
                "ALL SCORES AND REGISTERED "
                "PLAYER NAMES WILL BE REMOVED."
            ),
            True,
            WHITE
        )


        warning_rect = warning.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 20
            )
        )


        surface.blit(
            warning,
            warning_rect
        )


        controls = self.header_font.render(
            "[Y] YES, CLEAR     [N / ESC] CANCEL",
            True,
            CYAN
        )


        controls_rect = controls.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 55
            )
        )


        surface.blit(
            controls,
            controls_rect
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
            "CYBOTICS // LEADERBOARD",
            True,
            CYAN
        )


        title_rect = title.get_rect(
            center=(
                WIDTH // 2,
                70
            )
        )


        surface.blit(
            title,
            title_rect
        )


        subtitle = self.small_font.render(
            (
                "LOCAL CORE PERFORMANCE "
                "DATABASE // TOP 10"
            ),
            True,
            PURPLE
        )


        subtitle_rect = subtitle.get_rect(
            center=(
                WIDTH // 2,
                108
            )
        )


        surface.blit(
            subtitle,
            subtitle_rect
        )


        # ----------------------------------------------------
        # CURRENT RANK
        # ----------------------------------------------------

        if self.highlight_rank is not None:

            if self.highlight_rank <= 10:

                rank_message = (
                    f"CURRENT RUN // RANK "
                    f"#{self.highlight_rank}"
                    " // TOP 10 ENTRY"
                )

                rank_color = CYAN

            else:

                rank_message = (
                    f"CURRENT RUN // RANK "
                    f"#{self.highlight_rank}"
                )

                rank_color = WHITE


            rank_text = self.header_font.render(
                rank_message,
                True,
                rank_color
            )


            rank_rect = rank_text.get_rect(
                center=(
                    WIDTH // 2,
                    145
                )
            )


            surface.blit(
                rank_text,
                rank_rect
            )


        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        table_rect = pygame.Rect(
            100,
            180,
            1080,
            420
        )


        pygame.draw.rect(
            surface,
            (
                8,
                15,
                27
            ),
            table_rect,
            border_radius=8
        )


        pygame.draw.rect(
            surface,
            (
                35,
                90,
                120
            ),
            table_rect,
            width=2,
            border_radius=8
        )


        # ----------------------------------------------------
        # HEADERS
        # ----------------------------------------------------

        headers = [
            (
                "RANK",
                145
            ),
            (
                "PLAYER",
                260
            ),
            (
                "SCORE",
                500
            ),
            (
                "LEVELS",
                710
            ),
            (
                "TIME",
                855
            ),
            (
                "DEATHS",
                1040
            ),
        ]


        for header, x in headers:

            header_text = (
                self.header_font.render(
                    header,
                    True,
                    PURPLE
                )
            )


            surface.blit(
                header_text,
                (
                    x,
                    200
                )
            )


        pygame.draw.line(
            surface,
            (
                35,
                70,
                95
            ),
            (
                120,
                232
            ),
            (
                1160,
                232
            ),
            width=1
        )


        # ----------------------------------------------------
        # EMPTY LEADERBOARD
        # ----------------------------------------------------

        if not self.entries:

            empty = self.row_font.render(
                "NO RUNS RECORDED YET",
                True,
                WHITE
            )


            empty_rect = empty.get_rect(
                center=(
                    WIDTH // 2,
                    390
                )
            )


            surface.blit(
                empty,
                empty_rect
            )


        # ----------------------------------------------------
        # ENTRIES
        # ----------------------------------------------------

        start_y = 250
        row_height = 34


        for index, entry in enumerate(
            self.entries
        ):

            rank = (
                index + 1
            )


            y = (
                start_y
                + index * row_height
            )


            is_highlighted = (
                entry["id"]
                == self.highlight_run_id
            )


            row_rect = pygame.Rect(
                120,
                y - 5,
                1040,
                29
            )


            if is_highlighted:

                pygame.draw.rect(
                    surface,
                    (
                        12,
                        43,
                        58
                    ),
                    row_rect,
                    border_radius=4
                )


                pygame.draw.rect(
                    surface,
                    CYAN,
                    row_rect,
                    width=1,
                    border_radius=4
                )


                text_color = (
                    CYAN_LIGHT
                )

            else:

                text_color = (
                    WHITE
                )


            rank_text = self.row_font.render(
                f"{rank:02d}",
                True,
                text_color
            )


            name_text = self.row_font.render(
                str(
                    entry[
                        "player_name"
                    ]
                )[:12],
                True,
                text_color
            )


            score_text = self.row_font.render(
                self.format_score(
                    entry[
                        "score"
                    ]
                ),
                True,
                text_color
            )


            levels_text = self.row_font.render(
                str(
                    entry[
                        "levels_completed"
                    ]
                ),
                True,
                text_color
            )


            time_text = self.row_font.render(
                self.format_time(
                    entry[
                        "total_time"
                    ]
                ),
                True,
                text_color
            )


            deaths_text = self.row_font.render(
                str(
                    entry[
                        "deaths"
                    ]
                ),
                True,
                text_color
            )


            surface.blit(
                rank_text,
                (
                    150,
                    y
                )
            )


            surface.blit(
                name_text,
                (
                    260,
                    y
                )
            )


            surface.blit(
                score_text,
                (
                    500,
                    y
                )
            )


            surface.blit(
                levels_text,
                (
                    735,
                    y
                )
            )


            surface.blit(
                time_text,
                (
                    855,
                    y
                )
            )


            surface.blit(
                deaths_text,
                (
                    1065,
                    y
                )
            )


        # ----------------------------------------------------
        # DATABASE COUNTS
        # ----------------------------------------------------

        total_runs = (
            self.database.get_total_runs()
        )


        total_players = (
            self.database.get_total_players()
        )


        total_text = self.small_font.render(
            (
                "PLAYERS // "
                f"{total_players}"
                "     RUNS // "
                f"{total_runs}"
            ),
            True,
            PURPLE
        )


        surface.blit(
            total_text,
            (
                105,
                620
            )
        )


        # ----------------------------------------------------
        # STATUS MESSAGE
        # ----------------------------------------------------

        if self.status_message:

            status = self.small_font.render(
                self.status_message,
                True,
                CYAN
            )


            status_rect = status.get_rect(
                center=(
                    WIDTH // 2,
                    620
                )
            )


            surface.blit(
                status,
                status_rect
            )


        # ----------------------------------------------------
        # CONTROLS
        # ----------------------------------------------------

        controls = self.small_font.render(
            (
                "[R] REFRESH     "
                "[C] CLEAR LEADERBOARD     "
                "[ESC] MAIN MENU"
            ),
            True,
            WHITE
        )


        controls_rect = controls.get_rect(
            center=(
                WIDTH // 2,
                665
            )
        )


        surface.blit(
            controls,
            controls_rect
        )


        # ----------------------------------------------------
        # CONFIRMATION
        # ----------------------------------------------------

        if self.confirm_clear:

            self._draw_clear_confirmation(
                surface
            )