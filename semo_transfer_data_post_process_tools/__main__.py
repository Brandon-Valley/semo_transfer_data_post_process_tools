import csv
from pathlib import Path
from pprint import pprint
from typing import OrderedDict

from semo_transfer_data_post_process_tools._easy_csv_db import EasyCsvDb
from semo_transfer_data_post_process_tools.utils import file_io_utils


_SCRIPT_PARENT_DIR_PATH = Path(__file__).parent
REPO_ROOT_DIR_PATH = _SCRIPT_PARENT_DIR_PATH.parent
WORK_DIR_PATH = REPO_ROOT_DIR_PATH / "work"
OUT_DIR_PATH = REPO_ROOT_DIR_PATH / "outputs"
IN_DIR_PATH = REPO_ROOT_DIR_PATH / "inputs"

OUT_FULL_JOIN_CSV_PATH = Path(OUT_DIR_PATH / "full_join.csv")

INPUT_SEMO_CLASS_LAYOUT_CSV_PATH = Path(IN_DIR_PATH / "SEMO Class Layout - Working Courses.csv")

INPUT_SEMO_TRANSFER_COURSE_EQUIVALENCIES_NO_ELECTIVES_CSV_PATH = Path(
    "C:/p/semo_transfer_data_downloader/outputs/semo_transfer_course_equivalencies_no_electives.csv"
)


def _write_full_join_csv(dest_csv_path: Path) -> None:
    semo_transfer_course_equivalencies_no_electives_csv_path = (
        INPUT_SEMO_TRANSFER_COURSE_EQUIVALENCIES_NO_ELECTIVES_CSV_PATH
    )
    semo_class_layout_csv_path = INPUT_SEMO_CLASS_LAYOUT_CSV_PATH

    db = EasyCsvDb()
    db.create_table_from_csv(
        semo_transfer_course_equivalencies_no_electives_csv_path, table_name="semo_transfer_course_equiv"
    )
    db.create_table_from_csv(semo_class_layout_csv_path, table_name="semo_class_layout")

    # Return everything from full join:
    #   - semo_transfer_course_equiv.semo_course_1_dept_num == semo_class_layout.'Class #' and order by Class #
    cursor = db.connection.execute(
        """
        SELECT * FROM semo_transfer_course_equiv
        JOIN semo_class_layout
        ON semo_transfer_course_equiv.semo_course_1_dept_num = semo_class_layout."Class #"
        ORDER BY "Class #";
        """
    )

    # Write the full join to a CSV file
    print(f"Writing full join to: {dest_csv_path}...")
    file_io_utils.write_csv_from_sqlite3_cursor(cursor, dest_csv_path)


def _get_institutions_by_semo_course_num(in_csv_path: Path):
    row_dicts = file_io_utils.read_csv_as_row_dicts(in_csv_path)
    institutions_by_semo_course_num = {}
    for row_dict in row_dicts:
        semo_course_num = row_dict["Class #"]
        institution = row_dict["institution_name"]
        if semo_course_num not in institutions_by_semo_course_num:
            institutions_by_semo_course_num[semo_course_num] = []
        institutions_by_semo_course_num[semo_course_num].append(institution)
    return institutions_by_semo_course_num


def _get_occurrences_by_institution(institutions_by_semo_course_num):
    occurrences_by_institution = {}
    for semo_course_num, institutions in institutions_by_semo_course_num.items():
        for institution in institutions:
            if institution not in occurrences_by_institution:
                occurrences_by_institution[institution] = 0
            occurrences_by_institution[institution] += 1
    return occurrences_by_institution


def _get_ordered_occurrences_by_institution(occurrences_by_institution) -> OrderedDict:
    return OrderedDict(sorted(occurrences_by_institution.items(), key=lambda item: item[1], reverse=True))


_write_full_join_csv(OUT_FULL_JOIN_CSV_PATH)
institutions_by_semo_course_num = _get_institutions_by_semo_course_num(OUT_FULL_JOIN_CSV_PATH)
print("institutions_by_semo_course_num:")
pprint(institutions_by_semo_course_num)

occurrences_by_institution = _get_occurrences_by_institution(institutions_by_semo_course_num)
print("occurrences_by_institution:")
pprint(occurrences_by_institution)

ordered_occurrences_by_institution = _get_ordered_occurrences_by_institution(occurrences_by_institution)
print("ordered_occurrences_by_institution:")
pprint(ordered_occurrences_by_institution)

print("Writing ordered_occurrences_by_institution to JSON...")
file_io_utils.write_json(
    ordered_occurrences_by_institution, Path(OUT_DIR_PATH / "ordered_occurrences_by_institution.json")
)
