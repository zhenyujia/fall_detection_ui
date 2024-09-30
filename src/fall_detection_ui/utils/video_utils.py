import pafy
import os
from loguru import logger
import cv2
from pytubefix import YouTube
import time
import streamlit as st

def download_youtube_videos(youtube_video_url, output_directory):
    video = pafy.new(youtube_video_url)

    title = video.title

    video_best = video.getbest()

    output_file_path = f'{output_directory}/{title}.mp4'
    print(output_file_path)
    video_best.download(filepath=output_file_path, quiet=True)

    return title

def download(youtube_video_url, output_directory):
    yt = YouTube(youtube_video_url, use_po_token=True)
    #print(yt.title)

    ys = yt.streams.get_highest_resolution()
    ys.download()


def display_frames(frames, fps):
    delay = 1 / fps

    for frame in frames:
        start_time = time.time()

        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame = Image.fromarray(frame)
        #frame = ImageTk.PhotoImage(frame)

        #self.video_label.config(image=frame)
        # self.video_label.image = frame
        #
        # self.root.update_idletasks()
        # self.root.update()

        st.image(frame)

        time_elapsed = time.time() - start_time
        time_to_wait = delay - time_elapsed
        if time_to_wait > 0:
            time.sleep(delay)

if __name__ == "__main__":

    # neither worked. Eventually I used https://publer.io/tools/youtube-short-downloader

    video_download_directory = "download_videos"
    os.makedirs(video_download_directory, exist_ok = True)

    test_video = download("https://youtube.com/shorts/GUPVUurqqPY?si=3XosAdXNmPgZ-Wkb", video_download_directory)