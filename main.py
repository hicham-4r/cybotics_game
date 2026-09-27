from pathlib import Path
import math

import pygame

from game.audio import AudioManager
from game.effects import EffectsManager
from game.level import Level
from game.player import Player
from game.leaderboard import LeaderboardDatabase
from game.preferences import Preferences

from game.scoring import (
    calculate_level_score,
    calculate_death_penalty,
    calculate_run_completion_bonuses,
)

from ui.menu import MainMenu
from ui.name_entry import NameEntryScreen
from ui.leaderboard import LeaderboardScreen
from ui.settings_screen import SettingsScreen
from ui.transitions import TransitionManager

from settings import (
    WIDTH,
    HEIGHT,
    FPS,
    BACKGROUND,
    GRID_COLOR,
    CYAN,
    CYAN_LIGHT,
    PURPLE,
    WHITE,
    OVERLAY_COLOR,
    DEATH_PENALTY_PERCENT,
    FULL_COMPLETION_BONUS,
    PERFECT_RUN_BONUS,
    DEFAULT_FULLSCREEN,
    DEFAULT_MUSIC_VOLUME,
    DEFAULT_SFX_VOLUME,
    DEFAULT_MUTED,
    VOLUME_STEP,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LEVELS_DIR = BASE_DIR / "levels"

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "images"
    / "cybotics_logo.jpg"
)

AUDIO_DIR = (
    BASE_DIR
    / "assets"
    / "audio"
)

DATA_DIR = (
    BASE_DIR
    / "data"
)

DATABASE_PATH = (
    DATA_DIR
    / "leaderboard.db"
)

PREFERENCES_PATH = (
    DATA_DIR
    / "preferences.json"
)


# ============================================================
# PREFERENCES
# ============================================================

preferences = Preferences(
    PREFERENCES_PATH,
    default_fullscreen=DEFAULT_FULLSCREEN,
    default_music_volume=DEFAULT_MUSIC_VOLUME,
    default_sfx_volume=DEFAULT_SFX_VOLUME,
    default_muted=DEFAULT_MUTED
)


# ============================================================
# PYGAME
# ============================================================

pygame.init()


# ============================================================
# DISPLAY
# ============================================================

fullscreen_enabled = (
    preferences.fullscreen
)


def create_display(
    fullscreen
):
    if fullscreen:
        return pygame.display.set_mode(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.FULLSCREEN
        )

    return pygame.display.set_mode(
        (
            WIDTH,
            HEIGHT
        )
    )


try:
    screen = create_display(
        fullscreen_enabled
    )

except pygame.error:
    fullscreen_enabled = False

    preferences.set_fullscreen(
        False
    )

    screen = create_display(
        False
    )


pygame.display.set_caption(
    "CYBOTICS — GRAVITY SHIFT"
)


clock = pygame.time.Clock()


# ============================================================
# WORLD SURFACE
# ============================================================

world_surface = pygame.Surface(
    (
        WIDTH,
        HEIGHT
    )
).convert()


# ============================================================
# AUDIO
# ============================================================

audio = AudioManager(
    AUDIO_DIR,
    music_volume=(
        preferences.music_volume
    ),
    sfx_volume=(
        preferences.sfx_volume
    ),
    muted=(
        preferences.muted
    )
)


audio.start_music()


# ============================================================
# EFFECTS
# ============================================================

effects = EffectsManager(
    WIDTH,
    HEIGHT
)


# ============================================================
# TRANSITIONS
# ============================================================

transitions = TransitionManager(
    WIDTH,
    HEIGHT
)


# ============================================================
# DATABASE
# ============================================================

leaderboard_database = (
    LeaderboardDatabase(
        DATABASE_PATH
    )
)


# ============================================================
# UI
# ============================================================

main_menu = MainMenu(
    LOGO_PATH,
    sound_manager=audio
)


name_entry = (
    NameEntryScreen()
)


leaderboard_screen = (
    LeaderboardScreen(
        leaderboard_database
    )
)


settings_screen = (
    SettingsScreen()
)


# ============================================================
# FONTS
# ============================================================

hud_font = pygame.font.SysFont(
    "consolas",
    22,
    bold=True
)


small_font = pygame.font.SysFont(
    "consolas",
    17
)


complete_font = pygame.font.SysFont(
    "consolas",
    52,
    bold=True
)


complete_sub_font = pygame.font.SysFont(
    "consolas",
    22,
    bold=True
)


failure_font = pygame.font.SysFont(
    "consolas",
    56,
    bold=True
)


pause_font = pygame.font.SysFont(
    "consolas",
    58,
    bold=True
)


# ============================================================
# LEVEL FILES
# ============================================================

LEVEL_FILES = sorted(
    LEVELS_DIR.glob(
        "level_*.json"
    )
)


if not LEVEL_FILES:
    raise FileNotFoundError(
        (
            "No level files found in: "
            f"{LEVELS_DIR}"
        )
    )


current_level_index = 0


# ============================================================
# LOAD LEVEL
# ============================================================

def load_level(
    index
):
    return Level(
        LEVEL_FILES[
            index
        ]
    )


level = load_level(
    current_level_index
)


# ============================================================
# PLAYER
# ============================================================

player = Player(
    level.player_start.x,
    level.player_start.y
)


# ============================================================
# APPLICATION STATE
# ============================================================

app_state = "MENU"

player_name = ""

level_complete = False
demo_complete = False
player_dead = False
paused = False


# ============================================================
# TIME
# ============================================================

level_elapsed_time = 0.0
completion_time = 0.0
run_elapsed_time = 0.0

completed_level_times = []


# ============================================================
# SCORE
# ============================================================

run_score = 0

current_completion_bonus = 0
current_time_bonus = 0
current_level_score = 0

completed_level_scores = []


# ============================================================
# COMPLETION BONUSES
# ============================================================

full_completion_bonus_awarded = 0
perfect_run_bonus_awarded = 0

completion_bonuses_applied = False


# ============================================================
# RUN STATISTICS
# ============================================================

death_count = 0
restart_count = 0

last_death_penalty = 0
total_death_penalties = 0


# ============================================================
# HIGH SCORE
# ============================================================

best_score_at_run_start = (
    leaderboard_database
    .get_best_score()
)

previous_best_score = (
    best_score_at_run_start
)

is_new_high_score = False


# ============================================================
# DATABASE STATE
# ============================================================

run_saved = False

current_run_id = None
current_run_rank = None


# ============================================================
# FORMAT TIME
# ============================================================

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


# ============================================================
# FORMAT SCORE
# ============================================================

def format_score(
    score
):
    return f"{int(score):,}"


# ============================================================
# CENTER TEXT
# ============================================================

def draw_center(
    surface,
    value,
    font,
    color,
    y
):
    text = font.render(
        value,
        True,
        color
    )

    surface.blit(
        text,
        text.get_rect(
            center=(
                WIDTH // 2,
                y
            )
        )
    )


# ============================================================
# FULLSCREEN
# ============================================================

def toggle_fullscreen():
    global screen
    global fullscreen_enabled

    requested_mode = (
        not fullscreen_enabled
    )

    try:
        new_screen = create_display(
            requested_mode
        )

    except pygame.error:
        return False

    screen = new_screen

    fullscreen_enabled = (
        requested_mode
    )

    preferences.set_fullscreen(
        fullscreen_enabled
    )

    pygame.display.set_caption(
        "CYBOTICS — GRAVITY SHIFT"
    )

    return True


# ============================================================
# AUDIO SETTINGS
# ============================================================

def change_music_volume(
    amount
):
    audio.change_music_volume(
        amount
    )

    preferences.set_music_volume(
        audio.music_volume
    )

    audio.play(
        "menu_move"
    )


def set_music_volume(
    value
):
    audio.set_music_volume(
        value
    )

    preferences.set_music_volume(
        audio.music_volume
    )


def change_sfx_volume(
    amount
):
    audio.change_sfx_volume(
        amount
    )

    preferences.set_sfx_volume(
        audio.sfx_volume
    )

    audio.play(
        "menu_move"
    )


def set_sfx_volume(
    value
):
    audio.set_sfx_volume(
        value
    )

    preferences.set_sfx_volume(
        audio.sfx_volume
    )

    audio.play(
        "menu_move"
    )


def toggle_audio_mute():
    if not audio.muted:
        audio.play(
            "menu_click"
        )

    audio.toggle_mute()

    preferences.set_muted(
        audio.muted
    )

    if not audio.muted:
        audio.play(
            "menu_click"
        )


# ============================================================
# GRAVITY
# ============================================================

def change_gravity(
    direction
):
    if (
        player.gravity_name
        == direction
    ):
        return

    player.set_gravity(
        direction
    )

    effects.gravity_shift(
        player.rect.center,
        direction
    )

    audio.play(
        "gravity"
    )


# ============================================================
# RESET LEVEL
# ============================================================

def reset_level(
    count_restart=True
):
    global level_complete
    global player_dead
    global paused

    global level_elapsed_time
    global completion_time

    global current_completion_bonus
    global current_time_bonus
    global current_level_score

    global restart_count
    global last_death_penalty

    if count_restart:
        restart_count += 1

    player.reset()
    level.reset()

    effects.clear()

    level_complete = False
    player_dead = False
    paused = False

    level_elapsed_time = 0.0
    completion_time = 0.0

    current_completion_bonus = 0
    current_time_bonus = 0
    current_level_score = 0

    last_death_penalty = 0


# ============================================================
# START CURRENT LEVEL
# ============================================================

def start_current_level():
    global level

    global level_complete
    global player_dead
    global paused

    global level_elapsed_time
    global completion_time

    global current_completion_bonus
    global current_time_bonus
    global current_level_score

    global last_death_penalty

    level = load_level(
        current_level_index
    )

    player.set_spawn(
        level.player_start.x,
        level.player_start.y
    )

    effects.clear()

    level_complete = False
    player_dead = False
    paused = False

    level_elapsed_time = 0.0
    completion_time = 0.0

    current_completion_bonus = 0
    current_time_bonus = 0
    current_level_score = 0

    last_death_penalty = 0


# ============================================================
# START NEW RUN
# ============================================================

def start_new_run():
    global app_state
    global current_level_index

    global level_complete
    global demo_complete
    global player_dead
    global paused

    global completed_level_times
    global completed_level_scores

    global run_score
    global run_elapsed_time

    global death_count
    global restart_count

    global last_death_penalty
    global total_death_penalties

    global full_completion_bonus_awarded
    global perfect_run_bonus_awarded
    global completion_bonuses_applied

    global best_score_at_run_start
    global previous_best_score
    global is_new_high_score

    global run_saved
    global current_run_id
    global current_run_rank

    current_level_index = 0

    level_complete = False
    demo_complete = False
    player_dead = False
    paused = False

    completed_level_times = []
    completed_level_scores = []

    run_score = 0
    run_elapsed_time = 0.0

    death_count = 0
    restart_count = 0

    last_death_penalty = 0
    total_death_penalties = 0

    full_completion_bonus_awarded = 0
    perfect_run_bonus_awarded = 0

    completion_bonuses_applied = False

    best_score_at_run_start = (
        leaderboard_database
        .get_best_score()
    )

    previous_best_score = (
        best_score_at_run_start
    )

    is_new_high_score = False

    run_saved = False

    current_run_id = None
    current_run_rank = None

    start_current_level()

    app_state = "PLAYING"

    effects.level_transition(
        player.rect.center
    )

    audio.play(
        "run_start"
    )


# ============================================================
# RETURN TO MENU
# ============================================================

def return_to_menu():
    global app_state

    global paused
    global player_dead
    global level_complete
    global demo_complete

    paused = False
    player_dead = False
    level_complete = False
    demo_complete = False

    effects.clear()

    app_state = "MENU"


# ============================================================
# NAME ENTRY
# ============================================================

def open_new_run_name_entry():
    global app_state

    name_entry.reset()

    app_state = "NAME_ENTRY"


# ============================================================
# COMPLETION BONUSES
# ============================================================

def apply_run_completion_bonuses():
    global run_score

    global full_completion_bonus_awarded
    global perfect_run_bonus_awarded
    global completion_bonuses_applied

    if completion_bonuses_applied:
        return

    result = (
        calculate_run_completion_bonuses(
            death_count=death_count,
            full_completion_bonus=(
                FULL_COMPLETION_BONUS
            ),
            perfect_run_bonus=(
                PERFECT_RUN_BONUS
            )
        )
    )

    full_completion_bonus_awarded = (
        result[
            "full_completion_bonus"
        ]
    )

    perfect_run_bonus_awarded = (
        result[
            "perfect_run_bonus"
        ]
    )

    run_score += (
        result[
            "total_bonus"
        ]
    )

    completion_bonuses_applied = True


# ============================================================
# SAVE RUN
# ============================================================

def save_current_run(
    completed=False
):
    global run_saved

    global current_run_id
    global current_run_rank

    global previous_best_score
    global is_new_high_score

    if run_saved:
        return current_run_id

    previous_best_score = (
        leaderboard_database
        .get_best_score()
    )

    current_run_id = (
        leaderboard_database
        .save_run(
            player_name=player_name,
            score=run_score,
            levels_completed=len(
                completed_level_scores
            ),
            total_time=run_elapsed_time,
            deaths=death_count,
            restarts=restart_count,
            death_penalties=(
                total_death_penalties
            ),
            completed=completed
        )
    )

    current_run_rank = (
        leaderboard_database
        .get_rank(
            current_run_id
        )
    )

    is_new_high_score = (
        run_score
        > previous_best_score
    )

    run_saved = True

    if is_new_high_score:
        effects.high_score()

        audio.play(
            "high_score"
        )

    return current_run_id


# ============================================================
# LEADERBOARD
# ============================================================

def open_leaderboard(
    highlight_current_run=False
):
    global app_state

    if (
        highlight_current_run
        and current_run_id is not None
    ):
        leaderboard_screen.refresh(
            current_run_id
        )

    else:
        leaderboard_screen.refresh()

    app_state = "LEADERBOARD"


# ============================================================
# END RUN
# ============================================================

def end_run_to_leaderboard():
    global paused
    global player_dead
    global level_complete
    global demo_complete

    save_current_run(
        completed=False
    )

    paused = False
    player_dead = False
    level_complete = False
    demo_complete = False

    open_leaderboard(
        highlight_current_run=True
    )


# ============================================================
# DEATH
# ============================================================

def trigger_death():
    global player_dead
    global death_count

    global run_score

    global last_death_penalty
    global total_death_penalties

    player_dead = True

    death_count += 1

    last_death_penalty = (
        calculate_death_penalty(
            run_score,
            DEATH_PENALTY_PERCENT
        )
    )

    run_score -= (
        last_death_penalty
    )

    total_death_penalties += (
        last_death_penalty
    )

    player.velocity.update(
        0,
        0
    )

    effects.death(
        player.rect.center
    )

    audio.play(
        "death"
    )


# ============================================================
# RETRY
# ============================================================

def retry_after_death():
    global player_dead

    global level_elapsed_time
    global completion_time

    global current_completion_bonus
    global current_time_bonus
    global current_level_score

    global last_death_penalty

    player.reset()
    level.reset()

    effects.clear()

    player_dead = False

    level_elapsed_time = 0.0
    completion_time = 0.0

    current_completion_bonus = 0
    current_time_bonus = 0
    current_level_score = 0

    last_death_penalty = 0

    audio.play(
        "menu_click"
    )


# ============================================================
# NEXT LEVEL / COMPLETE RUN
# ============================================================

def next_level():
    global current_level_index

    global demo_complete
    global level_complete

    if (
        current_level_index
        < len(
            LEVEL_FILES
        ) - 1
    ):
        current_level_index += 1

        start_current_level()

        effects.level_transition(
            player.rect.center
        )

        audio.play(
            "level_transition"
        )

        return

    level_complete = False
    demo_complete = True

    player.velocity.update(
        0,
        0
    )

    apply_run_completion_bonuses()

    save_current_run(
        completed=True
    )

    if not is_new_high_score:
        audio.play(
            "run_complete"
        )


# ============================================================
# TRANSITION ACTIONS
# ============================================================

def handle_transition_action(
    action
):
    global app_state

    if action is None:
        return

    # --------------------------------------------------------
    # MENU -> NAME ENTRY
    # --------------------------------------------------------

    if action == "OPEN_NAME_ENTRY":
        open_new_run_name_entry()

        transitions.start_fade_in()

    # --------------------------------------------------------
    # MENU -> LEADERBOARD
    # --------------------------------------------------------

    elif action == "OPEN_LEADERBOARD":
        open_leaderboard(
            highlight_current_run=False
        )

        transitions.start_fade_in()

    # --------------------------------------------------------
    # MENU -> SETTINGS
    # --------------------------------------------------------

    elif action == "OPEN_SETTINGS":
        app_state = "SETTINGS"

        transitions.start_fade_in()

    # --------------------------------------------------------
    # ANY SCREEN -> MENU
    # --------------------------------------------------------

    elif action == "RETURN_MENU":
        return_to_menu()

        transitions.start_fade_in()

    # --------------------------------------------------------
    # NAME ENTRY -> LEVEL 1
    # --------------------------------------------------------

    elif action == "START_RUN":
        start_new_run()

        transitions.start_fade_in(
            level_number=level.number,
            level_name=level.name
        )

    # --------------------------------------------------------
    # NEXT LEVEL OR RUN COMPLETE
    # --------------------------------------------------------

    elif action == "NEXT_LEVEL":
        next_level()

        if demo_complete:
            transitions.start_fade_in()

        else:
            transitions.start_fade_in(
                level_number=level.number,
                level_name=level.name
            )


# ============================================================
# GRID
# ============================================================

def draw_grid(
    surface
):
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


# ============================================================
# GOAL
# ============================================================

def draw_goal(
    surface
):
    time_seconds = (
        pygame.time.get_ticks()
        / 1000.0
    )

    pulse = (
        math.sin(
            time_seconds * 4
        )
        + 1
    ) / 2

    if level_complete:
        radius = int(
            43
            + pulse * 13
        )

    else:
        radius = int(
            30
            + pulse * 8
        )

    center = (
        level.goal_rect.center
    )

    glow_surface = pygame.Surface(
        (
            150,
            150
        ),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        glow_surface,
        (
            50,
            220,
            255,
            18
        ),
        (
            75,
            75
        ),
        radius + 30
    )

    pygame.draw.circle(
        glow_surface,
        (
            70,
            220,
            255,
            35
        ),
        (
            75,
            75
        ),
        radius + 18
    )

    pygame.draw.circle(
        glow_surface,
        (
            120,
            80,
            255,
            35
        ),
        (
            75,
            75
        ),
        radius + 8
    )

    surface.blit(
        glow_surface,
        (
            center[0] - 75,
            center[1] - 75
        )
    )

    pygame.draw.circle(
        surface,
        CYAN,
        center,
        radius,
        width=3
    )

    pygame.draw.circle(
        surface,
        PURPLE,
        center,
        max(
            8,
            radius - 9
        ),
        width=2
    )

    pygame.draw.circle(
        surface,
        CYAN_LIGHT,
        center,
        16
    )

    pygame.draw.circle(
        surface,
        WHITE,
        center,
        8
    )

    text = small_font.render(
        "CORE",
        True,
        CYAN
    )

    surface.blit(
        text,
        text.get_rect(
            center=(
                center[0],
                center[1] + 54
            )
        )
    )


# ============================================================
# FIRST LEVEL TUTORIAL
# ============================================================

def draw_first_level_tutorial(
    surface
):
    panel = pygame.Surface(
        (
            390,
            180
        ),
        pygame.SRCALPHA
    )

    panel.fill(
        (
            5,
            12,
            24,
            215
        )
    )

    pygame.draw.rect(
        panel,
        (
            70,
            210,
            255,
            180
        ),
        panel.get_rect(),
        width=2,
        border_radius=8
    )

    title = hud_font.render(
        "CHANGE GRAVITY",
        True,
        CYAN
    )

    panel.blit(
        title,
        title.get_rect(
            center=(
                195,
                28
            )
        )
    )

    lines = [
        "[W]  UP",
        "[A]  LEFT        [D]  RIGHT",
        "[S]  DOWN",
        "REACH THE GLOWING CORE",
    ]

    for index, text_value in enumerate(
        lines
    ):
        color = (
            CYAN_LIGHT
            if index == 3
            else WHITE
        )

        text = small_font.render(
            text_value,
            True,
            color
        )

        panel.blit(
            text,
            text.get_rect(
                center=(
                    195,
                    67
                    + index * 30
                )
            )
        )

    surface.blit(
        panel,
        (
            130,
            150
        )
    )


# ============================================================
# HUD
# ============================================================

def draw_hud(
    surface
):
    level_text = hud_font.render(
        (
            f"LEVEL {level.number:02d} "
            f"// {level.name.upper()}"
        ),
        True,
        WHITE
    )

    surface.blit(
        level_text,
        (
            30,
            15
        )
    )

    gravity_text = hud_font.render(
        (
            "GRAVITY // "
            f"{player.gravity_name}"
        ),
        True,
        CYAN
    )

    surface.blit(
        gravity_text,
        (
            30,
            45
        )
    )

    score_text = hud_font.render(
        (
            "SCORE // "
            f"{format_score(run_score)}"
        ),
        True,
        CYAN
    )

    surface.blit(
        score_text,
        (
            420,
            15
        )
    )

    best_text = small_font.render(
        (
            "BEST // "
            f"{format_score(best_score_at_run_start)}"
        ),
        True,
        PURPLE
    )

    surface.blit(
        best_text,
        (
            620,
            18
        )
    )

    timer_text = small_font.render(
        (
            "TIME // "
            f"{format_time(level_elapsed_time)}"
        ),
        True,
        WHITE
    )

    surface.blit(
        timer_text,
        (
            420,
            48
        )
    )

    target_text = small_font.render(
        (
            "TARGET // "
            f"{format_time(level.target_time)}"
        ),
        True,
        PURPLE
    )

    surface.blit(
        target_text,
        (
            620,
            48
        )
    )

    progress_text = small_font.render(
        (
            "CORE SEQUENCE // "
            f"{current_level_index + 1}"
            f"/{len(LEVEL_FILES)}"
        ),
        True,
        CYAN
    )

    surface.blit(
        progress_text,
        (
            850,
            18
        )
    )

    deaths_text = small_font.render(
        (
            "DEATHS // "
            f"{death_count}"
        ),
        True,
        PURPLE
    )

    surface.blit(
        deaths_text,
        (
            850,
            48
        )
    )

    player_text = small_font.render(
        (
            "PLAYER // "
            f"{player_name}"
        ),
        True,
        WHITE
    )

    player_rect = (
        player_text.get_rect()
    )

    player_rect.topright = (
        WIDTH - 30,
        48
    )

    surface.blit(
        player_text,
        player_rect
    )

    controls = small_font.render(
        (
            "WASD / ARROWS = GRAVITY    "
            "R = RESET    "
            "ESC = PAUSE    "
            "F11 = FULLSCREEN"
        ),
        True,
        PURPLE
    )

    surface.blit(
        controls,
        (
            30,
            680
        )
    )


# ============================================================
# LEVEL COMPLETE
# ============================================================

def draw_complete_screen(
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
        OVERLAY_COLOR
    )

    surface.blit(
        overlay,
        (
            0,
            0
        )
    )

    draw_center(
        surface,
        "LEVEL COMPLETE",
        complete_font,
        CYAN,
        HEIGHT // 2 - 155
    )

    draw_center(
        surface,
        (
            "TIME // "
            f"{format_time(completion_time)}"
        ),
        complete_sub_font,
        WHITE,
        HEIGHT // 2 - 80
    )

    draw_center(
        surface,
        (
            "LEVEL BONUS // +"
            f"{format_score(current_completion_bonus)}"
        ),
        complete_sub_font,
        WHITE,
        HEIGHT // 2 - 30
    )

    draw_center(
        surface,
        (
            "TIME BONUS // +"
            f"{format_score(current_time_bonus)}"
        ),
        complete_sub_font,
        PURPLE,
        HEIGHT // 2 + 15
    )

    draw_center(
        surface,
        (
            "LEVEL SCORE // +"
            f"{format_score(current_level_score)}"
        ),
        complete_sub_font,
        CYAN,
        HEIGHT // 2 + 65
    )

    draw_center(
        surface,
        format_score(
            run_score
        ),
        complete_font,
        WHITE,
        HEIGHT // 2 + 125
    )

    if (
        current_level_index
        < len(
            LEVEL_FILES
        ) - 1
    ):
        action_text = (
            "[ENTER] NEXT LEVEL"
        )

    else:
        action_text = (
            "[ENTER] COMPLETE RUN"
        )

    draw_center(
        surface,
        action_text,
        small_font,
        CYAN,
        HEIGHT // 2 + 185
    )


# ============================================================
# DEATH SCREEN
# ============================================================

def draw_death_screen(
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
            20,
            3,
            8,
            205
        )
    )

    surface.blit(
        overlay,
        (
            0,
            0
        )
    )

    draw_center(
        surface,
        "SYSTEM FAILURE",
        failure_font,
        (
            255,
            70,
            80
        ),
        HEIGHT // 2 - 190
    )

    draw_center(
        surface,
        (
            "PLAYER // "
            f"{player_name}"
        ),
        small_font,
        WHITE,
        HEIGHT // 2 - 145
    )

    draw_center(
        surface,
        (
            "LEVEL // "
            f"{level.number:02d}"
        ),
        complete_sub_font,
        WHITE,
        HEIGHT // 2 - 105
    )

    draw_center(
        surface,
        (
            "DEATH PENALTY // -"
            f"{format_score(last_death_penalty)}"
        ),
        complete_sub_font,
        (
            255,
            90,
            100
        ),
        HEIGHT // 2 - 60
    )

    draw_center(
        surface,
        (
            "SCORE // "
            f"{format_score(run_score)}"
        ),
        complete_sub_font,
        CYAN,
        HEIGHT // 2 - 15
    )

    draw_center(
        surface,
        (
            "BEST // "
            f"{format_score(best_score_at_run_start)}"
        ),
        small_font,
        PURPLE,
        HEIGHT // 2 + 25
    )

    if (
        run_score
        > best_score_at_run_start
        and run_score > 0
    ):
        draw_center(
            surface,
            "NEW HIGH SCORE",
            complete_sub_font,
            CYAN_LIGHT,
            HEIGHT // 2 + 65
        )

    draw_center(
        surface,
        "[ENTER] RETRY LEVEL",
        complete_sub_font,
        (
            255,
            110,
            120
        ),
        HEIGHT // 2 + 125
    )

    draw_center(
        surface,
        (
            "[Q / ESC] "
            "END RUN + SAVE SCORE"
        ),
        small_font,
        PURPLE,
        HEIGHT // 2 + 175
    )


# ============================================================
# PAUSE
# ============================================================

def draw_pause_screen(
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

    draw_center(
        surface,
        "SYSTEM PAUSED",
        pause_font,
        CYAN,
        HEIGHT // 2 - 175
    )

    draw_center(
        surface,
        (
            "PLAYER // "
            f"{player_name}"
        ),
        small_font,
        WHITE,
        HEIGHT // 2 - 130
    )

    draw_center(
        surface,
        (
            f"LEVEL {level.number:02d} "
            f"// {level.name.upper()}"
        ),
        complete_sub_font,
        PURPLE,
        HEIGHT // 2 - 90
    )

    draw_center(
        surface,
        (
            f"RUN TIME "
            f"{format_time(run_elapsed_time)}"
            f"   //   DEATHS {death_count}"
            f"   //   RESTARTS {restart_count}"
        ),
        small_font,
        WHITE,
        HEIGHT // 2 - 45
    )

    draw_center(
        surface,
        "[ESC / ENTER] RESUME",
        complete_sub_font,
        WHITE,
        HEIGHT // 2 + 15
    )

    draw_center(
        surface,
        "[R] RESTART LEVEL",
        complete_sub_font,
        CYAN,
        HEIGHT // 2 + 60
    )

    draw_center(
        surface,
        "[M] MUTE / UNMUTE",
        complete_sub_font,
        WHITE,
        HEIGHT // 2 + 105
    )

    draw_center(
        surface,
        "[F11] TOGGLE FULLSCREEN",
        complete_sub_font,
        WHITE,
        HEIGHT // 2 + 150
    )

    draw_center(
        surface,
        "[Q] END RUN + LEADERBOARD",
        complete_sub_font,
        PURPLE,
        HEIGHT // 2 + 195
    )


# ============================================================
# RUN COMPLETE
# ============================================================

def draw_demo_complete(
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
        OVERLAY_COLOR
    )

    surface.blit(
        overlay,
        (
            0,
            0
        )
    )

    draw_center(
        surface,
        "RUN COMPLETE",
        complete_font,
        CYAN,
        70
    )

    if is_new_high_score:
        draw_center(
            surface,
            "NEW HIGH SCORE",
            complete_sub_font,
            CYAN_LIGHT,
            125
        )

    draw_center(
        surface,
        (
            "PLAYER // "
            f"{player_name}"
        ),
        complete_sub_font,
        CYAN,
        165
    )

    draw_center(
        surface,
        (
            "LEVELS // "
            f"{len(completed_level_scores)}"
            f"/{len(LEVEL_FILES)}"
            f"     DEATHS // {death_count}"
            f"     RESTARTS // {restart_count}"
        ),
        small_font,
        PURPLE,
        205
    )

    draw_center(
        surface,
        (
            "RUN TIME // "
            f"{format_time(run_elapsed_time)}"
        ),
        complete_sub_font,
        WHITE,
        245
    )

    draw_center(
        surface,
        (
            "CORE COMPLETION BONUS // +"
            f"{format_score(full_completion_bonus_awarded)}"
        ),
        complete_sub_font,
        CYAN,
        295
    )

    if perfect_run_bonus_awarded > 0:
        perfect_message = (
            "PERFECT RUN BONUS // +"
            f"{format_score(perfect_run_bonus_awarded)}"
        )

        perfect_color = CYAN_LIGHT

    else:
        perfect_message = (
            "PERFECT RUN BONUS // NOT ACHIEVED"
        )

        perfect_color = PURPLE

    draw_center(
        surface,
        perfect_message,
        complete_sub_font,
        perfect_color,
        335
    )

    draw_center(
        surface,
        (
            "TOTAL DEATH PENALTIES // -"
            f"{format_score(total_death_penalties)}"
        ),
        small_font,
        (
            255,
            100,
            110
        ),
        375
    )

    draw_center(
        surface,
        "FINAL SCORE",
        complete_sub_font,
        WHITE,
        430
    )

    draw_center(
        surface,
        format_score(
            run_score
        ),
        complete_font,
        CYAN,
        485
    )

    draw_center(
        surface,
        (
            "PREVIOUS BEST // "
            f"{format_score(previous_best_score)}"
        ),
        small_font,
        PURPLE,
        535
    )

    if current_run_rank is not None:
        if current_run_rank <= 10:
            rank_message = (
                f"RANK // #{current_run_rank}"
                "   //   TOP 10"
            )

            rank_color = CYAN

        else:
            rank_message = (
                f"RANK // "
                f"#{current_run_rank}"
            )

            rank_color = WHITE

        draw_center(
            surface,
            rank_message,
            complete_sub_font,
            rank_color,
            575
        )

    draw_center(
        surface,
        (
            "[ENTER] LEADERBOARD"
            "     [P] NEW RUN"
            "     [ESC] MAIN MENU"
        ),
        small_font,
        WHITE,
        635
    )


# ============================================================
# MAIN LOOP
# ============================================================

running = True


while running:
    frame_time = (
        clock.tick(
            FPS
        )
        / 1000.0
    )

    physics_dt = min(
        frame_time,
        0.033
    )

    # ========================================================
    # MENU ANIMATION
    # ========================================================

    if app_state == "MENU":
        main_menu.update(
            frame_time
        )

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        # ----------------------------------------------------
        # WINDOW CLOSE
        # ----------------------------------------------------

        if event.type == pygame.QUIT:
            running = False
            continue

        # ----------------------------------------------------
        # GLOBAL FULLSCREEN
        # ----------------------------------------------------

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_F11
        ):
            if toggle_fullscreen():
                audio.play(
                    "menu_click"
                )

            continue

        # ----------------------------------------------------
        # BLOCK INPUT DURING FADE
        # ----------------------------------------------------

        if transitions.blocks_input:
            continue

        # ====================================================
        # MENU
        # ====================================================

        if app_state == "MENU":
            action = main_menu.handle_event(
                event
            )

            if action == "START":
                transitions.start_fade_out(
                    "OPEN_NAME_ENTRY"
                )

            elif action == "LEADERBOARD":
                transitions.start_fade_out(
                    "OPEN_LEADERBOARD"
                )

            elif action == "SETTINGS":
                transitions.start_fade_out(
                    "OPEN_SETTINGS"
                )

            elif action == "EXIT":
                running = False

            continue

        # ====================================================
        # NAME ENTRY
        # ====================================================

        if app_state == "NAME_ENTRY":
            action = name_entry.handle_event(
                event
            )

            if action == "SUBMIT":
                candidate_name = (
                    name_entry.value
                )

                if (
                    leaderboard_database
                    .player_name_exists(
                        candidate_name
                    )
                ):
                    name_entry.set_error(
                        (
                            "NAME ALREADY REGISTERED"
                            " // CHOOSE ANOTHER"
                        )
                    )

                    audio.play(
                        "menu_move"
                    )

                else:
                    player_name = (
                        candidate_name
                    )

                    audio.play(
                        "menu_click"
                    )

                    transitions.start_fade_out(
                        "START_RUN"
                    )

            elif action == "BACK":
                audio.play(
                    "menu_click"
                )

                transitions.start_fade_out(
                    "RETURN_MENU"
                )

            continue

        # ====================================================
        # LEADERBOARD
        # ====================================================

        if app_state == "LEADERBOARD":
            action = (
                leaderboard_screen
                .handle_event(
                    event
                )
            )

            if action == "BACK":
                audio.play(
                    "menu_click"
                )

                transitions.start_fade_out(
                    "RETURN_MENU"
                )

            elif action in (
                "REFRESH",
                "CONFIRM_CLEAR",
                "CANCEL_CLEAR"
            ):
                audio.play(
                    "menu_move"
                )

            elif action == "CLEARED":
                audio.play(
                    "menu_click"
                )

            continue

        # ====================================================
        # SETTINGS
        # ====================================================

        if app_state == "SETTINGS":
            action = (
                settings_screen
                .handle_event(
                    event
                )
            )

            if action == "BACK":
                audio.play(
                    "menu_click"
                )

                transitions.start_fade_out(
                    "RETURN_MENU"
                )

            elif action == "MOVE":
                audio.play(
                    "menu_move"
                )

            elif action == "TOGGLE_FULLSCREEN":
                if toggle_fullscreen():
                    audio.play(
                        "menu_click"
                    )

            elif action == "TOGGLE_MUTE":
                toggle_audio_mute()

            elif action == "MUSIC_DOWN":
                change_music_volume(
                    -VOLUME_STEP
                )

            elif action == "MUSIC_UP":
                change_music_volume(
                    VOLUME_STEP
                )

            elif action == "SFX_DOWN":
                change_sfx_volume(
                    -VOLUME_STEP
                )

            elif action == "SFX_UP":
                change_sfx_volume(
                    VOLUME_STEP
                )

            elif (
                isinstance(
                    action,
                    tuple
                )
                and len(
                    action
                ) == 2
            ):
                setting_name = (
                    action[0]
                )

                setting_value = (
                    action[1]
                )

                if setting_name == "SET_MUSIC":
                    set_music_volume(
                        setting_value
                    )

                elif setting_name == "SET_SFX":
                    set_sfx_volume(
                        setting_value
                    )

            continue

        # ====================================================
        # PLAYING
        # ====================================================

        if app_state == "PLAYING":

            if event.type != pygame.KEYDOWN:
                continue

            # ------------------------------------------------
            # PAUSED
            # ------------------------------------------------

            if paused:
                if event.key in (
                    pygame.K_ESCAPE,
                    pygame.K_RETURN
                ):
                    paused = False

                    audio.play(
                        "menu_click"
                    )

                elif event.key == pygame.K_r:
                    reset_level(
                        count_restart=True
                    )

                    audio.play(
                        "menu_click"
                    )

                elif event.key == pygame.K_m:
                    toggle_audio_mute()

                elif event.key == pygame.K_q:
                    audio.play(
                        "menu_click"
                    )

                    end_run_to_leaderboard()

                continue

            # ------------------------------------------------
            # RUN COMPLETE
            # ------------------------------------------------

            if demo_complete:
                if event.key == pygame.K_RETURN:
                    audio.play(
                        "menu_click"
                    )

                    open_leaderboard(
                        highlight_current_run=True
                    )

                elif event.key == pygame.K_p:
                    audio.play(
                        "menu_click"
                    )

                    open_new_run_name_entry()

                elif event.key == pygame.K_ESCAPE:
                    audio.play(
                        "menu_click"
                    )

                    transitions.start_fade_out(
                        "RETURN_MENU"
                    )

                continue

            # ------------------------------------------------
            # LEVEL COMPLETE
            # ------------------------------------------------

            if level_complete:
                if event.key == pygame.K_RETURN:
                    transitions.start_fade_out(
                        "NEXT_LEVEL"
                    )

                continue

            # ------------------------------------------------
            # DEAD
            # ------------------------------------------------

            if player_dead:
                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_r
                ):
                    retry_after_death()

                elif event.key in (
                    pygame.K_q,
                    pygame.K_ESCAPE
                ):
                    audio.play(
                        "menu_click"
                    )

                    end_run_to_leaderboard()

                continue

            # ------------------------------------------------
            # NORMAL GAMEPLAY
            # ------------------------------------------------

            if event.key == pygame.K_ESCAPE:
                paused = True

                audio.play(
                    "menu_click"
                )

            elif event.key == pygame.K_r:
                reset_level(
                    count_restart=True
                )

                audio.play(
                    "menu_click"
                )

            elif event.key in (
                pygame.K_w,
                pygame.K_UP
            ):
                change_gravity(
                    "UP"
                )

            elif event.key in (
                pygame.K_a,
                pygame.K_LEFT
            ):
                change_gravity(
                    "LEFT"
                )

            elif event.key in (
                pygame.K_s,
                pygame.K_DOWN
            ):
                change_gravity(
                    "DOWN"
                )

            elif event.key in (
                pygame.K_d,
                pygame.K_RIGHT
            ):
                change_gravity(
                    "RIGHT"
                )

    # ========================================================
    # TRANSITION UPDATE
    # ========================================================

    transition_action = (
        transitions.update(
            frame_time
        )
    )

    if transition_action is not None:
        handle_transition_action(
            transition_action
        )

    # ========================================================
    # GAMEPLAY UPDATE
    # ========================================================

    if (
        app_state == "PLAYING"
        and not level_complete
        and not demo_complete
        and not player_dead
        and not paused
        and not transitions.blocks_gameplay
    ):
        level_elapsed_time += (
            frame_time
        )

        run_elapsed_time += (
            frame_time
        )

        # ----------------------------------------------------
        # GOAL PARTICLES
        # ----------------------------------------------------

        effects.emit_goal_idle(
            level.goal_rect.center,
            frame_time
        )

        # ----------------------------------------------------
        # SAVE VELOCITY
        # ----------------------------------------------------

        previous_velocity = (
            player.velocity.copy()
        )

        # ----------------------------------------------------
        # PLAYER UPDATE
        # ----------------------------------------------------

        player.update(
            physics_dt,
            level.solids
        )

        # ----------------------------------------------------
        # PLAYER TRAIL
        # ----------------------------------------------------

        effects.emit_player_trail(
            player.rect.center,
            player.velocity,
            frame_time
        )

        # ----------------------------------------------------
        # COLLISION SPARKS
        # ----------------------------------------------------

        if (
            abs(
                previous_velocity.x
            ) > 180
            and abs(
                player.velocity.x
            ) < 1
        ):
            normal = (
                (
                    -1,
                    0
                )
                if previous_velocity.x > 0
                else (
                    1,
                    0
                )
            )

            effects.collision_sparks(
                player.rect.center,
                normal
            )

        if (
            abs(
                previous_velocity.y
            ) > 180
            and abs(
                player.velocity.y
            ) < 1
        ):
            normal = (
                (
                    0,
                    -1
                )
                if previous_velocity.y > 0
                else (
                    0,
                    1
                )
            )

            effects.collision_sparks(
                player.rect.center,
                normal
            )

        # ----------------------------------------------------
        # LEVEL UPDATE
        # ----------------------------------------------------

        level.update(
            physics_dt
        )

        # ----------------------------------------------------
        # HAZARD
        # ----------------------------------------------------

        if level.player_hit_hazard(
            player.rect
        ):
            trigger_death()

        # ----------------------------------------------------
        # CORE
        # ----------------------------------------------------

        elif player.rect.colliderect(
            level.goal_rect
        ):
            level_complete = True

            completion_time = (
                level_elapsed_time
            )

            score_result = (
                calculate_level_score(
                    completion_time,
                    level.target_time,
                    level.completion_bonus,
                    level.time_multiplier
                )
            )

            current_completion_bonus = (
                score_result[
                    "completion_bonus"
                ]
            )

            current_time_bonus = (
                score_result[
                    "time_bonus"
                ]
            )

            current_level_score = (
                score_result[
                    "level_score"
                ]
            )

            run_score += (
                current_level_score
            )

            completed_level_times.append(
                completion_time
            )

            completed_level_scores.append(
                current_level_score
            )

            player.velocity.update(
                0,
                0
            )

            effects.goal_complete(
                level.goal_rect.center
            )

            audio.play(
                "goal"
            )

    # ========================================================
    # EFFECTS UPDATE
    # ========================================================

    if (
        app_state == "PLAYING"
        and not paused
    ):
        effects.update(
            frame_time
        )

    # ========================================================
    # DRAW MENU
    # ========================================================

    if app_state == "MENU":
        main_menu.draw(
            screen
        )

        transitions.draw(
            screen
        )

        pygame.display.flip()

        continue

    # ========================================================
    # DRAW NAME ENTRY
    # ========================================================

    if app_state == "NAME_ENTRY":
        name_entry.draw(
            screen
        )

        transitions.draw(
            screen
        )

        pygame.display.flip()

        continue

    # ========================================================
    # DRAW LEADERBOARD
    # ========================================================

    if app_state == "LEADERBOARD":
        leaderboard_screen.draw(
            screen
        )

        transitions.draw(
            screen
        )

        pygame.display.flip()

        continue

    # ========================================================
    # DRAW SETTINGS
    # ========================================================

    if app_state == "SETTINGS":
        settings_screen.draw(
            screen,

            fullscreen_enabled=(
                fullscreen_enabled
            ),

            audio_available=(
                audio.available
            ),

            music_percent=(
                audio.get_music_volume_percent()
            ),

            sfx_percent=(
                audio.get_sfx_volume_percent()
            ),

            muted=(
                audio.muted
            )
        )

        transitions.draw(
            screen
        )

        pygame.display.flip()

        continue

    # ========================================================
    # DRAW GAME
    # ========================================================

    if app_state == "PLAYING":

        # ----------------------------------------------------
        # WORLD
        # ----------------------------------------------------

        world_surface.fill(
            BACKGROUND
        )

        draw_grid(
            world_surface
        )

        level.draw(
            world_surface
        )

        draw_goal(
            world_surface
        )

        if (
            not level_complete
            and not demo_complete
            and not player_dead
        ):
            player.draw_gravity_indicator(
                world_surface
            )

        player.draw(
            world_surface
        )

        effects.draw(
            world_surface
        )

        # ----------------------------------------------------
        # SCREEN SHAKE
        # ----------------------------------------------------

        shake_x, shake_y = (
            effects.get_camera_offset()
        )

        screen.fill(
            BACKGROUND
        )

        screen.blit(
            world_surface,
            (
                shake_x,
                shake_y
            )
        )

        # ----------------------------------------------------
        # STABLE HUD
        # ----------------------------------------------------

        draw_hud(
            screen
        )

        # ----------------------------------------------------
        # LEVEL 1 TUTORIAL
        # ----------------------------------------------------

        if (
            level.number == 1
            and level_elapsed_time < 8.0
            and not level_complete
            and not player_dead
            and not paused
            and not transitions.busy
        ):
            draw_first_level_tutorial(
                screen
            )

        # ----------------------------------------------------
        # GAME OVERLAYS
        # ----------------------------------------------------

        if level_complete:
            draw_complete_screen(
                screen
            )

        elif player_dead:
            draw_death_screen(
                screen
            )

        elif demo_complete:
            draw_demo_complete(
                screen
            )

        elif paused:
            draw_pause_screen(
                screen
            )

        # ----------------------------------------------------
        # PARTICLE SCREEN FX
        # ----------------------------------------------------

        effects.draw_screen_fx(
            screen
        )

        # ----------------------------------------------------
        # FADE + LEVEL INTRO
        # ----------------------------------------------------

        transitions.draw(
            screen
        )

    pygame.display.flip()


# ============================================================
# CLEAN EXIT
# ============================================================

audio.shutdown()

pygame.quit()