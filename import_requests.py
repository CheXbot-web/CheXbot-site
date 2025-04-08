import requests

params = {
    "key": "AIzaSyAzizoJdpjysvJOIa8rk9WCxHB1JevKwcw",
    "cx": "750eea185037c4ae7",
    "q": "The Moon has an atmosphere"
}

res = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
print(res.json())
