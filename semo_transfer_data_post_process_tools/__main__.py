import csv
from pathlib import Path

# from semo_transfer_data_post_process_tools._easy_csv_db import EasyCsvDb
# from semo_transfer_data_post_process_tools._all_inst_list_html_to_csv import all_inst_list_html_to_csv
# from semo_transfer_data_post_process_tools._all_equiv_list_html_to_csv import all_equiv_list_html_to_csv
# from semo_transfer_data_post_process_tools.utils import file_sys_utils
# from semo_transfer_data_post_process_tools.utils.file_io_utils import (
#     read_csv_as_row_dicts,
#     write_csv_from_concatenated_csvs,
#     write_csv_from_row_dicts,
# )
# from .scrape_html.scrape_html import scrape_html


_SCRIPT_PARENT_DIR_PATH = Path(__file__).parent
REPO_ROOT_DIR_PATH = _SCRIPT_PARENT_DIR_PATH.parent
WORK_DIR_PATH = REPO_ROOT_DIR_PATH / "work"
OUT_DIR_PATH = REPO_ROOT_DIR_PATH / "outputs"


# def _concat_csvs_in_dir(in_dir_path, out_csv_path: Path):
#     csv_paths = file_sys_utils.get_abs_paths_to_child_files_no_recurs(in_dir_path)
#     print(f"Concatenating all equivalency list csvs into {out_csv_path}...")
#     write_csv_from_concatenated_csvs(csv_paths, out_csv_path)


# # print("Step #1 - Scraping HTML...")
# # scrape_html(WORK_INST_LIST_HTML_DOWNLOADS_DIR_PATH, WORK_EQUIV_LIST_HTML_DOWNLOADS_DIR_PATH)

# # print("Step #2 - Converting Institution List HTMLs to CSVs...")
# # all_inst_list_html_to_csv(WORK_INST_LIST_HTML_DOWNLOADS_DIR_PATH, WORK_INST_LIST_CSVS_DIR_PATH)

# # print("Step #3 - Converting Equivalency List HTMLs to CSVs...")
# # all_equiv_list_html_to_csv(WORK_EQUIV_LIST_HTML_DOWNLOADS_DIR_PATH, WORK_EQUIV_LIST_CSVS_DIR_PATH)

# # print("Step #4 - Concatenating all equivalency list csvs by inst...")
# # _concat_csvs_in_dir(WORK_EQUIV_LIST_CSVS_DIR_PATH, WORK_CONCATENATED_EQUIV_LIST_CSV_PATH)

# # print("Step #5 - Concatenating all inst list csvs...")
# # _concat_csvs_in_dir(WORK_INST_LIST_CSVS_DIR_PATH, WORK_CONCATENATED_INST_LIST_CSV_PATH)

# print("Step #6 - Joining institutions and equivalencies...")
# # Full inner and outer join of the equiv_table and inst_table by using the institution_name
# # field - the values of the inst_table should come after that of the equiv_table
# db = EasyCsvDb()
# db.create_table_from_csv(WORK_CONCATENATED_INST_LIST_CSV_PATH, "inst_table")
# db.create_table_from_csv(WORK_CONCATENATED_EQUIV_LIST_CSV_PATH, "equiv_table")
# df = db.query(
#     """
#     SELECT * FROM inst_table
#     JOIN equiv_table
#     ON inst_table.institution_name = equiv_table.institution_name
# """
# )
# print(f"Writing {OUT_TRANSFERS_FULL_CSV_PATH=}...")
# df.to_csv(OUT_TRANSFERS_FULL_CSV_PATH, index=False)

# print("Step #7 - Creating No-Elective version...")
# full_row_dicts = read_csv_as_row_dicts(OUT_TRANSFERS_FULL_CSV_PATH)
# no_elective_row_dicts = [row_dict for row_dict in full_row_dicts if "ELECTIVE" not in row_dict["semo_course_1_name"]]
# print(f"Writing {OUT_TRANSFERS_NO_ELECTIVE_CSV_PATH=}...")
# write_csv_from_row_dicts(no_elective_row_dicts, OUT_TRANSFERS_NO_ELECTIVE_CSV_PATH)
