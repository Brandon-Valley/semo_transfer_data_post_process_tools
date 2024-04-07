import csv
from pathlib import Path
from pprint import pprint
from typing import OrderedDict
from datetime import datetime

from semo_transfer_data_post_process_tools._easy_csv_db import EasyCsvDb
from semo_transfer_data_post_process_tools.utils import file_io_utils


_SCRIPT_PARENT_DIR_PATH = Path(__file__).parent
REPO_ROOT_DIR_PATH = _SCRIPT_PARENT_DIR_PATH.parent
WORK_DIR_PATH = REPO_ROOT_DIR_PATH / "work"
OUT_DIR_PATH = REPO_ROOT_DIR_PATH / "outputs"
IN_DIR_PATH = REPO_ROOT_DIR_PATH / "inputs"

datetime_str = datetime.now().strftime("%Y-%m-%d")

OUT_FULL_JOIN_CSV_PATH = Path(OUT_DIR_PATH / f"transferable_courses_tool_as_of_{datetime_str}.csv")

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


def _get_institutions_by_offered_semo_course_num(in_csv_path: Path):
    row_dicts = file_io_utils.read_csv_as_row_dicts(in_csv_path)
    institutions_by_offered_semo_course_num = {}
    for row_dict in row_dicts:
        semo_course_num = row_dict["Class #"]
        institution = row_dict["institution_name"]
        if semo_course_num not in institutions_by_offered_semo_course_num:
            institutions_by_offered_semo_course_num[semo_course_num] = []
        institutions_by_offered_semo_course_num[semo_course_num].append(institution)
    return institutions_by_offered_semo_course_num


def _get_total_semo_courses_offered_at_this_institution_by_institution(institutions_by_offered_semo_course_num):
    total_semo_courses_offered_at_this_institution_by_institution = {}
    for semo_course_num, institutions in institutions_by_offered_semo_course_num.items():
        for institution in institutions:
            if institution not in total_semo_courses_offered_at_this_institution_by_institution:
                total_semo_courses_offered_at_this_institution_by_institution[institution] = 0
            total_semo_courses_offered_at_this_institution_by_institution[institution] += 1
    return total_semo_courses_offered_at_this_institution_by_institution


def _get_num_institutions_that_have_course_by_course_num(institutions_by_offered_semo_course_num):
    num_institutions_that_have_course_by_course_num = {}
    for semo_course_num, institutions in institutions_by_offered_semo_course_num.items():
        num_institutions_that_have_course_by_course_num[semo_course_num] = len(institutions)
    return num_institutions_that_have_course_by_course_num


def _get_ordered_total_semo_courses_offered_at_this_institution_by_institution(
    total_semo_courses_offered_at_this_institution_by_institution,
) -> OrderedDict:
    return OrderedDict(
        sorted(
            total_semo_courses_offered_at_this_institution_by_institution.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )


_write_full_join_csv(OUT_FULL_JOIN_CSV_PATH)
institutions_by_offered_semo_course_num = _get_institutions_by_offered_semo_course_num(OUT_FULL_JOIN_CSV_PATH)
print("institutions_by_offered_semo_course_num:")
pprint(institutions_by_offered_semo_course_num)

total_semo_courses_offered_at_this_institution_by_institution = (
    _get_total_semo_courses_offered_at_this_institution_by_institution(institutions_by_offered_semo_course_num)
)
print("total_semo_courses_offered_at_this_institution_by_institution:")
pprint(total_semo_courses_offered_at_this_institution_by_institution)

ordered_total_semo_courses_offered_at_this_institution_by_institution = (
    _get_ordered_total_semo_courses_offered_at_this_institution_by_institution(
        total_semo_courses_offered_at_this_institution_by_institution
    )
)
print("ordered_total_semo_courses_offered_at_this_institution_by_institution:")
pprint(ordered_total_semo_courses_offered_at_this_institution_by_institution)

print("Writing ordered_total_semo_courses_offered_at_this_institution_by_institution to JSON...")
file_io_utils.write_json(
    ordered_total_semo_courses_offered_at_this_institution_by_institution,
    Path(OUT_DIR_PATH / "ordered_total_semo_courses_offered_at_this_institution_by_institution.json"),
)

num_institutions_that_have_course_by_course_num = _get_num_institutions_that_have_course_by_course_num(
    institutions_by_offered_semo_course_num
)
print("num_institutions_that_have_course_by_course_num:")
pprint(num_institutions_that_have_course_by_course_num)

sorted_num_institutions_that_have_course_by_course_num = OrderedDict(
    sorted(num_institutions_that_have_course_by_course_num.items(), key=lambda item: item[1], reverse=True)
)

print("sorted_num_institutions_that_have_course_by_course_num:")
pprint(sorted_num_institutions_that_have_course_by_course_num)

file_io_utils.write_json(
    sorted_num_institutions_that_have_course_by_course_num,
    Path(OUT_DIR_PATH / "sorted_num_institutions_that_have_course_by_course_num.json"),
)


# Add occurrences to the full join CSV
full_join_row_dicts = file_io_utils.read_csv_as_row_dicts(OUT_FULL_JOIN_CSV_PATH)
for row_dict in full_join_row_dicts:
    semo_course_num = row_dict["Class #"]
    institutions = institutions_by_offered_semo_course_num[semo_course_num]
    occurrences = len(institutions)
    row_dict["total_semo_courses_offered_at_this_institution"] = occurrences
file_io_utils.write_csv_from_row_dicts(
    full_join_row_dicts, OUT_FULL_JOIN_CSV_PATH, ordered_headers=["total_semo_courses_offered_at_this_institution"]
)

# Add sorted_num_institutions_that_have_course_by_course_num to the full join CSV
full_join_row_dicts = file_io_utils.read_csv_as_row_dicts(OUT_FULL_JOIN_CSV_PATH)
for row_dict in full_join_row_dicts:
    semo_course_num = row_dict["Class #"]
    num_institutions = num_institutions_that_have_course_by_course_num[semo_course_num]
    row_dict["total_institutions_offering_this_semo_course"] = num_institutions
file_io_utils.write_csv_from_row_dicts(
    full_join_row_dicts,
    OUT_FULL_JOIN_CSV_PATH,
    ordered_headers=["total_institutions_offering_this_semo_course"],
)

# Order full join CSV by "Class #" then by "occurrences" (total_semo_courses_offered_at_this_institution) then by "total_semo_courses_offered_at_this_institution"
full_join_row_dicts = file_io_utils.read_csv_as_row_dicts(OUT_FULL_JOIN_CSV_PATH)
full_join_row_dicts.sort(
    key=lambda x: (
        -int(x["total_institutions_offering_this_semo_course"]),
        -int(x["total_semo_courses_offered_at_this_institution"]),
        x["Class #"],
    )
)
file_io_utils.write_csv_from_row_dicts(full_join_row_dicts, OUT_FULL_JOIN_CSV_PATH)
