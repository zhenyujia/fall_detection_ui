import time


import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import os
from PIL import Image, ImageTk
import time
import tensorflow as tf
import numpy as np
import threading
from loguru import logger


class FallDetector:

    def __init__(self):
        self.root = tk.Tk()
        self.result = None  # Result will be set later
        self.video_label = None
        self.result_label = None
        self.file_entry = None
        self.selected_file = None  # To store the selected file path
        self.model_input_queue = []
        self.display_queue = []
        self.model_output_queue = []

        working_directory = os.getcwd()
        model_path = os.path.join(working_directory, "model", 'LRCN_FAIL_Date_Time_2024_08_20__00_12_41__Loss_0.6136224865913391__Accuracy_0.8586956262588501.h5')
        self.model = tf.keras.models.load_model(model_path)

    def run_predict(self, model_input_queue, predict_output_queue, cv: threading.Condition):
        while True:
            with cv:
                while not model_input_queue:
                    start_time = time.time()
                    logger.debug("waiting for model input...")
                    cv.wait()

                time_took = time.time() - start_time
                logger.debug("Received module input after waiting for {t} secs".format(t=time_took))

                start_time = time.time()
                frames_list = []
                for f in model_input_queue:
                    resized_frame = cv2.resize(f, (124, 124))
                    frames_list.append(resized_frame)
                prob = self.model.predict(np.expand_dims(frames_list, axis=0))[0]
                predict_output_queue.append(prob)
                model_input_queue.clear()
                time_took = time.time() - start_time
                logger.debug("Prediction done. It took {t} secs".format(t=time_took))
                cv.notify()


    def play_video(self):
        while True:
            while True:
                if self.display_queue:
                    frames = self.display_queue.copy()
                    self.display_queue.clear()

                    self.model_input_queue = frames.copy()

                    #display frames
                    print(f"video playing. frames size {len(frames)}")
                    self.display_frames(frames, 30)
                    break

                else:
                    time.sleep(.3)
                    print("sleeping 0.2 play_video")

            while not self.model_output_queue:
                print("waiting model output")
                time.sleep(.3)

            # model outputs here (0 or 1)
            self.result = self.model_output_queue[0]
            print("recieved results", self.result)
            self.model_output_queue.clear()


            # find a way to display results from model
            if self.result is not None:
                # Create and place the result label over the video
                self.result_label = tk.Label(self.video_label, font=("Helvetica", 36), fg="white")
                self.result_label.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-20)
                self.update_result_indicator()

            if self.result_label:
                self.result_label.destroy()


    def update_result_indicator(self):
        if self.result:
            self.result_label.config(text="Fall", bg="red")
        else:
            self.result_label.config(text="Normal", bg="green")


    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a Video Feed",
            filetypes=[("All Video Feeds", "*.mp4;*.avi;*.mov"), ("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("MOV files", "*.mov")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.selected_file = file_path  # Store the selected file path

            # Determine the result based on file name
            file_name = os.path.basename(file_path)
            # model = tf.keras.models.load_model('fall-detection_v2.h5')

            self.result = 0

    def get_selected_file(self):
        return self.selected_file

    def toggle_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
        return "break"

    def end_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)
        return "break"

    def display(self):
        self.root.title("Video Player Interface")
        self.root.configure(bg='blue')

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)

        self.file_entry = tk.Entry(self.root, font=("Helvetica", 14))
        self.file_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        browse_button = tk.Button(self.root, text="Select Feed", command=self.browse_file, font=("Helvetica", 14))
        browse_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        play_button = tk.Button(self.root, text="View Feed", command=self.start_video, font=("Helvetica", 14))
        play_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.root.mainloop()