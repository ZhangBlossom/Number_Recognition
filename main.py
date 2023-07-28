import time, sensor, image, ustruct
from image import SEARCH_EX, SEARCH_DS
from pyb import UART,LED

one=LED(1)
#从imgae模块引入SEARCH_EX和SEARCH_DS。使用from import仅仅引入SEARCH_EX,
#SEARCH_DS两个需要的部分，而不把image模块全部引入。
clock = time.clock()
#重启传感器
sensor.reset()
#初始化传感器
sensor.set_contrast(1)      #设置对比度
sensor.set_gainceiling(16)  #设定增益曲线
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
#sensor.skip_frames(2000) #跳过两秒等待稳定  不加
#串口3定义
uart1 = UART(3,115200,bits=8, parity=None, stop=1)

#初始模板
templatedemo = ["/1.pgm", "/2.pgm", "/3.pgm", "/4.pgm","/5.pgm", "/6.pgm", "/7.pgm", "/8.pgm"]
##分类模板  暂定12张
templates = (["/33.pgm", "/34.pgm", "/36.pgm","/306.pgm","/311.pgm","/312.pgm"], #ok
            ["/42.pgm", "/43.pgm", "/44.pgm","/45.pgm", "/403.pgm","/410.pgm"],  #ok
            ["/53.pgm", "/55.pgm", "/501.pgm","/504.pgm","/507.pgm","/508.pgm"], #待定
            ["/64.pgm","/65.pgm", "/602.pgm","/606.pgm","/611.pgm","/614.pgm"],  #ok
            ["/75.pgm", "/76.pgm","/701.pgm","/702.pgm","/706.pgm","/707.pgm"],  #ok
            ["/85.pgm","/82.pgm", "/801.pgm","/803.pgm","/804.pgm","/806.pgm"])  #8\


imgarray=[0,0,0,0,0,0,0,0]  #初始八个数据模板
imgarrays=[0,0,0,0,0,0]     #单个数字模板
first=0                     #初识别数字


"""
sending_data部分由于使用了两个openmv
因此只需要帧头帧尾不同
stm32单片机即可知道是从那边接收而来
"""
def sending_data(isget):#发送数据
    global uart1
    datasum=ustruct.pack("<bb",
                    0xA6,  #左边   右边0xA6
                    #isget,
                    0x20)
    #print("sending",isget ) #用于判断有无获取
    uart1.write(datasum)

"""
病房号识别输入，返回存储一到八图片的模组
"""
def get_first(img):
    global imgarray
    i=0
    for t in imgarray:
        r = img.find_template(t, 0.70, step=4, search=SEARCH_EX) #, roi=(10, 0, 60, 60))
        i+=1
        if r:
            return i
    return 0

"""
判断是否输入成功
如若成功，则openmv上的led灯
将对应亮相应的次数
"""
def isget(num):
    if num is not 0:
        for i in range (num):
            one.on()
            print(num) #使用时删除 给自己看的
            time.sleep_ms(300)
            one.off()
            time.sleep_ms(300)

"""
传入对应的数字匹配模组
将会导入对应的图片
如数字7，那么会导入数字7对应的图片
"""
def getimgs(imgarr):
    i=0
    for t in imgarr:
        imgarrays[i]=image.Image((t))
        i+=1
    return imgarrays

"""
模板匹配，将当前帧数据与模板数据
比对，如果存在，则框出对应位置，
同时调用串口发送给单片机
"""
def match_img(photos,img):
    isget=0
    for t in photos:
        r=img.find_template(t,0.5,step=4,search=SEARCH_EX)
        if r:
            img.draw_rectangle(r)
            isget=1
            break
    if isget!=0:
        sending_data(0x04) #0x03->left  0x04->right
        isget=0

"""
初始八张图片的导入函数
"""
def loadimg():
    i=0
    for t in templatedemo:
        imgarray[i]=image.Image(str(t))
        i+=1
    return imgarray


#-------------------------------程序执行部分----------------------------
imgarray=loadimg()                              #加载初始八张图

while (True):
    clock.tick()                                    #时钟初始化
    img = sensor.snapshot()                         #获取当前帧
    if imgarrays[0]!=0:                             #且当已经加载好了多模板库后只会执行当前if
        match_img(imgarrays,img)                    #比对当前帧图片与加载进来的模板库匹配
    else:
        if first==0:                                #获取初始图片标志位
            first=get_first(img)                    #first用于判断当前是那张图片
            isget(first)                            #亮灯提醒是否识别到初始图片
        elif first==1:
            sending_data(0x01)                      #确定是1
        elif first==2:
            sending_data(0x02)                      #确定是2
        elif imgarrays[0]==0:                       #确定图片缓冲区第一次是空
            imgarrays=getimgs(templates[first-3])   #load photo 加载图片 执行一次
    #print("FPS:",clock.fps())                      #帧率显示
