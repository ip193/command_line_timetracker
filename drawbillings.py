import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from datetime import datetime, timedelta

from billingsconstants import *

drawclients = []

if len(sys.argv) > 1 and sys.argv[1] != "":
    client = get_client_by_name(sys.argv[1])
else:
    client = None

if client is None:
    if client_list is None or len(client_list)==0:
        raise RuntimeError("Got None clients_list or no clients have been added yet!")
    print("Got no client for drawbillings, drawing for each")
    drawclients = client_list
else:
    drawclients = [client]


def get_minutes_map(map_me):
    """
    Turn a column of delimited fields into a zero-initialized map
    :param map_me:
    :return:
    """
    split_m = []
    for m in map_me:
        M = m.split(set_delim)
        split_m += [m_s for m_s in M]

    map_minutes = {}
    for m in split_m:
        map_minutes[m] = 0

    return map_minutes


def show_pie(client, pie_values, pie_labels):

    _, autotexts = plt.pie(pie_values, labels=pie_labels, shadow=True, explode=np.ones(len(pie_values))*0.04)

    for i, a in enumerate(autotexts):
        a.set_text(pie_labels[i]+": {} ({}%)".format(int(pie_values[i]), int(1000*(pie_values[i]/VERIFY_MINUTES))/10))

    plt.title(plot_time_distribution_in_minutes[client.language])
    plt.axis('equal')
    plt.show()

    plt.show()
    hours = [pie_values[i]/60 for i in range(len(pie_labels))]
    bills = [hours[i] * client.hourly_wage for i in range(len(hours))]
    
    for i in range(len(pie_labels)):
        print("Area: "+str(pie_labels[i]) + ", Hours: "+to_truncated_string(hours[i])+", Billing: "+client.currency_symbol+to_truncated_string(bills[i]))
    
    
def print_conversion_subscript(client, amount):
    print("      (= €"+to_truncated_string(amount*CONVERSIONS_TO_EUR[client.currency_symbol])+")")


def add_mins_for_column(map_add_me, column, column_name):
    """
    Add up the minutes for a column
    :param map_add_me:
    :param column:
    :return:
    """
    for l in column:  # split up the entries by label to add them
        l_view = df.where(df[column_name] == l, None)
        l_split = l.split(set_delim)

        for sublabel in l_split:
            min_sum = l_view["Minutes"].sum(skipna=True)
            map_add_me[sublabel] += (min_sum/len(l_split))

    RESULT_SUM = 0
    for v in map_add_me.values():
        RESULT_SUM += v

    assert abs(VERIFY_MINUTES - RESULT_SUM )<0.1, "Expected {} minutes, got {} minutes".format(VERIFY_MINUTES, RESULT_SUM)


def get_daily_work_volume(client, starting_time_columns_client):
    try:
        this_month_records = len(starting_time_columns_client[0][0]) - 1
        START, MINUTES = [], []
        for starting_time, minutes in starting_time_columns_client:
            START.extend(starting_time)
            MINUTES.extend(minutes)
        START, MINUTES = np.array(START), np.array(MINUTES)
        daily_volumes = {}
        start_day_strings = [start_time[:10] for start_time in START]  # read in the first ten characters of the date string (equal to the calendar day, month, and year)
        for ind, start_day_string in enumerate(start_day_strings):
            daily_volumes[start_day_string] = []
            if ind == this_month_records:
                print("INFO: Worked on {} days since: ".format(len(daily_volumes))+start_day_strings[0])  # we only want to know about this month
        for ind, start_day_string in enumerate(start_day_strings):
            daily_volumes[start_day_string].append(ind)  # get the indices of common start days

        for start_day in daily_volumes.keys():
            daily_volumes[start_day] = MINUTES[daily_volumes[start_day]].sum()

        now = datetime.now()
        yesterday = now - timedelta(hours=24)
        
        try:
            earning = (daily_volumes[now.strftime(time_format)[:10]]/60)*client.hourly_wage
            print("Worked {} minutes today, earning {}".format(daily_volumes[now.strftime(time_format)[:10]], client.currency_symbol+to_truncated_string(earning)))
            if client.currency_symbol != '€':
                print_conversion_subscript(client, earning)
        except KeyError as e:
            pass
           
        try:
            earning = (daily_volumes[yesterday.strftime(time_format)[:10]]/60)*client.hourly_wage
            print("Worked {} minutes yesterday, earning {}".format(daily_volumes[yesterday.strftime(time_format)[:10]], client.currency_symbol+to_truncated_string(earning)))
            if client.currency_symbol != '€':
                print_conversion_subscript(client, earning)
        except Exception as e:
            print(e)
        
        return daily_volumes.values()
    except Exception as e:
        print("Failed to generate daily work volumes. (Expected if there is no client history)")


exception = False
total_euro = 0
total_monthly_payout = 0
conversion_used = []

starting_time_columns = {}  

smallsep =  "---------"
bigsep = "---------------------"


for client in drawclients:
    try:
        print(bigsep)
        print("Client: "+client.name)
        starting_time_columns[client.name] = []
        
        with open(client.billings_filepath, 'r') as f:
        
            data_active = pd.read_csv(f, sep=csv_delim)
            starting_time_past = data_active.loc[:]["Starting time"]
            minutes_past = data_active.loc[:]["Minutes"]
            starting_time_columns[client.name].append((starting_time_past, minutes_past))
            
            for dir_path, directory_names, file_names in os.walk(client.history_folder, topdown=True):
                # print(dir_path, directory_names, file_names, top_level_folder)
                if os.path.exists(os.path.join(dir_path, client.past_billings_filename)):
                    with open(os.path.join(dir_path, client.past_billings_filename), 'r') as p:
                        data = pd.read_csv(p, sep=csv_delim)
                        starting_time_past = data.loc[:]["Starting time"]
                        minutes_past = data.loc[:]["Minutes"]
                        starting_time_columns[client.name].append((starting_time_past, minutes_past))
                        
                elif os.path.exists(os.path.join(dir_path, client.get_billings_file_name())):
                    with open(os.path.join(dir_path, client.get_billings_file_name()), 'r') as p:
                        data = pd.read_csv(p, sep=csv_delim)
                        starting_time_past = data.loc[:]["Starting time"]
                        minutes_past = data.loc[:]["Minutes"]
                        starting_time_columns[client.name].append((starting_time_past, minutes_past))                        

            # df = pd.read_csv(f, sep=csv_delim)
            df = data_active
            starting_time = df.loc[:]["Starting time"]
            minutes = df.loc[:]["Minutes"]
            VERIFY_MINUTES = df["Minutes"].sum()
            
            # print("VERIFY_MINUTES: "+str(VERIFY_MINUTES))

            labels = list(set(df.loc[:]["Labels"]))
            projects = list(set(df.loc[:]["Projects"]))

            label_minutes = get_minutes_map(labels)
            project_minutes = get_minutes_map(projects)

            add_mins_for_column(label_minutes, labels, "Labels")
            add_mins_for_column(project_minutes, projects, "Projects")

            labels_pie_values = list(label_minutes.values())
            labels_pie_legend = list(label_minutes.keys())

            projects_pie_values = list(project_minutes.values())
            projects_pie_legend = list(project_minutes.keys())

            print(smallsep)
            show_pie(client, labels_pie_values, labels_pie_legend)
            print(smallsep)
            show_pie(client, projects_pie_values, projects_pie_legend)            
            print(smallsep)


            #volumes = get_daily_work_volume(client, starting_time_columns[client.name])
            #if len(starting_time_columns)==1:
            #    plt.hist(volumes, bins="auto")
            #    plt.show()
                  
            print("Total time worked: " + str(int(VERIFY_MINUTES//60)) + " hours and " + str(int(VERIFY_MINUTES%60)) + " minutes.") 
            print(smallsep)
            print("\n")
            income = VERIFY_MINUTES * (client.hourly_wage/60.)
            print("Total client billing: "+client.currency_symbol + to_truncated_string(income))
            client_euro = income*CONVERSIONS_TO_EUR[client.currency_symbol]
            total_euro += client_euro
            
            if client.currency_symbol != '€':
                conversion_used.append(client.currency_symbol)
                print_conversion_subscript(client, income)
            
            now = datetime.now().strftime(time_format)
            today_int = int(now[0:2])
            # print("Today: "+str(today_int))
            
            if client_euro == 0:
                print("No payments yet (expected payout cannot be calculated)")
            else:
                days_past_due = today_int - client.due_date if today_int > client.due_date else ((31 + today_int) - client.due_date)
                if days_past_due == 0:
                    if(client_euro > 300):
                        print("Got due date equal to today's day of the month, assuming the invoice contains a full month's work (is not new)")
                        days_past_due = 31
                    else:
                        print("Got due date equal to today's day of the month, assuming the invoice is due in 31 days")
                        days_past_due = 1
                # print("Days past due: "+str(days_past_due))
                payout_multiplicator = 31/days_past_due
                # print("Client payout multiplicator: "+str(payout_multiplicator))
                total_monthly_payout += payout_multiplicator*client_euro

            if len(drawclients) > 1:
                if(client_euro!=0):
                    print("Expected client payout: "+client.currency_symbol+to_truncated_string(payout_multiplicator*income))
                    if client.currency_symbol != '€':
                        print_conversion_subscript(client, payout_multiplicator*income)
                    
                print("\n")
                print("End Client: "+client.name)
                
    except Exception as e:
        exception = True
        print(e)

   
if not exception:
    
    print(bigsep)
    print("Total current billing"+ (" (conversion not up-to-date)" if conversion_used else "")+ ": €"+to_truncated_string(total_euro))
    print("Expected end-of-billings payout (for these and no further clients, each over 31 days): \n\n\n          €"+to_truncated_string(total_monthly_payout)+"\n\n")
    for symbol in conversion_used:
        print("Conversion rate (not up-to-date) "+symbol+" -> € = "+to_truncated_string(CONVERSIONS_TO_EUR[symbol]))










