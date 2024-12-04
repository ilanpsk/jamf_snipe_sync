from config import SNIPEIT_API_URL, SNIPEIT_API_TOKEN
from models import SnipeItItem, ModelItem, JamfItem
from requests.exceptions import HTTPError
import requests
import time

HEADERS_SNIPEIT = {"Authorization": f"Bearer {SNIPEIT_API_TOKEN}", "Accept": "application/json"}


def fetch_snipeit_items():
    """
    Fetches items from the JAMF API and returns them as a list of JamfItem objects.

    Returns:
        list: A list of JamfItem objects containing information about the computers.
    """
    response = requests.get(f"{SNIPEIT_API_URL}/api/v1/hardware", headers=HEADERS_SNIPEIT)

    response.raise_for_status()
    return [SnipeItItem(

        name=item['name'],
        serial=item['serial'],
        assigned_user=item['assigned_to']['username'] if item['assigned_to'] else None,
        model=item['model']['name'],
        model_number=item['model_number'],
    ) for item in response.json()["rows"]]


def create_snipeit_item(item: JamfItem, model_item: ModelItem):
    """
    Creates a new hardware item in the Snipe-IT system.

    Args:
        item (JamfItem): The JamfItem object containing the hardware details.
        model_item (ModelItem): The ModelItem object containing the model details.

    Returns:
        dict: The response from the Snipe-IT API after creating the item.
    """
    payload = {
        "name": item.name,
        "status_id": 2,
        "model_id": model_item.model_id,
        "serial": item.serial_number,
    }
    print(payload)
    response = requests.post(f"{SNIPEIT_API_URL}/api/v1/hardware", headers=HEADERS_SNIPEIT, json=payload)
    response.raise_for_status()
    print(response.json())
    return response.json()


def checkout_snipeit_item(item: JamfItem, snipe_id: int, assigned_user: int):
    """
    Checks out a hardware item to a user in the Snipe-IT system.

    Args:
        item (JamfItem): The JamfItem object containing the hardware details.
        snipe_id (int): The ID of the hardware item in Snipe-IT.
        assigned_user (int): The ID of the user to whom the item is assigned.

    Returns:
        dict: The response from the Snipe-IT API after checking out the item.
    """
    payload = {
        "id": snipe_id,
        "status_id": 2,
        "checkout_to_type": "user",
        "assigned_user": assigned_user,
    }
    response = requests.post(f"{SNIPEIT_API_URL}/api/v1/hardware/{snipe_id}/checkout", headers=HEADERS_SNIPEIT,
                             json=payload)
    response.raise_for_status()
    return response.json()


def get_user_id(username: str):
    """
    Retrieves the user ID from the Snipe-IT system based on the username.

    Args:
        username (str): The email address of the user.

    Returns:
        int or None: The user ID if found, otherwise None.
    """
    base_url = f"{SNIPEIT_API_URL}/api/v1/users"
    params = {"email": username}
    max_retries = 10
    backoff_factor = 0.1

    for i in range(max_retries):
        try:
            response = requests.get(base_url, params=params, headers=HEADERS_SNIPEIT)
            response.raise_for_status()
            data = response.json()
            if data['rows']:
                return data['rows'][0]['id']
            else:
                return None
        except HTTPError as http_err:
            if response.status_code == 429:
                sleep_time = backoff_factor * (2 ** i)  # Exponential backoff
                time.sleep(sleep_time)
            else:
                raise http_err


def fetch_snipeit_models():
    """
    Fetches models from the Snipe-IT API and returns them as a list of ModelItem objects.

    Returns:
        list: A list of ModelItem objects containing information about the models.
    """
    response = requests.get(f"{SNIPEIT_API_URL}/api/v1/models", headers=HEADERS_SNIPEIT)
    response.raise_for_status()
    return [ModelItem(
        model_name=model['name'],
        model_number=model['model_number'],
        model_id=model['id']
    ) for model in response.json()["rows"]]


def create_snipeit_model(model_item: ModelItem):
    """
    Creates a new model in the Snipe-IT system.

    Args:
        model_item (ModelItem): The ModelItem object containing the model details.

    Returns:
        dict: The response from the Snipe-IT API after creating the model.
    """
    payload = {
        "name": model_item.model_name,
        "model_number": model_item.model_number,
        "category_id": 3,
    }
    response = requests.post(f"{SNIPEIT_API_URL}/api/v1/models", headers=HEADERS_SNIPEIT, json=payload)
    response.raise_for_status()
    return response.json()


def fetch_snipeit_item_by_serial(serial: str):
    """
    Fetches a hardware item from the Snipe-IT API based on its serial number.

    Args:
        serial (str): The serial number of the hardware item.

    Returns:
        dict or None: The hardware item details if found, otherwise None.
    """
    base_url = f"{SNIPEIT_API_URL}/api/v1/hardware/byserial/{serial}"
    max_retries = 10
    backoff_factor = 0.1

    for i in range(max_retries):
        try:
            response = requests.get(base_url, headers=HEADERS_SNIPEIT)
            response.raise_for_status()
            rows = response.json().get('rows', [])
            if rows:
                return rows[0]
            else:
                return None
        except HTTPError as http_err:
            if response.status_code == 429:
                sleep_time = backoff_factor * (2 ** i)  # Exponential backoff
                time.sleep(sleep_time)
            else:
                raise http_err
