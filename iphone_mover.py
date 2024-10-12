import os
import pathlib
import shutil
import time
from datetime import datetime, timezone, timedelta

FORMATS = {}
LOCATIONS = {}

MOVE_FORMATS = [".JPEG", ".JPG", ".MOV", ".MP4", ".PNG", ".PLIST"]


def runtime(start: float) -> str:
    """Returns the runtime of a function in seconds."""
    return f"{round(float(time.time() - start), 2)}s"


def is_valid_epoch(epoch_string: str, n_minutes: int) -> bool:
    """Check if a string is a valid epoch timestamp within the last n minutes.

    Args:
        epoch_string: Epoch timestamp as a string.
        n_minutes: Last n minutes to check.

    Returns:
        bool:
        True if the epoch is within the last n minutes, False otherwise.
    """
    try:
        epoch_time = int(epoch_string)
        dt = datetime.fromtimestamp(epoch_time, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        n_minutes_ago = current_time - timedelta(minutes=n_minutes)
        return n_minutes_ago <= dt <= current_time
    except (ValueError, OverflowError):
        return False


def cleanup(dir_path: str) -> None:
    """Remove epoch timestamps from filenames in a directory.

    Args:
        dir_path: Directory path to clean up.
    """
    start = time.time()
    timestamp_len = len(str(int(start)))
    n = 0
    for __path, __directory, __file in os.walk(dir_path):
        for file in __file:
            file_obj = pathlib.Path(str(os.path.join(__path, file)))
            if len(file_obj.stem) < timestamp_len:
                continue
            maybe_timestamp = file_obj.stem[-timestamp_len:]
            if not is_valid_epoch(maybe_timestamp, 90):
                continue
            new_name = file_obj.stem.replace(maybe_timestamp, "") + file_obj.suffix
            new_path = os.path.join(__path, new_name)
            shutil.move(file_obj, new_path)
            n += 1
    print(f"{n} files renamed in {runtime(start)}")


def debug(location: str, file_obj: pathlib.Path) -> None:
    """Debug function for dry run mode.

    Args:
        location: File location.
        file_obj: File object.
    """
    LOCATIONS[location] = LOCATIONS.get(location, 0) + 1
    FORMATS[file_obj.suffix] = FORMATS.get(file_obj.suffix, 0) + 1


def main(dir_path: str, dry_run: bool = True) -> None:
    """Move files from subdirectories to the parent directory.

    Args:
        dir_path: Root directory path.
        dry_run: Dry run mode.
    """
    start = time.time()
    n = 0
    for __path, __directory, __file in os.walk(dir_path):
        for file in __file:
            file_obj = pathlib.Path(os.path.join(__path, file))
            if file_obj.suffix.upper() not in MOVE_FORMATS:
                continue

            parent = __path.split(os.path.sep)[-1]

            # This condition ensures that there are no overlaps in the current dir
            if dir_path.endswith(parent):
                continue

            if dry_run:
                debug(parent, file_obj)
            else:
                old_path = str(file_obj)
                if file in os.listdir(dir_path):
                    new_name = file.replace(file_obj.suffix, f"{int(time.time())}{file_obj.suffix}")
                    new_path = os.path.join(dir_path, new_name)
                else:
                    new_path = os.path.join(dir_path, file)
                shutil.move(old_path, new_path)
                n += 1

    if dry_run:
        import pprint
        pprint.pprint({"format_ct": FORMATS, "location_ct": LOCATIONS})
    else:
        print(f"{n} files moved in {runtime(start)}")
