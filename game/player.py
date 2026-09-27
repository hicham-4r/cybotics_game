import pygame

from settings import (
    PLAYER_SIZE,
    GRAVITY_STRENGTH,
    MAX_SPEED,
    CYAN,
    CYAN_GLOW,
    PURPLE,
    WHITE,
)


class Player:
    def __init__(self, start_x, start_y):

        self.spawn_position = pygame.Vector2(
            start_x,
            start_y
        )

        self.position = pygame.Vector2(
            start_x,
            start_y
        )

        self.velocity = pygame.Vector2(
            0,
            0
        )

        self.gravity_direction = pygame.Vector2(
            0,
            1
        )

        self.gravity_name = "DOWN"


    # ========================================================
    # RECT
    # ========================================================

    @property
    def rect(self):

        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            PLAYER_SIZE,
            PLAYER_SIZE
        )


    # ========================================================
    # CHANGE SPAWN
    # ========================================================

    def set_spawn(self, x, y):

        self.spawn_position.update(
            x,
            y
        )

        self.reset()


    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.position.update(
            self.spawn_position.x,
            self.spawn_position.y
        )

        self.velocity.update(
            0,
            0
        )

        self.gravity_direction.update(
            0,
            1
        )

        self.gravity_name = "DOWN"


    # ========================================================
    # CHANGE GRAVITY
    # ========================================================

    def set_gravity(self, direction):

        if direction == "UP":

            self.gravity_direction.update(
                0,
                -1
            )

            self.gravity_name = "UP"


        elif direction == "LEFT":

            self.gravity_direction.update(
                -1,
                0
            )

            self.gravity_name = "LEFT"


        elif direction == "DOWN":

            self.gravity_direction.update(
                0,
                1
            )

            self.gravity_name = "DOWN"


        elif direction == "RIGHT":

            self.gravity_direction.update(
                1,
                0
            )

            self.gravity_name = "RIGHT"


    # ========================================================
    # PHYSICS UPDATE
    # ========================================================

    def update(self, dt, solids):

        # ----------------------------------------------------
        # APPLY GRAVITY
        # ----------------------------------------------------

        self.velocity += (
            self.gravity_direction
            * GRAVITY_STRENGTH
            * dt
        )


        # ----------------------------------------------------
        # LIMIT SPEED
        # ----------------------------------------------------

        self.velocity.x = max(
            -MAX_SPEED,
            min(
                MAX_SPEED,
                self.velocity.x
            )
        )

        self.velocity.y = max(
            -MAX_SPEED,
            min(
                MAX_SPEED,
                self.velocity.y
            )
        )


        # ====================================================
        # HORIZONTAL MOVEMENT
        # ====================================================

        self.position.x += (
            self.velocity.x * dt
        )

        player_rect = self.rect

        for solid in solids:

            if player_rect.colliderect(
                solid
            ):

                if self.velocity.x > 0:

                    self.position.x = (
                        solid.left
                        - PLAYER_SIZE
                    )

                elif self.velocity.x < 0:

                    self.position.x = (
                        solid.right
                    )

                self.velocity.x = 0

                player_rect = self.rect


        # ====================================================
        # VERTICAL MOVEMENT
        # ====================================================

        self.position.y += (
            self.velocity.y * dt
        )

        player_rect = self.rect

        for solid in solids:

            if player_rect.colliderect(
                solid
            ):

                if self.velocity.y > 0:

                    self.position.y = (
                        solid.top
                        - PLAYER_SIZE
                    )

                elif self.velocity.y < 0:

                    self.position.y = (
                        solid.bottom
                    )

                self.velocity.y = 0

                player_rect = self.rect


    # ========================================================
    # DRAW PLAYER
    # ========================================================

    def draw(self, surface):

        player_rect = self.rect

        glow_size = (
            PLAYER_SIZE + 40
        )

        glow_surface = pygame.Surface(
            (
                glow_size,
                glow_size
            ),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            glow_surface,
            (40, 180, 255, 45),
            pygame.Rect(
                5,
                5,
                glow_size - 10,
                glow_size - 10
            ),
            border_radius=10
        )

        surface.blit(
            glow_surface,
            (
                player_rect.centerx
                - glow_size // 2,

                player_rect.centery
                - glow_size // 2
            )
        )


        # ----------------------------------------------------
        # OUTER BODY
        # ----------------------------------------------------

        pygame.draw.rect(
            surface,
            CYAN_GLOW,
            player_rect,
            border_radius=4
        )


        # ----------------------------------------------------
        # INNER BODY
        # ----------------------------------------------------

        inner_rect = player_rect.inflate(
            -8,
            -8
        )

        pygame.draw.rect(
            surface,
            CYAN,
            inner_rect,
            border_radius=3
        )


        # ----------------------------------------------------
        # CORE
        # ----------------------------------------------------

        core_rect = player_rect.inflate(
            -20,
            -20
        )

        pygame.draw.rect(
            surface,
            WHITE,
            core_rect,
            border_radius=2
        )


    # ========================================================
    # GRAVITY INDICATOR
    # ========================================================

    def draw_gravity_indicator(
        self,
        surface
    ):

        center = pygame.Vector2(
            self.position.x
            + PLAYER_SIZE / 2,

            self.position.y
            + PLAYER_SIZE / 2
        )

        arrow_end = (
            center
            + self.gravity_direction * 58
        )

        pygame.draw.line(
            surface,
            PURPLE,
            center,
            arrow_end,
            width=4
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(arrow_end.x),
                int(arrow_end.y)
            ),
            5
        )