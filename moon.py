# Used to make calls to the Discord API
import requests

# Used to read the config file
import json

# Used to display the last update time
from datetime import datetime

# Read the config file
with open("config.json", "r") as f:
    config = json.load(f)

def resolve_icon(weather):
    """
    Resolve the weather icon

    Args:
        weather (str): The weather object

    Returns:
        emoji (str): The emoji name
    """
    # Map moon phase data to appropriate emoji
    # There's only 4 phases that OpenWeatherMap recognises. 
    if weather['moon_phase'] == 0 or weather['moon_phase'] == 1:
        emoji = "🌑"
    elif weather['moon_phase'] < 0.25: # FIrst Quarter
        emoji = "🌒"
    elif weather['moon_phase'] < 0.5: # Full Moon
        emoji = "🌕"
    elif weather['moon_phase'] < 0.75: # Last Quarter
        emoji = "🌔"
    else:
        emoji = "🌙"
    return emoji


def update_custom_status(text, emoji):
    """
    Update the Discord Custom Status with the specified text and emoji

    Args:
        text (str): The new custom status content
        emoji (str): The emoji to use in the custom status

    Returns:
        data (any): The Discord response
    """

    custom_status = {'custom_status':{'text': text, 'emoji_name': emoji}}

    url = "https://discord.com/api/v6/users/@me/settings"
    headers = {
        "Authorization": config["discord_token"],
        "Content-Type": "application/json",
    }
    response = requests.patch(url, json.dumps(custom_status), headers=headers)
    data = response.json()
    return data

def get_weather_of(lat, lon):
    # Open Weather Map API Base URL
    base_url = (
        "https://api.openweathermap.org/data/2.5/onecall?"
        + "lat=" + config["lat"]
        + "&lon=" + config["lon"]
        + "&appid=" + config["api_key"]
        + "&exclude=" + config["exclude"]
    )
    response = requests.get(base_url)
    data = response.json()
    
    try:
        # Returns moon phase
        return {'moon_phase': data['daily'][0]['moon_phase']}
    except KeyError:
        print("Error: Could not find moon phase in API response.")
        return {}

def generate_custom_status_content(weather):
    """
    Generate the custom status content

    Args:
        weather (str): The weather of the city

    Returns:
        custom_status_content (str): The final custom status content
    """
    # The current time (hours and minutes)
    now = datetime.now().strftime("%I:%M")

    # Get the weather emoji
    emoji = resolve_icon(weather)

    # Generate the custom status content
    custom_status_content = f"Moon phase: {emoji} | {now}"
    return custom_status_content

def main():
    """
    Main code which calls the other functions
    """
    # Get the weather of the city
    weather = get_weather_of(config["lat"], config["lon"])
    # Get the weather emoji
    emoji = resolve_icon(weather)
    # Update the Custom Status
    status = update_custom_status("", emoji)
    # Log
    log_prefix = "[" + datetime.now().strftime("%I:%M %p") + "]"

    if "locale" in status:
        print(log_prefix + " Successfully updated custom status.")

    else:
        # If Discord returns an error
        print(log_prefix + f" Error: {status['message']}")
        # If Discord returned a message
        if "message" in status:
            # If the error is caused by the personal access token
            if status["message"] == "401: Unauthorized":
                print(
                    log_prefix
                    + " Seems like your Discord personal access token is invalid..."
                )
            else:
                print(
                    log_prefix
                    + " Something happened. Message is the following: "
                    + status["message"]
                )
        # If Discord didn't return anything
        else:
            print(
                log_prefix
                + " Something happened. Here is the Discord API response: "
                + status["message"]
            )

if __name__ == "__main__":
    main()
