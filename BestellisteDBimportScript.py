import time

import pandas as pd
import requests
from copy import deepcopy

# Constants
EXCEL_PATH = "test_data/Bestellliste-Defender-IMPORT.xlsx"
ORDERABLE_PARTS_ENDPOINT = "http://localhost:8080/api/orderable_parts"
PROJECT_PARTS_ENDPOINT_TEMPLATE = "http://localhost:8080/api/project/parts/{}"
PROJECT_ENDPOINT = "http://localhost:8080/api/projects"
MANUFACTURER_ENDPOINT = "http://localhost:8080/api/manufacturers"
MANUFACTURER_PARTS_ENDPOINT_TEMPLATE = "http://localhost:8080/api/manufacturer/parts/{}"

# Default orderable part with hardcoded default values
DEFAULT_ORDERABLE_PART = {
    "name": "No Name Entered",
    "category": "No Category Entered",
    "inStock": 0,
    "price": {
        "priceEuro": 0.0
    },
    "manufacturerInfo": {
        "manufacturerName": "No Manufacturer Entered",
        "manufacturerPartDescription": "No Description Entered",
        "manufacturerPartNumber": "No Part Number Entered"
    },
    "project":{}
}


# Function to create a payload from a dataframe row
def create_payload(row):
    payload = deepcopy(DEFAULT_ORDERABLE_PART)  # Use deepcopy here

    # Update fields if they are not NaN
    if pd.notna(row["Bezeichnung "]):
        payload["manufacturerInfo"]["manufacturerPartDescription"] = row["Bezeichnung "]
        payload["name"] = row["Bezeichnung "]

    if pd.notna(row["Kategorie"]):
        payload["category"] = row["Kategorie"]

    if pd.notna(row["Menge"]):
        payload["inStock"] = row["Menge"]

    if pd.notna(row["Einzelpreis"]):
        payload["price"]["priceEuro"] = row["Einzelpreis"]

    if pd.notna(row["Händler"]):
        payload["manufacturerInfo"]["manufacturerName"] = row["Händler"]

    if pd.notna(row["Artikelnummer"]):
        payload["manufacturerInfo"]["manufacturerPartNumber"] = row["Artikelnummer"]

    if pd.notna(row["DI"]):
        payload["project"]["Diana"] = row["Menge DI"]

    if pd.notna(row["DA"]):
        payload["project"]["Darcy"] = row["Menge DA"]
    return payload


def clear_dbs():
    requests.delete(ORDERABLE_PARTS_ENDPOINT)
    requests.delete(PROJECT_ENDPOINT)
    requests.delete(MANUFACTURER_ENDPOINT)


if __name__ == '__main__':

    clear_dbs()

    # Load the excel file into a dataframe
    df = pd.read_excel(EXCEL_PATH)

    # Create a list of payloads
    payloads = [create_payload(row) for _, row in df.iterrows()]

    # ------------------- Inject Parts -------------------
    part_project_map = []
    part_manufacturer_map = {}

    for payload in payloads:
        try:
            response = requests.post(ORDERABLE_PARTS_ENDPOINT, json=payload)
            if response.status_code == 201:  # Assuming 201 means successful creation
                returned_data = response.json()
                part_project_map.append({returned_data['id']:payload['project']})
                part_manufacturer_map[returned_data['id']] = {
                    "manName":returned_data['manufacturerInfo']['manufacturerName'],
                    "inStock": returned_data['inStock']
                }
            else:
                print("Error while creating orderable part: {}".format(response.text))
                print(payload)
        except Exception as e:
            print("Error while making request: {}".format(e))
            print(payload)
    # ------------------- Inject Darlene and Diana -------------------

    project_inject_response_darcy = requests.post(PROJECT_ENDPOINT, json={
        "name": "Darcy",
        "notes": "TODO",
        "price": {
            "priceEuro": 0
        },
        "orderableParts": {}
    }).json()
    project_inject_response_diana = requests.post(PROJECT_ENDPOINT, json={
        "name": "Diana",
        "notes": "TODO",
        "price": {
            "priceEuro": 0
        },
        "orderableParts": {}
    }).json()

    # ------------------- Map Parts to Project DI or DA -------------------
    project_parts_payload_da = {}
    project_parts_payload_di = {}

    for part_mapping in part_project_map:
        for part_id, projects in part_mapping.items():
            if 'Darcy' in projects:
                project_parts_payload_da[part_id] = projects['Darcy']
            if 'Diana' in projects:
                project_parts_payload_di[part_id] = projects['Diana']

    response_da = requests.post(PROJECT_PARTS_ENDPOINT_TEMPLATE.format(project_inject_response_darcy['id']), json=project_parts_payload_da)
    if response_da.status_code != 200:
        print("Error while mapping parts to project: {}".format(response_da.text))
        print(project_parts_payload_da)
    response_di = requests.post(PROJECT_PARTS_ENDPOINT_TEMPLATE.format(project_inject_response_diana['id']), json=project_parts_payload_di)
    if response_di.status_code != 200:
        print("Error while mapping parts to project: {}".format(response_di.text))
        print(project_parts_payload_di)

    # ------------------- inject Manufacturer -------------------

    imported_manufacturers = {}

    # Using set to store unique manufacturers
    unique_manufacturers = set()
    for _, row in df.iterrows():
        if pd.notna(row["Händler"]):
            unique_manufacturers.add(row["Händler"])
    if not unique_manufacturers:
        unique_manufacturers.add("No Name Entered")

    payloads = [{'name': name} for name in unique_manufacturers]

    for payload in payloads:
        response = requests.post(MANUFACTURER_ENDPOINT, json=payload)
        imported_manufacturers[payload['name']] = response.json()
        if response.status_code != 201:
            print("Error while creating manuf: {}".format(response.text))
            print(payload)

    # ------------------- Map Parts to Manufacturer -------------------

    for manufacturer_name, db_item in imported_manufacturers.items():
        man_id = db_item['id']
        for part_id, values in part_manufacturer_map.items():
            if manufacturer_name == values['manName']:
                response = requests.post(MANUFACTURER_PARTS_ENDPOINT_TEMPLATE.format(man_id), json={part_id: values['inStock']})
                if response.status_code != 200:
                    print("Error while mapping parts to manuf: {}".format(response.text))
                    print(response.json())

    print("Completed!")
