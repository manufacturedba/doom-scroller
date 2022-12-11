import time
from adafruit_matrixportal.matrixportal import MatrixPortal
import gc
import terminalio
import board
import random

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

SCROLL_DELAY = 0.06
UPDATE_DELAY = 300

matrixportal = MatrixPortal(
    status_neopixel=board.NEOPIXEL,
    debug=True,
    height=64,
    width=64)

matrixportal.add_text(
    text_color=0xFF0000,
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 2) + 6),
    scrolling=True
)

matrixportal.set_background(0)

matrixportal.set_text('Doom scroller is loading', 0)
matrixportal.scroll_text(SCROLL_DELAY)

while True:
    matrixportal.network.connect()

    global items
    global pageToken

    pageToken = None

    minimumLength = 50
    titles = []

    while len(titles) < minimumLength:
        api_url = "https://youtube.googleapis.com/youtube/v3/playlistItems?maxResults=10&part=snippet&playlistId=PLlTLHnxSVuIzrARlmz9oCfQEF08UV-v-E"
        
        if pageToken:
            api_url += "&pageToken=" + pageToken

        reply = matrixportal.network._wifi.requests.get(api_url, timeout=10)
        print(reply.status_code)
        if reply.status_code == 200:
            json = reply.json()
            items = json.get('items')
            for item in items:
                title = item['snippet']['title']
                titles.append(title)

            pageToken = json.get('nextPageToken')
        
        # now clean up
        reply.close()
        reply = None

        gc.collect()

    blocklist = ['Private video', 'Deleted video', 'Unlisted video']
    replacelist = [['Tucker Carlson: ', ''], ['’', '\''], ['“', '"'], ['”', '"'], ['‘', '\'']]

    print(titles)

    while True:
        choice = random.choice(titles)

        if choice not in blocklist: 
            time.sleep(5)
            try:
                title = choice
                for replace in replacelist:
                    title = title.replace(replace[0], replace[1])
                matrixportal.set_text(title, 0)
                matrixportal.scroll_text(SCROLL_DELAY)
            except:
                print('Unable to set text')

    # while True:
    #     for item in items:
    #         if item['snippet']['title'] not in blocklist: 
    #             time.sleep(5)
    #             try:
    #                 title = item['snippet']['title']
    #                 for replace in replacelist:
    #                     title = title.replace(replace[0], replace[1])
    #                 matrixportal.set_text(title, 0)
    #                 matrixportal.scroll_text(SCROLL_DELAY)
    #                 time.sleep(5)
    #             except:
    #                 print('Unable to set text')
