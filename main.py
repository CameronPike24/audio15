import kivy
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
import numpy as np

from time import sleep
from audiostream import get_input
from audiostream import get_output, AudioSample

from array import array


class MainApp(App):

    def build(self):
        #get speakers, create sample and bind to speakers
        stream = get_output(channels=2, rate=22050, buffersize=1024)
        sample = AudioSample()
        stream.add_sample(sample)
        
        
        # get the default audio input (mic on most cases)
        mic = get_input(callback=mic_callback)
        mic.start()
        sample.play()
        sleep(3)  #record for 3 seconds
        mic.stop()
        sample.stop()        
        
        
        
        return MainGrid()
        
        
        
    #define what happens on mic input with arg as buffer
    def mic_callback(buf):
        '''
        print 'got', len(buf)
        #HERE: How do I manipulate buf?
        #modified_buf = function(buf)
        #sample.write(modified_buf)
        sample.write(buf)  
        '''
        # convert our byte buffer into signed short array
        values = array("h", buf)

        # get right values only
        r_values = values[1::2]

        # reduce by 20%
        r_values = map(lambda x: x * 0.8, r_values)

        # you can assign only array for slice, not list
        # so we need to convert back list to array
        values[1::2] = array("h", r_values)

        # convert back the array to a byte buffer for speaker
        sample.write(values.tostring())       
        
        
        
              


class MainGrid(BoxLayout):

    zoom = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = 512
        self.zoom = 1
        self.graph = Graph(y_ticks_major=0.5,
                           x_ticks_major=64,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=0, xmax=self.samples,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=True, y_grid_label=False)

        self.ids.modulation.add_widget(self.graph)
        self.plot_x = np.linspace(0, 1, self.samples)
        self.plot_y = np.zeros(self.samples)
        self.plot = LinePlot(color=[1, 1, 0, 1], line_width=1.5)
        self.graph.add_plot(self.plot)
        self.update_plot(1)

    def update_plot(self, freq):
        self.plot_y = np.sin(2*np.pi*freq*self.plot_x)
        self.plot.points = [(x, self.plot_y[x]) for x in range(self.samples)]

    def update_zoom(self, value):
        if value == '+' and self.zoom < 8:
            self.zoom *= 2
            self.graph.x_ticks_major /= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2
            self.graph.x_ticks_major *= 2


MainApp().run()
