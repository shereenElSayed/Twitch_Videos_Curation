##TODO
#1. get token: curl -X POST "https://id.twitch.tv/oauth2/token" -H "Content-Type: application/x-www-form-urlencoded" -d "client_id=19zaxqreb96fvg9pnkxou4qtvew1da&client_secret=9zkqhuadipo6ddtc8xvgfkio1uhvh6&grant_type=client_credentials"
#2. extract the token from step 1 then use it to get the streams
#3. streams: curl -X GET "https://api.twitch.tv/helix/streams" -H "Authorization: Bearer 6avslsam2g08dkcdr89j4yc377p8di" -H "Client-Id: 19zaxqreb96fvg9pnkxou4qtvew1da"
#Store what returned from step 3 and get the pagination key from the returned json
# get the next page of the next top most active streams after the first response -- update after:
#curl -X GET "https://api.twitch.tv/helix/streams?first=20&after=eyJiIjp7IkN1cnNvciI6ImV5SnpJam94TkRjNE9UTXVNakUwTmpZMk9UUXpPRElzSW1RaU9tWmhiSE5sTENKMElqcDBjblZsZlE9PSJ9LCJhIjp7IkN1cnNvciI6ImV5SnpJam95TWpRek15NHdNRFF3TWpJM05EUTFORFlzSW1RaU9tWmhiSE5sTENKMElqcDBjblZsZlE9PSJ9fQ" -H "Authorization: Bearer 6avslsam2g08dkcdr89j4yc377p8di" -H "Client-Id: 19zaxqreb96fvg9pnkxou4qtvew1da"

from cmath import log
import json
import logging
import traceback
import requests
import datetime

vidoes_to_watch = {'videos' : []}
today_date = datetime.datetime.now().date()
logging.basicConfig(filename=f'twitch_streams.log', filemode='w', format='%(funcName)s:%(lineno)s - %(levelname)s - %(message)s')
 


#Get access token
header = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = {'client_id': '19zaxqreb96fvg9pnkxou4qtvew1da',
'client_secret': '9zkqhuadipo6ddtc8xvgfkio1uhvh6',
'grant_type' :'client_credentials'}
res = None
try:
    res = requests.post(url='https://id.twitch.tv/oauth2/token', headers=header,
    data=payload)
except:
    print("Cannot get access tokens")

access_token = res.json()['access_token']
print(f'access token: {access_token}')
#Get most active streams
url = "https://api.twitch.tv/helix/streams"
bearer = 'Bearer ' +access_token
header = {'Authorization': bearer,
'Client-Id': '19zaxqreb96fvg9pnkxou4qtvew1da'}
payload = {}
activeStreamsList = []
morePages = True
after = ""
count = 0
# streams_file = open("streams_file.json", "w")
while morePages and count < 2:
    try:
        if after  == "":
            "Getting active stream"
            active_streams = requests.get(url, headers=header).json()
            # print(f"ACTIVE STREAM - no after: {active_streams}")
            # print(f"type of active stream {type(active_streams)}")
            activeStreamsList += (active_streams["data"])
        else:
            nextPageURL = url + f"?first=10&after={after}"
            active_streams = requests.get(nextPageURL, headers=header).json()
            # print(f"ACTIVE STREAM - no after: {active_streams}")
            # print(f"ACTIVE STREAM - WITH PAGE: {active_streams}")
            activeStreamsList += (active_streams["data"])
    except Exception as e:
        logging.error("Active streams cannot be retrieved")
        logging.error(traceback.print_exc())

    count += 1
    if "pagination" in active_streams:
        print("pagination")
        after = active_streams["pagination"]["cursor"]
        print(f"cursor: {after}")

    else:
        after = ""
        morePages = False
        logging.info("No more pages")
   
    # json.dump(active_streams, streams_file, indent=4)
    #Get most recent videos from these streams
for stream in activeStreamsList:
    user_id = stream["user_id"] #Streamer ID
    print(f"streamer: {user_id}")
    url = f"https://api.twitch.tv/helix/videos?user_id={user_id}"
    after = ""
    morePages = True
    pageCount = 0
    user_videos = []
    while morePages:
        try:
            print(f"page count {pageCount}")
            if after  == "":
                streamer_videos = requests.get(url, headers=header).json()
                # logging.info(f"streamer_videos - no after: {streamer_videos}")

                user_videos += streamer_videos['data']
                # logging.info("\n____________\n" + streamer_videos)
            else:
                nextPageURL = url + f"?first=100&after={after}"
                streamer_videos = requests.get(nextPageURL, headers=header).json()
                # logging.info(f"streamer_videos - with after: {streamer_videos}")
                user_videos += streamer_videos['data']

            if "pagination" in streamer_videos and streamer_videos["pagination"] != {} :
                print("pagination found")
                after = streamer_videos["pagination"]["cursor"]
                pageCount += 1
            else:
                after = ""
                morePages = False
        
    
        except Exception as e:
            logging.error("Active streams cannot be retrieved")
            logging.error(e)
    
    user_videos_file = open(f"user_videos_{user_id}.json", "w")
    json.dump(user_videos, user_videos_file, indent=4)
        # print(videos)
        # break
        # for video in videos:
        #     created_at = video["created_at"].split("T")[0]
        #     datetime_object = datetime.datetime.strptime(created_at, '%Y-%M-%d').date()

        #     if datetime_object.strftime('%Y-%M-%d') == today_date.strftime('%Y-%M-%d'):
        #         vidoes_to_watch["videos"].append(video)

        #To get all videos for this streamer:



videos_file = open(f"videos_file_{today_date.strftime('%Y_%M_%d')}.json", "w")
json.dump(vidoes_to_watch, videos_file, indent=4)