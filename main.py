from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str


class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]


@app.get("/")
def index():
    message = {
        "info": "Welcome to Weather an air quality Monitor",
        "status": "success"
    }
    return message


@app.get("/integration.json")
def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")

    integration_json = {
        "data": {
            "date": {"created_at": "2025-02-18", "updated_at": "2025-02-18"},
            "descriptions": {
                "app_name": "Weather and Air Quality Monitor",
                "app_description": "A Weather and Air Quality Monitor for a Specific Location",
                "app_logo": "https://i.ibb.co/B1r0BZn/freepik-abstract-logo-for-weather-and-air-quality-using-in-18737.jpg",
                "app_url": base_url,
                "background_color": "#fff",
            },
            "is_active": True,
            "integration_type": "interval",
            "key_features": [
                "- monitors weather conditions",
                "- monitors air quality"
            ],
            "integration_category": "Monitoring & Logging",
            "author": "Kenechi Nzewi",
            "website": base_url,
            "settings": [
                {
                    "label": "location",
                    "type": "text",
                    "required": True,
                    "default": "london"
                },
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "0 * * * *",
                },
            ],
            "target_url": "",
            "tick_url": f"{base_url}/tick"
        }
    }

    return integration_json


def handle_weather_request(payload: MonitorPayload):
    location = payload.settings[0].default

    weather_data = get_weather(location)

    send_message_to_telex(payload, weather_data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)