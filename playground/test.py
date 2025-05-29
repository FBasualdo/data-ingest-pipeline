from requests import get

markdown_google_drive_url = "https://docs.google.com/feeds/download/documents/export/Export?id=1lmy55R593uDuZmS0K_yXWO3u2n3Y5OsjieCQWTw6ggU&exportFormat=txt"

response = get(markdown_google_drive_url)

print(response.text)

