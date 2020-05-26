import re
import random
import requests
import time
import pygsheets
from bs4 import BeautifulSoup

gc = pygsheets.authorize(service_file='client_secret.json')
name_of_spreadsheet = 'Copy of DATA SHARING SCRAPING PORTAL'


# def get_row_range(list_of_rows, start, stop):
#     # rows = {}
#     rows = []
#     # count = start
#     for row in range(start, stop+1):
#         # print(wrk1.get_row(row))
#         rows.append(list_of_rows.get_row(row))
#         # rows[str(count)] = wrk1.get_row(row)
#         # count += 1
#     return rows



# Random USER AGENT


def random_user_agent():
    list_of_user_agent = [
        'Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.24 Safari/537.36',
        'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.34 (KHTML, like Gecko) Qt/4.8.2'
    ]
    return random.choice(list_of_user_agent)

# FIND token from response gotten


def find_token(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tag = soup.select_one('meta[name="csrf-token"]')
    csrf_token = {"_token": meta_tag.attrs.get(
        "content").lower()}

    return csrf_token

# extract text in between tags from the response gotten


def res_text(res):
    soup = BeautifulSoup(res.text, "html.parser")
    res_text = soup.find("h5").find_all(text=True, recursive=False)[
        0], soup.find("h3").find_all(text=True, recursive=False)[0]

    return res_text[0] + res_text[1]

# write error message to file
def write_error_log(error_message):
    file = open('error_log.txt', 'a+')
    file.write(str(error_message) + '\n')
    file.close()
    
# get user health details from a row
def get_health_details(worksheet_row, pos_id):
    _choice = {'yes': 1, 'no': 0, '': 0,
               'unknown': 2, 'maybe': 2, 'not sure': 2}
    if pos_id == 'have_fever':
        return _choice[str(worksheet_row[12]).lower()]

    elif pos_id == 'have_cough':
        return _choice[str(worksheet_row[13]).lower()]

    elif pos_id == 'difficult_breath':
        return _choice[str(worksheet_row[14]).lower()]

    elif pos_id == 'have_rigor':
        return _choice['no']

    elif pos_id == 'other_symptoms':
        other_symptoms = []
        check_for_other_symptoms = {
            'appetite': worksheet_row[15],
            'diarrhoea': worksheet_row[17],
            'lost_taste': worksheet_row[18],
            'lost_smell': worksheet_row[19],
            'fatigue_or_body_pain': worksheet_row[20],
            'stomach_ache': worksheet_row[21],
            'chest_pain': worksheet_row[22]
        }
        for symptom in check_for_other_symptoms:
            if (str(check_for_other_symptoms[symptom]).lower() == 'yes'):
                other_symptoms.append(symptom)
        if (len(other_symptoms) == 0):
            return 'none_of_above'
        else:
            return str(other_symptoms)

    elif pos_id == 'contact_traveller':
        return _choice[str(worksheet_row[24]).lower()]

    elif pos_id == 'gathering':
        return _choice[str(worksheet_row[24]).lower()]

    elif pos_id == 'past_medical_conditions':
        return _choice['no']

    elif pos_id == 'contact_exposed_healthcare':
        return   _choice[str(worksheet_row[24]).lower()]
    else:
        raise SystemError('Health details Not found...')
# get user contact details from a row


def get_contact_details(worksheet_row, pos_id):
    if pos_id == 'first_name':
        if (str(worksheet_row[1]).isdigit == True):
            # raise SystemError('First Name Error => ' + str(worksheet_row[1]))
            error_message = {
                'error': 'First Name Error => ' + str(worksheet_row[1])}
            write_error_log(error_message)
            return list(error_message.keys())[0]
        else:
            return worksheet_row[1]
    elif pos_id == 'last_name':
        if (str(worksheet_row[2]).isdigit == True):
            # raise SystemError('Last Name Error => ' + str(worksheet_row[2]))
            error_message = {
                'error': 'Last Name Error => ' + str(worksheet_row[2])}
            write_error_log(error_message)
            return list(error_message.keys())[0]
        else:
            return worksheet_row[2]
    elif pos_id == 'gender':
        g_list = ['male', 'female']
        gender = str(worksheet_row[3]).lower()
        if (gender not in g_list):
            # raise SystemError('Gender Error => ' + gender)
            error_message = {'error': 'Gender Error => ' + gender}
            write_error_log(error_message)
            return list(error_message.keys())[0]
        else:
            return gender
    elif pos_id == 'date_of_birth':
        # format => dd-mm-yy, former => # 6/15/2006
        d_list = str(worksheet_row[4]).split('/')
        return d_list[1] + '-' + d_list[0] + '-' + d_list[2]
    elif pos_id == 'phone_number':
        regex = "^[0]\d{10}$"
        phone_number = str(worksheet_row[5])
        if (re.search(regex, phone_number)):
            return phone_number
        else:
            # raise SystemError('Phone Number Error => ' + phone_number)
            error_message = {'error': 'Phone Number Error => ' + phone_number}
            write_error_log(error_message)
            return list(error_message.keys())[0]

    elif pos_id == 'address':
        return worksheet_row[6]
    elif pos_id == 'lga':
        return worksheet_row[10]
    elif pos_id == 'ward':
        return worksheet_row[11]

    raise SystemError('Contact details Not Found...')


spreadsheet = gc.open(name_of_spreadsheet)
#
spreadsheet_url = spreadsheet.url
spreadsheet_id = spreadsheet.id
spreadsheet_title = spreadsheet.title

# get worksheets
wrks = spreadsheet.worksheets()
length_of_wrks = len(spreadsheet.worksheets())
# sheet2 = spreadsheet.sheet2
# print the first worksheet
# wrk1 = wrks[0].get_all_values()
# print(wrk1[0])
# print(length_of_wrks)
# wrk = wrks[0]
# print(wrk)
# no_of_rows = wrk.rows
# print(no_of_rows)
#
# get_first_col = wrk.get_row(no_of_rows)[0] #Boolean
# print(get_first_col)
# print(no_of_rows, ' => ' , length_of_wrks , ' => ' , get_first_col)

# print(row_range[0][0])
# print(row_range)
# for record_key in row_range:
# if (row_range[record_key][0] == 'FALSE'):
#     print(row_range[record_key])
# print(str(record_key) + ' => ',
#   get_contact_details(row_range[record_key], 'phone_number'))
# get_row_range = get_row_range(no_of_rows, start, stop)
# row_name = wrk1.get_row(1)
# row = wrk1.get_row(11900)

# for i in range(12,26):
#     print(str(i) + ': ' + str(row_name[i]) + ' => ' + str(row[i]))


# print(len(row))
