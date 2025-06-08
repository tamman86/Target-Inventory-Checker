import requests
import json
import FreeSimpleGUI as sg

sg.theme('DarkGrey')

layout = [
    [sg.Text("Enter API Key:")],
    [sg.Input(key="-APIKEY-", readonly=False),
     sg.Button(button_text="Clear", key="-CLEAR-")],
    [sg.Text("Enter TCIN Number:"), sg.Input(key="-TCINNUMBER-", readonly=False)],
    [sg.Text("Enter ZIP Code:"), sg.Input(key="-ZIPCODE-", readonly=False)],
    [sg.Button("Search for Item", key="-SEARCH-"), sg.Button("Exit")],
    [sg.Text("Output Log:")],
    [sg.Output(size=(80, 20), key='-OUTPUT-')]
]

window = sg.Window("Target Stock Checker", layout,
                   finalize=True)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    elif event == "-CLEAR-":
        window["-APIKEY-"].update("")

    elif event == "-SEARCH-":
        window['-OUTPUT-'].update('')                   # Clear output window

        API_KEY = values["-APIKEY-"]
        TCIN_NUMBER = values["-TCINNUMBER-"]
        ZIPCODE = values["-ZIPCODE-"]

        if not all([API_KEY, TCIN_NUMBER, ZIPCODE]):
            print("Error: Please fill in all fields.")
            continue                                    # Skips the API call if any fields are empty

        # set up the request parameters
        params = {
          'api_key': API_KEY,
          'type': 'store_stock',
          'tcin': TCIN_NUMBER,
          #'tcin': '90380994',                                  (Special Delivery diapers)
          'store_stock_zipcode': ZIPCODE,
        }

        # make the http GET request to RedCircle API
        api_result = requests.get('https://api.redcircleapi.com/request', params)
        response_json = api_result.json()

        # credits remaining
        creditsRemaining = api_result.json()['request_info']['credits_remaining']
        print("Credits Remaining: " + str(creditsRemaining))
        print("-" * 30)

        found_in_stock = False
        store_stock_results = response_json.get("store_stock_results", [])

        for store in store_stock_results:
            if store.get('in_stock'):
                print(f"Store: {store.get('store_name', 'Unknown Store')}")
                print(f"In Stock: {store.get('in_stock')}")
                print(f"Stock Level: {store.get('stock_level', 'Not Available')}")
                print('\n')
                found_in_stock = True

        if not found_in_stock:
            print(f"Item {TCIN_NUMBER} not in stock at any stores near ZIP code {ZIPCODE}.")