import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Optional
from typing import Generator


########################################################################################################################
#  TXT
########################################################################################################################


def read_txt_as_line_generator(file_path: Path) -> Generator[str, None, None]:
    """Reads file as list of strings (one element per line) with no trailing whitespace."""
    assert isinstance(file_path, Path), f"Expected pathlib.Path object from {file_path=}, got {type(file_path)=}"
    assert file_path.is_file(), file_path

    with open(file_path) as f:
        for line in f:
            yield line.rstrip()


def read_txt_as_line_list(file_path: Path) -> List[str]:
    """Reads file as list of strings (one element per line) with no trailing whitespace."""
    assert isinstance(file_path, Path), f"Expected pathlib.Path object from {file_path=}, got {type(file_path)=}"
    assert file_path.is_file(), file_path

    return list(read_txt_as_line_generator(file_path))


def write_txt_from_lines(
    lines: Iterator,
    file_path: Path,
    write_mode: Literal["overwrite", "append"] = "overwrite",
    encoding="utf-8",
    decoding=False,
):
    """
    Writes a list of lines to a text file.

    Args:
        lines: The lines to write. Can be any iterator like: list, tuple, or generator.
        file_path: The path to the file.
        write_mode: The write mode. Defaults to 'overwrite'.
        encoding: The encoding of the file. Defaults to "utf-8". ("ascii" is also a common choice)
        decoding: Whether to decode the lines. Defaults to False.
    """
    # Determine write mode
    if write_mode == "overwrite":
        open_text_mode = "w"
    elif write_mode == "append":
        open_text_mode = "a"
    else:
        raise ValueError("Invalid write_mode: " + write_mode)

    # Write lines to file
    with open(file_path, open_text_mode, encoding=encoding) as f:

        if decoding and encoding:
            # Convert each line to string and decode
            f.write("\n".join(str(line).encode(encoding).decode(decoding, "ignore") for line in lines))
        else:
            # Convert each line to string and decode
            f.write("\n".join(str(line) for line in lines))


def delete_last_n_lines_from_txt(file_path: Path, num_lines_to_delete: int) -> None:
    """
    Deletes the last `num_lines_to_delete` lines from a text file.

    Args:
        file_path: The path to the file.
        num_lines_to_delete: The number of lines to delete.
    """
    assert isinstance(file_path, Path), f"Expected pathlib.Path object from {file_path=}, got {type(file_path)=}"
    assert file_path.is_file(), file_path

    # Read lines from file
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Write lines back to file
    with open(file_path, "w") as f:
        f.writelines(lines[:-num_lines_to_delete])


########################################################################################################################
#  JSON
########################################################################################################################


def read_json(json_path: Path) -> Any:
    assert isinstance(json_path, Path), f"Expected pathlib.Path object from {json_path=}, got {type(json_path)=}"
    assert json_path.is_file(), json_path
    return json.load(open(json_path, "r"))


def write_json(obj: Any, json_path: Path, indent: int = 4) -> None:
    """
    Write `obj` to `json_path` as JSON with `indent`
        - Will create parent directories if needed
        - If file exists, it will be overwritten
    """
    assert isinstance(json_path, Path), f"Expected pathlib.Path object from {json_path=}, got {type(json_path)=}"
    Path(json_path).parent.mkdir(exist_ok=True, parents=True)

    with open(json_path, "w") as f:
        json.dump(obj, f, indent=indent)


########################################################################################################################
#  CSV
########################################################################################################################


def read_csv_as_row_dicts(csv_path: Path) -> List[Dict[str, str]]:
    """
    Reads .csv file as a List of 'row-Dicts' (row_dicts)
        - The returned row_dicts will be a List with one element for each line.
        - Each element of this list will be a dictionary mapping the relevant 'Column Header' to the value in that
          column for the given row as a string

    Example:

    ```text
        As .csv:  >>  As Spreadsheet:  >>  As as returned "row_dicts":
        --------  >>  ---------------  >>  ------------------------
        Foo,Bar   >>  |Foo|Bar|        >>  [
        abc,123   >>  +---+---+        >>      {
        3.1,$%^   >>  |abc|123|        >>          'Foo': 'abc',
                  >>  +---+---+        >>          'Bar': '123'
                  >>  |3.1|$%^|        >>      },
                  >>                   >>      {
                  >>                   >>          'Foo': '3.1',
                  >>                   >>          'Bar': '$%^'
                  >>                   >>      }
                  >>                   >>  ]
    ```
    """
    assert isinstance(csv_path, Path), f"Expected pathlib.Path object from {csv_path=}, got {type(csv_path)=}"
    assert csv_path.is_file(), csv_path
    return list(csv.DictReader(open(csv_path, encoding="utf-8", newline=""), dialect="excel"))


def write_csv_from_row_dicts(
    row_dicts: List[Dict[Any, Any]], csv_path: Path, ordered_headers: Optional[List[str]] = None
) -> None:
    assert isinstance(csv_path, Path), f"Expected pathlib.Path object from {csv_path=}, got {type(csv_path)=}"
    assert isinstance(row_dicts, list), f"Expected list object from {row_dicts=}, got {type(row_dicts)=}"

    # Build ordered_fieldname_dict (Dicts maintain insert order - Python 3.7+)
    ordered_fieldname_dict: dict = {}

    # Add ordered headers first
    if ordered_headers:
        for header in ordered_headers:
            ordered_fieldname_dict[header] = None

    # Add all other "unordered" headers
    for row_dict in row_dicts:
        for key in row_dict.keys():
            ordered_fieldname_dict[key] = None

    # Create parent dir if needed
    csv_path.parent.mkdir(exist_ok=True, parents=True)

    # Write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=ordered_fieldname_dict.keys())
        dict_writer.writeheader()
        dict_writer.writerows(row_dicts)


def write_csv_from_concatenated_csvs(csv_paths: List[Path], out_csv_path: Path):
    """
    Write a new .csv file to `out_csv_path` that is the concatenation of all the .csv files in `csv_paths`.
    Include the header from only the first .csv file.
    """
    out_csv_path.parent.mkdir(exist_ok=True, parents=True)

    # Track whether the first file is being processed
    is_first_file = True

    with open(out_csv_path, "w", encoding="utf-8", newline="") as out_csv:
        for csv_path in csv_paths:
            with open(csv_path, "r", encoding="utf-8", newline="") as in_csv:
                # Read the file's lines
                lines = in_csv.readlines()

                # If it's the first file, write all lines (including the header)
                if is_first_file:
                    out_csv.writelines(lines)
                    # Subsequent files will no longer be considered the first
                    is_first_file = False
                else:
                    # For subsequent files, skip the first line (header) and write the rest
                    out_csv.writelines(lines[1:])
