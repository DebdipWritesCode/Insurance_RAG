import requests

CITY_TO_LANDMARK = {
    "Delhi": "Gateway of India",
    "Mumbai": "India Gate",
    "Chennai": "Charminar",
    "Hyderabad": "Marina Beach",
    "Ahmedabad": "Howrah Bridge",
    "Mysuru": "Golconda Fort",
    "Kochi": "Qutub Minar",
    "Pune": "Meenakshi Temple",
    "Nagpur": "Lotus Temple",
    "Chandigarh": "Mysore Palace",
    "Kerala": "Rock Garden",
    "Bhopal": "Victoria Memorial",
    "Varanasi": "Vidhana Soudha",
    "Jaisalmer": "Sun Temple",
    "Paris": "Taj Mahal",
    # Add rest if needed...
    
    # From PDF, only those relevant for mapping
    "Hyderabad": "Taj Mahal",
    "New York": "Eiffel Tower",
    "Tokyo": "Big Ben",
    "Istanbul": "Big Ben"
}

LANDMARK_TO_API = {
    "Gateway of India": "https://register.hackrx.in/teams/public/flights/getFirstCityFlightNumber",
    "Taj Mahal": "https://register.hackrx.in/teams/public/flights/getSecondCityFlightNumber",
    "Eiffel Tower": "https://register.hackrx.in/teams/public/flights/getThirdCityFlightNumber",
    "Big Ben": "https://register.hackrx.in/teams/public/flights/getFourthCityFlightNumber"
}

def get_flight_number():
    fav_city_resp = requests.get("https://register.hackrx.in/submissions/myFavouriteCity", timeout=5)
    fav_city_resp.raise_for_status()
    city = fav_city_resp.json()["data"]["city"]

    landmark = CITY_TO_LANDMARK.get(city)
    if not landmark:
        raise ValueError(f"No landmark mapping found for city: {city}")

    api_url = LANDMARK_TO_API.get(landmark, "https://register.hackrx.in/teams/public/flights/getFifthCityFlightNumber")

    flight_resp = requests.get(api_url, timeout=5)
    flight_resp.raise_for_status()
    flight_number = flight_resp.json()["data"]["flightNumber"]

    return flight_number