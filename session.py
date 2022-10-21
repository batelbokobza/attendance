from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import Constant
import attendance

app = Flask(__name__)
Bootstrap(app)

app.secret_key = "secret key string"  # For CSRF protection.  Any string can be used for the secret key.


def process_request(request_type, user_input=None):
    """A request for the attendance data from the attendance class.
                :param request_type: int:  request number from constant according to the user's request selection.
                :param user_input: (string): optional parameter. user input if required by the type of request.
                :return:
                    response object - (object list(response number, response data))"""
    if user_input is not None:
        response = attendance.Attendance().calculate_attendance(request_type, user_input)
    else:
        response = attendance.Attendance().calculate_attendance(request_type)
    if type(response) is NameError:
        raise NameError("Error")
    else:
        return response


def view_attendance_data(response, optional_msg):
    """Displaying a template page containing the data to the user.

                :param response: (object list(headers, unique name columns, response data)).
                :param optional_msg: (string): optional message that will be displayed according to the user's choice.
                :return:
                     template page that contains data according to the user's request."""
    try:
        res_number, res_data = response
        headers, unique_name_cols, response_data = res_data
        return render_template('display_page.html', number_columns=len(headers), headers=headers,
                               unique_class=unique_name_cols, data_list=response_data, optional_message=optional_msg)
    except NameError as err:  # if type(response) is NameError
        attendance.Attendance().data_reset()
        return render_template('exception_page.html', error_message=err)


@app.route("/table", methods=["GET", "POST"])
def get_request():
    """Receiving the user's requests from the home page, processing the request,
    and creating a request for a response according to the user's choice."""
    try:
        response = None
        msg = Constant.Response.OTHER_MSG
        input_name = request.args.get("name_search", None)
        input_date_from, input_date_to = request.args.get("formDatePicker", None), request.args.get("toDatePicker",
                                                                                                    None)
        input_email = request.args.get("email_search", None)
        connection_type = request.args.get("connection-type", None)  # Possible values - mobile or desktop.
        all_participants_data = request.args.get("allParticipantsData", None)  # The value of the variable is "true".
        all_meetings_data = request.args.get("allMeetingsData", None)  # The value of the variable is "true" in string.
        if all_meetings_data == "true":
            response = process_request(Constant.Request.Type.ALL_MEETINGS_DATA)
        elif all_participants_data == "true":
            response = process_request(Constant.Request.Type.ALL_PARTICIPANTS_DATA)
        elif input_name is not None:
            response = process_request(Constant.Request.Type.BY_NAME, input_name)
            msg = Constant.Response.BY_NAME_MSG + input_name + Constant.Response.OTHER_MSG
        elif input_email is not None:
            response = process_request(Constant.Request.Type.BY_EMAIL, input_email)
            msg = Constant.Response.BY_EMAIL_MSG + input_email
        elif input_date_from is not None and input_date_to is not None:
            response = process_request(Constant.Request.Type.BY_DATE, (input_date_from, input_date_to))
            msg = Constant.Response.BY_DATE_MSG + input_date_from + "  -  " + input_date_to
        elif connection_type is not None:
            response = process_request(Constant.Request.Type.BY_CONNECTION_TYPE, connection_type)
            msg = Constant.Response.BY_CONNECTION_TYPE_MSG + connection_type
        else:
            pass
        if response is not None and not type(response) is NameError:
            return view_attendance_data(response, msg)
        return render_template("base.html")
    except NameError as err:  # if type(response) is NameError
        attendance.Attendance().data_reset()
        return render_template('exception_page.html', error_message=err)


@app.route("/", methods=["GET", "POST"])
def start():
    """Shows the user the page of the home screen."""
    try:
        return render_template("base.html")
    except NameError as err:
        print(err)


# def run_application(): app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
