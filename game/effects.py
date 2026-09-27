import math
import random

import pygame


class Particle:

    def __init__(
        self,
        position,
        velocity,
        color,
        radius,
        lifetime,
        alpha=255,
        drag=0.0,
        acceleration=(0, 0),
        glow=False,
        shrink=True
    ):

        self.position = pygame.Vector2(
            position
        )

        self.velocity = pygame.Vector2(
            velocity
        )

        self.acceleration = pygame.Vector2(
            acceleration
        )

        self.color = color

        self.radius = float(
            radius
        )

        self.max_lifetime = max(
            0.01,
            float(
                lifetime
            )
        )

        self.lifetime = (
            self.max_lifetime
        )

        self.alpha = int(
            alpha
        )

        self.drag = max(
            0.0,
            float(
                drag
            )
        )

        self.glow = bool(
            glow
        )

        self.shrink = bool(
            shrink
        )


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):

        self.lifetime -= (
            dt
        )


        if self.lifetime <= 0:

            return False


        self.velocity += (
            self.acceleration
            * dt
        )


        if self.drag > 0:

            drag_amount = max(
                0.0,
                1.0
                - self.drag
                * dt
            )

            self.velocity *= (
                drag_amount
            )


        self.position += (
            self.velocity
            * dt
        )


        return True


    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface
    ):

        life_ratio = max(
            0.0,
            min(
                1.0,
                self.lifetime
                / self.max_lifetime
            )
        )


        current_alpha = int(
            self.alpha
            * life_ratio
        )


        if self.shrink:

            current_radius = max(
                1,
                int(
                    self.radius
                    * (
                        0.25
                        + 0.75
                        * life_ratio
                    )
                )
            )

        else:

            current_radius = max(
                1,
                int(
                    self.radius
                )
            )


        center = (
            int(
                self.position.x
            ),
            int(
                self.position.y
            )
        )


        # ----------------------------------------------------
        # GLOW
        # ----------------------------------------------------

        if self.glow:

            glow_radius = max(
                current_radius + 2,
                current_radius * 3
            )


            pygame.draw.circle(
                surface,
                (
                    self.color[0],
                    self.color[1],
                    self.color[2],
                    max(
                        1,
                        current_alpha // 5
                    )
                ),
                center,
                glow_radius
            )


        # ----------------------------------------------------
        # PARTICLE CORE
        # ----------------------------------------------------

        pygame.draw.circle(
            surface,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                current_alpha
            ),
            center,
            current_radius
        )


class DirectionalPulse:

    def __init__(
        self,
        center,
        direction,
        color,
        lifetime=0.30
    ):

        self.center = pygame.Vector2(
            center
        )

        self.direction = pygame.Vector2(
            direction
        )


        if self.direction.length_squared() > 0:

            self.direction = (
                self.direction.normalize()
            )


        self.color = color

        self.max_lifetime = float(
            lifetime
        )

        self.lifetime = (
            self.max_lifetime
        )


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):

        self.lifetime -= (
            dt
        )

        return (
            self.lifetime > 0
        )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(
        self,
        surface
    ):

        life_ratio = max(
            0.0,
            min(
                1.0,
                self.lifetime
                / self.max_lifetime
            )
        )


        progress = (
            1.0
            - life_ratio
        )


        alpha = int(
            180
            * life_ratio
        )


        radius = int(
            18
            + 48
            * progress
        )


        center = (
            int(
                self.center.x
            ),
            int(
                self.center.y
            )
        )


        pygame.draw.circle(
            surface,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha
            ),
            center,
            radius,
            width=2
        )


        end_position = (
            self.center
            + self.direction
            * (
                35
                + 45
                * progress
            )
        )


        pygame.draw.line(
            surface,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha
            ),
            center,
            (
                int(
                    end_position.x
                ),
                int(
                    end_position.y
                )
            ),
            width=4
        )


        pygame.draw.circle(
            surface,
            (
                235,
                250,
                255,
                alpha
            ),
            (
                int(
                    end_position.x
                ),
                int(
                    end_position.y
                )
            ),
            4
        )


class EffectsManager:

    MAX_PARTICLES = 450


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        width,
        height
    ):

        self.width = int(
            width
        )

        self.height = int(
            height
        )


        self.particles = []

        self.pulses = []


        self.trail_timer = 0.0

        self.goal_idle_timer = 0.0


        self.goal_stream_center = None

        self.goal_stream_remaining = 0.0

        self.goal_stream_timer = 0.0


        # ----------------------------------------------------
        # SCREEN SHAKE
        # ----------------------------------------------------

        self.shake_remaining = 0.0

        self.shake_duration = 0.0

        self.shake_intensity = 0.0


        # ----------------------------------------------------
        # FLASH
        # ----------------------------------------------------

        self.flash_remaining = 0.0

        self.flash_duration = 0.0

        self.flash_color = (
            255,
            255,
            255
        )

        self.flash_alpha = 0


        # ----------------------------------------------------
        # HIGH SCORE
        # ----------------------------------------------------

        self.high_score_remaining = 0.0

        self.high_score_duration = 0.0


    # ========================================================
    # CLEAR
    # ========================================================

    def clear(
        self
    ):

        self.particles.clear()

        self.pulses.clear()


        self.trail_timer = 0.0

        self.goal_idle_timer = 0.0


        self.goal_stream_center = None

        self.goal_stream_remaining = 0.0

        self.goal_stream_timer = 0.0


        self.shake_remaining = 0.0

        self.shake_duration = 0.0

        self.shake_intensity = 0.0


        self.flash_remaining = 0.0

        self.high_score_remaining = 0.0


    # ========================================================
    # SAFE ADD PARTICLE
    # ========================================================

    def _add_particle(
        self,
        particle
    ):

        self.particles.append(
            particle
        )


        if len(
            self.particles
        ) > self.MAX_PARTICLES:

            excess = (
                len(
                    self.particles
                )
                - self.MAX_PARTICLES
            )


            del self.particles[
                :excess
            ]


    # ========================================================
    # SCREEN SHAKE
    # ========================================================

    def shake(
        self,
        intensity,
        duration
    ):

        self.shake_intensity = max(
            self.shake_intensity,
            float(
                intensity
            )
        )


        self.shake_duration = max(
            self.shake_duration,
            float(
                duration
            )
        )


        self.shake_remaining = max(
            self.shake_remaining,
            float(
                duration
            )
        )


    # ========================================================
    # FLASH
    # ========================================================

    def flash(
        self,
        color,
        alpha,
        duration
    ):

        self.flash_color = color

        self.flash_alpha = int(
            alpha
        )

        self.flash_duration = max(
            0.01,
            float(
                duration
            )
        )

        self.flash_remaining = (
            self.flash_duration
        )


    # ========================================================
    # PLAYER TRAIL
    # ========================================================

    def emit_player_trail(
        self,
        center,
        velocity,
        dt
    ):

        self.trail_timer += (
            dt
        )


        speed = pygame.Vector2(
            velocity
        ).length()


        if speed < 60:

            return


        interval = 0.035


        while (
            self.trail_timer
            >= interval
        ):

            self.trail_timer -= (
                interval
            )


            jitter = pygame.Vector2(
                random.uniform(
                    -5,
                    5
                ),
                random.uniform(
                    -5,
                    5
                )
            )


            backwards = (
                -pygame.Vector2(
                    velocity
                )
                * 0.035
            )


            particle_velocity = (
                backwards
                + pygame.Vector2(
                    random.uniform(
                        -18,
                        18
                    ),
                    random.uniform(
                        -18,
                        18
                    )
                )
            )


            self._add_particle(
                Particle(
                    position=(
                        pygame.Vector2(
                            center
                        )
                        + jitter
                    ),
                    velocity=(
                        particle_velocity
                    ),
                    color=(
                        70,
                        210,
                        255
                    ),
                    radius=random.uniform(
                        2.0,
                        4.5
                    ),
                    lifetime=random.uniform(
                        0.20,
                        0.38
                    ),
                    alpha=125,
                    drag=4.0,
                    glow=True
                )
            )


    # ========================================================
    # COLLISION SPARKS
    # ========================================================

    def collision_sparks(
        self,
        center,
        normal
    ):

        direction = pygame.Vector2(
            normal
        )


        if direction.length_squared() == 0:

            direction.update(
                0,
                -1
            )


        direction = (
            direction.normalize()
        )


        for _ in range(
            8
        ):

            spread = pygame.Vector2(
                random.uniform(
                    -0.7,
                    0.7
                ),
                random.uniform(
                    -0.7,
                    0.7
                )
            )


            velocity = (
                direction
                + spread
            )


            if velocity.length_squared() > 0:

                velocity = (
                    velocity.normalize()
                )


            velocity *= random.uniform(
                70,
                180
            )


            self._add_particle(
                Particle(
                    position=center,
                    velocity=velocity,
                    color=(
                        150,
                        240,
                        255
                    ),
                    radius=random.uniform(
                        1.5,
                        3.0
                    ),
                    lifetime=random.uniform(
                        0.15,
                        0.28
                    ),
                    alpha=190,
                    drag=3.0,
                    glow=True
                )
            )


    # ========================================================
    # GRAVITY CHANGE
    # ========================================================

    def gravity_shift(
        self,
        center,
        direction_name
    ):

        direction_map = {
            "UP": pygame.Vector2(
                0,
                -1
            ),

            "DOWN": pygame.Vector2(
                0,
                1
            ),

            "LEFT": pygame.Vector2(
                -1,
                0
            ),

            "RIGHT": pygame.Vector2(
                1,
                0
            ),
        }


        direction = direction_map.get(
            direction_name,
            pygame.Vector2(
                0,
                1
            )
        )


        self.pulses.append(
            DirectionalPulse(
                center=center,
                direction=direction,
                color=(
                    120,
                    80,
                    255
                )
            )
        )


        perpendicular = pygame.Vector2(
            -direction.y,
            direction.x
        )


        for _ in range(
            22
        ):

            speed = random.uniform(
                80,
                230
            )


            spread = random.uniform(
                -0.75,
                0.75
            )


            velocity_direction = (
                direction
                + perpendicular
                * spread
            )


            if velocity_direction.length_squared() > 0:

                velocity_direction = (
                    velocity_direction.normalize()
                )


            velocity = (
                velocity_direction
                * speed
            )


            color = random.choice(
                (
                    (
                        70,
                        210,
                        255
                    ),
                    (
                        120,
                        80,
                        255
                    ),
                    (
                        190,
                        120,
                        255
                    ),
                )
            )


            self._add_particle(
                Particle(
                    position=center,
                    velocity=velocity,
                    color=color,
                    radius=random.uniform(
                        2.0,
                        4.5
                    ),
                    lifetime=random.uniform(
                        0.20,
                        0.42
                    ),
                    alpha=210,
                    drag=2.5,
                    glow=True
                )
            )


        self.flash(
            color=(
                100,
                80,
                255
            ),
            alpha=24,
            duration=0.12
        )


    # ========================================================
    # GOAL IDLE PARTICLES
    # ========================================================

    def emit_goal_idle(
        self,
        center,
        dt
    ):

        self.goal_idle_timer += (
            dt
        )


        interval = 0.075


        while (
            self.goal_idle_timer
            >= interval
        ):

            self.goal_idle_timer -= (
                interval
            )


            angle = random.uniform(
                0,
                math.tau
            )


            radius = random.uniform(
                28,
                55
            )


            position = pygame.Vector2(
                center
            ) + pygame.Vector2(
                math.cos(
                    angle
                ),
                math.sin(
                    angle
                )
            ) * radius


            tangent = pygame.Vector2(
                -math.sin(
                    angle
                ),
                math.cos(
                    angle
                )
            )


            velocity = (
                tangent
                * random.uniform(
                    15,
                    35
                )
            )


            self._add_particle(
                Particle(
                    position=position,
                    velocity=velocity,
                    color=random.choice(
                        (
                            (
                                70,
                                210,
                                255
                            ),
                            (
                                150,
                                240,
                                255
                            ),
                            (
                                120,
                                80,
                                255
                            ),
                        )
                    ),
                    radius=random.uniform(
                        1.5,
                        3.5
                    ),
                    lifetime=random.uniform(
                        0.45,
                        0.85
                    ),
                    alpha=135,
                    drag=1.2,
                    glow=True
                )
            )


    # ========================================================
    # GOAL COMPLETION
    # ========================================================

    def goal_complete(
        self,
        center
    ):

        center_vector = pygame.Vector2(
            center
        )


        # ----------------------------------------------------
        # CENTRAL BURST
        # ----------------------------------------------------

        for _ in range(
            55
        ):

            angle = random.uniform(
                0,
                math.tau
            )


            direction = pygame.Vector2(
                math.cos(
                    angle
                ),
                math.sin(
                    angle
                )
            )


            velocity = (
                direction
                * random.uniform(
                    80,
                    300
                )
            )


            self._add_particle(
                Particle(
                    position=center_vector,
                    velocity=velocity,
                    color=random.choice(
                        (
                            (
                                70,
                                210,
                                255
                            ),
                            (
                                150,
                                240,
                                255
                            ),
                            (
                                235,
                                245,
                                255
                            ),
                            (
                                120,
                                80,
                                255
                            ),
                        )
                    ),
                    radius=random.uniform(
                        2,
                        6
                    ),
                    lifetime=random.uniform(
                        0.40,
                        0.85
                    ),
                    alpha=230,
                    drag=2.0,
                    glow=True
                )
            )


        # ----------------------------------------------------
        # PARTICLES FLOWING INTO CORE
        # ----------------------------------------------------

        self.goal_stream_center = (
            center_vector
        )

        self.goal_stream_remaining = (
            1.20
        )

        self.goal_stream_timer = 0.0


        self.shake(
            intensity=4,
            duration=0.18
        )


        self.flash(
            color=(
                70,
                210,
                255
            ),
            alpha=65,
            duration=0.25
        )


    # ========================================================
    # SPAWN GOAL STREAM PARTICLE
    # ========================================================

    def _spawn_goal_stream_particle(
        self
    ):

        if self.goal_stream_center is None:

            return


        angle = random.uniform(
            0,
            math.tau
        )


        radius = random.uniform(
            110,
            250
        )


        start = (
            self.goal_stream_center
            + pygame.Vector2(
                math.cos(
                    angle
                ),
                math.sin(
                    angle
                )
            )
            * radius
        )


        direction = (
            self.goal_stream_center
            - start
        )


        if direction.length_squared() > 0:

            direction = (
                direction.normalize()
            )


        velocity = (
            direction
            * random.uniform(
                150,
                280
            )
        )


        self._add_particle(
            Particle(
                position=start,
                velocity=velocity,
                color=random.choice(
                    (
                        (
                            70,
                            210,
                            255
                        ),
                        (
                            150,
                            240,
                            255
                        ),
                        (
                            120,
                            80,
                            255
                        ),
                    )
                ),
                radius=random.uniform(
                    2,
                    4
                ),
                lifetime=random.uniform(
                    0.55,
                    0.90
                ),
                alpha=200,
                drag=0.3,
                glow=True
            )
        )


    # ========================================================
    # DEATH
    # ========================================================

    def death(
        self,
        center
    ):

        center_vector = pygame.Vector2(
            center
        )


        for _ in range(
            65
        ):

            angle = random.uniform(
                0,
                math.tau
            )


            direction = pygame.Vector2(
                math.cos(
                    angle
                ),
                math.sin(
                    angle
                )
            )


            speed = random.uniform(
                100,
                370
            )


            color = random.choice(
                (
                    (
                        255,
                        70,
                        80
                    ),
                    (
                        255,
                        130,
                        60
                    ),
                    (
                        255,
                        200,
                        90
                    ),
                    (
                        120,
                        80,
                        255
                    ),
                )
            )


            self._add_particle(
                Particle(
                    position=(
                        center_vector
                        + pygame.Vector2(
                            random.uniform(
                                -8,
                                8
                            ),
                            random.uniform(
                                -8,
                                8
                            )
                        )
                    ),
                    velocity=(
                        direction
                        * speed
                    ),
                    color=color,
                    radius=random.uniform(
                        2,
                        6
                    ),
                    lifetime=random.uniform(
                        0.30,
                        0.75
                    ),
                    alpha=240,
                    drag=2.0,
                    acceleration=(
                        0,
                        100
                    ),
                    glow=True
                )
            )


        self.shake(
            intensity=13,
            duration=0.42
        )


        self.flash(
            color=(
                255,
                40,
                55
            ),
            alpha=115,
            duration=0.28
        )


    # ========================================================
    # LEVEL TRANSITION
    # ========================================================

    def level_transition(
        self,
        center
    ):

        center_vector = pygame.Vector2(
            center
        )


        for _ in range(
            32
        ):

            angle = random.uniform(
                0,
                math.tau
            )


            direction = pygame.Vector2(
                math.cos(
                    angle
                ),
                math.sin(
                    angle
                )
            )


            self._add_particle(
                Particle(
                    position=center_vector,
                    velocity=(
                        direction
                        * random.uniform(
                            90,
                            240
                        )
                    ),
                    color=random.choice(
                        (
                            (
                                70,
                                210,
                                255
                            ),
                            (
                                120,
                                80,
                                255
                            ),
                        )
                    ),
                    radius=random.uniform(
                        2,
                        5
                    ),
                    lifetime=random.uniform(
                        0.25,
                        0.55
                    ),
                    alpha=180,
                    drag=3.0,
                    glow=True
                )
            )


        self.flash(
            color=(
                70,
                210,
                255
            ),
            alpha=40,
            duration=0.20
        )


    # ========================================================
    # HIGH SCORE
    # ========================================================

    def high_score(
        self
    ):

        center = pygame.Vector2(
            self.width / 2,
            125
        )


        for _ in range(
            90
        ):

            angle = random.uniform(
                0,
                math.tau
            )


            direction = pygame.Vector2(
                math.cos(
                    angle
                ),
                math.sin(
                    angle
                )
            )


            self._add_particle(
                Particle(
                    position=center,
                    velocity=(
                        direction
                        * random.uniform(
                            90,
                            320
                        )
                    ),
                    color=random.choice(
                        (
                            (
                                70,
                                210,
                                255
                            ),
                            (
                                150,
                                240,
                                255
                            ),
                            (
                                120,
                                80,
                                255
                            ),
                            (
                                235,
                                245,
                                255
                            ),
                        )
                    ),
                    radius=random.uniform(
                        2,
                        6
                    ),
                    lifetime=random.uniform(
                        0.55,
                        1.20
                    ),
                    alpha=230,
                    drag=1.8,
                    glow=True
                )
            )


        self.high_score_duration = (
            1.5
        )

        self.high_score_remaining = (
            self.high_score_duration
        )


        self.flash(
            color=(
                70,
                210,
                255
            ),
            alpha=90,
            duration=0.30
        )


        self.shake(
            intensity=5,
            duration=0.22
        )


    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt
    ):

        dt = min(
            float(
                dt
            ),
            0.05
        )


        # ----------------------------------------------------
        # PARTICLES
        # ----------------------------------------------------

        alive_particles = []


        for particle in self.particles:

            if particle.update(
                dt
            ):

                alive_particles.append(
                    particle
                )


        self.particles = (
            alive_particles
        )


        # ----------------------------------------------------
        # PULSES
        # ----------------------------------------------------

        alive_pulses = []


        for pulse in self.pulses:

            if pulse.update(
                dt
            ):

                alive_pulses.append(
                    pulse
                )


        self.pulses = (
            alive_pulses
        )


        # ----------------------------------------------------
        # GOAL PARTICLE STREAM
        # ----------------------------------------------------

        if self.goal_stream_remaining > 0:

            self.goal_stream_remaining = max(
                0.0,
                self.goal_stream_remaining
                - dt
            )


            self.goal_stream_timer += (
                dt
            )


            interval = 0.025


            while (
                self.goal_stream_timer
                >= interval
            ):

                self.goal_stream_timer -= (
                    interval
                )


                self._spawn_goal_stream_particle()


        else:

            self.goal_stream_center = (
                None
            )


        # ----------------------------------------------------
        # SHAKE
        # ----------------------------------------------------

        self.shake_remaining = max(
            0.0,
            self.shake_remaining
            - dt
        )


        # ----------------------------------------------------
        # FLASH
        # ----------------------------------------------------

        self.flash_remaining = max(
            0.0,
            self.flash_remaining
            - dt
        )


        # ----------------------------------------------------
        # HIGH SCORE
        # ----------------------------------------------------

        self.high_score_remaining = max(
            0.0,
            self.high_score_remaining
            - dt
        )


    # ========================================================
    # CAMERA OFFSET
    # ========================================================

    def get_camera_offset(
        self
    ):

        if (
            self.shake_remaining <= 0
            or self.shake_duration <= 0
        ):

            return (
                0,
                0
            )


        ratio = (
            self.shake_remaining
            / self.shake_duration
        )


        intensity = int(
            max(
                0,
                self.shake_intensity
                * ratio
            )
        )


        if intensity <= 0:

            return (
                0,
                0
            )


        return (
            random.randint(
                -intensity,
                intensity
            ),
            random.randint(
                -intensity,
                intensity
            )
        )


    # ========================================================
    # DRAW WORLD EFFECTS
    # ========================================================

    def draw(
        self,
        surface
    ):

        fx_surface = pygame.Surface(
            (
                self.width,
                self.height
            ),
            pygame.SRCALPHA
        )


        for particle in self.particles:

            particle.draw(
                fx_surface
            )


        for pulse in self.pulses:

            pulse.draw(
                fx_surface
            )


        surface.blit(
            fx_surface,
            (
                0,
                0
            )
        )


    # ========================================================
    # DRAW SCREEN EFFECTS
    # ========================================================

    def draw_screen_fx(
        self,
        surface
    ):

        # ----------------------------------------------------
        # FLASH
        # ----------------------------------------------------

        if (
            self.flash_remaining > 0
            and self.flash_duration > 0
        ):

            ratio = (
                self.flash_remaining
                / self.flash_duration
            )


            alpha = int(
                self.flash_alpha
                * ratio
            )


            flash_surface = pygame.Surface(
                (
                    self.width,
                    self.height
                ),
                pygame.SRCALPHA
            )


            flash_surface.fill(
                (
                    self.flash_color[0],
                    self.flash_color[1],
                    self.flash_color[2],
                    alpha
                )
            )


            surface.blit(
                flash_surface,
                (
                    0,
                    0
                )
            )


        # ----------------------------------------------------
        # HIGH SCORE BORDER
        # ----------------------------------------------------

        if (
            self.high_score_remaining > 0
            and self.high_score_duration > 0
        ):

            time_value = (
                pygame.time.get_ticks()
                / 1000.0
            )


            pulse = (
                math.sin(
                    time_value
                    * 14
                )
                + 1
            ) / 2


            ratio = (
                self.high_score_remaining
                / self.high_score_duration
            )


            alpha = int(
                (
                    90
                    + 100
                    * pulse
                )
                * ratio
            )


            border_surface = pygame.Surface(
                (
                    self.width,
                    self.height
                ),
                pygame.SRCALPHA
            )


            pygame.draw.rect(
                border_surface,
                (
                    70,
                    210,
                    255,
                    alpha
                ),
                pygame.Rect(
                    8,
                    8,
                    self.width - 16,
                    self.height - 16
                ),
                width=5,
                border_radius=10
            )


            pygame.draw.rect(
                border_surface,
                (
                    120,
                    80,
                    255,
                    max(
                        0,
                        alpha // 2
                    )
                ),
                pygame.Rect(
                    16,
                    16,
                    self.width - 32,
                    self.height - 32
                ),
                width=2,
                border_radius=8
            )


            surface.blit(
                border_surface,
                (
                    0,
                    0
                )
            )