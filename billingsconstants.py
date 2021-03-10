import os 

FINANCIAL_DIR =  r"C:\Set\Your\Path\Here"   # forward or backward slashes allowed


csv_delim = ";"
set_delim = ","
default_label_string = 'MISC'

time_format = '%d.%m.%Y %H:%M'
time_format_daily = '%d.%m.%Y'

PAUSEFILE_NAME = "pause.txt"
BILLINGSFILE_NAME = "billings.csv"
CLIENT_CACHE_FILE_NAME = "lastclient.txt"
BILLINGS_BACKUPFILE_NAME = "billings_backup.csv"
header_string = "Starting time;Labels;Projects;Description;Ending time;Minutes;"

DEFAULT_CLIENT_NAME = None  # optionally set a default client name here

CONVERSIONS_TO_EUR = {'€':1., '$':0.85}  


plot_time_distribution_in_minutes = {"DE":"Zeitverteilung in Minuten" , "EN":"Time distribution in minutes"}

def to_truncated_string(amount):
    return str(int(amount*100)/100)




client_list = []
class Client:
    """
    Describes a customer with unique projects and billable activities
    Name should be unique

    Due date is the day of the month (out of 31) on which the invoice is submitted and a new, current one is created
    """
    
    def get_billings_file_name(self):
        return self.name+"_"+BILLINGSFILE_NAME
        
    def get_billings_backup_file_name(self):
        return self.name+"_"+BILLINGS_BACKUPFILE_NAME

    def __init__(self, client_list, name, hourly_wage, currency_symbol, language, due_date):
        self.name = name
        self.billings_filepath = os.path.join(FINANCIAL_DIR, self.get_billings_file_name())
        self.billings_backup_filepath = os.path.join(FINANCIAL_DIR, self.get_billings_backup_file_name())
        self.financial_folder = FINANCIAL_DIR
        self.hourly_wage = hourly_wage
        self.currency_symbol = currency_symbol
        self.past_billings_filename = "billings.csv"  # When traversing past work, assume this billings filename
        self.pausefile_name = self.name + "_" +PAUSEFILE_NAME
        self.history_folder = os.path.join(FINANCIAL_DIR, self.name+ "_history")
        self.language = language
        self.due_date = due_date

        client_list.append(self)
        

def get_client_by_name(name):
    if name is None:
        return None
    for client in client_list:
        if client.name == name:
            return client

    print("Got name argument: "+name)
    for client in client_list:
        print("Client: "+client.name)
    raise RuntimeError("Client not found in list (is the name spelled correctly?)")

"""
Client name should contain no spaces (else use quotes in the command line)

Use single quotes around the currency symbol. 

Supported languages: EN and DE. 

Due date is the day of the month on which the invoice is created and a new time tracking file is created. Optional feature, use 31 for a sensible default. 

To create a new client, follow the instructions below
"""


# create a client with name ExampleClient, who is billed 20 € per hour. Use German language chart titles. 

ExampleClient = Client(client_list, "ExampleClient", 20., '€', "DE", 31)  #  Use client_list as the first value in all new clients

"""
New Clients/Projects go below here: 
"""

# To create a client named JaneDoe who is billed 25 $ per hour and wants English language chart titles, remove the '#' from the line below: 
# JaneDoe = Client(client_list, "JaneDoe", 25., '$', "EN", 31)
