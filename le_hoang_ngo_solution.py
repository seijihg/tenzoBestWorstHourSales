"""
Please write you name here: Le Hoang Ngo
"""

import csv
import re
import datetime
import operator


def checkBetweenTime(timeObject, startTime, endTime):
    startTimeObj = datetime.datetime.strptime(startTime, '%H:%M')
    endTimeObj = datetime.datetime.strptime(endTime, '%H:%M')

    if startTimeObj < timeObject < endTimeObj:
        return True

    return False


def timeFix(timeString, startTime, endTime):
    keywords = ["AM", "PM"]
    removedSpace = timeString.replace(" ", "")
    replacedDotString = removedSpace.replace('.', ':')

    # Check for AM or PM inside the String.
    if any(keyword in replacedDotString for keyword in keywords):

        if ":" not in replacedDotString:
            if "AM" or "PM" in replacedDotString:
                hour = int(list(re.split('[AM PM]', replacedDotString))[0])
                if hour > 12:
                    return {"error": "Wrong input!"}

            date_time_obj = datetime.datetime.strptime(
                replacedDotString, '%I%p')
            return date_time_obj.time()

        # filter() function to remove empty splits "" since it will return iterator list() is needed. Just used to experiment in this case.
        hour = int(list(re.split(':', replacedDotString))[0])
        minute = re.split(':', replacedDotString)[1]
        minuteSpit = int(list(filter(None, re.split('[AM PM]', minute)))[0])

        if hour > 24:
            return {"error": "Wrong hour input!"}
        if minuteSpit >= 60:
            return {"error": "Wrong minute input!"}

        date_time_obj = datetime.datetime.strptime(
            replacedDotString, '%I:%M%p')
        return date_time_obj.time()

    # if not AM or PM process here.
    if ":" not in replacedDotString:
        replacedDotString = removedSpace + ":00"

    hour = int(list(re.split(':', replacedDotString))[0])
    minute = int(list(re.split(':', replacedDotString))[1])

    if hour > 24:
        return {"error": "Wrong hour input!"}
    if minute >= 60:
        return {"error": "Wrong minute input!"}

    date_time_obj = datetime.datetime.strptime(replacedDotString, '%H:%M')

    # Check if the time is between the working hours if not then add 12 to make it proper time due to lazy managers.
    if not checkBetweenTime(date_time_obj, startTime, endTime):
        addHour = int(hour) + 12
        timeAdded = str(addHour) + ":" + str(minute)
        date_time_obj = datetime.datetime.strptime(timeAdded, '%H:%M')

        return date_time_obj.time()

    return date_time_obj.time()


def timeLoop(array):
    result = {}

    for hour in range(9, 23):
        time_now = str(hour) + ":00"

        # print("Time now:", time_now)
        # print("***")

        pay_this_hour = []

        for shift in array:
            start_work = shift["start_time"]
            start_break = shift["break_start"]
            end_break = shift["break_end"]
            end_work = shift['end_time']

            working_shift_minutes = 60

            # Check working or taking break.
            if (start_work <= time_now < start_break) or (end_break <= time_now < end_work):

                # Check how many minutes was worked for this hour.
                for minute in range(0, 60):
                    if start_work <= time_now < start_break:
                        if str(minute) == start_break.split(":")[1]:
                            working_shift_minutes = minute
                    if end_break <= time_now < end_work:
                        if str(minute) == end_break.split(":")[1]:
                            working_shift_minutes = 60 - minute

            # Calculate shift money
            pay_rate_per_minute = float(shift["pay_rate"]) / 60
            pay_this_hour.append(pay_rate_per_minute * working_shift_minutes)

            # print("Working Time:", working_shift_minutes)
            # print("Start Work:", start_work)
            # print("Start Break:", start_break)
            # print("End Break:", end_break)
            # print("End Work:", end_work)
            # print("Pay for the Hour", pay_this_hour)
            # print("---")

        final_pay_hour = sum(pay_this_hour)
        result[time_now] = int(final_pay_hour)

    return result


def process_shifts(path_to_csv):
    """

    :param path_to_csv: The path to the work_shift.csv
    :type string:
    :return: A dictionary with time as key (string) with format %H:%M
        (e.g. "18:00") and cost as value (Number)
    For example, it should be something like :
    {
        "17:00": 50,
        "22:00: 40,
    }
    In other words, for the hour beginning at 17:00, labour cost was
    50 pounds
    :rtype dict:
    """

    arrShift = []
    with open(path_to_csv) as csvfile:
        arr = []

        spamreader = csv.reader(csvfile)
        for row in spamreader:
            arr.append(row)

        for index in range(1, len(arr)):
            # Naming var
            startTime = arr[index][3]
            endTime = arr[index][1]

            # Calculating the time difference with break notes
            splitBreakNotes = arr[index][0].split("-")
            dateTimeA = datetime.datetime.combine(
                datetime.date.today(), timeFix(splitBreakNotes[0], startTime, endTime))
            dateTimeB = datetime.datetime.combine(
                datetime.date.today(), timeFix(splitBreakNotes[1], startTime, endTime))

            breakTime = str(dateTimeB - dateTimeA)

            # Appending an Array with new Object
            arrShift.append(
                {
                    "break_notes": arr[index][0],
                    "break_time": breakTime[:-3],
                    "break_start": str(timeFix(splitBreakNotes[0], startTime, endTime).strftime("%H:%M")),
                    "break_end": str(timeFix(splitBreakNotes[1], startTime, endTime).strftime("%H:%M")),
                    "end_time": endTime,
                    "pay_rate": arr[index][2],
                    "start_time": startTime
                }
            )

    return timeLoop(arrShift)


def process_sales(path_to_csv):
    """

    :param path_to_csv: The path to the transactions.csv
    :type string:
    :return: A dictionary with time (string) with format %H:%M as key and
    sales as value (string),
    and corresponding value with format %H:%M (e.g. "18:00"),
    and type float)
    For example, it should be something like :
    {
        "17:00": 250,
        "22:00": 0,
    },
    This means, for the hour beginning at 17:00, the sales were 250 dollars
    and for the hour beginning at 22:00, the sales were 0.

    :rtype dict:
    """
    result = {}
    with open(path_to_csv) as csvfile:
        arr = []

        spamreader = csv.reader(csvfile)
        for row in spamreader:
            arr.append(row)

        # Hours range is working range from 9AM to 23PM
        for hour in range(9, 23):
            time_now = str(hour) + ":00"
            time_end = str(hour) + ":59"
            money_this_hour = []

            # print("Time Now:", time_now)

            for row in arr[1:]:
                amount = row[0]
                time = row[1]
                if time_now <= time <= time_end:
                    money_this_hour.append(float(amount))

            sum_money = sum(money_this_hour)
            result[time_now] = sum_money

            # print("Money this hour:", money_this_hour)
            # print("---")

    return result


def compute_percentage(shifts, sales):
    """

    :param shifts:
    :type shifts: dict
    :param sales:
    :type sales: dict
    :return: A dictionary with time as key (string) with format %H:%M and
    percentage of labour cost per sales as value (float),
    If the sales are null, then return -cost instead of percentage
    For example, it should be something like :
    {
        "17:00": 20,
        "22:00": -40,
    }
    :rtype: dict
    """
    result = {}

    # Hours range is working range from 9 to 23
    for hour in range(9, 23):
        time_now = str(hour) + ":00"
        if sales[time_now] == 0:
            result[time_now] = 0 - shifts[time_now]
        else:
            result[time_now] = (100 * shifts[time_now]) / sales[time_now]

    return result


def best_and_worst_hour(percentages):
    """

    Args:
    percentages: output of compute_percentage
    Return: list of strings, the first element should be the best hour,
    the second (and last) element should be the worst hour. Hour are
    represented by string with format %H:%M
    e.g. ["18:00", "20:00"]

    """
    maxItem = max(percentages.items(), key=operator.itemgetter(1))[0]
    minItem = min(percentages.items(), key=operator.itemgetter(1))[0]

    return [maxItem, minItem]


def main(path_to_shifts, path_to_sales):
    """
    Do not touch this function, but you can look at it, to have an idea of
    how your data should interact with each other
    """

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour


if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = ""
    path_to_shifts = ""
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)


# Please write you name here: Le Hoang Ngo
