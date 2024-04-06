# import csv
# from pathlib import Path
# import pprint
# import re
# from typing import Dict, List, Optional
# from semo_transfer_data_post_process_tools.utils import file_sys_utils
# from semo_transfer_data_post_process_tools.utils import file_io_utils
# from semo_transfer_data_post_process_tools.utils.file_io_utils import delete_last_n_lines_from_txt
# from semo_transfer_data_post_process_tools.utils.html_io_utils import read_soup_from_html_file
# import csv
# from pathlib import Path
# from typing import List, Dict


# def _parse_init_course_str(course_str: str) -> None:
#     def _add_space_before_first_digit(s):
#         return re.sub(r"(\D)(\d)", r"\1 \2", s)

#     def _contains_alpha(s):
#         return any(c.isalpha() for c in s)

#     def _contains_alpha_and_digit(s):
#         return any(c.isalpha() or c.isdigit() for c in s)

#     if " " not in course_str:
#         og_course_str = course_str
#         print(f"No space found in {course_str=}, attempting to add space before first digit...")
#         course_str = _add_space_before_first_digit(course_str)
#         if " " not in course_str or not _contains_alpha(course_str):
#             raise NotImplementedError(f"Dont know how to deal with:{course_str=}, {og_course_str=}")

#     # THRA257 CREATIVE AWARENESS (2) -> THRA 257 CREATIVE AWARENESS (2)
#     lead_str = course_str.split(" ")[0]
#     without_lead_str = course_str[len(lead_str) :]
#     if _contains_alpha_and_digit(lead_str):
#         new_lead_str = _add_space_before_first_digit(lead_str)
#         course_str = new_lead_str + without_lead_str

#     # print(f"Parsing {course_str=}...")
#     course_dept = course_str.split(" ")[0]
#     course_num = course_str.split(" ")[1]

#     # If has hours
#     if "(" in course_str:
#         course_name = " ".join(course_str.split(" ")[2:-1])
#         course_hours = course_str.split(" ")[-1].strip("()")
#     else:
#         course_name = " ".join(course_str.split(" ")[2:])
#         course_hours = ""
#     # course_name = " ".join(course_str.split(" ")[2:-1])
#     # course_hours = course_str.split(" ")[-1].strip("()")
#     return course_dept, course_num, course_name, course_hours


# class _InitHtmlTableRow:
#     def __init__(self, init_html_table_row_dict: Dict[str, str]):
#         self.inst_name = list(init_html_table_row_dict.keys())[0]
#         self.init_inst_course = init_html_table_row_dict[self.inst_name]
#         self.init_semo_course = init_html_table_row_dict["SOUTHEAST MISSOURI STATE UNIVERSITY"]
#         self.init_note = init_html_table_row_dict["Note?"]
#         self.init_begin = init_html_table_row_dict["Begin"]
#         self.init_end = init_html_table_row_dict["End"]

#         self._parse_init_inst_course()
#         self._parse_init_semo_course()

#     def get_row_dict(self) -> Dict[str, Optional[str]]:
#         semo_course_1_dept_num = self.semo_course_1_dept + self.semo_course_1_num
#         semo_course_2_dept_num = None
#         if self.semo_course_2_dept:
#             semo_course_2_dept_num = self.semo_course_2_dept + self.semo_course_2_num
#         row_dict = {
#             "institution_name": self.inst_name,
#             "inst_course_dept": self.inst_course_dept,
#             "inst_course_num": self.inst_course_num,
#             "inst_course_name": self.inst_course_name,
#             "inst_course_hours": self.inst_course_hours,
#             "semo_course_1_dept": self.semo_course_1_dept,
#             "semo_course_1_num": self.semo_course_1_num,
#             "semo_course_1_dept_num": semo_course_1_dept_num,
#             "semo_course_1_name": self.semo_course_1_name,
#             "semo_course_1_hours": self.semo_course_1_hours,
#             "semo_course_2_dept": self.semo_course_2_dept,
#             "semo_course_2_num": self.semo_course_2_num,
#             "semo_course_2_dept_num": semo_course_2_dept_num,
#             "semo_course_2_name": self.semo_course_2_name,
#             "semo_course_2_hours": self.semo_course_2_hours,
#             "note": self.init_note,
#             "begin": self.init_begin,
#             "end": self.init_end,
#         }
#         return row_dict

#     def _parse_init_inst_course(self) -> None:
#         """
#         Example #1:
#             Start:
#                 self.init_inst_course = ASB 305 POVERTY AND GLOBAL HEALTH (3)
#             End:
#                 self.inst_course_dept = ASB
#                 self.inst_course_num = 305
#                 self.inst_course_name = POVERTY AND GLOBAL HEALTH
#                 self.inst_course_hours = 3
#         Example #2:
#             Start:
#                 self.init_inst_course = "COM 312 COMMUNICATION, CONFLICT, AND NEGOTIATION (3)"
#             End:
#                 self.inst_course_dept = COM
#                 self.inst_course_num = 312
#                 self.inst_course_name = COMMUNICATION, CONFLICT, AND NEGOTIATION
#                 self.inst_course_hours = 3
#         """
#         self.inst_course_dept, self.inst_course_num, self.inst_course_name, self.inst_course_hours = (
#             _parse_init_course_str(self.init_inst_course)
#         )

#     def _parse_init_semo_course(self) -> None:
#         """
#         Example #1:
#             Start:
#                 self.init_semo_course = BS 108 BIOLOGY FOR LIVING (3)
#             End:
#                 self.semo_course_1_dept = BS
#                 self.semo_course_1_num = 108
#                 self.semo_course_1_name = BIOLOGY FOR LIVING
#                 self.semo_course_1_hours = 3
#                 self.semo_course_2_dept = None
#                 self.semo_course_2_num = None
#                 self.semo_course_2_name = None
#                 self.semo_course_2_hours = None
#         Example #2:
#             Start:
#                 self.init_inst_course = GE 124 ELECTIVE
#             End:
#                 self.semo_course_1_dept = GE
#                 self.semo_course_1_num = 124
#                 self.semo_course_1_name = ELECTIVE
#                 self.semo_course_1_hours = None
#                 self.semo_course_2_dept = None
#                 self.semo_course_2_num = None
#                 self.semo_course_2_name = None
#                 self.semo_course_2_hours = None
#         Example #3:
#             Start:
#                 self.init_semo_course = CH 184 GENERAL CHEMISTRY I LABORATORY (1)CH 185 GENERAL CHEMISTRY I (3)
#             End:
#                 self.semo_course_1_dept = CH
#                 self.semo_course_1_num = 184
#                 self.semo_course_1_name = GENERAL CHEMISTRY I LABORATORY
#                 self.semo_course_1_hours = 1
#                 self.semo_course_2_dept = CH
#                 self.semo_course_2_num = 185
#                 self.semo_course_2_name = GENERAL CHEMISTRY I
#                 self.semo_course_2_hours = 3
#         """
#         course_strs = []
#         # Build course_strs
#         s_strs = self.init_semo_course.split(")")
#         assert len(s_strs) < 4, f"Need more than 2 semo courses? {self.init_semo_course=}, {s_strs=}"

#         if len(s_strs) == 1:
#             course_strs.append(self.init_semo_course)
#         elif len(s_strs) == 2:
#             course_strs.append(s_strs[0] + ")")
#         elif len(s_strs) == 3:
#             course_strs.append(s_strs[0] + ")")
#             course_strs.append(s_strs[1] + ")")

#         # Set for semo course 1
#         self.semo_course_1_dept, self.semo_course_1_num, self.semo_course_1_name, self.semo_course_1_hours = (
#             _parse_init_course_str(course_strs[0])
#         )

#         # Set for semo course 2
#         if len(course_strs) == 2:
#             self.semo_course_2_dept, self.semo_course_2_num, self.semo_course_2_name, self.semo_course_2_hours = (
#                 _parse_init_course_str(course_strs[1])
#             )
#         else:
#             self.semo_course_2_dept = None
#             self.semo_course_2_num = None
#             self.semo_course_2_name = None
#             self.semo_course_2_hours = None


# def _get_out_csv_path(html_path: Path, out_dir_path: Path) -> Path:
#     """
#     Example:
#     Input: inst_list_page_2__inst_gdvInstWithEQ_btnCreditFromInstName_6__equiv_list_page_1.html
#     Output: inst_list_page_2__inst_gdvInstWithEQ_btnCreditFromInstName_6__equiv_list.csv
#     """
#     html_file_name = html_path.name
#     prefix = html_file_name.split("__equiv_list_page")[0]
#     csv_file_name = f"{prefix}__equiv_list.csv"
#     return out_dir_path / csv_file_name


# def _equiv_list_html_to_init_html_table_row_dicts(in_html_path: Path) -> List[Dict[str, str]]:
#     soup = read_soup_from_html_file(in_html_path)
#     rows = []

#     # Assuming data is in table rows after header in a table with class 'table'
#     table = soup.find("table", class_="table")
#     if not table:
#         raise ValueError(f"No table with class 'table' found in {in_html_path}")

#     headers = [th.get_text(strip=True) for th in table.find_all("th")]
#     for row_num, row in enumerate(table.find_all("tr")[1:]):  # Skip header row
#         cols = row.find_all(["td", "th"])
#         if len(cols) != len(headers):
#             continue  # Skip rows that don't have enough columns
#         row_data = {}
#         for i, col_and_header in enumerate(zip(cols, headers)):
#             col, header = col_and_header
#             row_data[header] = col.get_text(strip=True)
#         rows.append(row_data)

#     if len(rows) == 0:
#         return []

#     # If have extra row for pagination, remove it
#     if rows[-1]["SOUTHEAST MISSOURI STATE UNIVERSITY"].isdigit():
#         # if len(rows) == 52:
#         return rows[1:-1]

#     return rows[1:]


# def all_equiv_list_html_to_csv(in_dir_path: Path, out_dir_path: Path) -> None:
#     """
#     Convert all html files in in_dir_path to csv files in out_dir_path
#     :param in_dir_path: input directory containing html files
#     :param out_dir_path: output directory to contain csv files
#     :return: None
#     """
#     print("Deleting if exists:", out_dir_path)
#     file_sys_utils.delete_if_exists(out_dir_path)

#     for html_path in file_sys_utils.get_abs_path_generator_to_child_files_no_recurs(in_dir_path):
#         out_csv_path = _get_out_csv_path(html_path, out_dir_path)

#         print(f"Converting {html_path} to {out_csv_path}...")
#         init_html_table_row_dicts = _equiv_list_html_to_init_html_table_row_dicts(in_html_path=html_path)

#         # Build row_dicts
#         row_dicts = []
#         for init_html_table_row_dict in init_html_table_row_dicts:
#             row_dict = _InitHtmlTableRow(init_html_table_row_dict).get_row_dict()
#             if row_dict["semo_course_1_name"] == "DOES NOT TRANSFER":
#                 continue
#             row_dicts.append(row_dict)

#         # Create new or append to existing csv
#         if out_csv_path.exists():
#             existing_row_dicts = file_io_utils.read_csv_as_row_dicts(out_csv_path)
#             row_dicts = existing_row_dicts + row_dicts
#         else:
#             file_io_utils.write_csv_from_row_dicts(row_dicts, out_csv_path, ordered_headers=None)
#         # file_io_utils.write_csv_from_row_dicts(row_dicts, out_csv_path, ordered_headers=None)
