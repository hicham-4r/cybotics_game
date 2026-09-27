import pygame


# ============================================================
# COLORS
# ============================================================

HAZARD_DARK = (90, 18, 25)
HAZARD_RED = (255, 55, 70)
HAZARD_ORANGE = (255, 150, 55)
HAZARD_WHITE = (255, 225, 210)


class MovingHazard:
    def __init__(
        self,
        start,
        end,
        size,
        speed
    ):

        # ----------------------------------------------------
        # PATH
        # ----------------------------------------------------

        self.start = pygame.Vector2(
            float(start[0]),
            float(start[1])
        )

        self.end = pygame.Vector2(
            float(end[0]),
            float(end[1])
        )

        self.position = self.start.copy()


        # ----------------------------------------------------
        # SIZE
        # ----------------------------------------------------

        self.width = int(
            size[0]
        )

        self.height = int(
            size[1]
        )


        # ----------------------------------------------------
        # MOVEMENT
        # ----------------------------------------------------

        self.speed = float(
            speed
        )

        path_vector = (
            self.end
            - self.start
        )

        self.path_length = (
            path_vector.length()
        )

        if self.path_length <= 0:

            raise ValueError(
                "Moving hazard start and end "
                "positions must be different."
            )

        self.path_direction = (
            path_vector.normalize()
        )

        self.distance_along_path = 0.0

        # 1 = toward end
        # -1 = toward start
        self.travel_direction = 1


    # ========================================================
    # COLLISION RECT
    # ========================================================

    @property
    def rect(self):

        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )


    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.position = (
            self.start.copy()
        )

        self.distance_along_path = 0.0

        self.travel_direction = 1


    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        self.distance_along_path += (
            self.speed
            * self.travel_direction
            * dt
        )


        # ----------------------------------------------------
        # REACHED END
        # ----------------------------------------------------

        if (
            self.distance_along_path
            >= self.path_length
        ):

            self.distance_along_path = (
                self.path_length
            )

            self.travel_direction = -1


        # ----------------------------------------------------
        # REACHED START
        # ----------------------------------------------------

        elif (
            self.distance_along_path
            <= 0
        ):

            self.distance_along_path = 0

            self.travel_direction = 1


        # ----------------------------------------------------
        # CALCULATE POSITION
        # ----------------------------------------------------

        self.position = (
            self.start
            + self.path_direction
            * self.distance_along_path
        )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, surface):

        hazard_rect = self.rect


        # ----------------------------------------------------
        # GLOW
        # ----------------------------------------------------

        glow_rect = hazard_rect.inflate(
            16,
            16
        )

        glow_surface = pygame.Surface(
            (
                glow_rect.width,
                glow_rect.height
            ),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            glow_surface,
            (255, 40, 50, 35),
            glow_surface.get_rect(),
            border_radius=7
        )

        surface.blit(
            glow_surface,
            glow_rect.topleft
        )


        # ----------------------------------------------------
        # BODY
        # ----------------------------------------------------

        pygame.draw.rect(
            surface,
            HAZARD_DARK,
            hazard_rect,
            border_radius=4
        )

        inner_rect = hazard_rect.inflate(
            -4,
            -4
        )

        pygame.draw.rect(
            surface,
            HAZARD_RED,
            inner_rect,
            border_radius=3
        )


        # ----------------------------------------------------
        # BRIGHT CENTER LINE
        # ----------------------------------------------------

        if self.width >= self.height:

            pygame.draw.line(
                surface,
                HAZARD_ORANGE,
                (
                    hazard_rect.left + 6,
                    hazard_rect.centery
                ),
                (
                    hazard_rect.right - 6,
                    hazard_rect.centery
                ),
                width=3
            )

        else:

            pygame.draw.line(
                surface,
                HAZARD_ORANGE,
                (
                    hazard_rect.centerx,
                    hazard_rect.top + 6
                ),
                (
                    hazard_rect.centerx,
                    hazard_rect.bottom - 6
                ),
                width=3
            )


        # ----------------------------------------------------
        # CENTER CORE
        # ----------------------------------------------------

        pygame.draw.circle(
            surface,
            HAZARD_WHITE,
            hazard_rect.center,
            4
        )