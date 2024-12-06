# derived from https://stackoverflow.com/questions/10944621/dynamically-updating-plot-in-matplotlib

import matplotlib.pyplot as plt
import time
import math

plt.ion()

class DynamicGraph():

    def __init__(self, num_series, *fmt):
        #Set up plot
        #unpacking the tuple that is made by subplots into the two variables on the left
        self.num_series = num_series
        self.figure, self.ax = plt.subplots()
        self.series = list()

        for each in fmt:
            print(each)
            self.series.append(self.ax.plot([],[],each)[0])

        if len(self.series) != num_series:
            print("[TRAIN]: ERROR IN INIT, WRONG NUMBER OF SERIES")
            exit()

        print(self.series)
        print(self.series[0])
        print(type(self.series[0]))

            
        # self.lines = self.ax.plot([],[], 'ro', [], [], 'g-')
        
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(False)
        self.ax.set_ybound(15,-15)
        self.ax.set_autoscalex_on(True)

        # self.ax.set_ylim(-5, 25)

        self.ax.grid()

    # format of *data should be xdata1, ydata1, xdata2, ydata2, etc
    def graph(self, *data):
        #Update data (with the new _and_ the old points)
        count = 0
        for i in range(0,self.num_series):
            self.series[i].set_xdata(data[count])
            self.series[i].set_ydata(data[count+1])
            count += 2

        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


def main():

    plot1 = DynamicGraph(2,'r-','b-')

    xdata = []
    ydata = []
    ydata2 = []

    t = 0
    dt = 0.1

    while t < 400:
        t+= dt

        xdata.append(t)
        ydata.append(math.sin(t))
        ydata2.append(math.cos(t))

        xdata = xdata[-100:]
        ydata = ydata[-100:]
        ydata2 = ydata2[-100:]

        plot1.graph(xdata, ydata, xdata, ydata2)
        time.sleep(dt/10)


if __name__ == "__main__":
    print("[TRAIN]: RUNNING MAIN IN GRAPHING.PY")
    main()

