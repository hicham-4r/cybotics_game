import json
from datetime import datetime
from pathlib import Path


class Preferences:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        path,
        default_fullscreen=False,
        default_music_volume=0.35,
        default_sfx_volume=0.70,
        default_muted=False
    ):

        self.path = Path(
            path
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        self.defaults = {
            "fullscreen": bool(
                default_fullscreen
            ),

            "music_volume": self._clamp(
                default_music_volume
            ),

            "sfx_volume": self._clamp(
                default_sfx_volume
            ),

            "muted": bool(
                default_muted
            ),
        }


        self.data = dict(
            self.defaults
        )


        self.load()

        # Ensures the file exists and any invalid values
        # are rewritten safely.
        self.save()


    # ========================================================
    # CLAMP
    # ========================================================

    @staticmethod
    def _clamp(
        value
    ):

        try:

            return max(
                0.0,
                min(
                    1.0,
                    float(value)
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0


    # ========================================================
    # VALID NUMBER
    # ========================================================

    @staticmethod
    def _is_number(
        value
    ):

        return (
            isinstance(
                value,
                (
                    int,
                    float
                )
            )
            and not isinstance(
                value,
                bool
            )
        )


    # ========================================================
    # LOAD
    # ========================================================

    def load(
        self
    ):

        if not self.path.exists():

            return


        try:

            raw_data = json.loads(
                self.path.read_text(
                    encoding="utf-8"
                )
            )


            if not isinstance(
                raw_data,
                dict
            ):

                raise ValueError(
                    "Preferences file must contain an object."
                )


            fullscreen_value = raw_data.get(
                "fullscreen",
                self.defaults[
                    "fullscreen"
                ]
            )


            music_value = raw_data.get(
                "music_volume",
                self.defaults[
                    "music_volume"
                ]
            )


            sfx_value = raw_data.get(
                "sfx_volume",
                self.defaults[
                    "sfx_volume"
                ]
            )


            muted_value = raw_data.get(
                "muted",
                self.defaults[
                    "muted"
                ]
            )


            if isinstance(
                fullscreen_value,
                bool
            ):

                self.data[
                    "fullscreen"
                ] = fullscreen_value


            if self._is_number(
                music_value
            ):

                self.data[
                    "music_volume"
                ] = self._clamp(
                    music_value
                )


            if self._is_number(
                sfx_value
            ):

                self.data[
                    "sfx_volume"
                ] = self._clamp(
                    sfx_value
                )


            if isinstance(
                muted_value,
                bool
            ):

                self.data[
                    "muted"
                ] = muted_value


        except (
            OSError,
            json.JSONDecodeError,
            ValueError
        ):

            self._backup_corrupted_file()

            self.data = dict(
                self.defaults
            )


    # ========================================================
    # BACKUP CORRUPTED FILE
    # ========================================================

    def _backup_corrupted_file(
        self
    ):

        if not self.path.exists():

            return


        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )


        backup_path = (
            self.path.parent
            / (
                f"{self.path.stem}"
                f"_corrupted_{timestamp}"
                f"{self.path.suffix}"
            )
        )


        try:

            self.path.replace(
                backup_path
            )

        except OSError:

            pass


    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self
    ):

        temporary_path = (
            self.path.parent
            / (
                f"{self.path.name}.tmp"
            )
        )


        content = json.dumps(
            self.data,
            indent=4
        )


        temporary_path.write_text(
            content,
            encoding="utf-8"
        )


        temporary_path.replace(
            self.path
        )


    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def fullscreen(
        self
    ):

        return bool(
            self.data[
                "fullscreen"
            ]
        )


    @property
    def music_volume(
        self
    ):

        return float(
            self.data[
                "music_volume"
            ]
        )


    @property
    def sfx_volume(
        self
    ):

        return float(
            self.data[
                "sfx_volume"
            ]
        )


    @property
    def muted(
        self
    ):

        return bool(
            self.data[
                "muted"
            ]
        )


    # ========================================================
    # SET FULLSCREEN
    # ========================================================

    def set_fullscreen(
        self,
        value
    ):

        self.data[
            "fullscreen"
        ] = bool(
            value
        )

        self.save()


    # ========================================================
    # SET MUSIC VOLUME
    # ========================================================

    def set_music_volume(
        self,
        value
    ):

        self.data[
            "music_volume"
        ] = self._clamp(
            value
        )

        self.save()


    # ========================================================
    # SET SFX VOLUME
    # ========================================================

    def set_sfx_volume(
        self,
        value
    ):

        self.data[
            "sfx_volume"
        ] = self._clamp(
            value
        )

        self.save()


    # ========================================================
    # SET MUTED
    # ========================================================

    def set_muted(
        self,
        value
    ):

        self.data[
            "muted"
        ] = bool(
            value
        )

        self.save()