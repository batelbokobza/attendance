from enum import IntEnum
from strenum import StrEnum

NUM_DATA_ITEMS_IN_ROW = 9
REMOTE_DIRECTORY_PATH = '/var/tmp/csv_files/'
# Path to the directory you want to download on the remote server.
LOCAL_DIRECTORY_PATH = '/Users/batel/Desktop/CSV_FILES/'
# Local path where you want to save the files downloaded from the server.


class Request(object):
    class Type(IntEnum):
        BY_NAME = 1
        BY_DATE = 2
        BY_EMAIL = 3
        BY_CONNECTION_TYPE = 4
        ALL_PARTICIPANTS_DATA = 5
        ALL_MEETINGS_DATA = 6

    class ConnectionType(StrEnum):
        MOBILE = "mobile"
        DESKTOP = "desktop"


class Response(object):
    class Type(IntEnum):
        NAME_AND_EMAIL = 10
        NAME = 20
        DATA_BY_DATE = 30
        DATA_BY_EMAIL = 40
        ALL_MEETINGS_DATA = 50
        ALL_PARTICIPANTS_DATA = 60
        DATA_BY_CONNECTION_TYPE = 70

    class ConnectionType(StrEnum):
        MOBILE = "Mobile app"
        DESKTOP = "Desktop app"

    unique_name_for_columns_dict = {'Meeting Name': 'meeting-name', 'Meeting Date': 'meeting-date',
                                    'Meeting Start Time': 'meeting-start', 'Meeting End Time': 'meeting-end',
                                    'Name': 'name', 'Email': 'email',
                                    'Join Time': 'join-time', 'Leave Time': 'leave-time',
                                    'Attendance Duration': 'attendance-duration',
                                    'Attendance Percentage': 'attendance-percentage', 'Connection Type': 'conn-type'}

    BY_NAME_MSG = 'For the name: '
    BY_DATE_MSG = 'For dates: '
    BY_EMAIL_MSG = 'For email: '
    BY_CONNECTION_TYPE_MSG = 'For connection type: '
    OTHER_MSG = ' \n(There may be duplicate names for different emails).'
