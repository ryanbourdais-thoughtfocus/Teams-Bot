# Teams Bot

## Overview

The Teams Bot Screenshot Analyzer is a Python application designed to automate the process of taking screenshots of the Microsoft Teams application, analyzing them for unread messages, and providing the user with relevant information. The bot utilizes the OpenAI API to interpret the screenshots and determine the presence of unread messages, as well as their positions within the Teams interface.

## Features

- **Screenshot Capture**: Takes screenshots of the Teams application and the taskbar.
- **Grid Overlay**: Adds a grid overlay to screenshots for easier analysis of message positions.
- **Message Analysis**: Uses OpenAI's API to analyze screenshots for unread messages and their positions.
- **Mouse Automation**: Automatically clicks on the Teams application and unread messages based on the analysis.

## Data Flow

The data flow through the application can be summarized in the following steps:

1. **Initialization**:
   - The application loads environment variables, including the OpenAI API key, from a `.env` file.

2. **Main Loop**:
   - The `main()` function runs an infinite loop that checks if the bot is currently in the Teams application.

3. **Taskbar Screenshot**:
   - If the bot is not in Teams, it takes a screenshot of the taskbar and the Teams application shortcut.
   - The screenshots are encoded in base64 format for transmission to the OpenAI API.

4. **Notification Check**:
   - The bot sends the taskbar screenshot to the OpenAI API to check for any Teams message notifications.
   - The response includes whether a notification is present and the position of the Teams icon.

5. **Teams Application Interaction**:
   - If a notification is present, the bot checks if it is currently in the Teams application.
   - If not, it clicks on the Teams shortcut to open the application.

6. **Message Screenshot**:
   - Once in Teams, the bot takes two screenshots: one without a grid overlay and one with a grid overlay.
   - The grid overlay helps in identifying the positions of unread messages.

7. **Message Analysis**:
   - Both screenshots are sent to the OpenAI API for analysis.
   - The API responds with information about unread messages and their positions.

8. **Position Calculation**:
   - The bot extracts the message positions from the API response and calculates the average position of unread messages.

9. **Mouse Automation**:
   - The bot moves the mouse to the calculated position of the unread message and clicks on it.

10. **Repeat**:
    - The bot waits for a specified duration (e.g., 10 seconds) before repeating the process.

## State Management

The bot operates using a state machine with the following states defined in the `State` enum:

- **POLLING**: The initial state where the bot checks for Teams notifications in the taskbar.
- **IN_TEAMS**: Indicates that the bot is currently in the Teams application and ready to analyze messages.
- **MESSAGE_FOUND**: Indicates that an unread message has been detected, and the bot is preparing to respond.
- **CONFIDENCE_CHECK**: The bot is checking for the presence of a last read bar in the chat to confirm the message's context.
- **RESPONSE_SENT**: Indicates that the bot has sent a response to the detected message and is preparing to return to the POLLING state.

## Requirements

- Python 3.x
- Required Python packages:
  - `pyautogui`
  - `Pillow`
  - `python-dotenv`
  - `openai`
  - `json`

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd teams-bot
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
