import requests
from models import JamfItem
from config import JAMF_API_URL, JAMF_USERNAME, JAMF_PASSWORD


class JamfService:
    """
    Service class to interact with the JAMF API.
    """
    access_token = None

    @staticmethod
    def get_access_token():
        """
        Retrieves and sets the access token for the JAMF API.
        """
        auth_url = f"{JAMF_API_URL}/api/v1/auth/token"
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'
                   }

        response = requests.post(auth_url, auth=(JAMF_USERNAME, JAMF_PASSWORD), headers=headers)
        response.raise_for_status()

        JamfService.access_token = response.json()['token']

    @staticmethod
    def get_headers():
        """
        Returns the headers required for authenticated requests to the JAMF API.
        If the access token is not set, it retrieves a new one.

        Returns:
            dict: A dictionary containing the authorization and accept headers.
        """
        if not JamfService.access_token:
            JamfService.get_access_token()
        return {
            "Authorization": f"Bearer {JamfService.access_token}",
            "Accept": "application/json"
        }

    @staticmethod
    def fetch_jamf_items():
        """
        Fetches items from the JAMF API and returns them as a list of JamfItem objects.

        Returns:
            list: A list of JamfItem objects containing information about the computers.
        """
        headers = JamfService.get_headers()
        all_computers = []
        page = 0
        page_size = 50
        while True:
            response = requests.get(
                f"{JAMF_API_URL}/api/v1/computers-inventory?section=HARDWARE&section=GENERAL&section=USER_AND_LOCATION",
                headers=headers, params={"page": page, "page-size": page_size, "view": "Basic"})
            response.raise_for_status()
            computers = response.json()['results']
            computer_general_section = [computer for computer in computers]
            all_computers.extend(computer_general_section)
            if len(computers) < page_size:
                break
            page += 1
        # return all_computers
        return [JamfItem(

            name=item['general']['name'],
            serial_number=item['hardware']['serialNumber'],
            assigned_user=item['userAndLocation']['username'],
            model_identifier=item['hardware']['modelIdentifier'],
            model_name=item['hardware']['model'],
        ) for item in all_computers]
