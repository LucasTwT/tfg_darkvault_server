from fastapi import Request
import geoip2.database
from geoip2.errors import AddressNotFoundError

reader = geoip2.database.Reader(r"/app/app/core/GeoLite2-City.mmdb")


def get_client_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host

def get_user_agent(request: Request):
    return request.headers.get("User-Agent", "unknown")

def get_location_by_ip(ip: str):
    try:
        response = reader.city(ip)
        country = response.country.name
        city = response.city.name
        return country, city
    except AddressNotFoundError:
        return "Unknown", "Unknown"
    except Exception:
        return "Unknown", "Unknown"