import streamlit as st
import pandas as pd
from googleapiclient.discovery import build

from helpers import get_channel_data, fetch_video_ids, get_video_meta_data


st.title('YouTube Data Gathering Project')


def sidebar():

    st.sidebar.subheader('YouTube Data Gathering Project')
    st.sidebar.write('Get any favorite channel data with just a click.')

    st.sidebar.divider()

    st.sidebar.markdown('Source code can be found [here](https://github.com/Vamshi-Munukuntla/data_project_using_youtube_api)')

    st.sidebar.markdown('Made by [Vamshi Munukuntla](https://github.com/Vamshi-Munukuntla)')

def inputs():
    with st.form(key='youtube'):

        col1, col2 = st.columns(2)

        api_key = col1.text_input(label='API Key', key='api', placeholder="Please paste your API key here.")
        channel_id = col2.text_input(label='Channel ID', key='channel', placeholder="Please paste your channel id here.")

        submitted = st.form_submit_button("Get Data")

        if submitted and (not api_key or not channel_id):
            st.warning('Please provide both API Key and Channel Id')
            return None, None, submitted

    return api_key, channel_id, submitted


def get_data(api_key, channel_id):

    youtube = build(
        serviceName='youtube',
        version='v3',
        developerKey=api_key
    )

    channel_df = get_channel_data(youtube, channel_id)

    if not channel_df.empty:
        playlist_id = channel_df.loc[0, 'playlist_id']
        total_videos = channel_df.loc[0, 'total_videos']
        if total_videos == str(0):
            return st.warning('Channel has No Videos')
        else:
            video_ids = fetch_video_ids(youtube, playlist_id)
            video_df = get_video_meta_data(youtube, video_ids)
            total_df = pd.merge(video_df, channel_df, how='cross')

            return total_df


def download_data(df, filename):

    st.write('Top 5 Rows')
    st.dataframe(df.head())

    youtube_data = df.to_csv(index=False)

    st.download_button(
        label='Download Data',
        key='download_data',
        data=youtube_data,
        type='primary',
        file_name=filename
    )


if __name__ == "__main__":

    sidebar()
    api_key, channel_id, submitted = inputs()

    if submitted and api_key is not None and channel_id is not None:
        data = get_data(api_key, channel_id)

        if data is not None and not data.empty:
            download_data(data, data.loc[0, 'channel_title'])




