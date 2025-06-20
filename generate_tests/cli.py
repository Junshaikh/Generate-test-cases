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

def generate_test_cases(requirement, tribe, squad, custom_filename=None, skip_upload=False, tag=None, other_tags=None, background=None, additional_background=None):
    tribe = sanitize_filename(tribe)
    squad = sanitize_filename(squad)
    suggested_filename = sanitize_filename(requirement)
    base_filename = sanitize_filename(custom_filename) if custom_filename else suggested_filename
    folder_path = os.path.join("test-cases", tribe, squad)
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
        "- Consideration for Home Screen has verticals entry point called ‘Food’ ‘talabat mart’ ‘Groceries’ ‘Pharmacies’ ‘Sweets’ ‘Dineout’ ’Stores’ ‘Giveback’, below it it’s Meals for one swim-lane, trending vendors swim lane, Redeem and Save section which will show Rewards points and Vouchers options, GEM restaurants swim-lane, Order again swim-lane for logged in user, Big Brands near you grocery stores swim lane, Dineout Deals swimlane, also Home Screen has multi basket icon, voice search, search bar to find the vendors, stores, groceries and items, address bar on top to select from the saved address in case of logged in user or new address for guest user .\n"
        "- Consideration for Food order is tapping food icon from homescreen, it will navigate to food vendor list, user can search food or items, user can filter by cuisines, filter by ratings, sort by, can make vendor favourites by clicking on heart icon, can see vendor details likve vendor name ratings delivery time and delivery fee on vendor card, on the top vendor list there is vendor collection like 'super saver' and on clicking that icon it will list all the food vendor list part of that collection .\n"
        "- Consideration for Food Menu screen has screen has search icon on the top and heart icon to make it favourites and share icon and back button, food restaurant name showing with cuisine and ratings and delivery time and delivery fee and delivered by talabat or store if pro user then will show the Free delivery with pro tag, banks offers will display , user can select from the food Menu categories, View cart button will enable when user add the minimum order amount, on clicking ‘View cart’ user will navigate to the Cart screen .\n"
        "- Consideration for Food cart, screen has ‘Add items’ button on the top and clicking it will take back to the menu screen, back option, added item with price valued edit option, on click edit will open the item bottom sheet to modify item details, All user to enter Special request, allow user to enter the voucher code, show the Payment summary with Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied, also for some user will show the option to pay by postpaid, also will have the option to proceed to checkout .\n"
        "- Consideration for Food checkout, screen has Add showing on the top with map and also allow to change or add new address, Displayed the estimated delivery time, rider tip option , Pay with option with talabat credit wallet, Postpaid, saved cards, add new card or by cash, for Android additional Google pay option, for additional iPhone Apple Pay and for Huawei no google or Apple Pay option, Payment summary will display Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied .\n"
        "- Consideration for Dineout order, it is only in UAE country,  is tapping DineOut icon from homescreen, it will navigate to the dineout restaurants list, upon clicking restaurant card it will open up the to see the location and call option and menu and amenities, photo gallery and Pay bill option, when user clicks on pay billthen user can input the bill amount and can click on Unlock discount, after that user navigates to the checkout page where user have option to pay by new card and saved card and talabat credit and postpaid but not with cash .\n"
        "- Consideration for Grocery vendor, screen has search for products or stores, multi basket icon on the top, all supermarkets on the top swim lane below search bar, then below it recommended grocery stores, then ads banners, then Browse All stores with some filters like offers and under30mins and pro, when user tap on any grocery stores it navigates to the catalog screen .\n"
        "- Consideration for Grocery catalog, screen has search icon on the top and heart icon to make it favourites and share icon and back button, grocery store name showing with cuisine and ratings and delivery time and delivery fee and delivered by talabat or store if pro user then will show the Free delivery with pro tag, banks offers will display , user can select from the grocery Menu categories, View cart button will enable when user add the minimum order amount, on clicking ‘View cart’ user will navigate to the Cart screen .\n"
        "- Consideration for Grocery cart, screen has ‘Add items’ button on the top and clicking it will take back to the menu screen, back option, added item with price valued edit option, on click edit will open the item bottom sheet to modify item details, Allow user to enter Special request, allow user to enter the voucher code, show the Payment summary with Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied, also for some user will show the option to pay by postpaid, also will have the option to proceed to checkout .\n"
        "- Consideration for Grocery checkout, screen has Add showing on the top with map and also allow to change or add new address, Displayed the estimated delivery time, rider tip option , Pay with option with talabat credit wallet, Postpaid, saved cards, add new card or by cash, for Android additional Google pay option, for additional iPhone Apple Pay and for Huawei no google or Apple Pay option, Payment summary will display Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied .\n"
        "- Consideration for Pharmacy order, Pharmacy entry point is from Home Screen, when click from home it will navigate to the pharmacy list screen, showing search bar on the top to search any medicine items or pharmacy name, after search it will list all type of categories in pharmacy like Eye care Beauty Nutrition and many more, It will also show the Big Brands near you, then will show Browse all stores with filters like ‘Offers’ ‘Under 30mins’ ‘pro’, when you click on any pharmacy from the list it will navigate to the pharmacy item list where on the top search to search any items, shop by categories section, Best sellers near you section and many other sections from which user can select and click on ‘+’ to add to the cart, once reach minimum order amount then the ‘View cart’ will get enabled, Allow user to enter Special request, show the Payment summary with Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied, also for some user will show the option to pay by postpaid, also will have the option to proceed to checkout, checkout screen,screen has Address showing on the top with map and also allow to change or add new address, Displayed the estimated delivery time, rider tip option , Pay with option with talabat credit wallet, Postpaid, saved cards, add new card or by cash, for Android additional Google pay option, for additional iPhone Apple Pay and for Huawei no google or Apple Pay option, Payment summary will display Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied  .\n"
        "- Consideration for Stores order, Stores entry point is from Home Screen, when click from home it will navigate to the store list screen, showing search bar on the top to search any medicine items or pharmacy name, after search it will list all type of categories in pharmacy like Flowers Pets Cake&Sweets Beauty and many more, It will also show the ads banners, then will show Browse all stores with filters like ‘Offers’ ‘Under 30mins’ ‘pro’, when you click on any stores from the list it will navigate to the store item list where on the top search to search any items, shop by categories section, click on ‘+’ to add to the cart, once reach minimum order amount then the ‘View cart’ will get enabled, Allow user to enter Special request, show the Payment summary with Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied, also for some user will show the option to pay by postpaid, also will have the option to proceed to checkout, checkout,screen has Address showing on the top with map and also allow to change or add new address, Displayed the estimated delivery time, rider tip option , Pay with option with talabat credit wallet, Postpaid, saved cards, add new card or by cash, for Android additional Google pay option, for additional iPhone Apple Pay and for Huawei no google or Apple Pay option, Payment summary will display Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied  .\n"
        "- Consideration for Give back order, Give back entry point is from Home Screen, when click from home it will navigate to the Donate collection screen, user can choose any vendor add the to the cart, click on Donate Now, go to the cart and click on checkout, Pay with option with talabat credit wallet, Postpaid, saved cards, add new card or by cash, for Android additional Google pay option, for additional iPhone Apple Pay and for Huawei no google or Apple Pay option, Payment summary will display Subtotal, Delivery fee, Service fee and Total amount and pro discount, if user is pro and reach the amount to get free delivery then Free delivery tag will be applied  .\n"
        "- Consideration for Meals for one swim-lane are on Hoe screen and  displays items with actual and discounted prices and delivery time and free delivery and ‘+’ icon to add item, there is an right arrow on it when clicking it will navigate to the Meals for one screen and display all the vendors part of it also shows the cuisine selection and Sort by option, Sort by will sort by Recommended or Maximum savings Fastest delivery or Pre: Low to high and clicking on apply will filter based on the option selected, then clicking on the ‘+’ icon it will open the item screen, user can add item and reach to the cart screen, cart screen user can edit the item and increase or decrease, can add upselling items, add special request, add voucher code, payment summary showing Subtotal and Discount and Free Delivery in case of pro and Total amount, allow to pay by Postpaid, user can then proceed to checkout, checkout screen same as food checkout screen but here it will show the discount in payment summary for meals for one item and user can place order with any payment type .\n"
        "- Consideration for Rewards on homescreen will take user to the rewards screen and user can see their points history ‘All’ ‘Earned’ ‘Spent’ and details of how many points available and how many going to expire with date, also show how many vouchers user has, also allow user to redeem their points either on supermarket, food vendors, Pharmacy, Lifestyle rewards .\n"
        "- Consideration for GEM is available on Home Screen as swim-lane and food vendor list as gem popup can be minimize and on food list as a Collection, GEM open as a collection screen which will have all the restaurants part of GEM, gem timer running,  option to sort by and cuisine filters and ratings filter, clicking on any vendors on gem screen will navigate to the menu page with timer running, can add items to recharge the three tier discounted amount, there is limit on the third tier, the more user add items the more gem discount user gets it, timer should show on all the screen and on checkout in the payment summary user should see the gem discount if the minimum gem order discounted amount reach else the gem discount will not be applied, on cart and checkout should show the gem Discount amount,GEM is not a restaurant it’s just the ad name, cannot be search by GEM, GEM is not for the guest or non logged in user and it will not appear until user is logged in .\n"
        "- Consideration for Order again, user has to go to the Orders tab present at the Home Screen, user will get to see all the past orders with details of vendor names and all item details and amount paid and ‘View details’ link to see all the details of that order, if the vendor is not delivering to the selected address then it will display the message ‘Our of delivery area’ text, also there will be an option to rate the order out of 5 stars and on clicking on any stars it will open up the bottom sheet to rate the order, user can switch between the stars and also put the comments, after continue with vendors user can also rate the rider by giving them the stars and then finally can send the review by clicking on the ‘Send review’ button, all the vendors which are already rated will then not see the option rate again and also dine out and pickup vendors will not have the option to rate the orders  .\n"
        "- Consideration for talabat pay wallet, user has to go to the talabat pay tab present at the Home Screen, user will see talabat credit balance on the top, for some user it will show the PostPaid details section, also for some user the option talabat ADCB credit card details section, then it will show the Payment methods with saved cards details and user can swipe to see all the cards and user can manage the card to add or delete new card, user can see all the ‘talabat credit transactions’ , all In and Out transition made by talabat credit and Refund amount and Credit received from ADCB card who has that card and Employee gift credit  .\n"
        "- Consideration for PostPaid details, user has to go to the Account tab and click on the PostPaid then user will navigate to the ‘PostPaid’ screen, on the top user will have setting icon to make the Preferred auto-payment method, add and saved and change and make default card, also will have option to make it payment schedule, on the PostPaid main screen the Available to spend amount will be displayed, also will show the ‘Active’ ‘Complete’ payment details  .\n"
        "- Consideration for Refer a friend, user has to go to the Account tab and click on the Refer a friend then user will navigate to the ‘Refer a friend’ screen, user can see the details about the Refer a friend and also can have the code displayed and allow to click on ‘Share Code’ button and upon clicking on it then will open bottom sheet options to share with on any app  .\n"
        "- Consideration for talabat pro screen from Account tab, user has to go to the Account tab and click on the ‘talabat pro’ then user will navigate to the ‘talabat pro’ screen which will display all the Benefits, Manage section will have ‘View Terms and Conditions’ and ‘Cancel subscription’ option, on clicking the cancel subscription will give the user the bottom sheet with two button option ‘Confirm’ and ‘Keep benefits’ with the popup text display ‘Are you sure you want to cancel your subscription?’  .\n"
        "- Consideration for ‘Get help’ screen from Account tab, user has to go to the Account tab and click on the ‘Get help’ then user will navigate to the ‘Help Center’ screen which will have the title ‘How can we help?’ And list of options like ‘My orders’ ‘I can’t place my order’ Payment information’ My support requests’ ‘talabat ADCB Credit Card’ ‘talabat pro subscription’ ‘talabat pro family subscription’ Rewards’ ‘Cancellation policy’ ‘DineOut Deals’  .\n"
        "- Consideration for Settings screen, user has to navigate to the Account tab and click on the settings icon at the right top, then on the setting screen user can see the fields like ‘Account info’ ‘Saved Addresses’ ‘Change email’ ‘Change password’ ‘Notifications’ ‘Language’ ‘Country’ ‘Log out’  .\n"
        "- Consideration for Account info on Settings screen, user when click on the ‘Account info’ should navigate to the screen where user can see the account details like ‘Email’ ‘First name’ ‘Last name’ ‘Date of birth’ ‘Gender’ in disabled mode, user will have an option to edit the account info, user can see the ‘Delete account’ button in case need to delete the account details  .\n"
        "- Consideration for Change email on Settings screen, user when click on the ‘Change email’ should navigate to the screen where user can enter the New email and Confirm new email and Current password and click on Submit  .\n"
        "- Consideration for Change password on Settings screen, user when click on the ‘Change email’ should navigate to the screen where user can enter the Current password and New password and Confirm new password and click on Submit  .\n"
        "- Consideration for Change Language on Settings screen, user when click on the ‘Language’ should open the bottom sheet to select the languages like English and Arabic, Emariti will also be seen in UAE, Kurdish will also be seen in Iraq  .\n"
        "- Consideration for Change Country on Settings screen, user when click on the ‘Country’ should open the bottom sheet to select the country like Kuwait KSA Bahrain UAE Oman Qatar Jordan Egypt Iraq  .\n"
        "- Consideration for Logout on Settings screen, user when click on the ‘Log out’ should open the popup with display ‘Are you sure you want to logout? with two button option ‘Cancel’ and ‘Log out’  .\n"
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
    parser.add_argument("--tribe", help="Tribe name (e.g., Fintech)", default=os.getenv("TRIBE"))

    args = parser.parse_args()
    generate_test_cases(
        args.requirement, args.squad, args.file_name, args.no_upload,
        args.tag, args.other_tags, args.background, args.additional_background
    )

if __name__ == "__main__":
    main()
