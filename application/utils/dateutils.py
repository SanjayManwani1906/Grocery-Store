from datetime import datetime

def stringToDate(date_str,format):
    date_object = datetime.strptime(date_str,format).date()
    print(date_object)
    return date_object



