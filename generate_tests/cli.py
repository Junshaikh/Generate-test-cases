import os
import re
import google.generativeai as genai
import requests
import base64
import argparse
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def clean_gherkin_output(text):
    text = re.sub(r"\*\*Scenario\s*\d*.*\*\*", "", text)
    text = re.sub(r"```gherkin", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    text = re.sub(r"Scenario\s*\d*:", "Scenario:", text)
    return text.strip()

def sanitize_filename(name):
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name

def get_unique_filename(folder_path, base_filename):
    full_path = os.path.join(folder_path, base_filename + ".txt")
    counter = 1
    while os.path.exists(full_path):
        full_path = os.path.join(folder_path, f"{base_filename}_{counter}.txt")
        counter += 1
    return os.path.basename(full_path)

def generate_test_cases(requirement, squad, custom_filename=None, skip_upload=False, tag=None, other_tags=None, background=None, additional_background=None):
    squad = sanitize_filename(squad)
    suggested_filename = sanitize_filename(requirement)
    base_filename = sanitize_filename(custom_filename) if custom_filename else suggested_filename
    folder_path = f"test-cases/{squad}"
    os.makedirs(folder_path, exist_ok=True)

    final_filename = get_unique_filename(folder_path, base_filename)
    local_path = os.path.join(folder_path, final_filename)

    model = genai.GenerativeModel("gemini-2.0-flash")

    # Construct prompt
    prompt = (
        f"You are a QA engineer for Talabat, a food delivery application.\n"
        f"Generate Gherkin-style functional test cases based on the following requirement:\n\n"
        f"{requirement.strip()}\n\n"
    )

    if background:
        prompt += (
            f"Include this background in the test cases:\n"
            f"- This is for Talabat food delivery application\n"
            f"- {background.strip()}\n"
        )
    else:
        prompt += (
            f"Assume this is for Talabat food delivery app. Your scenarios should reflect that domain.\n"
        )

    if additional_background:
        prompt += f"Additional setup context (include in Background):\n- {additional_background.strip()}\n"

    prompt += (
        "\n\nImportant:\n"
        "- Only return valid clean Gherkin syntax (no markdown, no ```gherkin).\n"
        "- Include a `Background:` section before scenarios.\n"
        "- Test scenarios should focus on the Talabat app (ordering food, grocery, pharmcay, dineout, talabat mart, stores, payments, delivery, etc).\n"
        "- Test scenarios for food order is tapping food icon from homescreen, it will navigate to food vendor list, user can search food or items, user can filter by cuisines, filter by ratings, sort by, can make vendor favourites by clicking on heart icon, can see vendor details likve vendor name ratings delivery time and delivery fee on vendor card, on the top vendor list there is vendor collection like 'super saver' and on clicking that icon it will list all the food vendor list part of that collection .\n"
        "- Test scenarios for Dineout order, it is only in UAE country,  is tapping DineOut icon from homescreen, it will navigate to the dineout restaurants list, upon clicking restaurant card it will open up the to see the location and call option and menu and amenities, photo gallery and Pay bill option, when user clicks on pay billthen user can input the bill amount and can click on Unlock discount, after that user navigates to the checkout page where user have option to pay by new card and saved card and talabat credit and postpaid but not with cash .\n"
        "- Test scenarios for Grocery vendor screen has search for products or stores, multi basket icon on the top, all supermarkets on the top swim lane below search bar, then below it recommended grocery stores, then ads banners, then Browse All stores with some filters like offers and under30mins and pro, when user tap on any grocery stores it navigates to the catalog screen .\n"
        "- Test scenarios for Grocery catalog screen has search icon on the top and heart icon to make it favourites and share icon and back button, grocery store name showing with cuisine and ratings and delivery time and delivery fee and delivered by talabat or store if pro user then will show the Free delivery with pro tag, banks offers will display , user can select from the grocery Menu categories, View cart button will enable when user add the minimum order amount, on clicking ‘View cart’ user will navigate to the Cart screen .\n"
        "- Test scenarios for Grocery catalog screen has ‘Add items’ button on the top and clicking it will take back to the menu screen, back option, added item with price valued edit option, on click edit will open the item bottom sheet to modify item details, All user to enter Special request, allow user to enter the voucher code, show the Payment summary with Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied, also for some user will show the option to pay by postpaid, also will have the option to proceed to checkout .\n"
        "- Test scenarios for Grocery checkout screen has Add showing on the top with map and also allow to change or add new address, Displayed the estimated delivery time, rider tip option , Pay with option with talabat credit wallet, Postpaid, saved cards, add new card or by cash, for Android additional Google pay option, for additional iPhone Apple Pay and for Huawei no google or Apple Pay option, Payment summary will display Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied .\n"
        
    )

    response = model.generate_content(prompt)
    test_cases_raw = response.text
    test_cases = clean_gherkin_output(test_cases_raw)

    # Build tag line
    tags_line = []
    if tag:
        tags_line.append(f"@{tag}")
    if other_tags:
        extra_tags = re.split(r"[,\s]+", other_tags.strip())
        tags_line.extend([t if t.startswith("@") else f"@{t}" for t in extra_tags if t])

    if tags_line:
        test_cases = " ".join(tags_line) + "\n\n" + test_cases

    with open(local_path, "w") as file:
        file.write(test_cases)

    print(f"✅ Test cases saved to {local_path}")

    if not skip_upload:
        upload_to_github(test_cases, final_filename, squad, tag, other_tags)
    else:
        print("⚠️ Skipping GitHub upload (--no-upload enabled)")

def upload_to_github(content, file_name, squad, tag=None, other_tags=None):
    github_token = os.getenv("GITHUB_TOKEN")
    repo_owner = os.getenv("GITHUB_REPO_OWNER")
    repo_name = os.getenv("GITHUB_REPO_NAME")
    file_path = f"test-cases/{squad}/{file_name}"
    branch = os.getenv("GITHUB_BRANCH", "main")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    file_url = f"https://github.com/{repo_owner}/{repo_name}/blob/{branch}/{file_path}"

    tag_msg = ""
    if tag or other_tags:
        combined_tags = []
        if tag:
            combined_tags.append(f"`@{tag}`")
        if other_tags:
            extra_tags = re.split(r"[,\s]+", other_tags.strip())
            combined_tags.extend([f"`@{t}`" if not t.startswith("@") else f"`{t}`" for t in extra_tags if t])
        tag_msg = "\n\n**Tags**: " + ", ".join(combined_tags)

    message = f"Add test cases for `{file_name}` in `{squad}` squad.{tag_msg}\n\nPreview: {file_url}"
    encoded_content = base64.b64encode(content.encode()).decode()

    data = {
        "message": message,
        "content": encoded_content,
        "branch": branch
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"✅ Test case uploaded to GitHub: {file_url}")
    else:
        print(f"❌ Failed to upload file: {response.status_code} - {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Generate Gherkin test cases from a requirement.")
    parser.add_argument("--requirement", "-r", help="Requirement description", default=os.getenv("REQUIREMENT"))
    parser.add_argument("--squad", "-s", help="Squad name (e.g., squad-auth)", default=os.getenv("SQUAD"))
    parser.add_argument("--file-name", "-f", help="Custom file name", default=os.getenv("FILE_NAME"))
    parser.add_argument("--tag", "-t", help="Priority tag (e.g., P0, P1)", default=os.getenv("TAG"))
    parser.add_argument("--other-tags", help="Other tags (e.g., smoke, login)", default=os.getenv("OTHER_TAGS"))
    parser.add_argument("--background", help="Primary background context", default=os.getenv("BACKGROUND"))
    parser.add_argument("--additional-background", help="Extra background info (e.g., logged-in user)", default=os.getenv("ADDITIONAL_BACKGROUND"))
    parser.add_argument("--no-upload", action="store_true", default=os.getenv("NO_UPLOAD") == "true")

    args = parser.parse_args()
    generate_test_cases(
        args.requirement, args.squad, args.file_name, args.no_upload,
        args.tag, args.other_tags, args.background, args.additional_background
    )

if __name__ == "__main__":
    main()
