# Author: Jean Kossaifi

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

import os
from scipy.misc import imread
import glob
import numpy as np


class ShapeImageCollection(object):
    """ A simple class to iterate through the frames of a folder

    Simply builds a list of filenames corresponding to the images and their
    annotations and loads them when needed.
    """
    def __init__(self, folder, shape_ext='.pts', image_ext='.png', 
                 image_to_gray=True, verbose=0):
        """ Class that behave like a list of (shape, image)

        Each shape is a file containing facial landmarks on the face

        Parameters
        ----------
        folder: string
                path to the folder containing the images and shapes
        shape_ext: string, default is '.pts'
                extension of the shape files
        image_ext: string, default is '.png'
        image_to_gray: bool, default is True
                if True, image is converted to gray levels
        verbose: int
                level of verbosity
        """
        self.verbose = verbose
        self.image_to_gray = image_to_gray

        # Create a list of the shapes and images
        image_files = sorted(glob.glob(os.path.join(folder, '*' + image_ext)))

        self.filename_list = []
        for img_filename in image_files:
            frame_name = os.path.splitext(os.path.basename(img_filename))[0]
            shape_filename = os.path.join(folder, frame_name + shape_ext)
            if os.path.isfile(shape_filename):
                self.filename_list.append((shape_filename, img_filename))

        self.size = len(self.filename_list)
        if self.size == 0 and self.verbose:
            print('Problem, empty video: {}'.format(folder))

    def __len__(self):
        return len(self.filename_list)

    def __getitem__(self, index):
        shape_filename, image_filename = self.filename_list[index]
        shape = np.genfromtxt(shape_filename, skip_header=3, skip_footer=1)
        image = np.array(imread(image_filename, flatten=self.image_to_gray), dtype=np.float)
        return shape, image

    def delete(self, index):
        shape_filename, image_filename = self.filename_list.pop(index)
        os.remove(shape_filename)
        os.remove(image_filename)
        if self.verbose:
            print('Deleted frame {}'.format(index))

class VideoLoader():
    """ Class to load the videos.
    
    If you want to load the videos differently, just make sure you implement a
    similar class with the following methods:
    * __len__ to return the number of videos
    * load_video to return a list of (shape, image)
       (in practice it doesn't have to be a list, it just needs to have a
        __getitem__ method, it you don't need to load all the frames and shapes in memory)
    """
    
    def __init__(self, root_folder, img_ext='.png', shape_ext='.pts'):
        """ Class that just loads the videos and returns a list of (shape, image)
        
        Parameters
        ----------
        root_folder: string
            absolute path to the root folder containing the videos
            
        This function just creates a list of video folder, each of these containing the frames and shapes corresponding to that video
        """
        self.root_folder = root_folder
        self.sub_folders = sorted(os.listdir(root_folder))
        
    def __len__(self):
        """ Simply returns the number of videos
        """
        return len(self.sub_folders)
    
    def load_video(self, index):
        """ Returns a list of (shape, image) for the video number 'index'
        
        Parameters
        ----------
        index: int
                index of the video to read
        
        Returns
        -------
        list of (shape, image)
        """
        source = os.path.join(self.root_folder, self.sub_folders[index])
        return ShapeImageCollection(source, image_to_gray=True)

class VideoBrowser():
    """ Function to browse the videos returned by video loader

    Parameters
    ----------
    video_loader: any class that implement a __len__ method to count the videos and a 
                  load_video(index) method to load video index, with index in range(0, len(video_loader) - 1)
    
    autoplay: bool
                if True, autoplays frames on first display
    """
    def __init__(self, video_loader, autoplay=True):
        # Load initial shape and image
        self.video_loader = video_loader
        self.collection = video_loader.load_video(0)
        self.shape, self.image = self.collection[0]
        # Current video
        self.video_index = 0
        # Current frame of the current video
        self.frame = 0
        # Really I shouldn't be doing that
        self.fig = plt.figure('Video: {}'.format(self.video_loader.sub_folders[self.video_index]))
        self.create_figure(self.shape, self.image)
    
    def create_figure(self, shape, image):
        """ Fills the figure with image, shape and buttons
        """
        self.fig.clf()
        # Hide the toolbar
        plt.rcParams['toolbar'] = 'None'
        
        # Axes for the image and shape
        self.ax = self.fig.add_axes([0, 0.2, 1, 0.8])
        plt.axis('off')
        self.ax_img = self.ax.imshow(image, cmap=plt.cm.Greys_r)
        self.ax_scatter = self.ax.scatter(shape[:, 0], shape[:, 1], s=10)
        # Create axes for the slider and add the slider
        self.max_frame_value = 1
        self.ax_frame = self.fig.add_axes([0.15, 0.1, 0.65, 0.05], axisbg='yellow')
        
        # We use a trick: the slider has value between 0 and 1 which we then
        # convert into a frame number
        self.slider_frame = Slider(self.ax_frame, 'Frame:', 0, self.max_frame_value,
                                   valinit=self.frame / (len(self.collection) - 1) * self.max_frame_value)
        self.ax_video = self.fig.add_axes([0.15, 0.16, 0.65, 0.05], axisbg='yellow')
        # Here the number of videos is fixed so we used integer values for the
        # Slider
        self.slider_video = Slider(self.ax_video, 'Video:', 0, len(video_loader) - 1,
                              valinit=self.video_index, valfmt='%0.0f')
        # Create the axes for the buttons
        self.ax_prev_video = self.fig.add_axes([0.01, 0.02, 0.18, 0.065])
        self.ax_next_video = self.fig.add_axes([0.81, 0.02, 0.18, 0.065])
        self.ax_prev_frame = self.fig.add_axes([0.21, 0.02, 0.18, 0.065])
        self.ax_next_frame = self.fig.add_axes([0.6, 0.02, 0.18, 0.065])
        self.ax_play_video = self.fig.add_axes([0.81, 0.1, 0.18, 0.1])
        # Put actual buttons in the button axes
        self.button_next_video = Button(self.ax_next_video, 'Next video')
        self.button_prev_video = Button(self.ax_prev_video, 'Previous video')
        self.button_next_frame = Button(self.ax_next_frame, 'Next frame')
        self.button_prev_frame = Button(self.ax_prev_frame, 'Previous frame')
        self.button_play_video = Button(self.ax_play_video, 'PLAY')
        # Bind the buttons and sliders to their event handler
        self.button_next_video.on_clicked(self.next_video)
        self.button_prev_video.on_clicked(self.prev_video)    
        self.button_prev_frame.on_clicked(self.prev_frame) 
        self.button_next_frame.on_clicked(self.next_frame)
        self.button_play_video.on_clicked(self.play_video)
        self.slider_frame.on_changed(self.update_frame)
        self.slider_video.on_changed(self.update_video)
        plt.show()
        
    def refresh_video(self, update_slider_position=False):
        """ Update the current collection of shape and image
        """
        self.collection = self.video_loader.load_video(self.video_index)
        self.frame = 0
        self.shape, self.image = self.collection[self.frame]
        self.create_figure(self.shape, self.image)
        # TODO: remove that next ugly line
        self.fig.canvas.set_window_title('Video: {}'.format(self.video_loader.sub_folders[self.video_index]))
        if update_slider_position:
            self.slider_video.set_val(self.video_index)

    def refresh_frame(self, update_slider_position=False):
        """ Update the frame currently displayed

        Parameters
        ----------
        update_slider_position: bool, default is False
                if True, the position of the slider is updated to match
                self.frame
        """
        self.shape, self.image = self.collection[self.frame]
        if update_slider_position:
            self.slider_frame.set_val(self.frame / (len(self.collection) - 1) * self.max_frame_value)
        self.ax_img.set_array(self.image)
        self.ax_scatter.set_offsets(self.shape)
        plt.draw()

    def play_video(self, event):
        while self.frame < len(self.collection) - 1:
            self.frame += 1
            self.refresh_frame(True)
            #time.sleep(0.005)

    def next_video(self, event):
        if self.video_index < (len(self.video_loader) - 1):
            self.video_index += 1
            self.refresh_video(True)

    def prev_video(self, event):
        if self.video_index > 0:
            self.video_index -= 1
            self.refresh_video(True)

    def next_frame(self, event):
        if self.frame < (len(self.collection) - 1):
            self.frame += 1
            self.refresh_frame(True)

    def prev_frame(self, event):
        if self.frame > 0:
            self.frame -= 10
            self.refresh_frame(True)

    def update_frame(self, event):
        self.frame = int(self.slider_frame.val * (len(self.collection) - 1))
        self.refresh_frame(False)

    def update_video(self, event):
        self.video_index = int(self.slider_video.val)
        self.refresh_video(False)
        

if __name__ == '__main__':
    video_folder = './videos/'
    video_loader = VideoLoader(root_folder=video_folder)
    browser = VideoBrowser(video_loader)
