# main.py
import os
from page_handlers.scp_handler import generate_content  # or whatever you renamed s_in_handler.py
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Example usage:
    form_data = {
        "operation_details": "A new shop deployment to production environment.",
        "release_branch_name": "release/v1.2.3",
        "preparation_sql_query": "SELECT * FROM shops WHERE shop_id = 123;" ,
        "preparation_screenshot": "link to screenshot"
    }

    try:
        title, content = generate_content(form_data=form_data)
        print("Title:", title)
        print("Content:", content)
    except Exception as e:
        print(f"Error in main.py: {e}")
