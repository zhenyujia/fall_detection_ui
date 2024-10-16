import os
from loguru import logger
import cv2
from numpy.f2py.auxfuncs import throw_error
from threading import Condition
import threading
import time




class FrameFetcher:

    def __init__(self, selected_file):
        self.selected_file = selected_file
        self.start = False
        self.stop = False

    def run_fetch(self, frames_to_update, cv: Condition, step):
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
            start_time = time.time()
            logger.debug("start to get frames...")
            frames, start_index = self.get_n_frames(start_index, total_frame, cap, 15, step)
            if not frames:
                break

            time_took = time.time() - start_time
            logger.debug("got frames. Time spent: {t} secs".format(t=time_took))
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



    def get_n_frames(self, start_index, total_frame, cap: cv2.VideoCapture, num_frames_to_get, step = 1):
        frames = []
        next_index = start_index

        if total_frame < start_index:
            return []
        for index in range(start_index, min(start_index + num_frames_to_get * step, total_frame), step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)

            ret, frame = cap.read()
            frames.append(frame)
            next_index += step

        return frames, next_index