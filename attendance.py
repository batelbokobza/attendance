import csv
import re
from collections import defaultdict
from datetime import datetime
import database
import objects
import Constant
import response
from Server import Server


def get_csv_file_data(file_path):
    """Reading the data in the table from the file located in the requested path.
                :param file_path: (string): Path to the file from which you want to read data.
                :return:
                    list object - (list(headers, rows_data(list)))"""
    rows_data = []
    with open(file_path, 'r', encoding="utf-16", errors='ignore') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = re.split('[\t]', next(csv_reader)[0])
        for row in csv_reader:
            if len(row) == 0:
                continue
            row = re.split('[\t]', row[0])
            rows_data.append(row)
    return headers, rows_data


def get_non_overlapping_times_list(attendance_arr):
    """ Merge all overlapping intervals into one, and returns a list of time ranges with non-overlapping
        intervals only.
            :param attendance_arr: list of time ranges. Each item contains a start time and an end time.
            :return: List - (array(start, end)):  list of time ranges with non-overlapping intervals only. """
    attendance_arr.sort(key=lambda start: start[0])  # Sort by the start of the time range.
    index1 = 0
    for index2 in range(1, len(attendance_arr)):  # Merge previous and current time Intervals.
        if attendance_arr[index1][1] >= attendance_arr[index2][0]:
            attendance_arr[index1][1] = max(attendance_arr[index1][1], attendance_arr[index2][1])
        else:
            index1 = index1 + 1
            attendance_arr[index1] = attendance_arr[index2]
    non_overlapping_times_list = [(attendance_arr[t][0], attendance_arr[t][1]) for t in range(index1 + 1)]
    return non_overlapping_times_list


def get_sum_total_minutes(time_ranges_arr):
    """ Getting the number of minutes from an array containing time ranges.
            :param time_ranges_arr: (array(start, end)): array containing time ranges.
            :return: minutes number - (float) """
    sum_total_minutes = 0
    for start, end in time_ranges_arr:
        total_meeting_time = datetime.strptime(str(end), '%H:%M:%S') - datetime.strptime(str(start), '%H:%M:%S')
        sum_total_minutes += (total_meeting_time.total_seconds() / 60)
    return round(sum_total_minutes, 2)


def create_attendance_ranges_by_emails(participant_obj_list):
    """ Creating and return a dictionary containing the all attendance times for each unique email.
            :param participant_obj_list: A list of "participant" type objects containing all user data.
            :return: email_and_ranges_time - (default-dict(list)) """
    email_and_ranges_time = defaultdict(list)
    for participant in participant_obj_list:
        email_and_ranges_time[participant.EMAIL].append([participant.JOIN_TIME, participant.LEAVE_TIME])
    return email_and_ranges_time


def get_emails_and_attendance_minutes(participant_obj_list):
    """ Creating and return a dictionary containing the number of attendance minutes for each unique email.
        * The calculation of attendance minutes takes into account and handles cases of time overlap.
            :param participant_obj_list: A list of "participant" type objects containing all user data.
            :return: names_and_attendance_minutes - (dict(email, attendance minutes)) """
    names_and_attendance_minutes = dict()
    all_names_and_ranges = create_attendance_ranges_by_emails(participant_obj_list)
    for email, range_times in all_names_and_ranges.items():
        non_overlapping_times = get_non_overlapping_times_list(range_times)
        names_and_attendance_minutes[email] = get_sum_total_minutes(non_overlapping_times)
    return names_and_attendance_minutes


def get_date_and_time_from_string(str_datetime):
    """ Convert a string containing a date and time to a datetime object.
            :param str_datetime: (string): string containing a date and time.
            :return: list object - (list(date, time)) """
    date_and_time = re.split('["]', str_datetime)[3]
    datetime_object = datetime.strptime(date_and_time, "%Y-%m-%d %H:%M:%S")
    return datetime_object.date(), datetime_object.time()


def is_valid_email(email):
    valid_characters = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(valid_characters, email)


class Attendance:

    def __init__(self):
        self.db = database.DataBase()
        self.server = Server(Constant.REMOTE_DIRECTORY_PATH, Constant.LOCAL_DIRECTORY_PATH)
        self.file_names_list = self.server.get_csv_file_names_list_from_remote_host()  # Files list without duplicates.
        self.names_and_emails = defaultdict(set)
        self.emails_and_attendance_minutes = defaultdict(lambda: 0)
        self.total_meetings_minutes = 0
        self.response = None

    def prepare_database(self):
        self.db.create_participant_data_table()
        self.db.create_emails_and_attendance_data_table()
        self.db.create_name_and_emails_table()
        self.db.create_attendance_table()

        self.calculate_attendance_data(Constant.LOCAL_DIRECTORY_PATH)
        self.add_attendance_data_to_database()

    def calculate_attendance_data(self, dir_path):
        """Calculation of attendance data from the data in the file."""
        rows_number = 0
        header_columns, data_rows, meetings_time = [], [], []
        for file_name in self.file_names_list:
            header_columns, data_rows = get_csv_file_data(dir_path + '/' + file_name)  # from file current
            participant_obj_list = self.get_valid_participant_obj_list(data_rows)
            meetings_time.append([participant_obj_list[0].MEETING_START_TIME, participant_obj_list[0].MEETING_END_TIME])
            rows_number += self.add_data_rows_from_csv(rows_number, participant_obj_list)
            for email, attendance_minutes in get_emails_and_attendance_minutes(participant_obj_list).items():
                self.emails_and_attendance_minutes[email] += attendance_minutes
            for row in data_rows:
                self.names_and_emails[row[3].title()].add(row[4].capitalize())  # row[3] = name and row[4] = email
        self.total_meetings_minutes = get_sum_total_minutes(meetings_time)

    def get_valid_participant_obj_list(self, data_rows):
        """Creating and receiving a valid list of the participants and participants data that appear in the current
            file that is reading."""
        participant_obj_list = []
        for row in data_rows:
            if len(row) == Constant.NUM_DATA_ITEMS_IN_ROW and '' not in row:
                m_date, m_start_time = get_date_and_time_from_string(row[1])
                m_end_time = str(get_date_and_time_from_string(row[2])[1])
                m_name, p_name, p_email, p_attendance, conn_type = str(row[0]), row[3], row[4], row[7], row[8]
                if not is_valid_email(p_email):
                    continue
                join_t = str(get_date_and_time_from_string(row[5])[1])
                leave_t = str(get_date_and_time_from_string(row[6])[1])
                participant_obj = objects.ParticipantDataObj(m_name, str(m_date), str(m_start_time), m_end_time, p_name,
                                                             p_email.capitalize(), join_t, leave_t, p_attendance,
                                                             conn_type)
                participant_obj_list.append(participant_obj)
        return participant_obj_list

    def add_data_rows_from_csv(self, rows_number, participant_obj_list):
        """Adding the participants' data to the database."""
        for participant in participant_obj_list:
            rows_number += 1
            self.db.add_participants_data((rows_number,) + participant.get_data_in_tuple_object())
        return rows_number

    def add_attendance_data_to_database(self):
        """Adding the calculated attendance data to the database."""
        index = 0
        for name, emails in self.names_and_emails.items():
            for email in list(emails):
                index += 1
                self.db.add_name_and_emails_data(index, name, email)
                attendance_by_email = self.emails_and_attendance_minutes[email]
                attendance_percentage = str(round((attendance_by_email / self.total_meetings_minutes) * 100, 2)) + " %"
                str_attendance_by_email = str(round(attendance_by_email, 2)) + " mins"
                attendance_data = objects.AttendanceDataObj(name, str_attendance_by_email, attendance_percentage, email)
                self.db.add_attendance_data((index,) + attendance_data.get_data_in_tuple_object())
                if not self.db.is_email_exist(email):
                    self.db.add_emails_and_attendance_data(email, str_attendance_by_email, attendance_percentage)

    def calculate_attendance(self, type_request, user_input=None):
        """Request to receive response data for the user's request.
            The request will be made after checking the correctness of the input if it exists.
                    :param type_request: int:  request number from constant according to the user's request selection.
                    :param user_input: (string): optional parameter. user input if required by the type of request.
                    :return:
                        list object - (response number, response data)"""
        if not self.db.is_database_exist():
            self.prepare_database()
        if type_request == Constant.Request.Type.BY_NAME and not self.db.is_name_participant_exist(user_input.title()):
            raise NameError("The name does not exist.")
        elif type_request == Constant.Request.Type.BY_EMAIL and not self.db.is_email_participant_exist(
                user_input.capitalize()):
            raise NameError("The email does not exist.")
        self.response = response.Response(self.db, type_request, user_input)
        response_number, response_data = self.response.get_response()
        return response_number, response_data

    def data_reset(self):
        """Deleting all data in the database."""
        self.db.delete_all_database()



