import pandas as pd
import streamlit as st
from googleapiclient.errors import HttpError


# Channel statistics and playlist id
def get_channel_data(youtube, channel_id):
    try:
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channel_id
        )
        response = request.execute()
        items = response.get('items', {})

        if not items:
            return st.warning("No Channel Found. Please provide a proper channel Id.")

        channel_items = items[0]
        snippet = channel_items.get('snippet', {})
        content_details = channel_items.get('contentDetails', {})
        statistics = channel_items.get('statistics', {})

        channel_details = {
            "channel_title": snippet.get('title', None),
            "playlist_id": content_details.get('relatedPlaylists', None).get('uploads', None),
            "total_views": statistics.get('viewCount', 0),
            "total_subscribers": statistics.get('subscriberCount', 0),
            "total_videos": statistics.get('videoCount', 0)
        }

        return pd.DataFrame([channel_details])
    except HttpError as e:
        if e.resp.status == 400:
            return st.warning('No API Found')
        else:
            return st.warning(f'Error getting channel details {e}')


# Video id's function
def fetch_video_ids(youtube, playlist_id):
    try:
        all_video_ids = []
        page_token = None

        while True:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=page_token
            )

            response = request.execute()
            items = response.get('items')

            for item in items:
                content_details = item.get('contentDetails', {})
                video_id = content_details.get("videoId")
                all_video_ids.append(video_id)

            page_token = response.get('nextPageToken', None)

            if not page_token:
                break

        return all_video_ids
    except HttpError as e:
        if e.resp.status == 404:
            return st.warning("No Videos in the channel")
        else:
            return st.warning(f'Error getting video details {e}')


# video meta data function
def get_video_meta_data(youtube, video_ids):
    try:

        all_video_details = []

        for i in range(0, len(video_ids), 50):
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids[i:i + 50])
            )

            response = request.execute()

            items = response.get('items', [])

            for item in items:
                snippet = item.get('snippet', {}),
                content_details = item.get('contentDetails', {}),
                statistics = item.get('statistics', {})

                video_details = {
                    'video_title': snippet[0].get('title', None),
                    'description': snippet[0].get('description', None),
                    'published_at': snippet[0].get('publishedAt', None),
                    'tags': snippet[0].get('tags', None),
                    'duration': content_details[0].get('duration', None),
                    'views': statistics.get('viewCount', 0),
                    'likes': statistics.get('likeCount', 0),
                    'comments': statistics.get('commentCount', 0)
                }

                all_video_details.append(video_details)

        return pd.DataFrame(all_video_details)
    except HttpError as e:
        return st.warning(f'Error getting video meta data details {e}')


