import json
import random
import copy
import math
import sys
import matplotlib
# matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import threading

print ("Proiect DMDW")
print ("Dealing with missing data: Imputation")

def randomize_data_loss(data, N):
    print ("Randomizing data loss ...")
    for i in range(N):
        random_index = random.randint(0, len(data) - 1)
        data[random_index]['daily_confirmed_cases'] = None

    print ("Corrupted " + str(N) + " out of " + str(len(data)) + " entries")


#----------------------------------- usefull modules----------------------------
def quantify_date(date):
    year = int(date[3:4])
    month = int(date[5:7])
    day = int(date[8:10])
    new_format = year * 365 + month * 30 + day
    return new_format

def calculate_mean(data):
    sum = 0
    counter = 0
    for entry in data:
        if entry['daily_confirmed_cases'] is not None:
            sum += int(entry['daily_confirmed_cases'])
            counter += 1
    mean = sum / counter
    return mean

def calculate_date_mean(data):
    sum = 0
    for entry in data:
        if entry['date'] is not None:
            sum += quantify_date(entry['date'])
    mean = sum / len(data)
    # print ("Mean is " + str(mean))
    return mean

def mean_error(fixed_data, clean_data):
    sum = 0
    counter = 0
    # print("mean in mean_error is: " + str(mean))
    # for entry in data:
    #     if entry['daily_confirmed_cases'] is None:
    #         print(entry)
    for i in range(len(fixed_data)):
        if fixed_data[i]['daily_confirmed_cases'] is not None:
            error = abs(int(fixed_data[i]['daily_confirmed_cases']) - int(clean_data[i]['daily_confirmed_cases']))
            sum += error
            counter += 1
    return sum / counter

def returnX(data):
    list = []
    for entry in data:
        list.append(entry['date'])
    return pd.to_datetime(list)

def returnY(data):
    list = []
    for entry in data:
        cases = int(entry['daily_confirmed_cases'])
        # print(cases)
        list.append(cases)
    # print("....\n\n\n\n\n")
    # print(list)
    return list

def diff(corrupted_data, fixed_data):
    data = []
    for i in range(len(corrupted_data)):
        if corrupted_data[i]['daily_confirmed_cases'] != fixed_data[i]['daily_confirmed_cases']:
            data.append(fixed_data[i])
    return data

def plotCorruptedData(corrupted_data, clean_data):
    data = []
    for i in range(len(corrupted_data)):
        if corrupted_data[i]['daily_confirmed_cases'] is None:
            data.append(clean_data[i])
    return data

#-------------------------------- /usefull modules -----------------------------

# hot_deck / last observation carried out
def hot_deck(corrupted_data):
    fixed_data = copy.deepcopy(corrupted_data)
    for i in range(len(fixed_data)):
        if fixed_data[i]['daily_confirmed_cases'] is None:
            if i == 0 & len(data) > 1:
                fixed_data[i]['daily_confirmed_cases'] = fixed_data[i + 1]['daily_confirmed_cases']
            elif i > 0:
                j = i - 1
                while j >= 0:
                    if fixed_data[j]['daily_confirmed_cases'] is not None:
                        fixed_data[i]['daily_confirmed_cases'] = fixed_data[j]['daily_confirmed_cases']
                        break
                    j =- 1
    return fixed_data


# cold_deck / replace missing data with past observations
# the field "state" will be used to search for similar events
def cold_deck(corrupted_data):
    fixed_data = copy.deepcopy(corrupted_data)
    for i in range(len(fixed_data)):
        if fixed_data[i]['daily_confirmed_cases'] is None:
            state = fixed_data[i]['state_name']
            #look for the closest past similar event
            for j in range(i, 0, -1):
                if (fixed_data[j]['state_name'] == state) & (fixed_data[j]['daily_confirmed_cases'] is not None):
                    fixed_data[i]['daily_confirmed_cases'] = fixed_data[j]['daily_confirmed_cases']
                    break
    return fixed_data


def mean_substition(corrupted_data):
    fixed_data = copy.deepcopy(corrupted_data)
    mean = calculate_mean(fixed_data)
    for entry in fixed_data:
        if entry['daily_confirmed_cases'] is None:
            entry['daily_confirmed_cases'] = mean
    return fixed_data

# liniar regression
# values generated after y = a + bx
def liniar_regression(corrupted_data):
    fixed_data = copy.deepcopy(corrupted_data)
    cases_mean = calculate_mean(corrupted_data)
    date_mean = calculate_date_mean(corrupted_data)
    N = 0
    marginal_error_sum = 0
    standard_deviation_date_sum = 0
    standard_deviation_cases_sum = 0
    #calculate sum[(date-avg_date)*(cases-avg_cases)]
    for entry in corrupted_data:
        if entry['daily_confirmed_cases'] is not None:
            N += 1
            delta_cases = int(entry['daily_confirmed_cases']) - cases_mean
            delta_date = int(quantify_date(entry['date'])) - date_mean
            marginal_error_sum += delta_date * delta_cases
            standard_deviation_date_sum += delta_date * delta_date
            standard_deviation_cases_sum += delta_cases * delta_cases

    pearson_coefficient = marginal_error_sum / math.sqrt(standard_deviation_date_sum * standard_deviation_cases_sum)

    # b = pers * sy/sx
    sy = math.sqrt(standard_deviation_cases_sum / (N - 1))
    sx = math.sqrt(standard_deviation_date_sum / (N - 1))
    b = pearson_coefficient * sy / sx

    # a = avg_y - avg_x * b
    a = cases_mean - date_mean * b

    # y = a + bx
    for i in range(len(fixed_data)):
        if fixed_data[i]['daily_confirmed_cases'] is None:
            fixed_data[i]['daily_confirmed_cases'] = a + quantify_date(fixed_data[i]['date']) * b

    return fixed_data



if __name__ == "__main__":
    # execute only if run as a script

    args = sys.argv[1:]

    if len(args) == 0:
        print ("Error, required patameter: Number of entries to corrupt")
    else:
        corrupted_entries = int(args[0])
        print ("Corrupted entries: " +  str(corrupted_entries))

    #open file
    with open('/home/andu/Documents/Proiect_DMDW/initial_dataset.json', 'r') as myfile:
        data = myfile.read()
    # parse file
    initial_dataset = json.loads(data)
    clean_data = copy.deepcopy(initial_dataset['data'])
    corrupted_data = copy.deepcopy(clean_data)

    randomize_data_loss(corrupted_data, corrupted_entries)

    DF = pd.DataFrame()
    DF['value'] = returnY(clean_data)
    DF = DF.set_index(returnX(clean_data))

    plt.plot(DF)
    plt.gcf().autofmt_xdate()
    plt.title("CLEAN DATA")
    # plt.show()

    # print(clean_data)
    # for entry in clean_data:
    #         print(entry['daily_confirmed_cases'])
    clean_mean = calculate_mean(clean_data)
    print("------------------------------------------------------")
    print("Mean of clean_data: " + str(clean_mean))
    print("Mean error for clean data: " +  str(mean_error(clean_data, clean_data)))
    DF = pd.DataFrame()
    DF['value'] = returnY(plotCorruptedData(corrupted_data,clean_data))
    DF = DF.set_index(returnX(plotCorruptedData(corrupted_data,clean_data)))
    plt.plot(DF)
    plt.gcf().autofmt_xdate()
    plt.title("CORRUPTED DATA")
    # plt.show()
    # print("Mean of corrupted_data")
    print("Mean of corrupted_data: " + str(calculate_mean(corrupted_data)))
    # print(mean_error(corrupted_data))

    # print("Mean of hot_deck")
    print("Mean of hot_deck: " + str(calculate_mean(hot_deck(corrupted_data))))
    print("Mean error of hot_deck: " + str(mean_error(hot_deck(corrupted_data), clean_data)))
    DF = pd.DataFrame()
    DF['value'] = returnY(diff(corrupted_data, hot_deck(corrupted_data)))
    DF = DF.set_index(returnX(diff(corrupted_data, hot_deck(corrupted_data))))
    plt.plot(DF)
    plt.gcf().autofmt_xdate()
    plt.title("HOT DECK")
    # plt.show()

    # print("Mean of cold_deck")
    print("Mean of cold_deck: " + str(calculate_mean(cold_deck(corrupted_data))))
    print("Mean error of cold_deck: " + str(mean_error(cold_deck(corrupted_data), clean_data)))
    DF = pd.DataFrame()
    DF['value'] = returnY(diff(corrupted_data, cold_deck(corrupted_data)))
    DF = DF.set_index(returnX(diff(corrupted_data, cold_deck(corrupted_data))))
    plt.plot(DF)
    plt.gcf().autofmt_xdate()
    plt.title("COLD DECK")
    # plt.show()

    # print("Mean of mean_substition")
    print("Mean of mean_substition: " + str(calculate_mean(mean_substition(corrupted_data))))
    print("Mean error of mean_substition: " + str(mean_error(mean_substition(corrupted_data), clean_data)))
    DF = pd.DataFrame()
    DF['value'] = returnY(diff(corrupted_data, mean_substition(corrupted_data)))
    DF = DF.set_index(returnX(diff(corrupted_data, mean_substition(corrupted_data))))
    plt.plot(DF)
    plt.gcf().autofmt_xdate()
    plt.title("MEAN SUBTITUTION")
    # plt.show()

    # print("Mean of liniar_regression")
    print("Mean of liniar_regression: " + str(calculate_mean(liniar_regression(corrupted_data))))
    print("Mean error of liniar_regression: " + str(mean_error(liniar_regression(corrupted_data), clean_data)))
    DF = pd.DataFrame()
    DF['value'] = returnY(diff(corrupted_data, liniar_regression(corrupted_data)))
    DF = DF.set_index(returnX(diff(corrupted_data, liniar_regression(corrupted_data))))
    plt.plot(DF)
    plt.gcf().autofmt_xdate()
    plt.title("LINIAR REGRESSION")
    # plt.show()
    # print(calculate_mean(liniar_regression(corrupted_data)))
