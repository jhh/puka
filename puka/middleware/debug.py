import os

from django.conf import settings
from django.db import connection


def terminal_width():
    """
    Function to compute the terminal width.
    WARNING: This is not my code, but I've been using it forever and
    I don't remember where it came from.
    """
    width = 0
    try:
        import fcntl
        import struct
        import termios

        s = struct.pack("HHHH", 0, 0, 0, 0)
        x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
        width = struct.unpack("HHHH", x)[1]
    except:
        pass
    if width <= 0:
        try:
            width = int(os.environ["COLUMNS"])
        except:
            pass
    if width <= 0:
        width = 80
    return width


class SqlPrintingMiddleware:
    """
    Middleware which prints out a list of all SQL queries done
    for each view that is processed.  This is only useful for debugging.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        indentation = 2
        pad = " " * indentation
        if len(connection.queries) > 0 and settings.DEBUG:
            width = terminal_width()
            total_time = 0.0
            for query in connection.queries:
                nice_sql = query["sql"].replace('"', "")
                sql = f"\033[1;31m[{query['time']}]\033[0m {nice_sql}"
                total_time = total_time + float(query["time"])
                while len(sql) > width - indentation:
                    print(f"{pad}{sql[: width - indentation]}")
                    sql = sql[width - indentation :]
                print(f"{pad}{sql}\n")
            print(f"{pad}\033[1;32m[TOTAL TIME: {str(total_time)} seconds]\033[0m")
        return response
