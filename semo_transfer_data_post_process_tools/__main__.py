import csv
from pathlib import Path

from semo_transfer_data_post_process_tools._easy_csv_db import EasyCsvDb


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
    #   - semo_transfer_course_equiv.semo_course_1_dept_num == semo_class_layout.'Class #'
    cursor = db.connection.execute(
        """
        SELECT * FROM semo_transfer_course_equiv
        JOIN semo_class_layout
        ON semo_transfer_course_equiv.semo_course_1_dept_num = semo_class_layout."Class #";
        """
    )

    # Write the full join to a CSV file
    print(f"Writing full join to: {dest_csv_path}...")
    dest_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_csv_path, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([description[0] for description in cursor.description])
        csv_writer.writerows(cursor.fetchall())


_write_full_join_csv(OUT_FULL_JOIN_CSV_PATH)
