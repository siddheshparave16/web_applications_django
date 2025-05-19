from datetime import datetime

class DateConverter:
    # the regex pattern to match the date
    regex = "[0-9]{8}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y%m%d").date()
    
    def to_url(self, object):
        return object.strftime("%Y%m%d")
