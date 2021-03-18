import argparse
from datetime import datetime, timedelta
import shutil 
import warnings
import pandas as pd
import subprocess

from billingsconstants import *

# NOTE TO EDITOR: Make sure you leave a blank line at the end of the billings file, otherwise the script may not work properly!

parser = argparse.ArgumentParser(description="Add billings records to a .csv billings file, differentiated by client.\n"
                                             "Automatically adds timestamped descriptions of billable activity.\n"
                                             "Entries are separated by ';', do not use this in descriptions.\n"
                                             "Creates (overwrites) a backup before any changes are made.")

parser.add_argument('-n', dest="client_name", metavar="client_name", action='store', type=str, default=DEFAULT_CLIENT_NAME,
                    help="Specify the client for whom entries are to be written. This will be written to a .txt file in your financial folder, so you don't have to add it every time if you aren't switching clients. Alternatively: set a default value in your constants file.")
parser.add_argument('mode', type=str, action='store', help="'start' and 'end' open and close a billable session, respectively.\n"
                                                           "'print' will display the current contents of the billings file"
                                                           ", regardless of whether a session is currently open. \n'reset' will "
                                                           "extend the length of the currently open session by subtracting from the beginning time"
                                                           " or, if no session is open, "
                                                           "will extend the length of the previous session by adding to the closing "
                                                           "time a positive or negative value 'minutes' (command line argument -m, see help). \n"
                                                           "Use 'pause' and 'unpause' to pause and resume a session. \n"
                                                           "Use 'check' to check if any entries have errors in minute and time counting. \n"
                                                            "Use 'NEW' to start a fresh billings file including headers (requires that no file at the billings path exists)")
parser.add_argument('-l', metavar='LABELS', dest='labels', type=str, action='store',
                    help='Add a label to the billable session, e.g. "CODE,LEARN,COMM" (comma-seperated).'
                         ' Can be used at beginning or end of session or both.', default=default_label_string)
parser.add_argument('-d', dest='description', metavar='description', type=str,
                    help="Add a description of what was done during the billable session. "
                         "If arguments are provided at start and end, both will be added to file.", default=None)
parser.add_argument('-p', metavar='PROJECTS', dest='projects', type=str, action='store',
                    help='Add a project to the billable session, e.g. "Project1,Project2" (comma-seperated).'
                         ' Can be used at beginning or end of session or both.', default=default_label_string)
parser.add_argument('-m', metavar='reset_minutes', dest='reset_minutes', type=int, default=None, help="Used in conjunction with mode = reset. "
                                                                                                      "The provided whole number value in minutes is added to the length"
                                                                                                      "of the billable session.")
class csv_entry:
    def __init__(self, start_date, labels, projects, description, end_date, minutes):
        self.start_date, self.labels, self.projects, self.description, self.end_date, self.minutes = start_date, labels, \
                                                                                projects, description, end_date, minutes

    def csv_format(self, d=csv_delim, close_delim=True):
        """
        Turn a list of items into a csv-compatible line.
        :return:
        """
        l = self.start_date + d + self.labels + d + self.projects + d + self.description + d + self.end_date + d + str(self.minutes) + (d if close_delim else "")

        return l


def csv_format(line_list, delim=csv_delim, close_delim=True):
    """
    Turn a list of items into a csv-compatible line.
    :param line_list:
    :return:
    """
    l = ""
    for ind, item in enumerate(line_list):
        l += (str(item) + (delim if (close_delim or (ind!=len(line_list)-1)) else ""))

    return l
        
def get_saved_client_name():
    """
    Returns the last client name that was entered 
    """
    client_cache_file_path = os.path.join(FINANCIAL_DIR ,CLIENT_CACHE_FILE_NAME)
    return_string = None
    if os.path.exists(client_cache_file_path):
        with open(client_cache_file_path, 'r') as f:
            return_string = f.readline()
            f.close()
    return return_string
    

def write_client_name(client_name):
    """
    Writes out the selected client name
    """
    client_cache_file_path = os.path.join(FINANCIAL_DIR ,CLIENT_CACHE_FILE_NAME)
    if os.path.exists(client_cache_file_path):
        os.remove(client_cache_file_path)
    with open(client_cache_file_path, 'w+') as f:
        f.write(client_name)
        f.close()
        
    subprocess.check_call(["attrib", "+H", client_cache_file_path])



def handle_exception(e, _print=True):
    """
    Print the time in case of exceptions
    """
    now = datetime.now()
    nowstring = now.strftime(time_format)
    
    print("Exception at: "+nowstring)
    if _print:
        print(e)


args_parsed = False
client = None
try:

    now = datetime.now()
    nowstring = now.strftime(time_format)
    command_line_parse = parser.parse_args()
    args_parsed = True
    
    input_client_name = command_line_parse.client_name
    
    if input_client_name is None:
        saved_client_name = get_saved_client_name()
        if saved_client_name is None:
            raise RuntimeError("Please pass a client name when calling (or add default client name) (No client name is saved)")
        
        input_client_name = saved_client_name

    client = get_client_by_name(input_client_name)
    if client is None:
        raise RuntimeError("Please pass a client name when calling (or add default client name)")
    else:
        print("Client: "+client.name)
        write_client_name(input_client_name)

    def finish(lines:list):
        """
        Write the file and exit the program.
        :param lines: New contents of the csv file, by line
        :return:
        """
        with open(client.billings_filepath, 'w+') as f:
            for ind, l in enumerate(lines):
                f.write(l)
            f.write("\n")
        exit()

    if command_line_parse.mode not in ["start", "end", "print", "reset", "pause", "unpause", "check", "NEW"]:
        raise RuntimeError("Please pass a valid 'mode' argument (see help with -h) ")

    if command_line_parse.mode == 'print':  # Just print the file contents
        with open(client.billings_filepath, 'r') as f:
            df = pd.read_csv(f, sep=';')
            pd.options.display.max_columns = len(df.columns)
            print(df)
            exit()

    if command_line_parse.mode == 'NEW':  #  create a new file if none exists
        if os.path.exists(client.billings_filepath):
            raise RuntimeError("Please delete or move the existing file at: "+client.billings_filepath+" before creating a new billings file")
        else:
            print("Initializing new file: "+client.billings_filepath)
            lines = [header_string]
            finish(lines)

    starting_entry = command_line_parse.mode == "start"
    closing_entry = command_line_parse.mode == "end"

    lines = []

    with open(client.billings_filepath, 'r') as f:
        lines.extend(f.readlines())

    unfinished_billable_session = False
    lastline_vals = None

    if len(lines) > 1:  # check for an unfinished session

        lastline = lines[-1]
        lastline_vals = lastline.split(csv_delim)
        lastline_vals = lastline_vals[:-1]  # the script adds a newline character at the end

        last_entry = csv_entry(*lastline_vals)

        if last_entry.end_date == "" and lastline != "":
            unfinished_billable_session = True

        if unfinished_billable_session and starting_entry:
            raise RuntimeError("Last session was not closed. Did you mean to call 'end'?")

        if not unfinished_billable_session and closing_entry:
            raise RuntimeError("Please start a session before ending it. Did you mean to call 'start'?")

    else:
        if command_line_parse.mode == 'reset':
            raise RuntimeError("No billable sessions to reset (empty file)")

    pausefile_path = os.path.join(client.financial_folder, client.pausefile_name)
    is_paused = os.path.exists(pausefile_path)

    if not unfinished_billable_session and command_line_parse.mode in ["pause", "unpause"]:
        raise RuntimeError("Cannot use pause management without an active session. Did you mean to call 'start'?")
    else:
        if is_paused:
            if command_line_parse.mode == "pause":
                raise RuntimeError("Cannot pause session - session is currently paused (hidden file {} exists)".format(pausefile_path))
            elif command_line_parse.mode == "unpause":
                with open(pausefile_path, 'r') as f:
                    start_time = f.readline()
                    start_time_obj = datetime.strptime(start_time, time_format)

                    time_elapsed = now - start_time_obj
                    time_elapsed_minutes = time_elapsed.seconds // 60

                print("Unpausing session at {}. Minutes elapsed: {}".format(nowstring, str(time_elapsed_minutes)))
                os.remove(pausefile_path)
                subprocess.call("powershell writebillings.ps1 reset -m {}".format("-"+str(time_elapsed_minutes)))
                exit()
        else:
            if command_line_parse.mode == "unpause":
                raise RuntimeError("Cannot unpause session - session not paused (hidden file {} does not exist)".format(pausefile_path))
            elif command_line_parse.mode == "pause":
                if os.path.exists(pausefile_path):
                    os.remove(pausefile_path)  #  shouldn't be necessary, but would throw an error if it exists
                with open(pausefile_path, "w+") as f:
                    f.write(nowstring)
                subprocess.check_call(["attrib", "+H", pausefile_path])
                print("Session paused at: "+nowstring)
                exit()

    if is_paused:
        raise RuntimeError("Please unpause session or delete pausefile {} before continuing.".format(pausefile_path))

    if unfinished_billable_session and command_line_parse.mode in ["check"]:
        raise RuntimeError("Cannot check for record health before active session is closed (call 'end')")

    shutil.copyfile(client.billings_filepath, client.billings_backup_filepath) # make a backup copy

    if len(lines) > 1:
        lastline_vals[-1] = lastline_vals[-1].replace("\n", "")  # this is because it adds a newline character to the last field

    if command_line_parse.mode == 'reset':
        if command_line_parse.reset_minutes is None:
            raise RuntimeError("Please provide a reset value with -m [value] (see -h help for help)")

        last_entry = csv_entry(*lastline_vals)

        reset_delta = timedelta(minutes=command_line_parse.reset_minutes)
        extend_session = command_line_parse.reset_minutes >= 0

        if unfinished_billable_session: # subtract the reset value from the beginning of the current session
            start_time = datetime.strptime(last_entry.start_date, time_format)
            start_time -= reset_delta
            last_entry.start_date = start_time.strftime(time_format)

            if extend_session:
                print("Subtracted {} minutes from begin of current billable session (session extended).".format(command_line_parse.reset_minutes))
            else:
                print("Added {} minutes to begin of current billable session (session shortened).".format(int(-1 * command_line_parse.reset_minutes)))
            lines[-1] = last_entry.csv_format(close_delim=True)
            finish(lines)
        else:
            end_time = last_entry.end_date
            end_time = datetime.strptime(end_time, time_format)
            end_time += reset_delta
            last_entry.end_date = end_time.strftime(time_format)
            start_time = datetime.strptime(last_entry.start_date, time_format)

            if not start_time < end_time:
                raise RuntimeError("Sessions must end after and not before they start. Did you use too large a reset?")

            time_diff = end_time - start_time  # recompute the time difference
            time_diff_minutes = time_diff.seconds // 60
            last_entry.minutes = time_diff_minutes

            if extend_session:
                print("Added {} minutes to the end of last billable session (session extended to {} minutes).".format(str(command_line_parse.reset_minutes), str(last_entry.minutes)))
            else:
                print("Subtracted {} minutes from the end of last billable session (session shortened to {} minutes).".format(str(int(-1 * command_line_parse.reset_minutes)), str(last_entry.minutes)))

            lines[-1] = last_entry.csv_format(close_delim=True)
            finish(lines)

    if command_line_parse.mode == "check":
        dirtylines = 0
        for ind, line in enumerate(lines[1:]):
            linevals = line.split(csv_delim)[:-1]
            record = csv_entry(*linevals)

            start_time = record.start_date
            end_time = record.end_date

            time_diff = datetime.strptime(end_time, time_format) - datetime.strptime(start_time, time_format)
            time_diff_minutes = time_diff.seconds // 60

            if abs(int(record.minutes) - int(time_diff_minutes)) > 0.1:
                print("Problem found with record on line "+str(ind+1))
                print("Expected record minutes: "+str(time_diff_minutes))
                print("Line values: "+record.csv_format())
                dirtylines += 1
        if dirtylines > 0:
            print("Counted "+str(dirtylines)+ " faulty line" + ("s" if dirtylines > 1 else "") + "(out of {})".format(len(lines)))
        else:
            print("Got {} healthy lines out of {}.".format(len(lines), len(lines)))

    use_description = command_line_parse.description is not None
    use_projects = command_line_parse.projects is not None

    def set_to_str(string_me, d=set_delim):
        """
        Format an iterable as a delimited string
        :param string_me: Iterable
        :param d: Delimiter
        :return:
        """
        outstring = ""
        for c in string_me:
            if c == "":
                continue
            outstring += (c + d)
        outstring = outstring[:-1*(len(d))]
        return outstring

    if starting_entry:
        new_entry = csv_entry(nowstring, command_line_parse.labels, command_line_parse.projects if use_projects else "",
                              command_line_parse.description if use_description else "", "", "")

        lines.append(new_entry.csv_format())
        print("Starting time: "+nowstring)
        finish(lines)

    elif closing_entry:  # closing the session
        lineitems = lastline_vals
        unfinished_entry = csv_entry(*lineitems)

        existing_labels = set(unfinished_entry.labels.split(set_delim))
        new_labels = set(command_line_parse.labels.split(set_delim))
        all_labels = existing_labels.union(new_labels)

        existing_projects = set(unfinished_entry.projects.split(set_delim))
        new_projects = set(command_line_parse.projects.split(set_delim)) if command_line_parse.projects is not None else {}
        all_projects = existing_projects.union(new_projects)

        if existing_labels == {default_label_string} and all_labels == existing_labels:
            warnings.warn(RuntimeWarning("Got only the default label at the beginning and end of session."))

        else:
            try:
                if len(all_labels) > 1:
                    all_labels.remove(default_label_string)
            except KeyError:
                pass
                
                
        if existing_projects == {default_label_string} and all_projects == existing_projects:
            warnings.warn(RuntimeWarning("Got only the default project at the beginning and end of session."))
            
        else:
            try:
                if len(all_projects) > 1:
                    all_projects.remove(default_label_string)
            except KeyError:
                pass
                

        unfinished_entry.labels = set_to_str(all_labels)
        unfinished_entry.projects = set_to_str(all_projects)

        if unfinished_entry.description == "" and command_line_parse.description is None:
            warnings.warn(RuntimeWarning("Did not get session description."))

        if command_line_parse.description is not None:
            unfinished_entry.description = unfinished_entry.description + (" + " if unfinished_entry.description != "" else "")+ command_line_parse.description

        start_time = unfinished_entry.start_date
        end_time = nowstring

        time_diff = datetime.strptime(end_time, time_format) - datetime.strptime(start_time, time_format)
        time_diff_minutes = time_diff.seconds // 60

        unfinished_entry.end_date = end_time  # there is a closing delim at this point
        unfinished_entry.minutes = time_diff_minutes

        lines[-1] = unfinished_entry.csv_format(close_delim=True)
        print("Ending time: "+nowstring)
        print("Worked for {} minutes".format(time_diff_minutes))
        print("Earned: "+to_truncated_string(client.hourly_wage*time_diff_minutes/60)+client.currency_symbol)
        finish(lines)

        
except SystemExit as s:
    # pause and unpause, finish
    if not args_parsed:  #  arg parse error, otherwise it quits without showing the timestamp
        handle_exception(s, _print=False)

except BaseException as e:
    handle_exception(e)















