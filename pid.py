from pyb import millis  #定时器
from math import pi, isnan  # pai  判断数据是不是对的

#写一个PID，结构体
#_kp 比例 _ki 积分 _kd微分
#要求 1：可以不精确但是大概东西得有 至少能大概指明转动多少
#2:pid 初始为-0
class PID:
    _kp = _ki = _kd = _integrator = _imax = 0  #记录kp
    _last_error = _last_derivative = _last_t = 0 #上一次误差
    _RC = 1/(2 * pi * 20)
    def __init__(self, p=0, i=0, d=0, imax=0):
        self._kp = float(p)  #浮点数确保精度增加
        self._ki = float(i)
        self._kd = float(d)
        self._imax = abs(imax)
        self._last_derivative = float('nan')  #确保缺失值没有大问题

    def get_pid(self, error, scaler):  #获取pid 让舵机大概旋转一定距离
        tnow = millis()
        dt = tnow - self._last_t
        output = 0
        if self._last_t == 0 or dt > 1000:
            dt = 0
            self.reset_I()
        self._last_t = tnow
        delta_time = float(dt) / float(1000)
        output += error * self._kp
        if abs(self._kd) > 0 and dt > 0:
            if isnan(self._last_derivative):
                derivative = 0
                self._last_derivative = 0
            else:
                derivative = (error - self._last_error) / delta_time
            derivative = self._last_derivative + \
                                     ((delta_time / (self._RC + delta_time)) * \
                                        (derivative - self._last_derivative))
            self._last_error = error
            self._last_derivative = derivative
            output += self._kd * derivative
        output *= scaler
        if abs(self._ki) > 0 and dt > 0:
            self._integrator += (error * self._ki) * scaler * delta_time
            if self._integrator < -self._imax: self._integrator = -self._imax
            elif self._integrator > self._imax: self._integrator = self._imax
            output += self._integrator
        return output

    def reset_I(self):  #pid初始化为0
        self._integrator = 0
        self._last_derivative = float('nan')
#参考
# 1 4 pid 23 python以及pid原理
#https://blog.csdn.net/u010256153/article/details/54928039?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522162797439316780269818010%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=162797439316780269818010&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-2-54928039.pc_search_result_control_group&utm_term=%E7%94%A8python%E5%86%99pid&spm=1018.2226.3001.4187
#https://blog.csdn.net/cumubi7552/article/details/107803856?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-4.pc_relevant_baidujshouduan&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-4.pc_relevant_baidujshouduan
#https://blog.csdn.net/weixin_42881419/article/details/86551249?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522162797403916780264079285%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=162797403916780264079285&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-86551249.pc_search_result_control_group&utm_term=PID&spm=1018.2226.3001.4187
#https://blog.csdn.net/weixin_43933169/article/details/104343441?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522162797439316780269818010%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=162797439316780269818010&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-104343441.pc_search_result_control_group&utm_term=%E7%94%A8python%E5%86%99pid&spm=1018.2226.3001.4187
