import os
from loguru import logger
import cv2
from numpy.f2py.auxfuncs import throw_error
from threading import Condition
import threading




class FrameFetcher:

    def __init__(self, selected_file):
        self.selected_file = selected_file
        self.start = False
        self.stop = False

    def run_fetch(self, frames_to_update, cv: Condition):
        logger.debug("run_fetch thread Id: {id}".format(id=threading.get_ident()))
        cap = cv2.VideoCapture(self.selected_file)
        total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if not cap.isOpened():
            error_msg = "Failed to open the video file : {file}".format(file=self.selected_file)
            logger.error(error_msg)
            throw_error(error_msg)

        self.start = True
        start_index = 0
        while True:
            frames, start_index = self.get_24_frames(start_index, total_frame, cap)
            if not frames:
                break

            logger.debug("got frames")
            # once new frames retrieved, check if the previous frames have been consumed
            with cv:
                while frames_to_update:
                    logger.debug("previous frames are not consumed yet. will wait...")
                    cv.wait()
                logger.debug("sending back frames")
                #frames_to_update = frames.copy()  # this will not change the variable outside this function
                frames_to_update.extend(frames)
                cv.notify()

        # at the end, release
        cap.release()



    def get_24_frames(self, start_index, total_frame, cap: cv2.VideoCapture):
        frames = []
        next_index = start_index

        if total_frame < start_index:
            return []
        for index in range(start_index, min(start_index + 24, total_frame)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)

            ret, frame = cap.read()
            frames.append(frame)
            next_index += 1

        return frames, next_index