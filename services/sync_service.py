import concurrent.futures
from models import ModelItem
from services import (
    JamfService, fetch_snipeit_items, create_snipeit_item, fetch_snipeit_models, create_snipeit_model,
    checkout_snipeit_item, get_user_id, fetch_snipeit_item_by_serial
)


def fetch_all_items():
    """
    Fetches a hardware item from the Snipe-IT API based on its serial number.

    Args:
        serial (str): The serial number of the hardware item.

    Returns:
        dict or None: The hardware item details if found, otherwise None.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        jamf_future = executor.submit(JamfService.fetch_jamf_items)
        snipeit_items_future = executor.submit(fetch_snipeit_items)
        snipeit_models_future = executor.submit(fetch_snipeit_models)

        # Fetch results as they become available
        for future in concurrent.futures.as_completed([jamf_future, snipeit_items_future, snipeit_models_future]):
            try:
                future.result()
            except Exception as exc:
                print(exc)

    # Get the results from the futures
    jamf_items = jamf_future.result()
    snipeit_items = snipeit_items_future.result()
    snipeit_models = snipeit_models_future.result()

    return jamf_items, snipeit_items, snipeit_models


def check_and_create_new_models(jamf_items: list, snipeit_models: list):
    """
    Checks for new models in Jamf items and creates them in Snipe-IT if they do not exist.

    Args:
        jamf_items (list): A list of JamfItem objects.
        snipeit_models (list): A list of ModelItem objects from Snipe-IT.
    """
    for item in jamf_items:
        if not any(model.model_number == item.model_identifier for model in snipeit_models):
            print(f"New model found: {item.model_name}")
            req = create_snipeit_model(ModelItem(model_name=item.model_name, model_number=item.model_identifier))
            print(req)
            if req['status'] != 'success':
                print(f"Error creating model: {item.model_name}")
                continue
            print(f"New model created: {item.model_name}")
    else:
        print("No new models found.")


def check_and_create_new_items(jamf_items: list, snipeit_items: list, snipeit_models: list):
    """
    Checks for new items in Jamf and creates them in Snipe-IT if they do not exist.

    Args:
        jamf_items (list): A list of JamfItem objects.
        snipeit_items (list): A list of SnipeItItem objects.
        snipeit_models (list): A list of ModelItem objects from Snipe-IT.
    """
    for item in jamf_items:
        if not any(snipe_item.serial == item.serial_number for snipe_item in snipeit_items):
            print(f"New item found: {item.serial_number}")
            model_item = next((model for model in snipeit_models if model.model_number == item.model_identifier), None)
            if model_item is None:
                model_item = ModelItem(model_name=item.model_name, model_number=item.model_identifier)
                create_snipeit_model(model_item)
                print(f"New model created: {item.model_name}")
            snipe_item = create_snipeit_item(item, model_item)
            print(f"New item created: {snipe_item['payload']['serial']}")

            # Find the assigned user in Jamf and assign to the same user in Snipe-IT
            if item.assigned_user:
                user_id = get_user_id(item.assigned_user)
                checkout_snipeit_item(item, snipe_item['payload']['id'], user_id)
                print(f"Assigned user updated: {item.assigned_user}")
    else:
        print("No new items found.")


def sync_users_to_items(jamf_items: list):
    """
    Syncs users from Jamf items to Snipe-IT items.

    Args:
        jamf_items (list): A list of JamfItem objects.
    """
    for item in jamf_items:
        if item.assigned_user:
            user_id = get_user_id(item.assigned_user)
            if user_id is None:
                print(f"User {item.assigned_user} not found in Snipe-IT")
                continue
            snipeit_item = fetch_snipeit_item_by_serial(item.serial_number)
            if snipeit_item['assigned_to'] is None:
                snipe_id = snipeit_item['id']
                checkout_snipeit_item(item, snipe_id, user_id)
                print("updated user: ", item.assigned_user, " ", item.asset_tag)


def sync_items():
    """
    Synchronizes items and users between Jamf and Snipe-IT.
    """
    jamf_items, snipeit_items, snipeit_models = fetch_all_items()
    check_and_create_new_models(jamf_items, snipeit_models)
    check_and_create_new_items(jamf_items, snipeit_items, snipeit_models)
    sync_users_to_items(jamf_items)
