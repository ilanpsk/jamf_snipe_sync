# Asset Management Synchronization

This project synchronizes items and users between Jamf and Snipe-IT asset management systems.

## Project Structure

- `models/jamf_model.py`: Defines the `JamfItem` model.
- `models/snipe_model.py`: Defines the `SnipeItItem` model.
- `app.py`: Entry point for the script, calls the `sync_items` function.
- `config.py`: Configuration file for environment variables.

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install pydantic
    ```

4. Set up environment variables:
    - Use the config file.
   or
    - Create a `.env` file in the root directory of the project.
    - Add the following variables to the `.env` file:
        ```env
        JAMF_API_URL=<your_jamf_api_url>
        JAMF_USERNAME=<your_jamf_username>
        JAMF_PASSWORD=<your_jamf_password>
        SNIPEIT_API_URL=<your_snipeit_api_url>
        SNIPEIT_API_TOKEN=<your_snipeit_api_token>
        ```

5. Uncomment the `load_dotenv()` line in `config.py`:
    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

## Usage

Run the script to synchronize items and users:
```sh
python app.py
```

## Models

### `JamfItem`
Represents a model in the Jamf asset management system.  
**Attributes**:  
- `name` (str): The name of the item.
- `serial_number` (str): The serial number of the item.
- `model_identifier` (str): The model identifier.
- `assigned_user` (Optional[str]): The user assigned to the item.
- `model_name` (str): The name of the model.

### `SnipeItItem`
Represents a model in the Snipe-IT asset management system.  
**Attributes**:  
- `name` (str): The name of the item.
- `serial` (str): The serial number of the item.
- `assigned_user` (Optional[str]): The user assigned to the item.
- `model` (str): The model name.
- `model_number` (str): The model number.

