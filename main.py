import requests
import json
import FreeSimpleGUI as sg

sg.theme('DarkTeal9')

# Inputs

input_layout = [
    [sg.Frame("Credentials", [
        [sg.Text("API Key:", size=(10, 1)),
         sg.Input(key="-APIKEY-", size=(30, 1), password_char='*'),
         sg.Button("Clear", key="-CLEAR-", size=(6, 1))]
    ], expand_x=True)],

    [sg.Frame("Search Parameters", [
        [sg.Text("TCIN:", size=(10, 1)), sg.Input(key="-TCINNUMBER-", size=(38, 1))],
        [sg.Text("Zip Code:", size=(10, 1)), sg.Input(key="-ZIPCODE-", size=(38, 1))],
    ], expand_x=True)],

    [sg.Push(), sg.Button("Search Inventory", key="-SEARCH-", size=(15, 1), button_color=('white', '#2c3e50')),
     sg.Button("Exit", size=(10, 1))]
]

# Results Table
headings = ['Store Name', 'Stock Status', 'Level', 'Address', 'Distance', 'City']

results_layout = [
    [sg.Text("Search Results:", font=("Helvetica", 12, "bold"))],
    [sg.Table(values=[], headings=headings,
              max_col_width=35,
              auto_size_columns=False,
              col_widths=[25, 10, 10, 35, 10, 25],
              display_row_numbers=True,
              justification='left',
              num_rows=10,
              key='-TABLE-',
              row_height=35,
              tooltip='Search Results Table')]
]

# Combined Layout
layout = [
    [sg.Column(input_layout, vertical_alignment='top'), sg.VSeparator(),
     sg.Column(results_layout, vertical_alignment='top')],
    [sg.Text("Ready", key="-STATUS-", size=(60, 1), relief=sg.RELIEF_SUNKEN, text_color='yellow')]
]

window = sg.Window("Target Stock Checker v2.0", layout, finalize=True)

# Event Loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    elif event == "-CLEAR-":
        window["-APIKEY-"].update("")

    elif event == "-SEARCH-":
        # Visual feedback that search is starting
        window['-STATUS-'].update("Searching... please wait.")
        window.refresh()  # Force GUI update before the blocking API call

        API_KEY = values["-APIKEY-"]
        TCIN_NUMBER = values["-TCINNUMBER-"]
        ZIPCODE = values["-ZIPCODE-"]

        # Validation
        if not all([API_KEY, TCIN_NUMBER, ZIPCODE]):
            sg.popup_error("Missing Information", "Please fill in API Key, TCIN, and Zip Code.")
            window['-STATUS-'].update("Error: Missing fields")
            continue

        params = {
            'api_key': API_KEY,
            'type': 'store_stock',
            'tcin': TCIN_NUMBER,
            'store_stock_zipcode': ZIPCODE,
        }

        try:
            # API Call
            api_result = requests.get('https://api.redcircleapi.com/request', params)

            # Check if request was successful
            if api_result.status_code != 200:
                window['-STATUS-'].update(f"API Error: {api_result.status_code}")
                sg.popup_error(f"API returned status code {api_result.status_code}")
                continue

            response_json = api_result.json()

            # Credits Logic
            req_info = response_json.get('request_info', {})
            credits_remaining = req_info.get('credits_remaining', 'Unknown')

            store_stock_results = response_json.get("store_stock_results", [])

            # Format data for the Table Widget
            table_data = []
            found_in_stock = False

            for store in store_stock_results:
                # We allow all stores into the table, but we can color code or filter logic here
                is_in_stock = store.get('in_stock', False)

                if is_in_stock:
                    found_in_stock = True
                    stock_str = "YES"
                else:
                    stock_str = "NO"

                row = [
                    store.get('store_name', 'Unknown'),
                    stock_str,
                    store.get('stock_level', 'N/A'),
                    store.get('address', 'N/A'),
                    store.get('distance', 'N/A'),
                    store.get('city', 'N/A'),
                ]
                table_data.append(row)

            # Update the Table
            window['-TABLE-'].update(values=table_data)

            # Update Status Bar
            status_msg = f"Search Complete. Credits Remaining: {credits_remaining}"
            if not found_in_stock:
                status_msg += " (No items found in stock)"

            window['-STATUS-'].update(status_msg)

        except Exception as e:
            window['-STATUS-'].update("An error occurred during execution.")
            sg.popup_error(f"Exception: {str(e)}")

window.close()