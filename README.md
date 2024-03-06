
# ChatGPTAutomation 🤖💻🧠

## Description
ChatGPTAutomation is a Python package that automates interactions with ChatGPT using Selenium, streamlining the process for developers and testers. 🚀

## Features
- Automated messaging to ChatGPT. 📩
- File upload support. 📁
- ChatGPT conversation retrieval and storage. 🗂️
- Customizable WebDriver for browser management. 🌐
- Configurable delays for various operations. ⏲️

## Installation
Install with:
```bash
pip install ChatGPTAutomation
```

## Usage

### Chrome WebDriver Download

- **Latest Chrome Version**: Download [here](https://googlechromelabs.github.io/chrome-for-testing/).
- **Older Chrome Versions**: Find compatible drivers [here](https://chromedriver.chromium.org/downloads).

### Setup

### Get the `user-data-dir` and `profile`

To easily authenticate to the ChatGPT account, the `user-data-dir` (path where all the user profiles are located) and `profile` (path where user data like cookies, extensions, etc are stored) is required. To obtain them:

1. Open the Chrome browser and type `chrome://version` in the search bar, after that, hit enter.
2. Search for the `Profile Path` entry. It should look something similar to `/Users/YourUserName/Library/Application Support/Google/Chrome/

Default`.
3. The `user-data-dir` is the whole `Profile Path` up to the penultimate directory: `/Users/YourUserName/Library/Application Support/Google/Chrome/`.
4. The `profile` is the last directory: `Default`.

### Install the library locally.

Install the library using `pip install -e .` in the root directory.


#### Automatic setup (without paths):
```python
from chatgpt_automation.chatgpt_automation import ChatGPTAutomation

chat_bot = ChatGPTAutomation(
    user_data={
        "path": "Users/YourUserName/Library/Application\ Support/Google/Chrome/", # Escape any spaces in the path.
        "profile": "Default",
    }

)
```

#### Manual setup (with paths):
```python
from chatgpt_automation.chatgpt_automation import ChatGPTAutomation

chat_bot = ChatGPTAutomation(
    chrome_path="path/to/chrome.exe", 
    chrome_driver_path="path/to/chromedriver.exe",
    user_data={
        "path": "Users/YourUserName/Library/Application\ Support/Google/Chrome/", # Escape any spaces in the path.
        "profile": "Default",
    }
)

# Send prompt
chat_bot.send_prompt_to_chatgpt("Hello, ChatGPT!")

# Wait for the response
while not chat_bot.check_response_status():
    pass

# Save conversation
chat_bot.save_conversation("conversation.txt")
```

### File upload
```python
chat_bot.upload_file_for_prompt("test_file.txt")
chat_bot.send_prompt_to_chatgpt("Explain this file?")
```

### Check response status
```python
if chat_bot.check_response_status():
    print("Response ready.")
else:
    print("Response issue.")
```

### Get last response
```python
chat_bot.send_prompt_to_chatgpt("Hello, ChatGPT!")
# Wait for the response
while not chat_bot.check_response_status():
    pass
response = chat_bot.return_last_response()
```

### Switch models
```python
chat_bot.switch_model(4)
```

### Login check
```python
if chat_bot.check_login_page():
    chat_bot.login()
```

---
## Delay Configurations

The `ChatGPTAutomation` class includes configurable delays for various operations, defined in the `DelayTimes` class:

- `CONSTRUCTOR_DELAY`: Time to wait for initialization.
- `SEND_PROMPT_DELAY`: Delay after sending a prompt to ChatGPT.
- `UPLOAD_FILE_DELAY`: Delay following a file upload.
- `RETURN_LAST_RESPONSE_DELAY`: Wait time to fetch the last response.
- `OPEN_NEW_CHAT_DELAY`: Delay in opening a new chat session.
- `DEL_CURRENT_CHAT_OPEN_MENU_DELAY`: Wait time before deleting current chat.
- `DEL_CURRENT_CHAT_AFTER_DELETE_DELAY`: Delay after deleting current chat.
- `DEL_CURRENT_CHAT_BEFORE_OPEN_NEW_CHAT_DELAY`: Wait time before opening new chat after deletion.
- `CHECK_RESPONSE_STATUS_DELAY`: Interval to check response status.

These delays are crucial for the stability and reliability of automated interactions with ChatGPT.


## Customizing Delay Times

The `ChatGPTAutomation` class comes with default delay settings for various operations, suitable for most use cases. However, you might find the need to adjust these delay times based on your network speed, system performance, or specific use case requirements. Here’s how you can customize these delay times.

### Accessing Delay Times

The delay settings are part of the `DelayTimes` inner class in `ChatGPTAutomation`. They are defined as class variables and can be accessed directly using the class name.

### Changing Delay Times

To change the delay times, access the respective variable in the `DelayTimes` class and set it to your desired value (in seconds). Here’s an example of how to do this:

```python
from chatgpt_automation.chatgpt_automation import ChatGPTAutomation

# Access and modify delay times
ChatGPTAutomation.DelayTimes.CONSTRUCTOR_DELAY = 10  # Set constructor delay to 10 seconds
ChatGPTAutomation.DelayTimes.SEND_PROMPT_DELAY = 25  # Set send prompt delay to 25 seconds
# ... similarly for other delay times

# Initialize ChatGPTAutomation with customized delay times
chat_bot = ChatGPTAutomation(
    username="<your username here>",
    password="<your password here>"
)

# The rest of your code...
```

### Recommended Practices

- **Testing**: When changing delay times, it's recommended to test the interaction with ChatGPT to ensure that the new settings work well in your environment.
- **Incremental Adjustments**: Make incremental adjustments and test each change rather than making large changes all at once.
- **Network Speed Consideration**: If you are working with a slow network connection, consider increasing the delay times to allow for longer response times from ChatGPT.

By following these steps and recommendations, you can fine-tune the behavior of the `ChatGPTAutomation` class to best fit your automation needs.

---

## Requirements
- Python 3.8+
- Selenium==4.9.0
- See `requirements.txt` for more.

## To-Do List

### Sign up:
- ✅ User login
- ⬜️ Sign up via email address

### Conversation Management:
- ✅ Create new conversation
- ✅ Get message list in a conversation
- ✅ Delete a conversation
- ⬜️ Edit Conversation Name
- ⬜️ Subscribe for realtime message
- ⬜️ Handle Random message such as popup, hints, and login attempts

### Advanced Features:
- ✅ Support for uploading files
- ⬜️ Support ChatGPT with internet
- ⬜️ Using GPTs
- ⬜️ API

### User Account Handling:
- ✅ Switch Between ChatGPT 3.5 and 4
- ⬜️ Fetch user detail like email and plan type
- ⬜️ Set custom instructions for more personalized conversations

### Browser:
- ⬜️ Headless Browser

## License
MIT License - see [LICENCE.md](LICENCE.md).

## Contact
Seyed Ali Hosseini 🧑‍💻 - iamseyedalipro@gmail.com 📧.

## Acknowledgements
- Thanks to OpenAI and Selenium. 🙏👨‍💻
