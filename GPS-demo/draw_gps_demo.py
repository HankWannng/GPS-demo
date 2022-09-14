from email import header
from re import X


#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date     :2022/07/27 11:15:00
@Author      :HankWang
@version      :1.0
'''
from flask import Flask
from flask import render_template #渲染
app = Flask(__name__)

"""
    li=[]
    a=open("E://12.HTML")
    a_r=a.read()
    for i in a_r:
        li.append(i)
    a.close()

    b = open("E://21.HTML")
    b_r = b.read()
    for j in b_r:
        li.append(j)
    b.close()

    c = open("E://1221.html","w")
    s=""
    c.write(s.join(li))
"""
    

@app.route('/map')
def map():
    
    return render_template('index.html')
# draw_gps(data_tf(),'blue')


if __name__ == '__main__':    
    app.run(host='0.0.0.0',debug=True,port=8099) #127.0.0.1 回路 自己返回自己