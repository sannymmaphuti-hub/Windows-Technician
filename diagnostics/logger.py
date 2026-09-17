# ==========================================================
# Windows Technician v0.5
# DIAGNOSTIC LOGGER
# ==========================================================

from datetime import datetime
from pathlib import Path


LOG_DIRECTORY = Path("logs")


def initialize_log_directory():
    """
    Create the log directory if it does not exist.
    """

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )


def get_log_timestamp():
    """
    Return a timestamp suitable for log entries.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def create_log_file():
    """
    Create a new timestamped diagnostic log file.
    """

    initialize_log_directory()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    log_path = (
        LOG_DIRECTORY /
        f"diagnostic_{timestamp}.log"
    )

    with open(
        log_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "==================================================\n"
        )

        file.write(
            "Windows Technician v0.5\n"
        )

        file.write(
            "DIAGNOSTIC LOG\n"
        )

        file.write(
            "==================================================\n"
        )

        file.write(
            f"Diagnostic Started : "
            f"{get_log_timestamp()}\n"
        )

        file.write("\n")

    return log_path


def write_log(
    log_path,
    level,
    category,
    message
):
    """
    Write a diagnostic event to the log.
    """

    timestamp = get_log_timestamp()

    with open(
        log_path,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"[{timestamp}] "
            f"[{level}] "
            f"[{category}] "
            f"{message}\n"
        )


def close_log(log_path):
    """
    Mark the end of a diagnostic run.
    """

    with open(
        log_path,
        "a",
        encoding="utf-8"
    ) as file:

        file.write("\n")

        file.write(
            "==================================================\n"
        )

        file.write(
            f"Diagnostic Completed : "
            f"{get_log_timestamp()}\n"
        )

        file.write(
            "==================================================\n"
        )


# ==========================================================
# MODULE TEST
# ==========================================================

if __name__ == "__main__":

    print("==========================================")
    print("LOGGER MODULE TEST")
    print("==========================================")

    log_file = create_log_file()

    print()
    print(f"Log created : {log_file}")

    write_log(
        log_file,
        "INFO",
        "SYSTEM",
        "Windows Technician diagnostic started."
    )

    write_log(
        log_file,
        "INFO",
        "CPU",
        "CPU diagnostic completed successfully."
    )

    write_log(
        log_file,
        "WARNING",
        "MEMORY",
        "Memory usage is elevated."
    )

    write_log(
        log_file,
        "INFO",
        "NETWORK",
        "Network connectivity is healthy."
    )

    close_log(log_file)

    print()
    print("Logger test completed.")

