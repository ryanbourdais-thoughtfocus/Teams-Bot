import pyautogui
import time
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
import json
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI with your API key
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)
spacing = 50 

# Function to take a screenshot and save it with a grid overlay

def take_screenshot_with_grid(filename):
    # Take a screenshot using pyautogui
    screenshot = pyautogui.screenshot()
    
    # Convert the screenshot to a PIL Image
    screenshot = screenshot.convert("RGBA")
    
    # Create a draw object
    draw = ImageDraw.Draw(screenshot)

    # Define grid line color and spacing
    grid_color = (255, 0, 0, 128)  # Red color with some transparency
    

    # Load a smaller font
    font_size = 13  # Set the desired font size
    font = ImageFont.truetype("arial.ttf", font_size)  # Load the font with the specified size

    # Draw vertical lines and place value pairs
    for x in range(0, screenshot.width, spacing):
        draw.line([(x, 0), (x, screenshot.height)], fill=grid_color)  # Draw vertical line
        for y in range(0, screenshot.height, spacing):
            # Place value pairs at each intersection
            grid_x = x // spacing + 1  # Calculate grid index for x (1-based)
            grid_y = y // spacing + 1  # Calculate grid index for y (1-based)
            value_pair = f"({grid_x}, {grid_y})"  # Create the value pair string based on grid index
            draw.text((x + 5, y + 5), value_pair, fill=(255, 255, 255, 255), font=font)  # Draw the text with the smaller font

    # Draw horizontal lines and place value pairs
    for y in range(0, screenshot.height, spacing):
        draw.line([(0, y), (screenshot.width, y)], fill=grid_color)  # Draw horizontal line

    # Save the modified screenshot
    screenshot.save(filename)

# Function to take a screenshot of the taskbar
def take_taskbar_screenshot(filename):
    taskbar_region = (0, 1030, 1920, 50)  # Example for a typical Windows taskbar
    screenshot = pyautogui.screenshot(region=taskbar_region)
    screenshot.save(filename)

# Function to encode an image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to send the base64-encoded images and prompt to OpenAI for analysis
def send_to_openai(images, prompt):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
            ] + [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img}",
                        "detail": "high"
                    },
                } for img in images
            ],
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300,
    )
    return response.choices[0]

# Function to take a screenshot without a grid overlay
def take_screenshot(filename):
    # Take a screenshot using pyautogui
    screenshot = pyautogui.screenshot()
    
    # Save the screenshot directly without modifications
    screenshot.save(filename)

# Function to take a 400x400 screenshot around the avatar position
def take_avatar_screenshot(avatar_position, filename):
    if avatar_position is None:
        print("Avatar position is None, cannot take screenshot.")
        return

    # Calculate the center of the avatar position
    x, y = avatar_position
    # Define the region for the screenshot (400x400 centered around the avatar)
    left = max(0, x - 200)
    top = max(0, y - 200)
    region = (left, top, 400, 400)  # (left, top, width, height)

    # Take the screenshot of the defined region
    avatar_screenshot = pyautogui.screenshot(region=region)
    avatar_screenshot.save(filename)

# Function to calculate the average position from the message positions
def calculate_average_position(message_positions):
    if not message_positions:
        return None

    total_x = 0
    total_y = 0
    count = 0

    for coord in message_positions:
        total_x += coord[0]
        total_y += coord[1]
        count += 1

    # Calculate average
    average_x = total_x // count
    average_y = total_y // count

    return (average_x, average_y)

# Function to extract the message position from the JSON response content
def extract_message_position(response_content):
    try:
        # Split the response content to isolate the JSON part
        cleaned_content = response_content.strip().split('```json', 1)[-1].strip()
        cleaned_content = cleaned_content.split('```', 1)[0].strip()  # Get the content before the closing ```

        print("cleaned_content: ", cleaned_content, "DONE")
        response_data = json.loads(cleaned_content)
        message_position = response_data.get("message_position")
        return message_position  # Return the message position list
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return None

# Function to read the new message from Teams
def read_new_message_from_teams():
    teams_screenshot_filename = "screenshot.png"
    teams_screenshot_with_grid_filename = "screenshot_with_grid.png"  # New filename for the grid screenshot
    take_screenshot(teams_screenshot_filename)  # Take a new screenshot without grid
    take_screenshot_with_grid(teams_screenshot_with_grid_filename)  # Take a new screenshot with grid
    teams_screenshot_base64 = encode_image_to_base64(teams_screenshot_filename)
    teams_screenshot_with_grid_base64 = encode_image_to_base64(teams_screenshot_with_grid_filename)  # Encode the grid screenshot

    prompt = """
        Please analyze the screenshot of the Teams window without the grid and tell me if there are any unread messages. Unread messages are denoted by 
        a white dot and the preview being bold. If there are unread messages, respond "Yes".
        Then, use the screenshot with the grid to provide the position of where the avatar of the unread message preview is, the unread message preview 
        includes a picture of the user, the user's name, and a small text preview of the message. Give the position of each corner as a list of a
        number pairs [(x, y),(x, y),(x, y),(x, y)] these pairs should be located in the grid overlay screenshot. Return these in json format with the 
        keys 'unread_message_present', and 'message_position'. The json should be formatted like this:
        {
            "unread_message_present": "Yes",
            "message_position": [[x, y],[x, y],[x, y],[x, y]]
        }
        ensure that no values are missing.
    """

    response = send_to_openai([teams_screenshot_base64, teams_screenshot_with_grid_base64], prompt)  # Send both images
    print(response.message.content)
    
    message_positions = extract_message_position(response.message.content.strip())  # Extract message positions
    print("message_positions: ", message_positions)

    if message_positions:
        average_position = calculate_average_position(message_positions)  # Calculate average position
        print("average_position: ", average_position)
        if average_position:
            # Convert grid position to pixel coordinates
            grid_x, grid_y = average_position
            pixel_x = (grid_x - 1) * spacing + (spacing // 2)  # Center the click in the grid cell
            pixel_y = (grid_y - 1) * spacing + (spacing // 2)  # Center the click in the grid cell
            
            # Move to the calculated position and click
            pyautogui.moveTo(pixel_x, pixel_y, 3)  # Move to the average position
            pyautogui.click()

    return response.message.content  # Return the response content

# Function to check if we are in the Teams app
def check_if_in_teams():
    screenshot_filename = "screenshot.png"
    screenshot_base64 = encode_image_to_base64(screenshot_filename)
    prompt = "Is the current window the Teams app? Please respond with 'Yes' or 'No'."
    
    response = send_to_openai([screenshot_base64], prompt)
    return "Yes" in response.message.content

# Function to navigate to the coordinates and click
def click_on_teams_shortcut(response_content):
    if not response_content:
        print("Response content is empty.")
        return
    
    cleaned_content = response_content.strip().split('\n', 1)[-1].strip()
    cleaned_content = cleaned_content.replace("```", "").strip()

    try:
        response_data = json.loads(cleaned_content)
        teams_shortcut_position = response_data.get("teams_shortcut_position")
        if teams_shortcut_position is not None:
            x = 75 + teams_shortcut_position * 50  # Calculate X coordinate based on position
            y = 1050  # Set Y coordinate to a fixed value
            
            pyautogui.moveTo(x, y, 3)
            pyautogui.click()
            return True  # Indicate that we clicked the Teams shortcut
        else:
            print("No teams_shortcut_position found in the response.")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        print(f"Response content: {cleaned_content}")

# Function to move the mouse to the avatar position and click
def move_and_click_on_avatar(avatar_position):
    if avatar_position is None:
        print("Avatar position is None, cannot move and click.")
        return

    # Assuming avatar_position is in the format "(x, y)"
    x, y = map(int, avatar_position.strip("()").split(","))
    pyautogui.moveTo(x, y, 3)  # Move to the avatar position
    pyautogui.click()  # Click at that position

# Main function to take a screenshot and send it
def main():
    in_teams = False  # Initialize in_teams as False
    while True:
        if not in_teams:  # Only run this block if not in Teams
            taskbar_screenshot_filename = "taskbar_screenshot.png"
            teams_shortcut_filename = "teams_shortcut.png"
            screenshot_filename = "screenshot.png"
            
            take_taskbar_screenshot(taskbar_screenshot_filename)
            take_screenshot(screenshot_filename)

            taskbar_screenshot_base64 = encode_image_to_base64(taskbar_screenshot_filename)
            teams_shortcut_base64 = encode_image_to_base64(teams_shortcut_filename)
            screenshot_base64 = encode_image_to_base64(screenshot_filename)

            images = [taskbar_screenshot_base64, teams_shortcut_base64, screenshot_base64]

            prompt = """
                Compare these two images, and tell me if there is currently a Teams message notification in the taskbar of the first image. 
                If there is not a notification, please analyze the image and identify the position of the Teams icon.
                Treat the icons on the taskbar as an array, starting from index 0 for the leftmost icon.
                If the Teams icon is present, provide its index in the array.

                Respond in json format and be sure that no values are missing.
                The object should have two keys: 
                'notification_present', and 'teams_shortcut_position'.
            """

            response = send_to_openai(images, prompt)
            response_content = response.message.content

            if "No" in response_content:
                print("Teams message notification is not present in the taskbar screenshot.")
            else:
                print(response_content)
                in_teams = check_if_in_teams() 
                if not in_teams:
                    in_teams = click_on_teams_shortcut(response_content)

        else:  # If in Teams, read the new message
            new_message_response = read_new_message_from_teams()
            print("New message summary:", new_message_response)  # Print the summary of new messages

        time.sleep(10)  # Wait for 10 seconds before taking another screenshot

if __name__ == "__main__":
    main()