'''
点用二维数组储存
折线和面都用二维数组储存
'''
import sys
from PyQt5.QtWidgets import QApplication,QDialog, QMainWindow, QComboBox, QLineEdit, QPushButton, QVBoxLayout, QWidget,QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor,QPen
from shapely.geometry import LineString, Polygon
import matplotlib.pyplot as plt
import numpy as np
import copy

#数学准备
def do_segments_intersect(a, b, c, d):
    #0代表重叠，1代表相离，2代表相交
    # 计算矢量方向
    vector_ab = (b[0] - a[0], b[1] - a[1])
    vector_cd = (d[0] - c[0], d[1] - c[1])

    # 计算矢量交点
    cross_product = vector_ab[0] * vector_cd[1] - vector_ab[1] * vector_cd[0]
    if cross_product == 0:
        if min(a[0], b[0]) <= max(c[0], d[0]) and min(c[0], d[0]) <= max(a[0], b[0]) \
            and min(a[1], b[1]) <= max(c[1], d[1]) and min(c[1], d[1]) <= max(a[1], b[1]):
            return 1#重叠
        else:
            return 0#相离
    line1=LineString([a,b])
    line2=LineString([c,d])
    if line1.intersects(line2):
        return 2#相交
    else:
        return 0#相离

def are_polylines_contained(polyline1, polyline2):
    # 将折线分段为线段列表
    segments1 = [(polyline1[i], polyline1[i+1]) for i in range(len(polyline1) - 1)]
    segments2 = [(polyline2[i], polyline2[i+1]) for i in range(len(polyline2) - 1)]

    # 创建 Shapely LineString 对象
    ls1 = LineString(polyline1)
    ls2 = LineString(polyline2)

    # 检查每个线段是否在另一条折线的内部
    for segment in segments1:
        if not ls2.contains(LineString(segment)):
            return False

    for segment in segments2:
        if not ls1.contains(LineString(segment)):
            return False

    return True
def point_point(point1, point2):
    # 判断两个点是否重叠
    if point1.points[0]==point2.points[0] and point1.points[1]==point2.points[1]:
        return "重合、重叠、包含"
    else:
        return "相离"
def point_polyline(point, polyline):
    # 判断点与线拓扑关系
    #邻接：有相同点
    for i in range(len(polyline.points)):
        if point.points[0]==polyline.points[i]:
            return "邻接"
    #包含：在线内
    for i in range(len(polyline.points)-1):
        if (point.points[1]-polyline.points[i][1])/(point.points[0]-polyline.points[i][0]) ==\
              (polyline.points[i+1][1]-polyline.points[i][1])/(polyline.points[i+1][0]-polyline.points[i][0]):
                if point.points[0]<=max(polyline.points[i][0],polyline.points[i+1][0]):
                    if point.points[0]>=min(polyline.points[i][0],polyline.points[i+1][0]):
                        if point.points[1]<=max(polyline.points[i][1],polyline.points[i+1][1]):
                            if point.points[1]>=min(polyline.points[i][1],polyline.points[i+1][1]):
                                return "包含"
    return "相离"
def point_polygon(point, polygon):
    # 判断点与面的拓扑关系
    #邻接：有相同点
    for i in range(len(polygon.points)):
        if point.points==polygon.points[i]:
            return "邻接"
    #包含：在面内
    n=len(polygon.points)
    inside=False
    p1x=polygon.points[0][0]
    p1y=polygon.points[0][1]
    for i in range(n+1):
        p2x=polygon.points[i%n][0]
        p2y=polygon.points[i%n][1]
        if point.points[1]<=max(p1y,p2y):
            if point.points[1]>=min(p1y,p2y):
                if point.points[0]>=min(p1x,p2x):
                    if point.points[0]<=max(p1x,p2x):
                        if p1y!=p2y:
                            xinters= (point.points[0]-p1x)*(p2y-p1y)/(p2x-p1x)+p1y
                            if p1y<p2y and point.points[1]<=xinters:
                                    inside=not inside
                                    break
    if (inside):
        return "包含"
    else:
        return "相离"
def polyline_polyline(polyline1, polyline2):
    #判断折线与折线的拓扑关系
    #重合：完全重叠
    if len(polyline1.points)==len(polyline2.points):
        for i in range(len(polyline1.points)):
            if polyline1.points[i]!=polyline2.points[i]:
                continue
        if i==len(polyline1.points):
            return "重合"
    #包含：分别判断每段线段是否都与另一个线段包含
    if are_polylines_contained(polyline1.points,polyline2.points)==1:
        return "包含"
    #邻接：有相同点
    for i in range(len(polyline1.points)):
        for j in range(len(polyline2.points)):
            if polyline1.points[i]==polyline2.points[j]:
                return "邻接、重叠"
    #相交：有相同点，相离
    jiao,die=0,0
    for i in range(len(polyline1.points)-1):
        for j in range(len(polyline2.points)-1):
            if do_segments_intersect(polyline1.points[i],polyline1.points[i+1],\
                                     polyline2.points[j],polyline2.points[j+1])==1:
                die=1
            if do_segments_intersect(polyline1.points[i],polyline1.points[i+1],\
                                     polyline2.points[j],polyline2.points[j+1])==2:
                jiao=1
    if jiao==1 and die==1:
        return "相交、重叠"
    elif jiao==1 and die==0:
        return "相交"
    elif jiao==0 and die==1:
        return "重叠"
    if jiao==0 and die==0:
        return "相离"
    
def polyline_polygon(polyline, polygon):
    #判断折线与面的拓扑关系
    #邻接：有公共点
    for i in range(len(polyline.points)):
        for j in range(len(polygon.points)):
            if polyline.points[i]==polygon.points[j]:
                return "邻接"
    #相交
    for i in range(len(polyline.points)-1):
        for j in range(len(polygon.points)-1):
            if do_segments_intersect(polyline.points[i],polyline.points[i+1],\
                                             polygon.points[j],polygon.points[j+1]  )==2:
                return "相交"
    #包含
    for i in range(len(polyline.points)):
        if point_polygon(polyline.points[i],polygon)!="包含":
            return "相离"
    return "包含"

def polygon_polygon(polygon1, polygon2):
    #判断面与面的拓扑关系
    #重合
    if len(polygon1.points)==len(polygon2.points):
        for i in range(len(polygon1.points)):
            if polygon1.points[i]!=polygon2.points[i]:
                break
        if i==len(polygon1.points):
            return "重合"

    #邻接
    for i in range(len(polygon1.points)-1):
       for j in range(len(polygon2.points)-1):
           if polygon1.points[i]==polygon2.points[j]:
               return "邻接"
    #相交
    for i in range(len(polygon1.points)-1):
        line1=GPolyline()
        line1.add_point(polygon1.points[i][0],polygon1.points[i][1])
        line1.add_point(polygon1.points[i+1][0],polygon1.points[i+1][1])
        for j in range(len(polygon2.points)-1):
            line2=GPolyline()
            line2.add_point(polygon2.points[j][0],polygon2.points[j][1])
            line2.add_point(polygon2.points[j+1][0],polygon2.points[j+1][1])
            if polyline_polyline(line1,line2)=="相交" or "相交、重叠":
                return "重叠"
    return "相离"
    

                
class SubWindow(QDialog):
    #定义子窗口用来展示绘图结果并判断拓扑关系
    def __init__(self,data, parent=None):
        super().__init__(parent)
        self.data=copy.copy(data)
        self.setWindowTitle("绘图与关系判断")
        #self.create_widgets()
        #self.layout_widgets()
        self.relation=self.relation_judge()
    def paintEvent(self, event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen=QPen(Qt.black,5)#参数代表画笔颜色，宽度
        painter.setPen(pen)
        for i in range(len(self.data)):
            if self.data[i].Gtype==0:
                painter.drawPoint(self.data[i].points[0],self.data[i].points[1])
            if self.data[i].Gtype==1:
                points = [QPoint(*point) for point in self.data[i].points]
                painter.drawPolyline(*points)
            if self.data[i].Gtype==2:
                points = [QPoint(*point) for point in self.data[i].points]
                painter.drawPolygon(*points)
        
        print(self.relation)

    def relation_judge(self):
        #判断拓扑关系
        if self.data[0].Gtype==0 and self.data[1].Gtype==0:#点&点
            return(point_point(self.data[0],self.data[1]))
        elif self.data[0].Gtype==0 and self.data[1].Gtype==1:#点&折线
            return(point_polyline(self.data[0],self.data[1]))
        elif self.data[0].Gtype==1 and self.data[1].Gtype==2:#折线&面
            return(polyline_polygon(self.data[0],self.data[1]))
        elif self.data[0].Gtype==2 and self.data[1].Gtype==2:#面&面
            return(polygon_polygon(self.data[0],self.data[1]))
        elif self.data[0].Gtype==1 and self.data[1].Gtype==0:#折线&点
            return(point_polyline(self.data[1],self.data[0]))
        elif self.data[0].Gtype==2 and self.data[1].Gtype==0:#面&点
            return(point_polygon(self.data[1],self.data[0]))
        elif self.data[0].Gtype==0 and self.data[1].Gtype==2:#点&面
            return(point_polygon(self.data[0],self.data[1]))
        elif self.data[0].Gtype==1 and self.data[1].Gtype==1:#折线&折线
            return(polyline_polyline(self.data[0],self.data[1]))
        elif self.data[0].Gtype==2 and self.data[1].Gtype==1:#面&折线
            return(polyline_polygon(self.data[1],self.data[0]))
        elif self.data[0].Gtype==1 and self.data[1].Gtype==2:#折线&面
            return(polyline_polygon(self.data[0],self.data[1]))
        
         
class GPoint:
    def __init__(self,x,y):
        self.points=((x,y))#二维数组储存点
    Gtype=0#0代表点，1代表折线，2代表面

class GPolyline:
    def __init__(self):
        self.points = ()#二维数组储存点
    def add_point(self, x, y):
        self.points=self.points+((x,y),)#二维数组储存点
    def __str__(self):
        return str(self.points)
    Gtype=1#0代表点，1代表折线，2代表面

class GPolygon:
    def __init__(self):
        self.points = ()#二维数组储存点
    def add_point(self, x, y):
        self.points=self.points+((x,y),) 
    def __str__(self):
        return str(self.points)
    Gtype=2#0代表点，1代表折线，2代表面

class SimpleGraphics(QMainWindow):#自定义窗口类，用作输入数据
    def __init__(self):#
        super().__init__()
        self.setWindowTitle("矢量数据输入")
        self.create_widgets()
        self.layout_widgets()
        self.connect_widgets()
        self.setGeometry(100, 100, 500, 300)#参数分别表示窗口左上角的横纵坐标和窗口的宽度和高度
        self.data=[GPoint(0,0),GPoint(0,0)]#初始化数据
        self.number=0#初始化数据个数
        self.show()
        
    def create_widgets(self):
        self.label1=QLabel("请选择数据类型")
        self.label2=QLabel("请输入地理点的坐标")
        self.label3=QLabel("如果你要提交你的数据，请点击“提交”")
        self.label4=QLabel("如果本组数据输入完成，请点击“完成”以输入下一组数据或绘制图片并判断拓扑关系")
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["点", "线", "面"])
        self.point_input = QLineEdit()
        self.point_input.setPlaceholderText("输入地理点的坐标,用逗号分隔开（不用加括号）")
        self.add_button = QPushButton("更新")
        self.finish_button = QPushButton("完成")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.update_graphics()
    
    def layout_widgets(self):
        layout = QVBoxLayout()#垂直布局
        layout.addWidget(self.label1)
        layout.addWidget(self.data_type_combo)
        layout.addWidget(self.label2)
        layout.addWidget(self.point_input)
        layout.addWidget(self.label3)
        layout.addWidget(self.add_button)
        layout.addWidget(self.label4)
        layout.addWidget(self.finish_button)#把4个控件放上去
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def connect_widgets(self):
        """响应按钮点击事件"""
        self.add_button.clicked.connect(self.on_add_button_click)
        self.finish_button.clicked.connect(self.on_finish_button_click)

    def on_add_button_click(self):
        data_type = self.data_type_combo.currentText()
        point_input = self.point_input.text()
        # 处理输入的数据
        if data_type == "点":
            # 解析输入的坐标字符串，例如：100,200
            point_x, point_y = map(int, point_input.split(","))
            self.data[self.number]=GPoint(point_x, point_y)
            self.data[self.number].Gtype=0
            print(f"地理点坐标：({point_x}, {point_y})")
        elif data_type == "线":
            point_x, point_y = map(int, point_input.split(","))
            if type(self.data[self.number])==GPoint:
                self.data[self.number]=GPolyline()
            self.data[self.number].add_point(point_x, point_y)
            self.data[self.number].Gtype=1
            print("输入线数据中，已添加点","(",point_x, ",",point_y,")")
        elif data_type == "面":
            point_x, point_y = map(int, point_input.split(","))
            if type(self.data[self.number])==GPoint:
                self.data[self.number]=GPolygon()
            self.data[self.number].add_point(point_x, point_y)
            self.data[self.number].Gtype=2
            print("输入面数据中，已添加点", "(",point_x, ",",point_y,")")
        else:
            print("无效的数据类型")
    def on_finish_button_click(self):
        if self.number==0:
            self.number=1
            print("第一组数据输入完成。请输入第二个数据:-)")
            return
        if self.number==1:
            print("数据输入完成,请检查绘图结果")
            self.paint()
            self.close()
            
    def paint(self):
        # 创建绘图窗口
        self.sub_window = SubWindow(self.data)
        self.sub_window.show()
        self.sub_window.exec_()
class paint_result(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIS拓扑关系判断")
        self.create_widgets()
        self.layout_widgets()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SimpleGraphics()
    main_window.show()
    sys.exit(app.exec_())