import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Ensure you have ChromeDriver installed and in your PATH
        self.driver.set_page_load_timeout(30)  # Set page load timeout to 30 seconds
        self.base_url = "http://127.0.0.1:5000"
        self.driver.get(self.base_url)
        
        # Go to the home page and upload an image
        self.driver.get(self.base_url)
        file_input = self.driver.find_element(By.NAME, "file")
        image_path = os.path.join(os.getcwd(), "static/foot-corn 151.jpg")  
        file_input.send_keys(image_path)
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Wait for the result page to load
        try:
            # Wait for the result page to load and display the result paragraph
            self.result_paragraph = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.result-content > p"))
            )
        except TimeoutException:
            self.driver.save_screenshot('upload_result_failure.png')
            with open('upload_result_failure.html', 'w') as f:
                f.write(self.driver.page_source)
            self.fail("Timed out waiting for page to load and display the result")

    def test_admin_login(self):
        # Go to the admin login page
        self.driver.get(f"{self.base_url}/login")

        # Add a delay to ensure the page is fully loaded
        time.sleep(2)

        try:
            # Locate the login form elements and submit credentials
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")

            username_input.send_keys("malshani") 
            password_input.send_keys("12345")  

            # Submit the login form
            self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

            # Wait for the redirection to the admin main page
            WebDriverWait(self.driver, 10).until(
                EC.url_to_be(f"{self.base_url}/admin_main_page")
            )

            # Add a delay to ensure the admin dashboard is fully loaded
            time.sleep(2)

            # Verify the admin dashboard content
            dashboard_header = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            self.assertIn("Welcome to the Admin Dashboard", dashboard_header.text)

        except TimeoutException:
            # Capture screenshot on failure
            self.driver.save_screenshot('admin_login_failure.png')
            # Print the page source for further debugging
            with open('admin_login_failure.html', 'w') as f:
                f.write(self.driver.page_source)
            self.fail("Admin dashboard did not load after login")

    def test_show_treatment(self):
        # Ensure that image upload and result retrieval is done in setUp
        try:
            # Click the "Show Treatment" button
            show_treatment_button = self.driver.find_element(By.ID, "showTreatment")
            show_treatment_button.click()

            # Pause for 2 seconds to allow the treatment content to load
            time.sleep(2)

            # Wait for the treatment div to populate
            treatment_div = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "treatment"))
            )

            time.sleep(2)


            # Validate the treatment for foot-corn
            treatment_text = treatment_div.text
            self.assertIn("Treatment: Surgery, Use corn pads", treatment_text)

        except TimeoutException:
            self.fail("Timed out waiting for treatment to appear")

    def test_feedback_submission(self):
        # Go to the feedback page
        self.driver.get(f"{self.base_url}/feedback")

        # Add a delay to ensure the feedback page is fully loaded
        time.sleep(2)

        # Wait for the feedback form to be visible
        feedback_form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
        )

        # Fill out the feedback form
        name_input = self.driver.find_element(By.NAME, "name")
        feedback_input = self.driver.find_element(By.NAME, "feedback")

        name_input.send_keys("Test User")
        feedback_input.send_keys("This is a test feedback.")

        # Pause for 2 seconds before submitting the form
        time.sleep(2)

        # Submit the form
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        try:
            # Wait for the feedback entries to be visible
            feedback_entries = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.feedback-entry"))
            )

            # Get the last feedback entry
            last_feedback_entry = feedback_entries[-1]  
            feedback_text = last_feedback_entry.text

            # Validate the feedback entry
            self.assertIn("Test User", feedback_text)
            self.assertIn("This is a test feedback.", feedback_text)

        except TimeoutException:
            self.fail("Timed out waiting for feedback to appear")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
