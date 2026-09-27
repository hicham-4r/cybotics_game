import math
import struct
import wave
from pathlib import Path

import pygame


class AudioManager:

    SAMPLE_RATE = 44100

    AUDIO_VERSION = "v2"


    # ========================================================
    # EFFECT MIX LEVELS
    # ========================================================

    SOUND_LEVELS = {
        "menu_move": 0.28,
        "menu_click": 0.40,
        "gravity": 0.48,
        "goal": 0.66,
        "death": 0.68,
        "level_transition": 0.52,
        "high_score": 0.75,
        "run_start": 0.54,
        "run_complete": 0.68,
    }


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        audio_dir,
        music_volume=0.35,
        sfx_volume=0.70,
        muted=False
    ):

        self.audio_dir = Path(
            audio_dir
        )

        self.audio_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        self.music_volume = self._clamp(
            music_volume
        )

        self.sfx_volume = self._clamp(
            sfx_volume
        )

        self.muted = bool(
            muted
        )


        self.available = False

        self.error_message = ""

        self.sounds = {}


        self.sound_paths = {

            "menu_move": (
                self.audio_dir
                / f"menu_move_{self.AUDIO_VERSION}.wav"
            ),

            "menu_click": (
                self.audio_dir
                / f"menu_click_{self.AUDIO_VERSION}.wav"
            ),

            "gravity": (
                self.audio_dir
                / f"gravity_{self.AUDIO_VERSION}.wav"
            ),

            "goal": (
                self.audio_dir
                / f"goal_{self.AUDIO_VERSION}.wav"
            ),

            "death": (
                self.audio_dir
                / f"death_{self.AUDIO_VERSION}.wav"
            ),

            "level_transition": (
                self.audio_dir
                / f"level_transition_{self.AUDIO_VERSION}.wav"
            ),

            "high_score": (
                self.audio_dir
                / f"high_score_{self.AUDIO_VERSION}.wav"
            ),

            "run_start": (
                self.audio_dir
                / f"run_start_{self.AUDIO_VERSION}.wav"
            ),

            "run_complete": (
                self.audio_dir
                / f"run_complete_{self.AUDIO_VERSION}.wav"
            ),
        }


        self.music_path = (
            self.audio_dir
            / f"cybotics_theme_{self.AUDIO_VERSION}.wav"
        )


        try:

            self._ensure_audio_files()


            if not pygame.mixer.get_init():

                pygame.mixer.init(
                    frequency=self.SAMPLE_RATE,
                    size=-16,
                    channels=2,
                    buffer=512
                )


            self._load_sounds()


            self.available = True


            self._apply_volumes()


        except (
            pygame.error,
            OSError,
            wave.Error,
            ValueError
        ) as error:

            self.available = False

            self.error_message = str(
                error
            )


    # ========================================================
    # CLAMP
    # ========================================================

    @staticmethod
    def _clamp(
        value
    ):

        return max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )


    # ========================================================
    # OSCILLATORS
    # ========================================================

    @staticmethod
    def _sine(
        frequency,
        time_value
    ):

        return math.sin(
            2.0
            * math.pi
            * frequency
            * time_value
        )


    @staticmethod
    def _triangle(
        frequency,
        time_value
    ):

        phase = (
            frequency
            * time_value
        ) % 1.0


        return (
            4.0
            * abs(
                phase
                - 0.5
            )
            - 1.0
        )


    @staticmethod
    def _square(
        frequency,
        time_value
    ):

        value = math.sin(
            2.0
            * math.pi
            * frequency
            * time_value
        )


        if value >= 0:

            return 1.0


        return -1.0


    # ========================================================
    # NOTE ENVELOPE
    # ========================================================

    @staticmethod
    def _note_envelope(
        local_time,
        note_duration,
        attack=0.03,
        release=0.12
    ):

        if (
            local_time < 0
            or local_time >= note_duration
        ):

            return 0.0


        attack_amount = min(
            1.0,
            local_time
            / max(
                attack,
                0.001
            )
        )


        remaining = (
            note_duration
            - local_time
        )


        release_amount = min(
            1.0,
            remaining
            / max(
                release,
                0.001
            )
        )


        return min(
            attack_amount,
            release_amount
        )


    # ========================================================
    # WAV WRITER
    # ========================================================

    def _write_wave(
        self,
        path,
        duration,
        sample_function,
        fade=True
    ):

        sample_count = max(
            1,
            int(
                self.SAMPLE_RATE
                * duration
            )
        )


        attack_samples = max(
            1,
            int(
                self.SAMPLE_RATE
                * 0.008
            )
        )


        release_samples = max(
            1,
            int(
                self.SAMPLE_RATE
                * 0.045
            )
        )


        frames = bytearray()


        for index in range(
            sample_count
        ):

            time_value = (
                index
                / self.SAMPLE_RATE
            )


            sample = float(
                sample_function(
                    time_value,
                    duration
                )
            )


            if fade:

                attack = min(
                    1.0,
                    index
                    / attack_samples
                )


                remaining = (
                    sample_count
                    - 1
                    - index
                )


                release = min(
                    1.0,
                    remaining
                    / release_samples
                )


                sample *= min(
                    attack,
                    release
                )


            sample = max(
                -1.0,
                min(
                    1.0,
                    sample
                )
            )


            value = int(
                sample
                * 32767
            )


            frames.extend(
                struct.pack(
                    "<h",
                    value
                )
            )


        with wave.open(
            str(path),
            "wb"
        ) as wav_file:

            wav_file.setnchannels(
                1
            )

            wav_file.setsampwidth(
                2
            )

            wav_file.setframerate(
                self.SAMPLE_RATE
            )

            wav_file.writeframes(
                frames
            )


    # ========================================================
    # CREATE FILES
    # ========================================================

    def _ensure_audio_files(
        self
    ):

        generators = {

            self.sound_paths["menu_move"]: (
                0.075,
                self._sample_menu_move,
                True
            ),

            self.sound_paths["menu_click"]: (
                0.12,
                self._sample_menu_click,
                True
            ),

            self.sound_paths["gravity"]: (
                0.18,
                self._sample_gravity,
                True
            ),

            self.sound_paths["goal"]: (
                0.50,
                self._sample_goal,
                True
            ),

            self.sound_paths["death"]: (
                0.48,
                self._sample_death,
                True
            ),

            self.sound_paths["level_transition"]: (
                0.32,
                self._sample_transition,
                True
            ),

            self.sound_paths["high_score"]: (
                0.82,
                self._sample_high_score,
                True
            ),

            self.sound_paths["run_start"]: (
                0.42,
                self._sample_run_start,
                True
            ),

            self.sound_paths["run_complete"]: (
                0.75,
                self._sample_run_complete,
                True
            ),

            self.music_path: (
                8.0,
                self._sample_music,
                False
            ),
        }


        for (
            path,
            (
                duration,
                generator,
                fade
            )
        ) in generators.items():

            if not path.exists():

                self._write_wave(
                    path,
                    duration,
                    generator,
                    fade=fade
                )


    # ========================================================
    # MENU MOVE
    # ========================================================

    def _sample_menu_move(
        self,
        t,
        duration
    ):

        progress = (
            t
            / duration
        )


        frequency = (
            520
            + 180
            * progress
        )


        return (
            0.42
            * self._sine(
                frequency,
                t
            )

            + 0.12
            * self._sine(
                frequency * 2,
                t
            )
        )


    # ========================================================
    # MENU CLICK
    # ========================================================

    def _sample_menu_click(
        self,
        t,
        duration
    ):

        progress = (
            t
            / duration
        )


        frequency = (
            430
            + 650
            * progress
        )


        return (
            0.40
            * self._sine(
                frequency,
                t
            )

            + 0.14
            * self._triangle(
                frequency * 0.5,
                t
            )
        )


    # ========================================================
    # GRAVITY
    # ========================================================

    def _sample_gravity(
        self,
        t,
        duration
    ):

        progress = (
            t
            / duration
        )


        frequency = (
            170
            + 950
            * (
                progress ** 1.5
            )
        )


        return (
            0.46
            * self._sine(
                frequency,
                t
            )

            + 0.18
            * self._sine(
                frequency * 2.03,
                t
            )

            + 0.08
            * self._sine(
                frequency * 4.07,
                t
            )
        )


    # ========================================================
    # GOAL
    # ========================================================

    def _sample_goal(
        self,
        t,
        duration
    ):

        notes = (
            392.00,
            523.25,
            659.25,
            783.99
        )


        note_duration = (
            duration
            / len(
                notes
            )
        )


        note_index = min(
            len(notes) - 1,
            int(
                t
                / note_duration
            )
        )


        local_time = (
            t
            - note_index
            * note_duration
        )


        frequency = (
            notes[
                note_index
            ]
        )


        envelope = (
            self._note_envelope(
                local_time,
                note_duration,
                attack=0.01,
                release=0.08
            )
        )


        return envelope * (

            0.43
            * self._sine(
                frequency,
                t
            )

            + 0.16
            * self._sine(
                frequency * 2,
                t
            )

            + 0.06
            * self._sine(
                frequency * 3,
                t
            )
        )


    # ========================================================
    # DEATH
    # ========================================================

    def _sample_death(
        self,
        t,
        duration
    ):

        progress = (
            t
            / duration
        )


        frequency = (
            270
            * (
                1.0
                - 0.78
                * progress
            )
        )


        low_drop = self._sine(
            frequency,
            t
        )


        distortion = self._square(
            max(
                45,
                frequency * 1.4
            ),
            t
        )


        glitch = self._sine(
            (
                800
                + 350
                * self._sine(
                    13,
                    t
                )
            ),
            t
        )


        return (
            0.44
            * low_drop

            + 0.10
            * distortion

            + 0.12
            * glitch
        )


    # ========================================================
    # TRANSITION
    # ========================================================

    def _sample_transition(
        self,
        t,
        duration
    ):

        progress = (
            t
            / duration
        )


        frequency = (
            250
            + 1100
            * progress
        )


        return (
            0.38
            * self._sine(
                frequency,
                t
            )

            + 0.13
            * self._sine(
                frequency * 1.5,
                t
            )
        )


    # ========================================================
    # HIGH SCORE
    # ========================================================

    def _sample_high_score(
        self,
        t,
        duration
    ):

        notes = (
            523.25,
            659.25,
            783.99,
            1046.50,
            1318.51
        )


        note_duration = (
            duration
            / len(
                notes
            )
        )


        note_index = min(
            len(notes) - 1,
            int(
                t
                / note_duration
            )
        )


        local_time = (
            t
            - note_index
            * note_duration
        )


        frequency = (
            notes[
                note_index
            ]
        )


        envelope = (
            self._note_envelope(
                local_time,
                note_duration,
                attack=0.008,
                release=0.09
            )
        )


        return envelope * (

            0.40
            * self._sine(
                frequency,
                t
            )

            + 0.16
            * self._triangle(
                frequency,
                t
            )

            + 0.08
            * self._sine(
                frequency * 2,
                t
            )
        )


    # ========================================================
    # RUN START
    # ========================================================

    def _sample_run_start(
        self,
        t,
        duration
    ):

        progress = (
            t
            / duration
        )


        frequency = (
            100
            + 650
            * progress
        )


        return (
            0.45
            * self._sine(
                frequency,
                t
            )

            + 0.15
            * self._triangle(
                frequency * 0.5,
                t
            )
        )


    # ========================================================
    # RUN COMPLETE
    # ========================================================

    def _sample_run_complete(
        self,
        t,
        duration
    ):

        notes = (
            261.63,
            392.00,
            523.25,
            659.25
        )


        note_duration = (
            duration
            / len(
                notes
            )
        )


        note_index = min(
            len(notes) - 1,
            int(
                t
                / note_duration
            )
        )


        local_time = (
            t
            - note_index
            * note_duration
        )


        frequency = (
            notes[
                note_index
            ]
        )


        envelope = (
            self._note_envelope(
                local_time,
                note_duration,
                attack=0.015,
                release=0.12
            )
        )


        return envelope * (

            0.45
            * self._sine(
                frequency,
                t
            )

            + 0.18
            * self._sine(
                frequency * 2,
                t
            )
        )


    # ========================================================
    # MUSIC PAD
    # ========================================================

    def _music_pad(
        self,
        t,
        chord
    ):

        root = chord[0]
        third = chord[1]
        fifth = chord[2]


        slow_lfo = (
            0.78
            + 0.22
            * self._sine(
                0.125,
                t
            )
        )


        pad = (

            0.13
            * self._sine(
                root,
                t
            )

            + 0.09
            * self._sine(
                third,
                t
            )

            + 0.09
            * self._sine(
                fifth,
                t
            )

            + 0.035
            * self._sine(
                root * 2,
                t
            )

            + 0.025
            * self._sine(
                fifth * 2,
                t
            )
        )


        return (
            pad
            * slow_lfo
        )


    # ========================================================
    # MUSIC BASS
    # ========================================================

    def _music_bass(
        self,
        t,
        root_frequency
    ):

        beat_duration = 0.5


        beat_position = (
            t
            % beat_duration
        )


        envelope = math.exp(
            -5.5
            * beat_position
        )


        bass = (

            0.22
            * self._sine(
                root_frequency,
                t
            )

            + 0.07
            * self._triangle(
                root_frequency,
                t
            )
        )


        return (
            bass
            * envelope
        )


    # ========================================================
    # MUSIC ARPEGGIO
    # ========================================================

    def _music_arpeggio(
        self,
        t,
        chord
    ):

        step_duration = 0.25


        step = int(
            t
            / step_duration
        )


        sequence = (
            0,
            1,
            2,
            1,
            0,
            2,
            1,
            2
        )


        note_index = (
            sequence[
                step
                % len(
                    sequence
                )
            ]
        )


        frequency = (
            chord[
                note_index
            ]
            * 2
        )


        local_time = (
            t
            % step_duration
        )


        envelope = (
            self._note_envelope(
                local_time,
                step_duration,
                attack=0.008,
                release=0.16
            )
        )


        return envelope * (

            0.075
            * self._triangle(
                frequency,
                t
            )

            + 0.035
            * self._sine(
                frequency * 2,
                t
            )
        )


    # ========================================================
    # MUSIC KICK
    # ========================================================

    def _music_kick(
        self,
        t
    ):

        beat_duration = 0.5


        local_time = (
            t
            % beat_duration
        )


        if local_time > 0.13:

            return 0.0


        envelope = math.exp(
            -30
            * local_time
        )


        frequency = (
            90
            - 45
            * (
                local_time
                / 0.13
            )
        )


        return (
            0.15
            * envelope
            * self._sine(
                frequency,
                local_time
            )
        )


    # ========================================================
    # MUSIC HI-HAT
    # ========================================================

    def _music_hat(
        self,
        t
    ):

        step_duration = 0.25


        local_time = (
            t
            % step_duration
        )


        if local_time > 0.045:

            return 0.0


        envelope = math.exp(
            -70
            * local_time
        )


        metallic = (

            self._sine(
                5100,
                t
            )

            + self._sine(
                6700,
                t
            )

            + self._sine(
                7900,
                t
            )

        ) / 3.0


        return (
            0.022
            * envelope
            * metallic
        )


    # ========================================================
    # CYBOTICS THEME
    # ========================================================

    def _sample_music(
        self,
        t,
        duration
    ):

        chord_duration = 2.0


        chord_index = int(
            t
            / chord_duration
        ) % 4


        chords = (

            (
                130.81,
                155.56,
                196.00
            ),

            (
                103.83,
                130.81,
                155.56
            ),

            (
                155.56,
                196.00,
                233.08
            ),

            (
                116.54,
                146.83,
                174.61
            ),
        )


        bass_roots = (
            65.41,
            51.91,
            77.78,
            58.27
        )


        chord = (
            chords[
                chord_index
            ]
        )


        root = (
            bass_roots[
                chord_index
            ]
        )


        pad = self._music_pad(
            t,
            chord
        )


        bass = self._music_bass(
            t,
            root
        )


        arp = self._music_arpeggio(
            t,
            chord
        )


        kick = self._music_kick(
            t
        )


        hat = self._music_hat(
            t
        )


        digital_pulse = (

            0.018
            * self._sine(
                880,
                t
            )

            * (
                0.5
                + 0.5
                * self._sine(
                    0.5,
                    t
                )
            )
        )


        return (
            pad
            + bass
            + arp
            + kick
            + hat
            + digital_pulse
        )


    # ========================================================
    # LOAD EFFECTS
    # ========================================================

    def _load_sounds(
        self
    ):

        for (
            sound_name,
            path
        ) in self.sound_paths.items():

            self.sounds[
                sound_name
            ] = pygame.mixer.Sound(
                str(
                    path
                )
            )


    # ========================================================
    # APPLY MUSIC + SFX VOLUMES
    # ========================================================

    def _apply_volumes(
        self
    ):

        if not self.available:

            return


        effective_sfx = (
            0.0
            if self.muted
            else self.sfx_volume
        )


        effective_music = (
            0.0
            if self.muted
            else self.music_volume
        )


        for (
            sound_name,
            sound
        ) in self.sounds.items():

            effect_level = (
                self.SOUND_LEVELS.get(
                    sound_name,
                    1.0
                )
            )


            sound.set_volume(
                self._clamp(
                    effective_sfx
                    * effect_level
                )
            )


        pygame.mixer.music.set_volume(
            self._clamp(
                effective_music
            )
        )


    # ========================================================
    # PLAY EFFECT
    # ========================================================

    def play(
        self,
        sound_name
    ):

        if (
            not self.available
            or self.muted
        ):

            return


        sound = self.sounds.get(
            sound_name
        )


        if sound is not None:

            sound.play()


    # ========================================================
    # START MUSIC
    # ========================================================

    def start_music(
        self
    ):

        if not self.available:

            return


        try:

            pygame.mixer.music.load(
                str(
                    self.music_path
                )
            )


            self._apply_volumes()


            pygame.mixer.music.play(
                -1
            )


        except pygame.error as error:

            self.error_message = str(
                error
            )


    # ========================================================
    # MUSIC VOLUME
    # ========================================================

    def set_music_volume(
        self,
        value
    ):

        self.music_volume = (
            self._clamp(
                value
            )
        )


        self._apply_volumes()


    def change_music_volume(
        self,
        amount
    ):

        self.set_music_volume(
            self.music_volume
            + float(
                amount
            )
        )


    # ========================================================
    # SFX VOLUME
    # ========================================================

    def set_sfx_volume(
        self,
        value
    ):

        self.sfx_volume = (
            self._clamp(
                value
            )
        )


        self._apply_volumes()


    def change_sfx_volume(
        self,
        amount
    ):

        self.set_sfx_volume(
            self.sfx_volume
            + float(
                amount
            )
        )


    # ========================================================
    # MUTE
    # ========================================================

    def toggle_mute(
        self
    ):

        self.muted = (
            not self.muted
        )


        self._apply_volumes()


        return self.muted


    # ========================================================
    # PERCENTAGES
    # ========================================================

    def get_music_volume_percent(
        self
    ):

        return int(
            round(
                self.music_volume
                * 100
            )
        )


    def get_sfx_volume_percent(
        self
    ):

        return int(
            round(
                self.sfx_volume
                * 100
            )
        )


    # ========================================================
    # SHUTDOWN
    # ========================================================

    def shutdown(
        self
    ):

        if not self.available:

            return


        pygame.mixer.music.stop()

        pygame.mixer.stop()