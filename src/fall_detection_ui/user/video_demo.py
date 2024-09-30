import asyncio

import streamlit as st

import os
import threading
import cv2
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from streamlit.runtime.scriptrunner import add_script_run_ctx

from tensorflow.python.ops.signal.shape_ops import frame

from fall_detection_ui.model.FallDetection import fall_detector  # Import the fall_detector function
from fall_detection_ui.utils.FrameFetcher import FrameFetcher
from fall_detection_ui.utils.video_utils import display_frames


@st.cache_data  # 👈 Add the caching decorator
def load_frame_fetcher(video_path):
    return FrameFetcher(video_path)

@st.cache_resource # 👈 Add the caching decorator
def get_thread_executor():
    return ThreadPoolExecutor(max_workers=10)

# Get the current working directory (this is the project folder)
project_directory = os.getcwd()
video_directory = os.path.join(project_directory, "..", "videos")

# Define the supported video file extensions
supported_extensions = ('.mp4', '.avi', '.mov')

# List all video files in the project directory
video_files = [f for f in os.listdir(video_directory) if f.endswith(supported_extensions)]

# Custom CSS for positioning buttons and text over the video
st.markdown(
    """
    <style>
    .video-container {
        position: relative;
    }
    .overlay-content {
        position: absolute;
        top: 20px;
        left: 20px;
        color: white;
        z-index: 10;
    }
    .overlay-buttons {
        position: absolute;
        top: 80px;
        left: 20px;
        z-index: 10;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# If there are video files, display buttons and fall detection result over the video
if video_files:
    selected_video = None

    # HTML container for video and overlay
    st.markdown('<div class="video-container">', unsafe_allow_html=True)

    # Display video buttons at the top left corner
    st.markdown('<div class="overlay-buttons">', unsafe_allow_html=True)

    # Display video buttons side by side
    cols = st.columns(3)
    for idx, video_file in enumerate(video_files):
        col = cols[idx % 3]
        if col.button(video_file):
            selected_video = video_file
    st.markdown('</div>', unsafe_allow_html=True)

    # If a video has been selected, display the video full-screen
    if selected_video:
        video_path = os.path.join(video_directory, selected_video)

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        # Display the video in full-screen
        #st.video(video_path, format="video/mp4", start_time=0)

        #1. start a thread to fetch 24 frames and put into st.session.
        #2  start another thread to run model and set result to st.session
        frame_fetcher=load_frame_fetcher(video_path)
        condition = threading.Condition()

        frames_to_display = []

        logger.debug("main thread Id: {id}".format(id=threading.get_ident()))
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)

        #executor = get_thread_executor()
        #asyncio.get_event_loop().run_in_executor(executor, frame_fetcher.run_fetch(frames_to_display, condition))
        thread = threading.Thread(target=frame_fetcher.run_fetch, args=(frames_to_display, condition))
        #add_script_run_ctx(thread)
        thread.start()

        with st.empty():
            with condition:
                while True:
                    while not frames_to_display:
                        logger.debug("waiting for frames to display...")
                        condition.wait()

                    logger.debug("done waiting. start to display.")
                    display_frames(frames_to_display,fps)
                    frames_to_display.clear()
                    condition.notify()




        # Display fall detection result as an overlay on the video
        detection_result = fall_detector(video_path)
        st.markdown(f'<div class="overlay-content"><h2>Fall Detection Result: {detection_result}</h2></div>',
                    unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.write("No video files found in the project directory.")
