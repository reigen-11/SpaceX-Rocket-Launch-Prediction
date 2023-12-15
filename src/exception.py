import sys


def error_message_details(error, error_details: sys):
    _, _, exc_tb = error_details.exc_info()

    file_name = exc_tb.tb_frame.f_code.co_filename
    file_no = exc_tb.tb_lineno

    error_msg = "Here is the Error : \n At this File : \n[{0}]\n At line number:{1}\n The error is : \n[{2}]\n"\
                .format(file_name, file_no, str(error))

    return error_msg  


class CustomExceptions(Exception):

    def __init__(self, error_msg, error_detail: sys):
        super().__init__(error_msg)

        self.error_message = error_message_details(error_msg, error_details=error_detail)

    def __str__(self):
        return self.error_message

