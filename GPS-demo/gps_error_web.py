#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date     :2022/08/11 08:38:03
@Author      :HankWang
@version      :1.0
'''
from select import select
import pandas as pd
import numpy as np
from datetime import datetime, date
from time import strftime
from time import gmtime
import pywebio
import pywebio.output as output
import pywebio.input as input
# import pywebio.input.input_group as input_group 
# from draw_gps_demo import draw_gps,data_tf
import folium
import os
import pandas as pd
import numpy as np
import math
# from coord_convert.transform import wgs2gcj, wgs2bd, gcj2wgs, gcj2bd, bd2wgs, bd2gcj #用于WGS-84(未偏移坐标), GCJ-02（国家测绘局、高德、谷歌中国地图）, BD-09(百度坐标系)三者之间的互相转换



pywebio.config(title='GPS异常数据检测')
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
pi = 3.1415926535897932384626  # π

def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lat, lng):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    # if out_of_china(lng, lat):  # 判断是否在国内
    #     return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglat, mglng]

def data_tf(df):
    # df = pd.read_excel(io=r'GPS1.xlsx',usecols="E:F")
    # print(df)
    # df.loc[:,['纬度','经度']] = df.loc[:,['经度', '纬度']]

    x_array = np.array(df)[1:,4:6]#.tolist()
    # print(x_array[:,[-1, 0]])
    x_array[:,[0, -1]] = x_array[:,[-1, 0]]  #交换经纬度  纬度在前
    data_list = x_array.tolist()
    # print(data_list)
    # 坐标转换成高德
    data_gcj_list = []
    for i in data_list:
        gcj_lon, gcj_lat = wgs84_to_gcj02(i[0], i[1])
        data_gcj_list.append([gcj_lon, gcj_lat])
    return data_gcj_list

def draw_gps(locations1,color1,error_zuobiao_list,stop_zuobiao_list):
    """
    绘制gps轨迹图
    :param locations: list, 需要绘制轨迹的经纬度信息，格式为[[lat1, lon1], [lat2, lon2], ...]
    :param output_path: str, 轨迹图保存路径
    :param file_name: str, 轨迹图保存文件名
    :return: None
    """
    m1 = folium.Map(locations1[0], 
                    zoom_start=10, 
                    # tiles="http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}",# 设置高德底图
                    # tiles="http://rt{s}.map.gtimg.com/realtimerender?z={z}&x={x}&y={y}&type=vector&style=0",# 设置腾讯底图
                    tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}&ltype=6',
                    attr='default'  )  # 中心区域的确定
    # m2 = folium.Map(locations2[0], zoom_start=15, attr='default')  # 中心区域的确定

    folium.PolyLine(  # polyline方法为将坐标用线段形式连接起来
        locations1,  # 将坐标点连接起来
        weight=4,  # 线的大小为3
        color=color1,  # 线的颜色为橙色
        opacity=0.8  # 线的透明度
    ).add_to(m1)  # 将这条线添加到刚才的区域m内

    # folium.PolyLine(  # polyline方法为将坐标用线段形式连接起来
    #     locations2,  # 将坐标点连接起来
    #     weight=3,  # 线的大小为3
    #     color=color2,  # 线的颜色为橙色
    #     opacity=0.8  # 线的透明度
    # ).add_to(m2)  # 将这条线添加到刚才的区域m内

    # 起始点，结束点
    folium.Marker(locations1[0], popup='<b>Starting Point</b>').add_to(m1)
    folium.Marker(locations1[-1], popup='<b>End Point</b>').add_to(m1)
    for i in error_zuobiao_list:
        gcj_lon, gcj_lat = wgs84_to_gcj02(i[0], i[1])
        acc_close_time = i[2]
        folium.Marker([gcj_lon, gcj_lat], icon=folium.Icon(color='red'),popup=f'<b>ACC关闭时长：{acc_close_time}</b>').add_to(m1)
    for x in stop_zuobiao_list:
        gcj_lonx, gcj_latx = wgs84_to_gcj02(x[0], x[1])
        car_stop_time = x[2]
        folium.Marker([gcj_lonx, gcj_latx], icon=folium.Icon(color='orange'),popup=f'<b>停车超时时长：{car_stop_time}</b>').add_to(m1)
    m1.save(os.path.join('./templates','index.html'))  # 将结果以HTML形式保存到指定路径
    # m2.save(os.path.join('D:\GPS', '21.HTML'))  # 将结果以HTML形式保存到指定路径
    # return m1
# df = pd.read_excel(io=r'D:\GPS\GPS1.xlsx',usecols="A:L")
# df_zg = df.replace({"开":1,"关":0})
# print(df_zg)
# def draw_map():
#     data_gcj_list = data_tf()
#     m1 = draw_gps(data_gcj_list)
#     return m1


def acc_on_off(df):
    df_zg = df.replace({"开":1,"关":0})
    x_array = np.array(df_zg)[1:,3:].tolist()
    start_time = ''
    interval_time_list,time_list=[],[]
    start_list,end_list,error_list,error_zuobiao_list = [],[],[],[]
    for i,_ in enumerate(x_array):
        try:
            if int(x_array[i+1][5]) - int(x_array[i][5]) < 0 :
                start_time = x_array[i+1][0]
                # start_list.append(x_array[i+1])

            if  int(x_array[i+1][5]) - int(x_array[i][5]) > 0 and start_time != "":
                end_time = x_array[i+1][0]
                time_1_struct = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                time_2_struct = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                interval_time = (time_2_struct - time_1_struct).seconds
                # interval_time = end_time - start_time
                time_list.append([start_time,end_time])
                # end_time_list.append(time_2_struct)
                interval_time_list.append(interval_time)
                
                speed = x_array[i][3]
                if x_array[i][5] == 0:
                    acc = "关"
                else:
                    acc = "开"
                # acc = x_array[i][5]
                weidu = x_array[i][2]
                jingdu = x_array[i][1]
                satus = x_array[i][6]
                address = x_array[i][8]
                interval_time_str = strftime("%H:%M:%S", gmtime(interval_time))
                error_list.append([start_time,end_time,interval_time_str,address,speed,acc,satus])
                error_zuobiao_list.append([weidu,jingdu,interval_time_str])
                start_time = ''
        except:
            pass
    # print(error_list)
    return error_list,error_zuobiao_list


def get_err_data(df):
    car_name = np.array(df)[1:,1:2].tolist()[0]
    x_array = np.array(df)[1:,3:].tolist()
    start_time = ''
    interval_time_list,time_list=[],[]
    start_list,end_list,error_list,error_zuobiao_list = [],[],[],[]
    for i,_ in enumerate(x_array):
        try:
            if int(x_array[i+1][3]) == 0 and int(x_array[i+1][3]) - int(x_array[i][3]) < 0 :
                start_time = x_array[i+1][0]
                # start_list.append(x_array[i+1])

            if int(x_array[i][3]) == 0 and int(x_array[i+1][3]) - int(x_array[i][3]) > 0 and start_time != "":
                end_time = x_array[i][0]
                time_1_struct = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                time_2_struct = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                interval_time = (time_2_struct - time_1_struct).seconds
                # interval_time = end_time - start_time
                time_list.append([start_time,end_time])
                # end_time_list.append(time_2_struct)
                interval_time_list.append(interval_time)
                if interval_time >=  3*60 :
                    weidu = x_array[i][2]
                    jingdu = x_array[i][1]
                    speed = x_array[i][3]
                    acc = x_array[i][5]
                    satus = x_array[i][6]
                    address = x_array[i][8]
                    interval_time_str = strftime("%H:%M:%S", gmtime(interval_time))
                    error_list.append([start_time,end_time,interval_time_str,address,speed,acc,satus])
                    error_zuobiao_list.append([weidu,jingdu,interval_time_str])
                start_time = ''
        except:
            pass
    # print(error_list)
    return error_list,str(car_name),error_zuobiao_list


def df_format(company,df):
    
    pass



def main():
    
    output.put_markdown('# GPS异常筛选程序')
#     output.put_markdown('功能如下：')
#     output.put_markdown("""
# - 选择文件
# - 自动判断输出异常记录

#     """)
    output.put_collapse('功能说明', [
        output.put_markdown("""
 - 选择excel文件(.xlsx)

        """),
        output.put_markdown("""

 - 自动判断输出异常记录
        """),
        output.put_markdown("""
 - 可选择异常判断时长（默认为3min）
        """),
            output.put_markdown("""
 - 点击绘制车辆行驶路线
        """)
        
    ], open=False).show()
    data = input.input_group(
    "运输公司及数据录入",
    [
        # input("What is your Name?", name="name", type=TEXT),
        # input("Input your age", name="age", type=NUMBER),
        
        input.radio("请选择运输公司：",name="company",options=["坤达","南化","通运","亚能","永顺","虞安"],inline=True,value=['坤达']),
        input.file_upload('选择一个excel文件', name="file",accpept ='.xlsx')
        # input.checkbox(
        #     "User Term", name="agreement", options=["I agree to terms and conditions"]
        # ),
    ],
)
    company,file = data['company'],data['file']
    
    # company = input.radio("请选择运输公司：",["坤达","南化","通运","亚能","永顺","虞安"],inline=True,value=['坤达'])
    # file = input.file_upload('选择一个excel文件','.xlsx')
    df = pd.read_excel(file['content'])
    
    err_data,car_name,stop_zuobiao_list = get_err_data(df)
    acc_data,error_zuobiao_list = acc_on_off(df)
    draw_gps(data_tf(df),'blue',error_zuobiao_list,stop_zuobiao_list) #绘图
    table_name = ['异常开始时间','异常结束时间','异常时长','异常发生位置','车速','ACC','定位']
    acc_name = ['ACC关闭开始时间','ACC关闭结束时间','关闭时长','异常发生位置','车速','ACC','定位']
    err_data.insert(0,table_name)
    acc_data.insert(0,acc_name)
    # output.put_table(
    #     [["车辆名称"],
    #     car_name]
    # )
    pywebio.output.put_link("绘制地图", url="http://localhost:8099/map", app=None, new_window=True,\
                     scope=None, position=- 1)

    output.put_markdown(f'车辆名称：{car_name}')
    output.put_markdown('## 车辆超时异常记录(默认为超过3分钟即可作为异常)：')

    output.put_table(
        err_data
    )
    
    output.put_markdown("## 车辆ACC关闭记录：")
    
    output.put_table(
        acc_data
    )
    # m1 = draw_map()
    # output.put_html(m1.to_html())
    # 

# if __name__=='__main__':
#     pywebio.platform.flask.start_server(main,port=8089, debug=False)
    # main()
    
if __name__=='__main__':
    pywebio.platform.flask.start_server(main,port=9089, debug=True)
    # main()

    