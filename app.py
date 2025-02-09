from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright,expect

import time
import re


def op_fi_scraping(annual_mileage, financed, financing_company, insurance_start_date, municipality, personal_id, postal_code, registration_number, under_24):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:

            page.goto("https://www.op.fi/henkiloasiakkaat/vakuutukset/ajoneuvovakuutus/autovakuutus-henkiloautolle/osta-henkiloautovakuutus")
            
            try:
                page.locator('#ocm-container button.ocm-button--continue').click()
            except:
                print("Continue button not found!")
                page.screenshot(path="continue_button_error.png")
                return {"error": "Continue button not found"}

            try:
                page.locator("input[maxlength='7'][type='text']").fill(registration_number)
            except:
                print("Input field for registration number not found!")
                page.screenshot(path="registration_input_error.png")
                return {"error": "Regis'5000',tration input field not found"}
        
            try:
                page.get_by_text('Jatka').click()
            except:
                print("Next button not clickable!")
                page.screenshot(path="next_button_error.png")
                return {"error": "Next button not clickable"}
            
            try:
                expect(page.locator('input[type="text"][maxlength="11"]')).to_be_visible()
                page.locator('input[type="text"][maxlength="11"]').fill(personal_id)
                expect(page.locator('input[type="text"][name="postcode"]')).to_be_visible()
                page.locator('input[type="text"][name="postcode"]').fill(postal_code)
            except:
                print("Personal ID or postal code input field not found!")
                page.screenshot(path="input_fields_error.png")
                return {"error": "Personal ID or postal code field missing"}

            # Odabir finansiranja
            try:
                if financed == 'no':
                    page.locator('xpath=//*[@id=":r4:"]/label[2]').click()
                else:
                    page.locator('xpath=//*[@id=":r4:"]/label[1').click()
            except:
                print("Financing options not found!")
                page.screenshot(path="financing_options_error.png")
                return {"error": "Financing options missing"}
            
            page.locator('xpath=//*[@id=":r6:"]/label[1]').click()
            # Odabir kilometraže
            
            
            try:
                page.evaluate(f"""
                    let select = document.querySelector("select");
                    let option = select.querySelector("option[value='{annual_mileage}']");
                    if (option) {{
                        select.value = option.value;
                        select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """) 
                mileage_options = {
                    '5000': 2, '10000': 3, '15000': 4, '20000': 5, '25000': 6,
                    '30000': 7, '40000': 8, '50000': 9, '50000+': 10
                }
                #page.locator('select[id=":r8:"]')//*[@id=":r6:"]
                #page.locator(f'option[value="{annual_mileage}"]').click()
                #page.locator(f'xpath=//select/option[{mileage_options.get(annual_mileage, 1)}]').click()
            except:
                print("Mileage options not found!")
                page.screenshot(path="mileage_options_error.png")
                return {"error": "Mileage dropdown missing"}
            page.get_by_text('Jatka').click()
            try:
                page.get_by_text('Jatka').click()
            except:
                print("Final submission button not found!")
                page.screenshot(path="final_submit_error.png")
                return {"error": "Final submit button missing"}

            # Extracting results
            
            try:
                result = {
                    "Superkasko": str(page.locator('css=#op-comparisontable-option_0 ._variantPriceGroup2_muaez_80').inner_text()),
                    "Kevytkasko": str(page.locator('css=#op-comparisontable-option_1 ._variantPriceGroup2_muaez_80').inner_text()),
                    "Osakasko": str(page.locator('css=#op-comparisontable-option_2 ._variantPriceGroup2_muaez_80').inner_text()),
                    "Liikennevakuutus": str(page.locator('css=#op-comparisontable-option_3 ._variantPriceGroup2_muaez_80').inner_text())
                }
            except:
                print("Result extraction failed!")
                page.screenshot(path="result_extraction_error.png")
                return {"error": "Failed to extract insurance details"}

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            page.screenshot(path="unexpected_error.png")
            return {"error": str(e)}

        finally:
            browser.close()

    return result

app = Flask(__name__)
CORS(app)  # Enable CORS if the module is available


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        # Use request.form to get URL-encoded form data.
        if not request.form:
            return jsonify(["Error: No form data received."]), 200

        # Convert ImmutableMultiDict to a regular dict for easier handling.
        data = request.form.to_dict()
        result = op_fi_scraping(
            data.get('annual_mileage'), data.get('financed'), data.get('financing_company'), data.get('insurance_start_date'), data.get('municipality'),
            data.get('personal_id'), data.get('postal_code'), data.get('registration_number'), data.get('under_24')
            )
        return jsonify(result)
        # confirmation = [
        #     "Data received successfully!",
        #     data
        # ]
        # return jsonify(confirmation), 200
    else:  # GET request
        return jsonify(["Welcome! Please send a POST request with form data."]), 200

if __name__ == '__main__':
    app.run(debug=True)


# # @app.route('/scrape', methods=['POST'])
# @app.route('/', methods=['GET', 'POST'])
# def root():
#     if request.method == 'POST':
#         data = request.form
#         if not data:
#             return jsonify({"error": "No input data provided"}), 400

#         result = op_fi_scraping(
#             data.get('annual_mileage'), data.get('financed'), data.get('financing_company'), data.get('insurance_start_date'), data.get('municipality'),
#             data.get('personal_id'), data.get('postal_code'), data.get('registration_number'), data.get('under_24')
#             )
#         return jsonify(result)
#     else:  # GET request
#         return jsonify(["Welcome! Please send a POST request with form data."]), 200

# if __name__ == '__main__':
#     app.run(debug=True)
