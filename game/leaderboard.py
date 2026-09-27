import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class LeaderboardDatabase:
    def __init__(self, database_path):

        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_with_recovery()


    # ========================================================
    # CONNECTION
    # ========================================================

    def _connect(self):

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        return connection


    # ========================================================
    # NORMALIZE PLAYER NAME
    # ========================================================

    @staticmethod
    def normalize_player_name(
        player_name
    ):

        return (
            str(player_name)
            .strip()
            .upper()
        )


    # ========================================================
    # INITIALIZE WITH RECOVERY
    # ========================================================

    def _initialize_with_recovery(self):

        try:

            self._initialize_database()

        except sqlite3.DatabaseError:

            if self.database_path.exists():

                timestamp = datetime.now(
                    timezone.utc
                ).strftime(
                    "%Y%m%d_%H%M%S"
                )

                backup_path = (
                    self.database_path
                    .with_name(
                        (
                            f"{self.database_path.stem}"
                            f"_corrupted_{timestamp}"
                            f"{self.database_path.suffix}"
                        )
                    )
                )

                self.database_path.replace(
                    backup_path
                )

            self._initialize_database()


    # ========================================================
    # CREATE DATABASE
    # ========================================================

    def _initialize_database(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    player_name TEXT NOT NULL,

                    score INTEGER NOT NULL DEFAULT 0,

                    levels_completed INTEGER NOT NULL DEFAULT 0,

                    total_time REAL NOT NULL DEFAULT 0,

                    deaths INTEGER NOT NULL DEFAULT 0,

                    restarts INTEGER NOT NULL DEFAULT 0,

                    death_penalties INTEGER NOT NULL DEFAULT 0,

                    completed INTEGER NOT NULL DEFAULT 0,

                    timestamp TEXT NOT NULL
                )
                """
            )


            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_runs_leaderboard
                ON runs (
                    score DESC,
                    total_time ASC
                )
                """
            )


            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_runs_player_name
                ON runs (
                    player_name
                )
                """
            )


    # ========================================================
    # PLAYER NAME EXISTS
    # ========================================================

    def player_name_exists(
        self,
        player_name
    ):

        clean_name = (
            self.normalize_player_name(
                player_name
            )
        )


        if not clean_name:

            return False


        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT id

                FROM runs

                WHERE UPPER(TRIM(player_name))
                      = UPPER(TRIM(?))

                LIMIT 1
                """,
                (
                    clean_name,
                )
            ).fetchone()


        return row is not None


    # ========================================================
    # SAVE RUN
    # ========================================================

    def save_run(
        self,
        player_name,
        score,
        levels_completed,
        total_time,
        deaths,
        restarts=0,
        death_penalties=0,
        completed=False
    ):

        clean_name = (
            self.normalize_player_name(
                player_name
            )
        )


        if not clean_name:

            raise ValueError(
                "Player name cannot be empty."
            )


        if self.player_name_exists(
            clean_name
        ):

            raise ValueError(
                (
                    f"Player name '{clean_name}' "
                    "already exists."
                )
            )


        timestamp = datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )


        with self._connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO runs (
                    player_name,
                    score,
                    levels_completed,
                    total_time,
                    deaths,
                    restarts,
                    death_penalties,
                    completed,
                    timestamp
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    clean_name,
                    max(
                        0,
                        int(score)
                    ),
                    max(
                        0,
                        int(levels_completed)
                    ),
                    max(
                        0.0,
                        float(total_time)
                    ),
                    max(
                        0,
                        int(deaths)
                    ),
                    max(
                        0,
                        int(restarts)
                    ),
                    max(
                        0,
                        int(death_penalties)
                    ),
                    (
                        1
                        if completed
                        else 0
                    ),
                    timestamp,
                )
            )


            return cursor.lastrowid


    # ========================================================
    # GET TOP RUNS
    # ========================================================

    def get_top_runs(
        self,
        limit=10
    ):

        safe_limit = max(
            1,
            min(
                int(limit),
                100
            )
        )


        with self._connect() as connection:

            rows = connection.execute(
                """
                WITH unique_runs AS (

                    SELECT
                        id,
                        player_name,
                        score,
                        levels_completed,
                        total_time,
                        deaths,
                        restarts,
                        death_penalties,
                        completed,
                        timestamp,

                        ROW_NUMBER() OVER (
                            PARTITION BY
                                UPPER(TRIM(player_name))

                            ORDER BY
                                score DESC,
                                total_time ASC,
                                id ASC
                        ) AS player_run_rank

                    FROM runs
                )

                SELECT
                    id,
                    player_name,
                    score,
                    levels_completed,
                    total_time,
                    deaths,
                    restarts,
                    death_penalties,
                    completed,
                    timestamp

                FROM unique_runs

                WHERE player_run_rank = 1

                ORDER BY
                    score DESC,
                    total_time ASC,
                    id ASC

                LIMIT ?
                """,
                (
                    safe_limit,
                )
            ).fetchall()


        return [
            dict(row)
            for row in rows
        ]


    # ========================================================
    # GET RUN
    # ========================================================

    def get_run(
        self,
        run_id
    ):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    id,
                    player_name,
                    score,
                    levels_completed,
                    total_time,
                    deaths,
                    restarts,
                    death_penalties,
                    completed,
                    timestamp

                FROM runs

                WHERE id = ?
                """,
                (
                    int(run_id),
                )
            ).fetchone()


        if row is None:

            return None


        return dict(
            row
        )


    # ========================================================
    # RANK
    # ========================================================

    def get_rank(
        self,
        run_id
    ):

        target_run = self.get_run(
            run_id
        )


        if target_run is None:

            return None


        target_name = (
            self.normalize_player_name(
                target_run[
                    "player_name"
                ]
            )
        )


        with self._connect() as connection:

            rows = connection.execute(
                """
                WITH unique_runs AS (

                    SELECT
                        id,
                        player_name,
                        score,
                        total_time,

                        ROW_NUMBER() OVER (
                            PARTITION BY
                                UPPER(TRIM(player_name))

                            ORDER BY
                                score DESC,
                                total_time ASC,
                                id ASC
                        ) AS player_run_rank

                    FROM runs
                )

                SELECT
                    id,
                    player_name,
                    score,
                    total_time

                FROM unique_runs

                WHERE player_run_rank = 1

                ORDER BY
                    score DESC,
                    total_time ASC,
                    id ASC
                """
            ).fetchall()


        for rank, row in enumerate(
            rows,
            start=1
        ):

            row_name = (
                self.normalize_player_name(
                    row[
                        "player_name"
                    ]
                )
            )


            if row_name == target_name:

                return rank


        return None


    # ========================================================
    # BEST SCORE
    # ========================================================

    def get_best_score(self):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT MAX(score) AS best_score
                FROM runs
                """
            ).fetchone()


        if (
            row is None
            or row["best_score"] is None
        ):

            return 0


        return int(
            row[
                "best_score"
            ]
        )


    # ========================================================
    # TOTAL RUNS
    # ========================================================

    def get_total_runs(self):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM runs
                """
            ).fetchone()


        return int(
            row[
                "total"
            ]
        )


    # ========================================================
    # TOTAL UNIQUE PLAYERS
    # ========================================================

    def get_total_players(self):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    COUNT(
                        DISTINCT
                        UPPER(TRIM(player_name))
                    ) AS total

                FROM runs
                """
            ).fetchone()


        return int(
            row[
                "total"
            ]
        )


    # ========================================================
    # CLEAR LEADERBOARD
    # ========================================================

    def clear_all_runs(self):

        with self._connect() as connection:

            connection.execute(
                """
                DELETE FROM runs
                """
            )


            # Reset AUTOINCREMENT so the next run begins at ID 1.
            connection.execute(
                """
                DELETE FROM sqlite_sequence
                WHERE name = ?
                """,
                (
                    "runs",
                )
            )