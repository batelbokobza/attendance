import os
import sqlite3
from sqlite3 import Error

EMPTY = 0
DATA_BASE_NAME = 'attendance.db'


class DataBase:

    def __init__(self):
        self.connect = sqlite3.connect(DATA_BASE_NAME)
        self.cursor = self.connect.cursor()  # to execute some queries after the connection.

    def create_participant_data_table(self):
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS CSVFilesData("
                                "Id INTEGER PRIMARY KEY, "
                                "MeetingName varchar(255) NOT NULL, "
                                "MeetingDate varchar(255) NOT NULL, "
                                "MeetingStartTime varchar(255) NOT NULL, "
                                "MeetingEndTime varchar(255) NOT NULL, "
                                "Name varchar(255) NOT NULL, "
                                "Email varchar(255) NOT NULL, "
                                "JoinTime varchar(255) NOT NULL, "
                                "LeaveTime varchar(255) NOT NULL, "
                                "AttendanceDuration varchar(255) NOT NULL, "
                                "ConnectionType varchar(255) NOT NULL)")
            self.connect.commit()
        except Error:
            print(Error)

    def create_attendance_table(self):
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Attendance("
                                "Id INTEGER PRIMARY KEY, "
                                "Name varchar(255) NOT NULL, "
                                "AttendanceDuration INTEGER NOT NULL, "
                                "AttendancePercentage varchar(255) NOT NULL, "
                                "Email varchar(255) NOT NULL)")
            self.connect.commit()
        except Error:
            print(Error)

    def create_name_and_emails_table(self):
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS NameAndEmails("
                                "Id INTEGER PRIMARY KEY, "
                                "Name varchar(255) NOT NULL, "
                                "Email varchar(255) NOT NULL)")
            self.connect.commit()
        except Error:
            print(Error)

    def create_emails_and_attendance_data_table(self):
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS EmailAndAttendance("
                                "Email varchar(255) PRIMARY KEY, "
                                "AttendanceDuration INTEGER NOT NULL, "
                                "AttendancePercentage varchar(255) NOT NULL)")
            self.connect.commit()
        except Error:
            print(Error)

    def get_column_names_for_participant_data(self):
        column_names = [description[0] for description in self.cursor.description]
        return column_names

    def get_column_names_for_all_data(self):
        column_names = [description[0] for description in self.cursor.description]
        return column_names

    def add_participants_data(self, data):
        self.connect.execute("INSERT INTO CSVFilesData VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        self.connect.commit()

    def get_attendance_data_by_date(self, date):
        return self.cursor.execute("SELECT * FROM CSVFilesData  "
                                   "WHERE MeetingDate = ?", (date,)).fetchall()

    def get_attendance_data_by_connection_type(self, connection_type):
        return self.cursor.execute("SELECT * FROM CSVFilesData  "
                                   "WHERE ConnectionType = ?", (connection_type,)).fetchall()

    def add_attendance_data(self, data):
        self.connect.execute("INSERT INTO Attendance VALUES(?, ?, ?, ?, ?)", data)
        self.connect.commit()

    def add_emails_and_attendance_data(self, email, attendance_duration, attendance_percentage):
        data = (email, attendance_duration, attendance_percentage)
        self.cursor.execute("INSERT INTO EmailAndAttendance VALUES(?, ?, ?)", data)
        self.connect.commit()

    def add_name_and_emails_data(self, index, name, email):
        data = (index, name, email)
        self.cursor.execute("INSERT OR IGNORE INTO NameAndEmails VALUES(?, ?, ?)", data)
        self.connect.commit()

    def is_name_participant_exist(self, name):
        return len(self.cursor.execute("SELECT * FROM NameAndEmails WHERE Name = ?", (name,)).fetchall()) != EMPTY

    def is_email_participant_exist(self, email):
        return len(self.cursor.execute("SELECT * FROM EmailAndAttendance WHERE Email = ?", (email,)).fetchall()) != EMPTY

    def is_email_exist(self, email):
        return len(self.cursor.execute("SELECT * FROM EmailAndAttendance WHERE Email = ?",
                                       (email,)).fetchall()) != EMPTY

    def get_email_by_name(self, name):
        return self.cursor.execute("SELECT Email FROM NameAndEmails WHERE Name = ?", (name,)).fetchall()

    def get_attendance_data_by_email(self, email):
        return self.cursor.execute("SELECT AttendanceDuration, AttendancePercentage FROM EmailAndAttendance WHERE "
                                   "Email = ?", (email,)).fetchall()

    def get_attendance_data_by_name(self, name):
        attendance_data = self.cursor.execute("SELECT NameAndEmails.Email, AttendanceDuration, AttendancePercentage "
                                              "FROM NameAndEmails INNER JOIN EmailAndAttendance ON "
                                              "EmailAndAttendance.Email = NameAndEmails.Email "
                                              "WHERE Name = ?", (name,)).fetchall()
        return attendance_data if attendance_data is not None else None

    def get_all_name_and_emails_data(self):
        return self.cursor.execute("SELECT * FROM NameAndEmails").fetchall()

    def get_all_participants_data(self):
        return self.cursor.execute("SELECT * FROM Attendance").fetchall()

    def get_all_emails_and_attendance_data(self):
        return self.cursor.execute("SELECT * FROM EmailAndAttendance").fetchall()

    def get_all_database(self):
        return self.cursor.execute("SELECT * FROM CSVFilesData").fetchall()

    def delete_all_database(self):
        os.remove(DATA_BASE_NAME)

    def is_database_exist(self):
        with open(DATA_BASE_NAME, 'r', encoding="utf-8", errors='ignore') as f:
            lines = len(f.readlines())
        return lines > 0


