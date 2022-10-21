import re
from datetime import timedelta, datetime
import Constant


class Response:

    def __init__(self, data_base, type_req, user_input=None):
        self.db = data_base
        self.type_request = type_req
        self.user_input = user_input

    def get_response(self):
        """Returning the response object.
                    :return:
                        response object - (object list(response number, response data))"""
        try:
            response = None
            if self.type_request == Constant.Request.Type.BY_NAME:
                response = self.get_response_values()
            elif self.type_request == Constant.Request.Type.BY_DATE:
                response = self.response_for_data_by_date()
            elif self.type_request == Constant.Request.Type.BY_CONNECTION_TYPE:
                response = self.response_for_data_by_connection_type()
            elif self.type_request == Constant.Request.Type.BY_EMAIL:
                response = self.get_response_values()
            elif self.type_request == Constant.Request.Type.ALL_PARTICIPANTS_DATA:
                response = self.get_response_values()
            elif self.type_request == Constant.Request.Type.ALL_MEETINGS_DATA:
                response = self.get_response_values()
            return response
        except NameError as err:
            return err

    def response_for_data_by_date(self):
        """Create the response object for a data request by date.
                    :return:
                        response object - (object list(response number, response data(tuple)))"""
        response_data = []
        date_from, date_to = self.user_input[0], self.user_input[1]
        date_curr, date_end_obj = datetime.strptime(date_from, "%Y-%m-%d"), datetime.strptime(date_to, "%Y-%m-%d")
        while date_curr <= date_end_obj:
            data = self.db.get_attendance_data_by_date(str(date_curr.date()))
            response_data.extend(self.get_response_data_list(data, 1))
            date_curr = date_curr + timedelta(days=1)
        columns_name = self.db.get_column_names_for_all_data()[1:]
        headers, unique_name_cols = self.get_headers_and_unique_name_cols(columns_name)
        return Constant.Response.Type.DATA_BY_DATE, (headers, unique_name_cols, response_data)

    def response_for_data_by_connection_type(self):
        """Create the response object for a data request by connection type.
                    :return:
                        response object - (object list(response number, response data(tuple)))"""
        if self.user_input == Constant.Request.ConnectionType.MOBILE:
            data = self.db.get_attendance_data_by_connection_type(Constant.Response.ConnectionType.MOBILE)
        else:  # if self.user_input == Constant.Request.ConnectionType.DESKTOP
            data = self.db.get_attendance_data_by_connection_type(Constant.Response.ConnectionType.DESKTOP)
        response_data = self.get_response_data_list(data, 1)
        columns_name = self.db.get_column_names_for_all_data()[1:10]
        headers, unique_name_cols = self.get_headers_and_unique_name_cols(columns_name)
        return Constant.Response.Type.DATA_BY_CONNECTION_TYPE, (headers, unique_name_cols, response_data)

    def get_response_values(self):
        """Creating the response object for a data request by name, email,
            or a request to display all data/participants.
                    :return:
                        response object - (object list(response number, response data(tuple)))"""
        if self.type_request == Constant.Request.Type.BY_NAME or self.type_request == Constant.Request.Type.BY_EMAIL:
            if self.type_request == Constant.Request.Type.BY_NAME:
                data = self.db.get_attendance_data_by_name(self.user_input.title())
                res_number = Constant.Response.Type.NAME_AND_EMAIL if len(data) > 1 else Constant.Response.Type.NAME
            else:
                data = self.db.get_attendance_data_by_email(self.user_input.capitalize())
                res_number = Constant.Response.Type.DATA_BY_EMAIL
            columns_name = self.db.get_column_names_for_participant_data()
            response_data = self.get_response_data_list(data)
        else:
            if self.type_request == Constant.Request.Type.ALL_PARTICIPANTS_DATA:
                data, res_number = self.db.get_all_participants_data(), Constant.Response.Type.ALL_PARTICIPANTS_DATA
                columns_name = self.db.get_column_names_for_participant_data()[1:]
            else:  # case is self.type_request = Constant.Request.Type.ALL_MEETINGS_DATA
                data, res_number = self.db.get_all_database(), Constant.Response.Type.ALL_MEETINGS_DATA
                columns_name = self.db.get_column_names_for_all_data()[1:]
            response_data = self.get_response_data_list(data, 1)

        headers, unique_name_cols = self.get_headers_and_unique_name_cols(columns_name)
        return res_number, (headers, unique_name_cols, response_data)

    def get_response_data_list(self, data, start_index=0):
        """Creating a list containing the requested data.
                    :param start_index: (int): An index containing the number of the column from which we would like
                                    to append the data into the list. default value = 0.
                    :param data: Data from the database.
                    :return:
                        response_data - (list) - List of data from the database."""
        response_data = []
        for row in data:
            # res = objects.AttendanceDataObj(*row[1:]) , append (list(get_data_in_tuple_object(row[1:]))
            res = row[start_index:]
            response_data.append(list(res))
        return response_data

    def get_headers_and_unique_name_cols(self, columns_name):
        """Creating a list containing the unique names column according to the user's request.
                    :param columns_name: (list): A list of column names from the database.
                    :return:
                    list object - (list(List of names for the column headers, list of column names from the data))"""
        headers = []
        unique_name_cols = []
        for col_name in columns_name:
            col_name_split = re.findall('[A-Z][^A-Z]*', col_name)
            header = " ".join([str(s) for s in col_name_split])
            headers.append(header)
            unique_name_cols.append(Constant.Response.unique_name_for_columns_dict[header])
        return headers, unique_name_cols
