import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QBrush, QColor, QPainterPath, QPen
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QPointF, QTimer, QPoint, QEvent
from noise import pnoise1
import math
import random
import json 

import HexRegistry
import PatternUtils

import Hex


# Make output link type

class DropDown(QComboBox):
    hide = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
    def hidePopup(self):
        super().hidePopup()
        self.hide.emit()

class HexagonalGridRenderer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 70)
        self.start_pos = (35, 35)
        self.noise_scale = 0.1  # Adjust for wiggle frequency
        self.offset = random.randint(0,1000000)  # Offset for animation

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_offset)
        self.timer.start(50)  # Update every 50 ms

        self.direction_string = None

    def render_pattern(self,angle):
        self.direction_string = angle
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        if self.direction_string == None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        

        path = self.get_hexagon_path()

        pen = QPen(QColor(243, 182, 237))  # Purple
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPath(path)

        pen = QPen(QColor(201, 185, 240))  # Blue
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)


    def move_in_direction(self, pos, angle):
        """ Calculate the new position based on the current position and angle """
        x, y = pos
        rad = math.radians(angle)
        new_x = x + math.cos(rad) * self.hex_size
        new_y = y + math.sin(rad) * self.hex_size
        return (new_x, new_y)

    def get_hexagon_path(self):

        angle = 300  # Start facing ne

        string = 'w'+self.direction_string

        # Get the path from the direction string
        path = PatternUtils.get_hexagon_path(string,angle)
        # Calculate the bounding hexagon
        center, radius = PatternUtils.calculate_bounding_hexagon(path)

        # Set the starting point for drawing
        self.hex_size = 25/max(radius,1)
        current_pos = tuple(a + b * self.hex_size for a, b in zip(self.start_pos, center))

        points = [QPointF(*current_pos)]
        # Iterate through each character in the direction string

        for command in string:
            if command == 'q':
                angle -= 60  # Turn left
                current_pos = self.move_in_direction(current_pos, angle)
            elif command == 'a':
                angle -= 120  # Sharp left
                current_pos = self.move_in_direction(current_pos, angle)
            elif command == 'w':
                # Move forward in the current direction
                current_pos = self.move_in_direction(current_pos, angle)
            elif command == 'e':
                angle += 60  # Turn right
                current_pos = self.move_in_direction(current_pos, angle)
            elif command == 'd':
                angle += 120  # Sharp right
                current_pos = self.move_in_direction(current_pos, angle)
            elif command == 's':
                angle += 180  # Move backwards
                current_pos = self.move_in_direction(current_pos, angle)
            angle%=360
            points.append(QPointF(*current_pos))
        

        path = QPainterPath()
        
        path.moveTo(points[0])
        
        amplitude = 2  # Height of the wiggle
        frequency = 5  # Frequency of the wiggle
        step = 1       # Step size for points along the edge

        for i in range(len(points)-1):
            start = points[i]
            end = points[i + 1]  # Loop back to the start
            
            dx = end.x() - start.x()
            dy = end.y() - start.y()
            length = math.hypot(dx, dy)
            
            if length != 0:
                dx /= length
                dy /= length
                
            for j in range(0, int(length), step):
                t = j / length
                x = start.x() + t * (end.x() - start.x())
                y = start.y() + t * (end.y() - start.y())
                
                # Add wiggle
                wiggle = pnoise1((self.offset + j) * self.noise_scale) * 1 * math.sqrt(1-(t*2-1)**2)
                path.lineTo(QPointF(x + wiggle * dy, y - wiggle * dx))  # Perpendicular wiggle
                
        return path
    def update_offset(self):
        self.offset += 1
        self.update()  # Trigger a repaint

class HexagonalButton(QWidget):
    link = pyqtSignal(int)
    change = pyqtSignal(str)



    def __init__(self, label, parent=None):
        super().__init__(parent)

        self.type_color = [QColor(255, 182, 193, 100),QColor(173, 216, 230, 100),QColor(205, 205, 104, 100),QColor(240, 179, 228, 100),QColor(144, 238, 144, 100),QColor(255, 228, 196, 100)]

        self.setFixedSize(70, 70)  # Set fixed size for the button
        self.link_type = [0]*6
        self.id = label

        self.noise_scale = 0.1  # Adjust for wiggle frequency
        self.offset = random.randint(0,1000000)  # Offset for animation

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_offset)
        self.timer.start(50)  # Update every 50 ms

        self.combo_box = DropDown(self)
        self.combo_box.addItem("Select an option")  # Placeholder item
        self.combo_box.addItem("numerical_ref:10")  # Placeholder item
        self.combo_box.addItems(HexRegistry.getAllPatternName())
        self.combo_box.setVisible(False)
        current_position = self.combo_box.pos()
        self.combo_box.move(current_position.x(), current_position.y() + 50)

        self.combo_box.hide.connect(lambda: self.combo_box.setVisible(False))

        self.combo_box.currentIndexChanged.connect(self.onDropdownChange)

        self.pattern = HexagonalGridRenderer(self)
    
    def getLinkType(self):
        return self.link_type

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = self.get_hexagon_path()

        pen = QPen(QColor(243, 182, 237))
        painter.setPen(pen)
        painter.drawPath(path)

        for i in range(6):
            if self.link_type[i] != 0:
                path = QPainterPath()
                path.moveTo(self.hexagon_point(i-1,29))
                path.lineTo(self.hexagon_point(i,29))
                pen.setColor(self.type_color[self.link_type[i]-1])
                pen.setWidth(4)
                painter.setPen(pen)
                painter.drawPath(path)

            

    def get_hexagon_path(self):
        path = QPainterPath()
        points = [self.hexagon_point(i) for i in range(6)]
        
        path.moveTo(points[0])
        
        amplitude = 1  # Height of the wiggle
        frequency = 5  # Frequency of the wiggle
        step = 5       # Step size for points along the edge

        for i in range(6):
            start = points[i]
            end = points[(i + 1) % 6]
            
            dx = end.x() - start.x()
            dy = end.y() - start.y()
            length = math.hypot(dx, dy)
            
            if length != 0:
                dx /= length
                dy /= length
                
            for j in range(0, int(length), step):
                t = j / length
                x = start.x() + t * (end.x() - start.x())
                y = start.y() + t * (end.y() - start.y())
                
                # Add wiggle
                wiggle = pnoise1((self.offset + j) * self.noise_scale) * 1 * math.sqrt(1-(t*2-1)**2)
                path.lineTo(QPointF(x + wiggle * dy, y - wiggle * dx))  # Perpendicular wiggle
                
        path.closeSubpath()
        return path
        

    def hexagon_point(self, i, dist = 35):
        # Calculate hexagon points
        angle = (i * (360 / 6)+(360 / 12) ) * (math.pi / 180)  # Convert to radians
        x = 35 + dist * math.cos(angle)
        y = 35 + dist * math.sin(angle)
        return QPointF(x, y)

    def mousePressEvent(self, event):
        selected_item = self.combo_box.currentText()
        x = event.x() - 35
        y = event.y() - 35

        #radii distance
        distance = math.sqrt(x**2 + y**2)
        angle = math.atan2(y, x) / math.pi * 180
        dir = int(((angle+30)//60)%6)
        #hexagon distance
        hdistance = distance*math.cos((angle-dir*60)*math.pi / 180)
        #print(hdistance)
        if hdistance > 30:
            return
        if distance < 14:
            if self.combo_box.isVisible():
                self.combo_box.setVisible(False)
            else:
                self.combo_box.setVisible(True)
                self.combo_box.show()  # Show the dropdown
                self.combo_box.showPopup()
        else:
            if event.button() == Qt.RightButton:
                pattern = HexRegistry.getPattern(selected_item)
                max_cnt = max(pattern[0],pattern[1])
                print(max_cnt)
                if pattern != None and max_cnt != 0:
                    self.link_type[dir] += 1 
                    self.link_type[dir] %= max_cnt + 1
                else:
                    self.link_type[dir] = 0
            else:
                self.link.emit(dir)

    def mouseReleaseEvent(self, event):

        if self.combo_box.isVisible():
            self.combo_box.setVisible(False)

    def onDropdownChange(self, index):
        selected_item = self.combo_box.currentText()
        for i in range(6):
            self.link_type[i] = 0
        if HexRegistry.getPattern(selected_item) == None:
            self.change.emit(None)
            self.pattern.render_pattern(None)
            return
        self.pattern.render_pattern(HexRegistry.getPattern(selected_item)[2])
        self.change.emit(selected_item)
        

    def update_offset(self):
        self.offset += 1
        self.update()  # Trigger a repaint

def distance(point1,point2):
    return math.sqrt((point2.x() - point1.x()) ** 2 + (point2.y() - point1.y()) ** 2)

class LinkWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.render_list = []
        self.setParent(parent)

    def getLinks(self):
        return self.render_list

    def link_a_b(self,source_widget,source_side,target_widget,target_side):
        if not self.islinked_a_b(source_widget,source_side,target_widget,target_side):
            self.render_list.append([source_widget,source_side,target_widget,target_side])

    def unlink_a_b(self,source_widget,source_side,target_widget,target_side):
        if self.islinked_a_b(source_widget,source_side,target_widget,target_side):
            self.render_list.remove([source_widget,source_side,target_widget,target_side])

    def reset_link_a_b(self,source_widget):
            self.render_list=list(filter(lambda x:not source_widget in x,self.render_list))
    
    def toggle_a_b_keep_oneway(self,source_widget,source_side,target_widget,target_side):
        if self.islinked_a_b(source_widget,source_side,target_widget,target_side):
            self.unlink_a_b(source_widget,source_side,target_widget,target_side)
        else:
            self.link_a_b(source_widget,source_side,target_widget,target_side)
        
        if self.islinked_a_b(target_widget,target_side,source_widget,source_side):
            self.unlink_a_b(target_widget,target_side,source_widget,source_side)

    def islinked_a_b(self,source_widget,source_side,target_widget,target_side):
        return [source_widget,source_side,target_widget,target_side] in self.render_list

    

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(201, 185, 240),2)
        painter.setPen(pen)

        for link in self.render_list:
            source_rect = link[0].geometry()
            source_angle = link[1]*math.pi/3
            target_rect = link[2].geometry()
            target_angle = link[3]*math.pi/3

            offset = 20
            toffset = 25

            sdx = offset * math.cos(source_angle)
            sdy = offset * math.sin(source_angle)

            tdx = toffset * math.cos(target_angle)
            tdy = toffset * math.sin(target_angle)

            source_center = QPointF(source_rect.center().x()+sdx, source_rect.center().y()+sdy)
            target_center = QPointF(target_rect.center().x()+tdx, target_rect.center().y()+tdy)

            path = QPainterPath()
            path.moveTo(source_center)

            c_offset = min(150,distance(source_center,target_center)*1.5)

            csdx = c_offset * math.cos(source_angle)
            csdy = c_offset * math.sin(source_angle)

            ctdx = c_offset * math.cos(target_angle)
            ctdy = c_offset * math.sin(target_angle)

            control_point_1 = QPointF(source_rect.center().x()+csdx, source_rect.center().y()+csdy)
            control_point_2 = QPointF(target_rect.center().x()+ctdx, target_rect.center().y()+ctdy)

            path.cubicTo(control_point_1, control_point_2, target_center)

            painter.drawPath(path)

            self.draw_arrowhead(painter, target_center, control_point_2)

    def draw_arrowhead(self, painter, target_center, control_point):
        dx = target_center.x() - control_point.x()
        dy = target_center.y() - control_point.y()
        angle = math.atan2(dy, dx)

        arrow_size = 6
        arrow_p1 = target_center - QPoint(int(arrow_size * math.cos(angle - 0.7)), int(arrow_size * math.sin(angle - 0.7)))
        arrow_p2 = target_center - QPoint(int(arrow_size * math.cos(angle + 0.7)), int(arrow_size * math.sin(angle + 0.7)))

        painter.drawLine(target_center, arrow_p1)
        painter.drawLine(target_center, arrow_p2)


class Worker(QThread):
    progress = pyqtSignal(str)  # Signal to communicate with the main thread
    end = pyqtSignal(list)

    def __init__(self, pattern, links, linktypes, buttons, parent=None):
        super().__init__(parent)
        self.pattern = pattern  # [name]
        self.links = links # [[from,dir,to,dir]]
        self.linktypes = linktypes # [[0,1,2,3,4,5]]
        self.buttons = buttons

    def run(self):
        self.progress.emit(f"Preprocessing ...")

        hex = Hex.Hex(81)

        links = [None] * 81

        mapping_b = {}
        for k in range(81):
            mapping_b[self.buttons[k]] = k

        for k in self.links:
            if links[mapping_b[k[2]]] == None:
                links[mapping_b[k[2]]] = [None] * 6
            if links[mapping_b[k[2]]][k[3]] == None:
                links[mapping_b[k[2]]][k[3]] = []
            links[mapping_b[k[2]]][k[3]]=[mapping_b[k[0]],k[1]]

        mapping_k = []
        for i in range(81):
            
            mapping_t = list(enumerate(self.linktypes[i]))
            mapping_t.sort(key=lambda x: x[1])

            mapping_k.append(mapping_t)

        print("mapping_k",mapping_k)
        for i in range(81):
            if self.pattern[i] == None:
                continue
            mapping_t = mapping_k[i]
            compliation_links = []

            for v,k in mapping_t:
                if k != 0 and links[i] and links[i][v]:
                    print(links[i])
                    targetediota = [value for key, value in mapping_k[links[i][v][0]] if key == links[i][v][1]]
                    print("target",targetediota[0])
                    compliation_links.append([links[i][v][0],targetediota[0]-1])
            
            print(i,self.pattern[i],compliation_links)
            hex.pushPattern(i,self.pattern[i],compliation_links)
        
        self.progress.emit(f"Compiling ...")

        result = hex.compile()
        
        if result == "Error: Not a DAG":
            self.progress.emit(f'There are repeating cycles in the Hex!')
            self.end.emit([])
            return

        resultcc = hex.assemble(result)

        self.end.emit([result,resultcc])
        self.progress.emit(f"Completed!")

class MainWindow(QWidget):
    rows = 9
    cols = 9
    Graph = [None] * 81
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hex-si")

        layout = QHBoxLayout(self)

        self.frame1 = QFrame(self)
        self.frame1.setStyleSheet("background-color: white;")
        
        self.frame2 = QFrame(self)
        self.frame2.setStyleSheet("background-color: white;")

        layout.addWidget(self.frame1)
        layout.addWidget(self.frame2)

        layout_side = QVBoxLayout(self.frame2)

        self.label = QLabel("Press the button to compile", self.frame2)
        self.label.setWordWrap(True) 

        self.label2 = QLabel("-", self.frame2)
        self.label2.setWordWrap(True) 

        self.button = QPushButton("Start Compiling", self.frame2)
        self.button.clicked.connect(self.start_task)  # Connect button click to the slot

        self.buttoncopy = QPushButton("Copy", self.frame2)
        self.button.clicked.connect(self.copy_to_clipboard)

        layout_side.addWidget(self.button)
        layout_side.addWidget(self.label)
        layout_side.addWidget(self.label2)
        layout_side.addWidget(self.buttoncopy)

        self.worker = None  # Initialize the worker

        

        rows = self.rows
        cols = self.cols

        self.hexButton = []
        
        
        for row in range(rows):
            for col in range(cols):
                hex_button = HexagonalButton(f"{row * cols + col + 1}", self.frame1)
                hex_button.move(col * 70 + (row+1) % 2 * 35, int(row * 70 * 0.86602540378)+2)
                id = row * cols + col + 1
                hex_button.link.connect(lambda dir,id=id:self.link(dir,id))
                hex_button.change.connect(lambda namespace,id=id:self.changePattern(namespace,id))
                #hex_button.setAttribute(Qt.WA_TransparentForMouseEvents)
                self.hexButton.append(hex_button)
                

        self.frame1.setFixedSize(int((cols+0.5) * 70),int(((rows+0.5) * 70) * 0.86602540378))
        self.setLayout(layout)

        self.link_widget = LinkWidget(self.frame1)
        self.link_widget.setAttribute(Qt.WA_TransparentForMouseEvents)

    def start_task(self):
        self.worker = Worker(self.Graph,self.link_widget.getLinks(),list(map(lambda x:x.getLinkType(),self.hexButton)),self.hexButton)  # Create an instance of the worker
        self.worker.progress.connect(self.update_label)  # Connect the signal to a slot
        self.worker.end.connect(self.compile_complete)  # Connect the signal to a slot
        self.worker.start()

    def update_label(self, message):
        self.label.setText(message)  # Update the label with progress messages

    def compile_complete(self, res):
        self.label2.setText(json.dumps(res[1]))  # Update the label with progress messages
        self.copy_to_clipboard()

    def copy_to_clipboard(self):
        text = self.label2.text()  # Get the text from QLineEdit
        clipboard = QApplication.clipboard()  # Get the clipboard object
        clipboard.setText(text)  # Set the text to the clipboard
        print(f"Copied to clipboard: {text}")  # Optional: print the copied text

    def link(self, dir, button):
        #print(dir,button,self.getAdjecent(dir, button))
        adjacent = self.getAdjecent(dir, button)
        if adjacent == None:
            return
        adjacent_o = self.hexButton[adjacent-1]
        button_o = self.hexButton[button-1]
        self.link_widget.toggle_a_b_keep_oneway(button_o,dir,adjacent_o,(dir+3)%6)

    def changePattern(self, namespace, button):
        #print(namespace,button)
        self.Graph[button-1] = namespace
        button_o = self.hexButton[button-1]
        self.link_widget.reset_link_a_b(button_o)

    def getAdjecent(self, dir, button):
        x = (button-1)%self.cols
        y = (button-1)//self.cols

        new_x = x
        new_y = y

        if dir < 2 or dir == 5:
            new_x += 1

        if dir == 3:
            new_x -= 1

        if dir % 3 != 0:
            if y % 2 == 1:
                new_x -= 1
            
            new_y -= (dir//3)*2-1

        #print(new_x,new_y)
        if new_x < 0 or new_x >= self.cols:
            return

        if new_y < 0 or new_y >= self.rows:
            return

        return new_x + new_y * self.cols + 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
