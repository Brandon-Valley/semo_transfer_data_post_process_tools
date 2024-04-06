import os
import shutil
import stat
from os.path import getsize, isdir, isfile, islink, join
from pathlib import Path
from typing import Callable, Generator, Iterable, List, Union

PATH_TYPES = Union[str, bytes, Path]
PATH_GEN = Generator[Path, None, None]


#######################################################################################################################
#  Delete FileSystemObjects
#######################################################################################################################
def delete_empty_child_dirs_recurs(in_dir_path: PATH_TYPES) -> None:
    for dir_str_path, child_dir_names, _child_file_names in os.walk(str(in_dir_path), followlinks=False):
        for child_dir_name in child_dir_names:
            child_dir_str_path = join(dir_str_path, child_dir_name)
            delete_empty_child_dirs_recurs(child_dir_str_path)

        if len(os.listdir(dir_str_path)) == 0:
            delete_if_exists(in_dir_path)


def delete_if_exists(path_or_path_iter: Union[PATH_TYPES, Iterable[PATH_TYPES]]) -> None:
    """For a given path or iterable of paths - Deletes everything that exists"""

    def _onerror(func: Callable, dir_path: Union[str, bytes, Path]) -> None:
        """
        Error handler for ``shutil.rmtree``.
          - If the error is due to an access error (read only file) it attempts to add write perms
            and then retries.
          - If the error is for another reason it re-raises the error.
          - Usage : ``shutil.rmtree(path, onerror=_onerror)``
        """
        if not os.access(dir_path, os.W_OK):
            os.chmod(dir_path, stat.S_IWUSR)  # Is the error an access error ?
            func(dir_path)
        else:
            raise

    def _delete_if_path_exists(in_path: Union[str, bytes, Path]) -> None:
        if Path(str(in_path)).exists():
            if isfile(in_path) or islink(in_path):
                os.remove(in_path)
            elif isdir(in_path):
                try:
                    shutil.rmtree(in_path, ignore_errors=False, onerror=_onerror)  # type: ignore [arg-type]
                except TypeError as e:
                    raise Exception(
                        f"Got TypeError when trying to delete {in_path}, probably means this dir contains a file that "
                        "is open in a program that is not allowing deletion (like a .csv open in Excel) - Close the "
                        "program and re-run"
                    ) from e
            else:
                raise ValueError(f"Unknown object: {path=} - {type(path)=}")

    # Delete path or every path in the iterable
    if isinstance(path_or_path_iter, (str, bytes, Path)):
        _delete_if_path_exists(path_or_path_iter)
    else:
        for path in path_or_path_iter:
            _delete_if_path_exists(path)


#######################################################################################################################
#  Relocate FileSystemObjects
#######################################################################################################################
def move_dir_content(src_dir_path: PATH_TYPES, dest_dir_path: PATH_TYPES) -> None:
    """
    Move content of src_dir_path to dest_dir_path
    Error if duplicate file exists in destination dir
    """
    assert isdir(src_dir_path)

    Path(str(dest_dir_path)).mkdir(parents=True, exist_ok=True)

    file_or_dir_names = os.listdir(src_dir_path)

    for file_or_dir_name in file_or_dir_names:
        shutil.move(join(str(src_dir_path), str(file_or_dir_name)), str(dest_dir_path))


#######################################################################################################################
#  Get Size of FileSystemObjects
#######################################################################################################################
def get_size(start_path: PATH_TYPES, unit: str = "B", num_decimal_places: int = 4) -> float:
    """
    Gets size of file or dir
      - unit: "B", "KB", "MB", "GB"
      - Does NOT follow SymLinks
    """
    total_size = 0
    if isdir(start_path):
        for dir_str_path, _child_dir_names, child_file_names in os.walk(str(start_path), followlinks=False):
            for child_file_name in child_file_names:
                child_file_str_path = join(dir_str_path, child_file_name)

                # Skip if fp is symbolic link
                if not islink(child_file_str_path):
                    total_size += getsize(child_file_str_path)
    elif isfile(start_path):
        total_size = getsize(start_path)

    if unit == "B":
        return total_size

    unit_dict = {"B": 1, "KB": 1000, "MB": 1000000, "GB": 1000000000}
    return round(total_size / unit_dict[unit], num_decimal_places)


#######################################################################################################################
#  Get Iterators of Paths to FileSystemObjects
#######################################################################################################################
def get_abs_path_generator_to_child_files_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> PATH_GEN:
    for path_obj in Path(str(in_dir_path)).rglob(regex):
        if path_obj.is_file():
            yield path_obj


def get_abs_path_generator_to_child_files_no_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> PATH_GEN:
    for path_obj in Path(str(in_dir_path)).glob(regex):
        if path_obj.is_file():
            yield path_obj


def get_abs_path_generator_to_child_dirs_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> PATH_GEN:
    for path_obj in Path(str(in_dir_path)).rglob(regex):
        if path_obj.is_dir():
            yield path_obj


def get_abs_path_generator_to_child_dirs_no_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> PATH_GEN:
    for path_obj in Path(str(in_dir_path)).glob(regex):
        if path_obj.is_dir():
            yield path_obj


def get_abs_path_generator_to_child_empty_dirs_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> PATH_GEN:
    for path_obj in Path(str(in_dir_path)).rglob(regex):
        if path_obj.is_dir() and not any(path_obj.iterdir()):
            yield path_obj


def get_abs_path_generator_to_child_empty_dirs_no_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> PATH_GEN:
    for path_obj in Path(str(in_dir_path)).glob(regex):
        if path_obj.is_dir() and not any(path_obj.iterdir()):
            yield path_obj


def get_abs_paths_to_child_files_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> List[Path]:
    return list(get_abs_path_generator_to_child_files_recurs(in_dir_path, regex))


def get_abs_paths_to_child_files_no_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> List[Path]:
    return list(get_abs_path_generator_to_child_files_no_recurs(in_dir_path, regex))


def get_abs_paths_to_child_dirs_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> List[Path]:
    return list(get_abs_path_generator_to_child_dirs_recurs(in_dir_path, regex))


def get_abs_paths_to_child_dirs_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> List[Path]:
    return list(get_abs_path_generator_to_child_dirs_no_recurs(in_dir_path, regex))


def get_abs_paths_to_child_dirs_no_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> List[Path]:
    return list(get_abs_path_generator_to_child_dirs_no_recurs(in_dir_path, regex))


def get_abs_paths_to_child_empty_dirs_no_recurs(in_dir_path: PATH_TYPES, regex: str = "*") -> List[Path]:
    return list(get_abs_path_generator_to_child_empty_dirs_no_recurs(in_dir_path, regex))
