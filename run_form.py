# import libs
from gsheets import *
from lga import *

SITE_URL = "https://covid19.edohip.com"
API_URL = "https://covid19.edohip.com/api/covid_self_test_response"

# mains

def main():
    print('URL => ', spreadsheet_url)
    print('ID => ', spreadsheet_id)
    print('TITLE => ', spreadsheet_title)
    print('Number of Spreadsheets => ', length_of_wrks)
    sheet_num = int(input('Enter the Sheet Number (e.g: 1 = oredo)  => ')) - 1
    # get worksheet 
    wrk_num = wrks[sheet_num]
    # get number of rows of worksheet
    no_of_rows = wrk_num.rows
    # p
    print('Number of ROWS => ', no_of_rows)
    # Enter row range
    print("ROW RANGE:\n")
    start = int(input("Enter Start range: "))
    stop = int(input("Enter Stop range: ")) + 1
    # TRASH
    TRASH = []
    # go through row range
    for row in range(start, stop): 
        # get a row in worksheet 
        worksheet_row = wrk_num.get_row(row)
        # 
        # 
        # SUBMIT API DATA function
        def submit_api_data(api_headers, api_data):

            # POST request to API
            try:
                api_response = session.post(
                    API_URL, data=api_data, headers=api_headers)
                status_code = api_response.status_code
                if status_code == 200:
                    return res_text(api_response)
                else:
                    error_message = '{' + str(status_code) + ' => ' + str(api_data) + '}'
                    write_error_log(error_message)
                    return "Sorry, An Error Occurred with the API...[" + str(status_code) + "]"


            except requests.exceptions.RequestException as e:
                raise SystemExit(e)


        # start session
        session = requests.Session()
        # goto site
        response = session.get(SITE_URL)
        status_code = response.status_code

        if (status_code == 200):
            # print(str(status_code) + " OK")
            # 
            # 
            token = find_token(response)['_token']
            # print(response.cookies)
            # print('Token Generated for site ' + SITE_URL + ': ' + token)
            # 
            # get first column in worksheet boolean value
            get_first_col = str(worksheet_row[0])
            # 
            if (str(get_first_col).upper() == 'TRUE'):
                print(str(row), ' => ' , get_first_col, ' => ' , 'Done by Somebody else...')
                TRASH.append(row)
                TRASH = []
            else:
                # 
                # 
                # HEADERS for API
                api_headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US, en, q = 0.9',
                    'Connection': 'keep-alive',
                    'Content-Length': '458',
                    'Content-Type': 'application/x-www-form-urlencoded charset = UTF-8',
                    'Cookie': 'XSRF-TOKEN=' + response.cookies['XSRF-TOKEN'] + ';' + ' laravel_session=' + response.cookies['laravel_session'],
                    'Host': SITE_URL[8:],
                    'Origin': SITE_URL,
                    'Referer': SITE_URL+'/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': random_user_agent(),
                    'X-CSRF-TOKEN': token,
                    'X-Requested-With': 'XMLHttpRequest'
                }
                # 
                # 
                # API DATA
                api_data = {
                    '_source': 'website',
                    '_token': token,
                    'have_fever': get_health_details(worksheet_row, 'have_fever'),
                    'have_cough': get_health_details(worksheet_row, 'have_cough'),
                    'difficult_breath': get_health_details(worksheet_row, 'difficult_breath'),
                    'have_rigor': get_health_details(worksheet_row, 'have_rigor'),
                    # list
                    'other_symptoms[]': get_health_details(worksheet_row, 'other_symptoms'),
                    'contact_traveller': get_health_details(worksheet_row, 'contact_traveller'),
                    'gathering': get_health_details(worksheet_row, 'gathering'),
                    'past_medical_conditions[]': get_health_details(worksheet_row, 'past_medical_conditions'),
                    'contact_exposed_healthcare': get_health_details(worksheet_row, 'contact_exposed_healthcare'),
                    # surname/last name/ family name
                    'last_name': get_contact_details(worksheet_row, 'last_name'),
                    'first_name': get_contact_details(worksheet_row, 'first_name'),
                    'gender': get_contact_details(worksheet_row, 'gender'),
                    # dd-mm-yy
                    'date_of_birth': get_contact_details(worksheet_row, 'date_of_birth'),
                    'phone_number': get_contact_details(worksheet_row, 'phone_number'),
                    'email': '',  # optional
                    'address': get_contact_details(worksheet_row, 'address'),
                    'state': '12',
                    'lga': get_lga_number(get_contact_details(worksheet_row, 'lga')),
                    'ward': get_ward_number(get_contact_details(worksheet_row, 'lga'), get_contact_details(worksheet_row, 'ward')),
                    'okhi_place_id': '',
                    'latitude': '',
                    'longitude': ''
                }
                # 
                # 
                if ('error' in list(api_data.values())):
                    write_error_log(row)
                    TRASH.append(row)
                    TRASH = []
                else:
                    API_RESPONSE = submit_api_data(api_headers, api_data)
                    print('Token Generated for site ' + SITE_URL + ': ' + token)
                    print(str(row) + ' => ' + API_RESPONSE)
                time.sleep(5)


if __name__ == "__main__":
    main()
