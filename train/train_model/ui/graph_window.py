import pyqtgraph as pg
from train.train_model.ui.ui_help import *

class Temp_Control_Graph(QMainWindow):

    DATA_POINTS_TO_GRAPH = 200

    def __init__(self):
        super(Temp_Control_Graph, self).__init__()
        self.setWindowTitle("Temperature Control Graph")
        
        self.graph = pg.PlotWidget()
        self.graph.setBackground('black')

        self.plotitem = self.graph.getPlotItem()
        self.viewbox = self.plotitem.getViewBox()

        self.setCentralWidget(self.graph)
        self.plotitem.showGrid(x=True, y=True)
        self.plotitem.setTitle("Temperature Control Loop", color='white')
        styles = {'color':'white', 'font-size':'20px'}
        self.plotitem.setLabel('left', 'Temperature (F)', **styles)
        self.plotitem.setLabel('bottom', 'Time (Seconds)', **styles)
        self.plotitem.addLegend(offset = -10)

        font=QFont()
        font.setPixelSize(18)
        self.plotitem.getAxis("bottom").setStyle(tickFont = font)
        self.plotitem.getAxis("left").setStyle(tickFont = font)

        self.time = [0] * Temp_Control_Graph.DATA_POINTS_TO_GRAPH
        self.act_temp = [0] * Temp_Control_Graph.DATA_POINTS_TO_GRAPH
        self.set_temp = [0] * Temp_Control_Graph.DATA_POINTS_TO_GRAPH

        pen = pg.mkPen(color=(255, 0, 0), width = 3)
        self.act_temp_line = self.plotitem.plot(self.time, self.act_temp, name="Actual Temp (F)", pen=pen)
        pen = pg.mkPen(color=(255, 255, 0), width = 3)
        self.set_temp_line = self.plotitem.plot(self.time, self.set_temp, name="Set Temp (F)", pen=pen)

        self.first_update_call = True
        self.pending_delete = False

    # Called when user closes the window
    def closeEvent(self, event: QCloseEvent) -> None:
        event.accept()
        self.pending_delete = True

    def update(self, new_time, new_set_temp, new_act_temp):

        if self.first_update_call:
            self.first_update_call = False
            self.time = [new_time] * Temp_Control_Graph.DATA_POINTS_TO_GRAPH
            self.act_temp = [new_act_temp] * Temp_Control_Graph.DATA_POINTS_TO_GRAPH
            self.set_temp = [new_set_temp] * Temp_Control_Graph.DATA_POINTS_TO_GRAPH
            
        self.time = self.time[1:]
        self.time.append(new_time)

        self.act_temp = self.act_temp[1:]
        self.act_temp.append(new_act_temp)

        self.set_temp = self.set_temp[1:]
        self.set_temp.append(new_set_temp)

        self.act_temp_line.setData(self.time, self.act_temp)
        self.set_temp_line.setData(self.time, self.set_temp)

    def __del__(self):
        print("[TRAIN]: Temp_Control_Graph Deleted.")



class Train_Control_Graph(QMainWindow):

    DATA_POINTS_TO_GRAPH = 200
    POWER_MIN = -20.0

    def __init__(self):
        super(Train_Control_Graph, self).__init__()

        self.setWindowTitle("Train Model Graph")

        self.graph_layout = pg.GraphicsLayout()

        self.graph = pg.PlotWidget()
        self.graph.setBackground('black')

        self.plotitem = self.graph.getPlotItem()
        self.viewbox = self.plotitem.getViewBox()

        
        self.plotitem.showGrid(x=True, y=True)
        self.plotitem.setTitle("Train Model Control Loop", color='white')
        styles = {'color':'white', 'font-size':'20px'}
        self.plotitem.setLabel('left', 'Value', **styles)
        self.plotitem.setLabel('bottom', 'Time (Seconds)', **styles)
        self.plotitem.addLegend(offset = (0,1))

        font=QFont()
        font.setPixelSize(18)
        self.plotitem.getAxis("bottom").setStyle(tickFont = font)
        self.plotitem.getAxis("left").setStyle(tickFont = font)
        
        self.time = [0] * Train_Control_Graph.DATA_POINTS_TO_GRAPH
        self.actual_vel = [0] * Train_Control_Graph.DATA_POINTS_TO_GRAPH
        self.power = [0] * Train_Control_Graph.DATA_POINTS_TO_GRAPH
        self.set_vel = [0] * Train_Control_Graph.DATA_POINTS_TO_GRAPH

        pen = pg.mkPen(color=(255, 0, 0), width = 3)
        self.vel_line = self.plotitem.plot(self.time, self.actual_vel, name="Actual Velocity (m/s)", pen=pen)
        pen = pg.mkPen(color=(0, 255, 0), width = 3)
        self.power_line = self.plotitem.plot(self.time, self.power, name="Power Command (kW)", pen=pen)
        pen = pg.mkPen(color=(255, 255, 0), width = 3)
        self.set_vel_line = self.plotitem.plot(self.time, self.set_vel, name="Set Velocity (m/s)", pen=pen)

        self.error_text = pg.TextItem(text="Power values nominal.")
        self.error_text.setParentItem(self.viewbox)
        self.error_text.setPos(0,30)
        self.updated_text = False

        self.setCentralWidget(self.graph)

        self.first_update_call = True
        self.pending_delete = False

    def get_widget(self):
        return self.graph

    def limit_power(self, new_power) -> float:
        new_power /= 10e3 # put in kw
        if new_power < Train_Control_Graph.POWER_MIN:
            new_power = Train_Control_Graph.POWER_MIN
            if not self.updated_text:
                self.error_text.setText("Power being capped to increase graph visibility. Actual power can be seen on the test bench.")
                self.updated_text = True
        elif self.updated_text:
            self.error_text.setText("Power values nominal.")
            self.updated_text = False

        return new_power
    
    # Called when user closes the window
    def closeEvent(self, event: QCloseEvent) -> None:
        event.accept()
        self.pending_delete = True
        
    def update(self, new_time, new_velocity, new_power, new_set_vel):

        if self.first_update_call:
            self.first_update_call = False
            self.time = [new_time] * Train_Control_Graph.DATA_POINTS_TO_GRAPH
            self.actual_vel = [new_velocity] * Train_Control_Graph.DATA_POINTS_TO_GRAPH
            self.power = [self.limit_power(new_power)] * Train_Control_Graph.DATA_POINTS_TO_GRAPH
            self.set_vel = [new_set_vel] * Train_Control_Graph.DATA_POINTS_TO_GRAPH
            return
        
        self.time = self.time[1:]
        self.time.append(new_time)

        self.actual_vel = self.actual_vel[1:]
        self.actual_vel.append(new_velocity)

        self.power = self.power[1:]
        self.power.append(self.limit_power(new_power))

        self.set_vel = self.set_vel[1:]
        self.set_vel.append(new_set_vel)

        self.vel_line.setData(self.time, self.actual_vel)
        self.power_line.setData(self.time, self.power)
        self.set_vel_line.setData(self.time, self.set_vel)

    def __del__(self):
        print("[TRAIN]: Train_Control_Graph Deleted.")

