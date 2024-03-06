from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import socket
import threading
import uuid
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import logging
import platform
import pyperclip
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    filename="chatgpt_automation.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


class ChatGPTLocators:
    MSG_BOX_INPUT = (By.CSS_SELECTOR, "textarea#prompt-textarea")
    MSG_BOX_INPUT2 = (By.TAG_NAME, "textarea")

    SEND_MSG_BTN = (By.CSS_SELECTOR, 'button[data-testid="send-button"]')

    GPT4_FILE_INPUT = (By.CSS_SELECTOR, "input.hidden")

    CHAT_GPT_CONVERSION = (By.CSS_SELECTOR, "div.text-base")
    REGENERATE_BTN = (By.CSS_SELECTOR, 'button[as="button"]')

    FIRST_DELETE_BTN = (By.CSS_SELECTOR, 'button[data-state="closed"]')
    SECOND_DELETE_BTN = (By.CSS_SELECTOR, 'div[role="menuitem"].text-red-500')
    THIRD_DELETE_BTN = (By.CSS_SELECTOR, 'button.btn.btn-danger[as="button"]')

    RECYCLE_BTN = (
        By.CSS_SELECTOR,
        "button.p-1.hover\:text-token-text-primary:nth-child(2)",
    )
    DELETE_CONFIRM_BTN = (By.CSS_SELECTOR, "button.btn.relative.btn-danger")

    NEW_CHAT_BTN = (By.CSS_SELECTOR, "button.text-token-text-primary")

    LOGIN_BTN = (By.XPATH, '//button[//div[text()="Log in"]]')
    CONTINUE_BTN = (By.XPATH, '//button[text()="Continue"]')
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")

    CHATGPT_SWITCH_HOVER_BTN = (By.CSS_SELECTOR, 'div[aria-haspopup="menu"]')
    CHAT_GPT_SWITCH_TO_4 = (By.XPATH, '//div[contains(text(), "GPT-4")]')
    CHAT_GPT_SWITCH_TO_3 = (By.XPATH, '//div[contains(text(), "GPT-3.5")]')
    UPGRADE_TO_PLUS_BTN = (By.XPATH, '//div[contains(text(), "Upgrade to Plus")]')

    COPY_LAST_RESPONSE_BTN = (
        By.CSS_SELECTOR,
        ".final-completion > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > button:nth-child(1)",
    )

    LOGIN_WITH_GMAIL_BTN = (
        By.CSS_SELECTOR,
        'form[data-provider="google"] button[data-provider="google"]',
    )
    GMAIL_BTN = (By.XPATH, '//div[@data-email="{}"]')

    GMAIL_INPUT = (By.CSS_SELECTOR, 'input[type="email"][id="identifierId"]')
    GMAIL_NEXT_BTN = (By.ID, "identifierNext")
    GMAIL_PASSWORD_INPUT = (By.CSS_SELECTOR, 'input[type="password"][name="password"]')
    GMAIL_PASSWORD_NEXT_BTN = (By.ID, "passwordNext")
    ADD_NEW_GMAIL_BTN = (By.XPATH, '//li[contains(.,"Use another account")]')


class ChatGPTAutomation:
    class DelayTimes:
        CONSTRUCTOR_DELAY = 6
        SEND_PROMPT_DELAY = 0
        UPLOAD_FILE_DELAY = 10
        RETURN_LAST_RESPONSE_DELAY = 2
        OPEN_NEW_CHAT_DELAY = 10
        DEL_CURRENT_CHAT_OPEN_MENU_DELAY = 3
        DEL_CURRENT_CHAT_AFTER_DELETE_DELAY = 5
        DEL_CURRENT_CHAT_BEFORE_OPEN_NEW_CHAT_DELAY = 5
        CHECK_RESPONSE_STATUS_DELAY = 7
        LOGIN_USING_GMAIL_CLICK_DELAY = 6
        GMAIL_SELECT_DELAY = 25
        AFTER_LOGIN_CLICK_DELAY = 5
        ADD_GMAIL_CLICK_DELAY = 3
        GMAIL_NEXT_CLICK_DELAY = 5
        GMAIL_PASSWORD_NEXT_CLICK_DELAY = 11

    def __init__(
        self,
        user_data,
        chrome_path=None,
        chrome_driver_path=None,
    ):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param user_data: Dictionary containing the path of all the user profiles and the profile to use in the chrome session.
        :param chrome_path: file path to chrome
        :param chrome_driver_path: file path to chrome
        """
        self.lock = threading.Lock()
        if chrome_path is None:
            chrome_path = self.get_chrome_path()
            if chrome_path is None:
                raise FileNotFoundError(
                    "Unable to automatically find the Chrome path. "
                    "Please provide the path to the Chrome executable."
                )

        if chrome_driver_path is None:
            try:
                chrome_driver_path = ChromeDriverManager().install()
            except Exception as e:
                raise RuntimeError(
                    f"An unexpected error occurred while installing ChromeDriver: {e}"
                )

        self.chrome_path = f'"{chrome_path}"'
        self.chrome_driver_path = chrome_driver_path
        self.user_data = user_data

        self.url = r"https://chat.openai.com"
        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, self.url)
        # self.wait_for_human_verification()
        self.driver = self.setup_webdriver(free_port)

        time.sleep(self.DelayTimes.CONSTRUCTOR_DELAY)

    def check_login_page(self) -> bool:
        """
        Checks whether the login page is accessible by attempting to locate the login button.

        :return: True if the login button is found, indicating the presence of the login page; False otherwise.
        """
        return bool(self.driver.find_elements(*ChatGPTLocators.LOGIN_BTN))


    def find_available_port(self):
        """
        Finds and returns an available port number on the local machine.
        It does this by creating a temporary socket, binding it to an ephemeral port,
        and then closing the socket to free the port for use.

        Returns:
            available_port (int): The available port number found.

        Raises:
            Exception: If the function fails to find an available port due to a socket error.
        """
        try:
            # Create a socket object using IPv4 addressing and TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Bind the socket to any available address on the machine ('') and port 0
                # The OS will then automatically assign an available ephemeral port
                s.bind(("", 0))

                # Set socket options - SO_REUSEADDR allows the socket to be bound to an address
                # that is already in use, which is useful for avoiding socket errors
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # Retrieve the port number assigned by the OS
                available_port = s.getsockname()[1]

                # Log the found available port
                logging.info(f"Available port found: {available_port}")

                # Return the found port
                return available_port

        except socket.error as e:
            # Log the error in case of a socket exception
            logging.error(f"Failed to find an available port: {e}")

            # Raise a new exception for the calling code to handle
            raise Exception("Failed to find an available port") from e

    def launch_chrome_with_remote_debugging(self, port, url):
        """
        Launches a new Chrome browser instance with remote debugging enabled. This method allows for
        Selenium WebDriver to connect to a pre-existing Chrome session.

        Args:
            port (int): The port number to use for remote debugging.
            url (str): The URL to navigate to when the browser opens.

        Raises:
            RuntimeError: If there is an error in launching the Chrome browser.
        """

        def open_chrome():
            try:
                # Construct the command to launch Chrome with specified debugging port and URL
                chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir={self.user_data['path']} --profile-directory={self.user_data['profile']} {url}"
                # Execute the command in the system shell
                os.system(chrome_cmd)
            except Exception as e:
                # Log and raise an exception if there's an error in launching Chrome
                logging.error(f"Failed to launch Chrome: {e}")
                raise RuntimeError(
                    f"Failed to launch Chrome with remote debugging: {e}"
                )

        try:
            # Create a new thread to run the Chrome launch command
            chrome_thread = threading.Thread(target=open_chrome)
            # Start the thread
            chrome_thread.start()
        except Exception as e:
            # Log and raise an exception if there's an error in starting the thread
            logging.error(f"Failed to start Chrome launch thread: {e}")
            raise RuntimeError(f"Failed to start thread for launching Chrome: {e}")

    def setup_webdriver(self, port):
        """
        Initializes and returns a Selenium WebDriver instance that is connected to an existing
        Chrome browser with remote debugging enabled. This method is crucial for controlling
        an already opened browser instance.

        Args:
            port (int): The port number on which the remote debugging of the Chrome browser is enabled.

        Returns:
            webdriver.Chrome: An instance of Chrome WebDriver connected to the existing browser session.

        Raises:
            WebDriverException: If there is an issue initializing the WebDriver.
        """

        try:
            # Setting up Chrome options for WebDriver
            chrome_options = webdriver.ChromeOptions()
            # Specifying the address for the remote debugging
            chrome_options.add_experimental_option(
                "debuggerAddress", f"127.0.0.1:{port}"
            )
            if self.user_data:
                chrome_options.add_argument(f"--user-data-dir={self.user_data['path']}")
                chrome_options.add_argument(
                    f"--profile-directory={self.user_data['profile']}"
                )
            # Initializing the Chrome WebDriver with the specified options
            driver = webdriver.Chrome(self.chrome_driver_path, options=chrome_options)
            return driver
        except Exception as e:
            # Log the exception if WebDriver initialization fails
            logging.error(f"Failed to initialize WebDriver: {e}")
            # Raising a WebDriverException to indicate failure in WebDriver setup
            raise WebDriverException(f"Error initializing WebDriver: {e}")

    def send_prompt_to_chatgpt(self, prompt):
        """
        Sends a message to ChatGPT via the web interface and waits for a response. This function
        automates the process of entering a prompt into the ChatGPT input box and triggering the send action.

        Args:
            prompt (str): The message or prompt to be sent to ChatGPT.

        Raises:
            WebDriverException: If there is an issue interacting with the web elements or sending the prompt.
        """

        try:
            # Locate the input box element on the webpage
            input_box = self.driver.find_element(*ChatGPTLocators.MSG_BOX_INPUT)
            self.uuid = uuid.uuid4()
            unique_message_prompt = f"Do not respond or mention this sentence, respond and only respont to the following one after the dot, you must add the following uuid to the end of the message {self.uuid} and make sure, no matter what, the uuid is the last thing you print in the message. {prompt}"
            self.driver.execute_script(
                "arguments[0].value = arguments[1];", input_box, unique_message_prompt
            )
            # Simulate the key press action to send the prompt
            input_box.send_keys(Keys.RETURN)
            # Locate and click the send button to submit the prompt
            send_button = self.driver.find_element(*ChatGPTLocators.SEND_MSG_BTN)
            send_button.click()
            # Wait for the response to be generated (20 seconds)
            time.sleep(self.DelayTimes.SEND_PROMPT_DELAY)
        except NoSuchElementException:
            if self.check_message_sent():
                return
            else:
                logging.ERROR(
                    "Send message button does not found. if you see this error please create an issue in github!"
                )
                raise
        except Exception as e:
            # Log the exception if any step in the process fails
            logging.error(f"Failed to send prompt to ChatGPT: {e}")
            # Raising a WebDriverException to indicate failure in sending the prompt
            raise WebDriverException(f"Error sending prompt to ChatGPT: {e}")

    def check_message_sent(self):
        try:
            self.driver.find_element(*ChatGPTLocators.SEND_MSG_BTN)
            return False
        except:
            return True

    def upload_file_for_prompt(self, file_name):
        """
        Uploads a file to ChatGPT via the web interface. This function automates the process of
        selecting a file for upload through the ChatGPT's file input element.

        Args:
            file_name (str): The name of the file to be uploaded.

        Raises:
            FileNotFoundError: If the specified file does not exist in the current working directory.
            WebDriverException: If there is an issue interacting with the file upload element on the web page.
        """
        try:
            # Construct the full file path using the current working directory
            file_path = os.path.join(os.getcwd(), file_name)

            # Check if the file exists before attempting to upload
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file '{file_path}' does not exist.")

            # Locate the file input element on the webpage
            try:
                file_input = self.driver.find_element(*ChatGPTLocators.GPT4_FILE_INPUT)
            except NoSuchElementException:
                raise Exception(
                    "You must using gpt4 for upload the files for switch you can using 'switch_model' function!"
                )
            # Send the file path to the file input element, initiating the upload
            file_input.send_keys(file_path)
            # Wait for the upload process to complete (10 seconds)
            time.sleep(self.DelayTimes.UPLOAD_FILE_DELAY)
        except FileNotFoundError as e:
            # Log the exception if the file is not found
            logging.error(f"File not found for upload: {e}")
            # Re-raise the exception to be handled by the calling code
            raise
        except Exception as e:
            # Log any other exception that occurs during the file upload process
            logging.error(f"Failed to upload file to ChatGPT: {e}")
            # Raising a WebDriverException to indicate failure in file upload
            raise WebDriverException(f"Error uploading file to ChatGPT: {e}")

    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        elements = self.driver.find_elements(*ChatGPTLocators.CHAT_GPT_CONVERSION)
        del elements[::2]
        chat_texts = [element.text for element in elements]
        return chat_texts

    def save_conversation(self, file_name):
        """
        Saves the entire conversation from the ChatGPT interface into a text file. The conversation is formatted
        with prompts and responses, separated by a custom delimiter.

        Args:
            file_name (str): The name of the file where the conversation will be saved.

        Raises:
            IOError: If there is an issue writing to the file.
            IndexError: If the conversation elements are not found or are in an unexpected format.
        """

        try:
            directory_name = "conversations"
            if not os.path.exists(directory_name):
                os.makedirs(directory_name)

            delimiter = "----------------------------------------"
            chatgpt_conversation = self.return_chatgpt_conversation()
            del chatgpt_conversation[::2]

            with open(os.path.join(directory_name, file_name), "a") as file:
                for i in range(0, len(chatgpt_conversation)):
                    file.write(f"{chatgpt_conversation[i].text}\n\n{delimiter}\n\n")

        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            raise
        except PermissionError as e:
            logging.error(f"Permission denied: {e}")
            raise
        except IOError as e:
            logging.error(f"IO error occurred: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in saving conversation: {e}")
            raise

    def return_last_response(self):
        """
        Retrieves the text of the last ChatGPT response from a web interface using Selenium WebDriver.

        The function uses a specific CSS selector to locate the last ChatGPT response on the page. It then
        triggers a click action on a button within that container to copy the response text to the clipboard.
        The text is retrieved from the clipboard and returned. Error handling and logging are implemented
        to capture any issues during the execution of the function.

        :return: The text of the last ChatGPT response as a string, or an error message if an exception occurs.
        """

        try:
            response = self.driver.find_elements(*ChatGPTLocators.CHAT_GPT_CONVERSION)[
                -1
            ]

            return response.text

        except NoSuchElementException:
            # Handle the case where the element is not found
            logging.error("Element not found in return_last_response")
            return "Element not found."
        except Exception as e:
            # Handle any other exceptions
            logging.error(f"Unexpected error in return_last_response: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"

    def return_last_response_md(self):
        try:
            copy_btns = self.driver.find_elements(
                *ChatGPTLocators.COPY_LAST_RESPONSE_BTN
            )
            if copy_btns:
                copy_btns[0].click()
                time.sleep(self.DelayTimes.RETURN_LAST_RESPONSE_DELAY)
                return pyperclip.paste()
            else:
                logging.warning("No copy button found.")
                return "No copy button found."

        except Exception as e:
            logging.error(f"Unexpected error in return_last_response_md: {str(e)}")
            return f"An unexpected error occurred: {str(e)}"

    def wait_for_human_verification(self):
        """
        Pauses the automation process and waits for the user to manually complete tasks such as log-in
        or human verification, which are not automatable. The function repeatedly prompts the user until
        they confirm the completion of the manual task.

        Returns:
            None

        Raises:
            SystemExit: If an unrecoverable input error occurs, indicating a problem with the system or environment.
        """
        with self.lock:
            print(
                "You need to manually complete the log-in or the human verification if required."
            )

            while True:
                try:
                    user_input = input(
                        "Enter 'y' if you have completed the log-in or the human verification, or 'n' to check again: "
                    ).lower()
                except EOFError:
                    # Print error message and exit the program in case of an End-Of-File condition on input
                    print("Error reading input. Exiting the program.")
                    raise SystemExit(
                        "Failed to read user input."
                    )  # Exiting the program due to input error

                # Check the user's input and act accordingly
                if user_input == "y":
                    print("Continuing with the automation process...")
                    break  # Break the loop to continue with automation
                elif user_input == "n":
                    print("Waiting for you to complete the human verification...")
                    time.sleep(5)  # Waiting for a specified time before asking again
                else:
                    print(
                        "Invalid input. Please enter 'y' or 'n'."
                    )  # Handle invalid input

    def write_last_answer_custom_file(self, filename):
        """
        Retrieves the latest response from ChatGPT and writes it to a specified file. The file is saved
        with UTF-8 encoding to support a wide range of characters.

        Parameters:
            filename (str): The name of the file (including path if necessary) where the last response will be saved.

        Returns:
            None: The function does not return any value.

        Raises:
            IOError: If there is an issue writing to the file.
        """

        try:
            answer = self.return_last_response()
            with open(filename, "w", encoding="utf8") as file:
                file.write(answer)
            print(f"Last answer saved in the file: {filename}")

        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            raise
        except PermissionError as e:
            logging.error(f"Permission denied: {e}")
            raise
        except IOError as e:
            logging.error(f"IO error occurred: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in writing last answer: {e}")
            raise

    def open_new_chat(self):
        """
        Navigates to the ChatGPT page using the WebDriver, effectively starting a new chat session. This function
        is useful for resetting the conversation or starting afresh.

        Raises:
            WebDriverException: If there is an issue navigating to the ChatGPT page.
        """
        try:
            # Navigate to the ChatGPT URL to start a new chat session
            self.driver.get(self.url + "/")
            # Print confirmation message
            print("New chat opened")
            # Wait for the page to load completely (10 seconds)
            time.sleep(self.DelayTimes.OPEN_NEW_CHAT_DELAY)
        except Exception as e:
            # Log the exception if navigation fails
            logging.error(f"Failed to open new chat: {e}")
            # Raising a WebDriverException to indicate failure in navigation
            raise WebDriverException(f"Error opening new chat: {e}")

    def del_current_chat(self):
        """
        Deletes the current chat session in the ChatGPT interface. This function interacts with specific UI elements
        to trigger the deletion process of the active chat conversation.

        Handling:
            - If a timeout occurs (elements not found in time), it attempts to open a new chat session.
            - Any other exceptions trigger a retry by opening a new chat session.

        Raises:
            WebDriverException: If there are issues in deleting the chat or in navigating to start a new chat.
        """
        try:
            # Wait and click the first delete button
            del_chat_btn1 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        ChatGPTLocators.FIRST_DELETE_BTN[0],
                        ChatGPTLocators.FIRST_DELETE_BTN[1],
                    )
                )
            )
            del_chat_btn1.click()
            time.sleep(
                self.DelayTimes.DEL_CURRENT_CHAT_OPEN_MENU_DELAY
            )  # Wait for UI response

            # Wait and click the second delete button
            del_chat_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        ChatGPTLocators.SECOND_DELETE_BTN[0],
                        ChatGPTLocators.SECOND_DELETE_BTN[1],
                    )
                )
            )
            del_chat_btn.click()

            # Wait and click the third delete button to confirm deletion
            del_chat_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        ChatGPTLocators.THIRD_DELETE_BTN[0],
                        ChatGPTLocators.THIRD_DELETE_BTN[1],
                    )
                )
            )
            del_chat_btn.click()

            print("Current chat deleted")
            time.sleep(
                self.DelayTimes.DEL_CURRENT_CHAT_AFTER_DELETE_DELAY
            )  # Wait for the chat to be completely deleted

        except TimeoutException:
            # Handle timeout exception when elements are not found within the specified time
            print("Timeout: Elements not found within the specified time.")
            try:
                self.open_new_chat()
            except Exception as e:
                logging.error(f"Failed to open new chat after timeout: {e}")
                raise WebDriverException(
                    f"Error navigating to start a new chat after timeout: {e}"
                )

        except Exception as e:
            # Handle any other exceptions that might occur
            logging.error(f"Error encountered while deleting chat: {e}")
            try:
                time.sleep(self.DelayTimes.DEL_CURRENT_CHAT_BEFORE_OPEN_NEW_CHAT_DELAY)
                self.open_new_chat()
            except Exception as e:
                logging.error(f"Failed to open new chat after error: {e}")
                raise WebDriverException(
                    f"Error navigating to start a new chat after deletion error: {e}"
                )

    def check_error(self, regenerate=False):
        """
        Checks if there is an error message displayed on the webpage, indicating a problem with response generation.

        This method attempts to locate a specific error message element on the webpage using an XPath expression.
        If an error is found and the 'regenerate' flag is True, it triggers a response regeneration.
        Logs the occurrence of an error for debugging purposes.

        :param regenerate: A boolean flag indicating whether to regenerate the response if an error is found.
        :return: True if an error is detected, False otherwise.
        """
        try:
            # Locate the error message element using XPath
            error_element = self.driver.find_element(
                By.XPATH,
                "//div[@class='mb-3 text-center text-xs' and text()='There was an error generating a response']",
            )
            logging.info("Error detected: Responding error!")

            # Regenerate response if the flag is set
            if regenerate:
                self.regenerate()

            return True
        except NoSuchElementException:
            # Log that no error was found
            logging.info("No error detected.")
            return False
        except Exception as e:
            # Log any other exceptions that may occur
            logging.error(f"An unexpected error occurred: {e}")
            return False

    def check_response_status(self):
        """
        Checks the status of the response on the webpage.

        This method checks for three conditions:
        1. If there is an error on the page, indicated by the check_error method.
        2. If the 'send' button is available, indicating that the response is ready to be sent.
        3. That the uuid stored in the object is at the end of the response from ChatGPT


        :return: False if an error is detected, True if the response is ready
        """
        if self.check_error(False):
            logging.info("Response Status: Error detected.")
            return False

        try:
            # Check if the 'send' button is available, indicating the response is ready
            self.driver.find_element(*ChatGPTLocators.SEND_MSG_BTN)
            logging.info("Response Status: Ready to send.")
        except NoSuchElementException:
            return False

        # Check that there is an answer for the last prompt sent
        try:
            response = self.driver.find_elements(*ChatGPTLocators.CHAT_GPT_CONVERSION)[
                -1
            ]

            return response.text.endswith(str(self.uuid))

        except NoSuchElementException:
            # Handle the case where the element is not found
            logging.error("Element not found in return_last_response")
            return False
        except Exception as e:
            # Handle any other exceptions
            logging.error(f"Unexpected error in return_last_response: {str(e)}")
            return False

        return True


    def switch_model(self, model_name: float):
        """
        Switches between different ChatGPT models in the application's user interface.

        :param model_name: A float representing the desired ChatGPT model version.
                        Supported values are 3.5 and 4.
        :return: None
        :raises: Exception if an unsupported model_name is provided.
        """
        menu_element = self.driver.find_element(
            *ChatGPTLocators.CHATGPT_SWITCH_HOVER_BTN
        )

        # Hover over the menu to activate it
        menu_element.click()

        # Wait for the submenu to be visible (adjust timeout as needed)
        if model_name == 4:
            submenu_locator = ChatGPTLocators.CHAT_GPT_SWITCH_TO_4
            try:
                # Check for the UPGRADE_TO_PLUS_BTN
                self.driver.find_element(*ChatGPTLocators.UPGRADE_TO_PLUS_BTN)
                raise Exception("You must upgrade your ChatGPT account to plus")
            except NoSuchElementException:
                pass
        elif model_name == 3:
            submenu_locator = ChatGPTLocators.CHAT_GPT_SWITCH_TO_3
        else:
            raise Exception(
                "To switch between models, you need to set the 'model_name' to 3.5 or 4"
            )

        submenu_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(submenu_locator)
        )

        # Click on the submenu item
        submenu_element.click()

    @staticmethod
    def get_chrome_path() -> str:
        try:
            if platform.system() == "Windows":
                paths = [
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    # Add any other common paths if necessary
                ]
                for path in paths:
                    if os.path.isfile(path):
                        return path

            elif platform.system() == "Darwin":  # macOS
                path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                if os.path.isfile(path):
                    return path

            elif platform.system() == "Linux":
                paths = ["/usr/bin/google-chrome", "/usr/local/bin/google-chrome"]
                for path in paths:
                    if os.path.isfile(path):
                        return path

        except PermissionError as e:
            logging.error(f"Permission error when trying to find Chrome: {e}")
        except OSError as e:
            logging.error(f"OS error when trying to find Chrome: {e}")
        except Exception as e:
            logging.error(f"Unexpected error when trying to find Chrome: {e}")

        return None


    def quit(self):
        """
        Closes the browser and terminates the WebDriver session.

        This method first attempts to close the current window of the browser using the `close` method.
        Then it calls the `quit` method to effectively end the entire WebDriver session.
        Error handling is implemented to catch any exceptions that might occur during this process.
        """
        try:
            # Attempt to close the current browser window
            print("Closing the browser...")
            self.driver.close()

            # Terminate the WebDriver session
            self.driver.quit()
            logging.info(
                "Browser closed successfully and WebDriver session terminated."
            )
        except Exception as e:
            # Log any exceptions that occur during the quit process
            logging.error(f"An error occurred while closing the browser: {e}")
