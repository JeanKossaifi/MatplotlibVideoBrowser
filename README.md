# MatplotlibVideoBrowser
Using [Matplotlib's GUI Neutral widgets](http://matplotlib.org/api/widgets_api.html) to through the frames of videos.

This is merely an example of how to easily use Matplotlib to create quickly a simple tool.
Here I needed to be able to quickly browse through some videos I annotated, ie visualise both the image and their facial landmarks.

## How does it work

### ShapeImageCollection
This is a simple class that allows you to access each tuple composed of a frame and its corresponding landmark as list.

### VideoLoader
Similarly, just a convenience class to load a ShapeImageCollection for each video.

## browse video
This is were the widgets are actually implemented.
We just create a figure, add some axes for the data to be plotted and the widgets.
We then bind each widget to an event handler (all of which are grouped in the EventHandler class) which updates the corresponding axes...


## Can I see?
Here is how it looks on ubuntu:
![alt text](https://github.com/JeanKossaifi/MatplotlibVideoBrowser/raw/master/images/ubuntu_screenshot.png "Screenshot ubuntu")

## Can I try?
Sure, all you need is python3, matplotlib, numpy and scipy (everyone has that, right?).

Just clone the repository and run 
```
python3 browser.py
```
