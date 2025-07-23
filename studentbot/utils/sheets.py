import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import logger, GOOGLE_CREDS, SPREADSHEET_NAME, QUESTIONS_SHEET_NAME

def get_sheet(sheet_name):
    """Returns a worksheet object."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME).worksheet(sheet_name)
        logger.info(f"Successfully accessed Google Sheet: {sheet_name}")
        return sheet
    except Exception as e:
        logger.error(f"Failed to access Google Sheet {sheet_name}: {e}")
        raise

def save_user_to_sheet(user_data):
    """Saves user data to the Google Sheet."""
    try:
        sheet = get_sheet("Users")
        sheet.append_row([
            user_data['user_id'],
            user_data['name'],
            user_data['family_name'],
            user_data['age'],
            user_data['email'],
            user_data['field_of_study'],
            user_data['country'],
            user_data['lang']
        ])
        logger.info(f"Successfully saved user data to sheet for user_id: {user_data['user_id']}")
    except Exception as e:
        logger.error(f"Failed to save user data to sheet for user_id {user_data['user_id']}: {e}")
        raise

def save_isee_to_sheet(user_id, isee_data):
    """Saves ISEE calculation data to the Google Sheet."""
    try:
        sheet = get_sheet("ISEE Calculations")
        sheet.append_row([
            user_id,
            isee_data['family_members'],
            isee_data['annual_income'],
            isee_data['property_status'],
            isee_data.get('property_size', 0),
            isee_data['isee_value'],
            isee_data['scholarship_status'],
            isee_data['scholarship_amount']
        ])
        logger.info(f"Successfully saved ISEE data to sheet for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Failed to save ISEE data to sheet for user_id {user_id}: {e}")
        raise
