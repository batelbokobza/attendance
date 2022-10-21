
class AttendanceDataObj:

    def __init__(self, name, attendance_minutes, attendance_percentage, email=None):
        self.NAME = name
        self.ATTENDANCE_DURATION = attendance_minutes
        self.ATTENDANCE_PERCENTAGE = attendance_percentage
        self.EMAIL = email

    def get_data_in_tuple_object(self):
        return self.NAME, self.ATTENDANCE_DURATION, self.ATTENDANCE_PERCENTAGE, self.EMAIL

    def __str__(self):
        return "Name: " + self.NAME, ", attendance duration: ", self.ATTENDANCE_DURATION, ", attendance percentage: ", \
               self.ATTENDANCE_PERCENTAGE, ", email: ", self.EMAIL


class ParticipantDataObj:

    def __init__(self, m_name, m_date, m_start, m_end, name, email, join, leave, attendance, conn_type):
        self.MEETING_NAME = m_name
        self.MEETING_DATE = m_date
        self.MEETING_START_TIME = m_start
        self.MEETING_END_TIME = m_end
        self.NAME = name
        self.EMAIL = email
        self.JOIN_TIME = join
        self.LEAVE_TIME = leave
        self.ATTENDANCE_DURATION = attendance
        self.CONNECTION_TYPE = conn_type

    def get_data_in_tuple_object(self):
        return (self.MEETING_NAME, self.MEETING_DATE, self.MEETING_START_TIME, self.MEETING_END_TIME,
                self.NAME, self.EMAIL, self.JOIN_TIME, self.LEAVE_TIME, self.ATTENDANCE_DURATION, self.CONNECTION_TYPE)

    def __str__(self):
        return "Meeting name: " + self.MEETING_NAME, ", meeting date: ", self.MEETING_DATE, ", meeting start time: ", \
               self.MEETING_START_TIME, ", meeting end time: ", self.MEETING_END_TIME, ", name: ", self.NAME, \
               ", email: ", self.EMAIL, ", join time: ", self.JOIN_TIME, ", leave time: ", self.LEAVE_TIME, \
               ", attendance duration: ", self.ATTENDANCE_DURATION, ", connection type: ", self.CONNECTION_TYPE
