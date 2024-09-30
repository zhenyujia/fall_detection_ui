import time


def fall_detector(video_path):
    time.sleep(1)
    return True

import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import os
from PIL import Image, ImageTk
import time
import tensorflow as tf
import numpy as np
import threading


class VideoDisplayObject:

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
        self.model = tf.keras.models.load_model('fall-detection_v2.h5')


    def get_24_frames(self, start_index):
        video_file = self.selected_file

        if not os.path.isfile(video_file):
            messagebox.showerror("File Error", "The file does not exist")
            return []

        cap = cv2.VideoCapture(video_file)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30

        if not cap.isOpened():
            messagebox.showerror("File Error", "Failed to open the video file")
            return []

        frames = []
        next_index = start_index
        total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if total_frame < start_index:
            return []
        for index in range(start_index, min(start_index + 24, total_frame)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)

            ret, frame = cap.read()
            frames.append(frame)
            next_index += 1

        cap.release()
        return frames, next_index, fps


    def async_get_frames(self):
        start_index = 0

        while True:
            frame_list, start_index, fps = self.get_24_frames(start_index)
            print(f'retreiving frames {len(frame_list)}')

            if not frame_list:
                break

            while self.display_queue:
                time.sleep(.4)
                print("sleeping .4 seconds async_get_frames")

            self.display_queue = frame_list.copy()
            print("saved to display_queue")


    def display_frames(self, frames, fps):
        delay = 1 / fps

        for frame in frames:
            start_time = time.time()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)

            self.video_label.config(image=frame)
            self.video_label.image = frame

            self.root.update_idletasks()
            self.root.update()

            time_elapsed = time.time() - start_time
            time_to_wait = delay - time_elapsed
            if time_to_wait > 0:
                time.sleep(delay)


    def async_analyze_frames(self):
        while True:
            if self.model_input_queue:
                print("model received data ", len(self.model_input_queue))
                frames_list = []

                for f in self.model_input_queue:
                    resized_frame = cv2.resize(f, (124, 124))
                    frames_list.append(resized_frame)

                self.model_input_queue.clear()

                predicted_label_probabilities = self.model.predict(np.expand_dims(frames_list, axis=0))[0]

                if predicted_label_probabilities > .7:
                    predicted_label = 1
                else:
                    predicted_label = 0

                predicted_class_name = ["nofall", "fall"][predicted_label]

                print(predicted_class_name, predicted_label_probabilities, int(predicted_label))

                while self.model_output_queue:
                    print("model waiting .3")
                    time.sleep(.3)

                self.model_output_queue.append(int(predicted_label))

            else:
                time.sleep(.3)
                print("analysis sleeping .3")


    def start_video(self):

        if self.selected_file is None:
            messagebox.showwarning("Input Error", "Please select a video file first.")
            return

        x = threading.Thread(target=self.async_analyze_frames)
        y = threading.Thread(target=self.async_get_frames)

        x.start()
        y.start()

        self.play_video()


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