# test_main.py

import pytest
from fastapi.testclient import TestClient
from main import app, MonitorPayload, Setting
from datetime import datetime

client = TestClient(app)

def test_get_integration_json():
    response = client.get("/integration.json")
    assert response.status_code == 200
    assert response.json()["data"]["descriptions"]["app_name"] == "Weather and Air Quality Monitor"

def test_handle_incoming_request(mocker):
    # Mock the handle_weather_request function
    mock_handle_weather_request = mocker.patch("main.handle_weather_request")

    payload = MonitorPayload(
        channel_id="test_channel",
        return_url="http://test/return",
        settings=[Setting(label="location", type="text", required=True, default="london")]
    )

    response = client.post("/tick", json=payload.model_dump())
    assert response.status_code == 202
    assert mock_handle_weather_request.called
    # Verify that the correct arguments were passed to the mock
    mock_handle_weather_request.assert_called_once_with(payload)

def test_weather_request(mocker):
    # Mock the get_weather function to avoid actual API calls
    mock_weather_data = {
        "location": {"name": "London"},
        "current": {
            "temp_c": 15.0,
            "condition": {"text": "Partly Cloudy"},
            "wind_kph": 10,
            "pressure_mb": 1015,
            "air_quality": {
                "co": 0.1,
                "no2": 0.2,
                "o3": 0.3,
                "so2": 0.1,
                "pm2_5": 5,
                "pm10": 10,
                "us-epa-index": 1
            }
        }
    }

    mocker.patch("main.get_weather_data", return_value=mock_weather_data)  # Mock get_weather
    mock_post = mocker.patch("requests.post")  # Mock requests.post

    payload = MonitorPayload(
        channel_id="test_channel",
        return_url="http://test/return",
        settings=[Setting(label="location", type="text", required=True, default="london")]
    )

    # Send a POST request to the /tick endpoint to trigger the background task
    response = client.post("/tick", json=payload.model_dump())
    assert response.status_code == 202

    # Verify that requests.post was called with the correct data
    expected_message = f"""
    Time: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}

    Location: London
    Temp.: 15.0 deg. celsius
    Condition: Partly Cloudy
    Wind Speed: 10 kmph
    Pressure: 1015 milibar
    Air Quality:
        CO2: 0.1
        NO2: 0.2
        O3: 0.3
        SO2: 0.1
        Fine Particle Matter: 5
        Particle Matter: 10
        Air Quality Index: 1
    """

    expected_data = {
        "message": expected_message,
        "username": "Weather and Air Quality Monitor",
        "event_name": "Weather and Air Quality check",
        "status": "success"
    }

    # Now verify that requests.post was called with the expected data
    mock_post.assert_called_once_with("http://test/return", json=expected_data)