import json
from pathlib import Path

import pygame

from entities.moving_hazard import MovingHazard

from settings import (
    ARENA_LEFT,
    ARENA_RIGHT,
    ARENA_TOP,
    ARENA_BOTTOM,
    WALL_THICKNESS,
    WALL_COLOR,
    WALL_BORDER,
    PLATFORM_COLOR,
    PLATFORM_BORDER,
)


# ============================================================
# STATIC HAZARD COLORS
# ============================================================

HAZARD_DARK = (90, 20, 25)
HAZARD_RED = (255, 60, 70)
HAZARD_GLOW = (255, 110, 50)


class Level:
    def __init__(self, file_path):

        self.file_path = Path(
            file_path
        )

        self._load_data()
        self._create_boundaries()


    # ========================================================
    # LOAD JSON
    # ========================================================

    def _load_data(self):

        if not self.file_path.exists():

            raise FileNotFoundError(
                f"Level file not found: "
                f"{self.file_path}"
            )


        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )


        # ----------------------------------------------------
        # BASIC INFORMATION
        # ----------------------------------------------------

        self.number = int(
            data["level"]
        )

        self.name = str(
            data.get(
                "name",
                f"Level {self.number}"
            )
        )


        # ----------------------------------------------------
        # SCORING
        # ----------------------------------------------------

        self.target_time = float(
            data.get(
                "target_time",
                0
            )
        )

        self.completion_bonus = int(
            data.get(
                "completion_bonus",
                0
            )
        )

        self.time_multiplier = float(
            data.get(
                "time_multiplier",
                0
            )
        )


        # ----------------------------------------------------
        # PLAYER START
        # ----------------------------------------------------

        player_start = data[
            "player_start"
        ]

        if len(player_start) != 2:

            raise ValueError(
                "player_start must contain [x, y]"
            )

        self.player_start = pygame.Vector2(
            float(player_start[0]),
            float(player_start[1])
        )


        # ----------------------------------------------------
        # GOAL
        # ----------------------------------------------------

        goal = data[
            "goal"
        ]

        if len(goal) != 4:

            raise ValueError(
                "goal must contain "
                "[x, y, width, height]"
            )

        self.goal_rect = pygame.Rect(
            int(goal[0]),
            int(goal[1]),
            int(goal[2]),
            int(goal[3])
        )


        # ----------------------------------------------------
        # PLATFORMS
        # ----------------------------------------------------

        self.platforms = []

        for platform_data in data.get(
            "platforms",
            []
        ):

            if len(platform_data) != 4:

                raise ValueError(
                    "Every platform must contain "
                    "[x, y, width, height]"
                )

            self.platforms.append(
                pygame.Rect(
                    int(platform_data[0]),
                    int(platform_data[1]),
                    int(platform_data[2]),
                    int(platform_data[3])
                )
            )


        # ----------------------------------------------------
        # STATIC HAZARDS
        # ----------------------------------------------------

        self.hazards = []

        for hazard_data in data.get(
            "hazards",
            []
        ):

            if len(hazard_data) != 4:

                raise ValueError(
                    "Every hazard must contain "
                    "[x, y, width, height]"
                )

            self.hazards.append(
                pygame.Rect(
                    int(hazard_data[0]),
                    int(hazard_data[1]),
                    int(hazard_data[2]),
                    int(hazard_data[3])
                )
            )


        # ----------------------------------------------------
        # MOVING HAZARDS
        # ----------------------------------------------------

        self.moving_hazards = []

        for moving_data in data.get(
            "moving_hazards",
            []
        ):

            start = moving_data[
                "start"
            ]

            end = moving_data[
                "end"
            ]

            size = moving_data[
                "size"
            ]

            speed = moving_data[
                "speed"
            ]


            if len(start) != 2:

                raise ValueError(
                    "Moving hazard start "
                    "must contain [x, y]"
                )


            if len(end) != 2:

                raise ValueError(
                    "Moving hazard end "
                    "must contain [x, y]"
                )


            if len(size) != 2:

                raise ValueError(
                    "Moving hazard size "
                    "must contain [width, height]"
                )


            self.moving_hazards.append(
                MovingHazard(
                    start=start,
                    end=end,
                    size=size,
                    speed=speed
                )
            )


    # ========================================================
    # CREATE OUTER WALLS
    # ========================================================

    def _create_boundaries(self):

        self.boundary_walls = [

            pygame.Rect(
                ARENA_LEFT,
                ARENA_TOP,
                ARENA_RIGHT - ARENA_LEFT,
                WALL_THICKNESS
            ),

            pygame.Rect(
                ARENA_LEFT,
                ARENA_BOTTOM - WALL_THICKNESS,
                ARENA_RIGHT - ARENA_LEFT,
                WALL_THICKNESS
            ),

            pygame.Rect(
                ARENA_LEFT,
                ARENA_TOP,
                WALL_THICKNESS,
                ARENA_BOTTOM - ARENA_TOP
            ),

            pygame.Rect(
                ARENA_RIGHT - WALL_THICKNESS,
                ARENA_TOP,
                WALL_THICKNESS,
                ARENA_BOTTOM - ARENA_TOP
            )
        ]


        # Only walls/platforms are solid.
        self.solids = (
            self.boundary_walls
            + self.platforms
        )


    # ========================================================
    # RESET DYNAMIC OBJECTS
    # ========================================================

    def reset(self):

        for moving_hazard in (
            self.moving_hazards
        ):

            moving_hazard.reset()


    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        for moving_hazard in (
            self.moving_hazards
        ):

            moving_hazard.update(
                dt
            )


    # ========================================================
    # CHECK HAZARD COLLISION
    # ========================================================

    def player_hit_hazard(
        self,
        player_rect
    ):

        # ----------------------------------------------------
        # STATIC
        # ----------------------------------------------------

        for hazard in self.hazards:

            if player_rect.colliderect(
                hazard
            ):

                return True


        # ----------------------------------------------------
        # MOVING
        # ----------------------------------------------------

        for moving_hazard in (
            self.moving_hazards
        ):

            if player_rect.colliderect(
                moving_hazard.rect
            ):

                return True


        return False


    # ========================================================
    # DRAW LEVEL
    # ========================================================

    def draw(self, surface):

        # ----------------------------------------------------
        # BOUNDARIES
        # ----------------------------------------------------

        for wall in self.boundary_walls:

            pygame.draw.rect(
                surface,
                WALL_COLOR,
                wall
            )

            pygame.draw.rect(
                surface,
                WALL_BORDER,
                wall,
                width=2
            )


        # ----------------------------------------------------
        # PLATFORMS
        # ----------------------------------------------------

        for platform in self.platforms:

            pygame.draw.rect(
                surface,
                PLATFORM_COLOR,
                platform,
                border_radius=3
            )

            pygame.draw.rect(
                surface,
                PLATFORM_BORDER,
                platform,
                width=2,
                border_radius=3
            )


        # ----------------------------------------------------
        # STATIC HAZARDS
        # ----------------------------------------------------

        for hazard in self.hazards:

            glow_rect = hazard.inflate(
                10,
                10
            )

            pygame.draw.rect(
                surface,
                HAZARD_DARK,
                glow_rect,
                border_radius=4
            )

            pygame.draw.rect(
                surface,
                HAZARD_RED,
                hazard,
                border_radius=3
            )

            pygame.draw.rect(
                surface,
                HAZARD_GLOW,
                hazard,
                width=2,
                border_radius=3
            )


            line_spacing = 16

            x = (
                hazard.left
                - hazard.height
            )

            while x < hazard.right:

                pygame.draw.line(
                    surface,
                    (255, 170, 70),
                    (
                        x,
                        hazard.bottom
                    ),
                    (
                        x + hazard.height,
                        hazard.top
                    ),
                    width=2
                )

                x += line_spacing


        # ----------------------------------------------------
        # MOVING HAZARDS
        # ----------------------------------------------------

        for moving_hazard in (
            self.moving_hazards
        ):

            moving_hazard.draw(
                surface
            )