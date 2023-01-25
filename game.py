import os
import pygame
from pygame.locals import *
import sys, time
import math, random
import json
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
try:
    fs = open("time.dat")
    fs.close()
except FileNotFoundError:
    if is_admin():
        lll = {"time": 999}
        with open("time.dat", "w") as f_obj:
            json.dump(lll, f_obj)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()
else:
    with open("time.dat") as f_obj:
        lll = json.load(f_obj)
# 地图列表
Map_List = []
# 图片列表
Image_List = []


# 变量类

class Variate:

    def __init__(self):
        # 界面宽高
        self.Screen_Width = 800
        self.Screen_Height = 480
        # 游戏横竖格子
        self.Game_Row = 6
        self.Game_Col = 10
        # 游戏表格面积
        self.Map_Sum = self.Game_Row * self.Game_Col
        # 方块图片种类数（在此可调整难度）
        self.Ele_Num = 15
        # 背景颜色
        self.BackGround_Color = (000, 220, 220)
        # 游戏标题
        self.Game_Title = '冬奥运连连看'
        # 游戏初始化界面图
        self.Begin_Img = './images/3987055.png'
        # 获胜照片
        self.Win_Img = './images/3987056.png'
        # 鼠标样式
        self.Mouse_Img = '点击.png'
        # 游戏尺寸
        self.Grid_Size = 80
        # 图片占格尺寸
        self.Ico_Size = (76, 76)
        # 目标数组
        self.Targets = []


# 实例化变量类
VariateObject = Variate()


# 图片模块
class Block:
    # 按下图片按钮的能力
    checkstate_able = True
    # 图片是否被选择
    checkstate_be = False

    def __init__(self, screen, image_path, x, y, number, element):
        self.x = x
        self.y = y
        self.element = element
        self.number = number
        self.screen = screen
        self.image = pygame.image.load(image_path)

        # 因为图片原始大小为 200x200，所以要进行缩放
        self.image = pygame.transform.scale(self.image, VariateObject.Ico_Size)

    # 选中高亮显示
    def Pitch_On(self):
        if self.checkstate_be:
            pygame.draw.rect(self.image, (255, 0, 0),
                             (0, 0, self.image.get_width() - 1, self.image.get_height() - 1), 2)
        else:
            pygame.draw.rect(self.image, (0, 205, 205, 0),
                             (0, 0, self.image.get_width() - 1, self.image.get_height() - 1), 2)
        self.screen.blit(self.image, (self.x, self.y))

    # 图片隐藏
    def Hide_Img(self):
        self.checkstate_be = False
        self.checkstate_able = False
        # 填充颜色
        self.image.fill((255, 255, 240))

    # 返回图片状态
    def Checkstate_Able_State(self):
        return self.checkstate_able

    # 判断是否点击同张图片
    def Is_Same_Click(self):
        self.checkstate_be = not self.checkstate_be
        return self.checkstate_be

    # 图片状态重置
    def Reset_Stats(self):
        self.checkstate_be = False

    # 获取图片大小信息
    def Get_Geometry(self):
        return (int(self.x), int(self.y), VariateObject.Ico_Size[0], VariateObject.Ico_Size[1])


# 构建游戏布局地图
def Map_Layout():
    # 存储零时照片数列
    temp_list = []
    for i in range(0, VariateObject.Map_Sum, 2):
        # 随机生成照片
        temp = math.ceil(random.random() * VariateObject.Ele_Num)
        temp_list.append(temp)
        temp_list.append(temp)

    # 最终得到的地图数列
    map_list = []
    for i in range(0, VariateObject.Map_Sum, 1):
        i = int((VariateObject.Map_Sum - i) * random.random())
        map_list.append(temp_list[i])
        # 不弹出则有大几率无解
        temp_list.pop(i)
    return map_list


# 检查全盘是否还有方块
def Inspection_All():
    for i in Map_List:
        if i > 0:
            return False
    return True


# https://blog.csdn.net/qq_41551359/article/details/82983513此处算法借鉴CSDN
# 水平检测
def Horizon(Targets):
    # 获取当前行格子数
    col = VariateObject.Game_Col
    # 获取 t1 t2 位置状态
    t1_x = int(Targets[0].number % col)
    t1_y = int(Targets[0].number / col)
    t2_x = int(Targets[1].number % col)
    t2_y = int(Targets[1].number / col)
    # 如果 p1 和 p2 在同一行，则不符合要求
    if t1_y == t2_y:
        return False
    # UpLine 为上水平线，DownLine 为下水平线
    if t1_y < t2_y:
        UpLine = t1_y
        DownLine = t2_y
    else:
        UpLine = t2_y
        DownLine = t1_y

    # 初始化左、右边界线为 0
    LeftLimit = 0
    RightLimit = col - 1
    # 寻找左边界线
    i = t1_x
    while i > 0:
        # 判断左边点是否为空
        if Map_List[t1_y * col + i - 1] != 0:
            break
        # 当左边点为空时会继续扫面下一个左边点
        i -= 1
    LeftLimit = i
    i = t2_x
    while i > 0:
        if Map_List[t2_y * col + i - 1] != 0:
            break
        i -= 1
    # LeftLimit 记录左边界线，该界线所在的点为空或p1、p2本身
    if i > LeftLimit:
        LeftLimit = i
    # 如果 leftLimit 为 0，说明p1、p2已经在外界接通了，直接返回
    if LeftLimit == 0:
        return True
    # 寻找右边界线
    i = t1_x
    while i < col - 1:
        if Map_List[t1_y * col + i + 1] != 0:
            break
        i += 1
    RightLimit = i
    i = t2_x
    while i < col - 1:
        if Map_List[t2_y * col + i + 1] != 0:
            break
        i += 1
    if i < RightLimit:
        RightLimit = i

    if RightLimit == col - 1:
        return True  # Bug

    # 判断 leftLimit 和 rightLimit
    if LeftLimit > RightLimit:
        # 如果左边界线超出右边界线，则无法连接
        return False
    else:
        # 从左往右扫描
        for i in range(LeftLimit, RightLimit + 1):
            j = UpLine + 1
            for j in range(UpLine + 1, DownLine):
                # 只要当前列有阻碍，马上跳出
                if Map_List[j * col + i] != 0:
                    # 回退一行
                    # j -= 1
                    break
                j += 1
            if j == DownLine:
                return True

        return False


# 垂直扫描
def Vertical(Targets):
    row = VariateObject.Game_Row
    col = VariateObject.Game_Col
    t1_x = int(Targets[0].number % col)
    t1_y = int(Targets[0].number / col)
    t2_x = int(Targets[1].number % col)
    t2_y = int(Targets[1].number / col)

    if t1_x == t2_x:
        return False

    if t1_x < t2_x:
        LeftLine1 = t1_x
        RightLine2 = t2_x
    else:
        LeftLine1 = t2_x
        RightLine2 = t1_x

    # 初始化上、下边界线
    UpLimit = 0
    DownLimit = row - 1

    # 寻找上边界线
    i = t1_y
    while i > 0:
        if Map_List[t1_x + (i - 1) * col] != 0:
            break  # 判断上边点是否为空
        i -= 1  # 当上边点为空时会继续扫面下一个上边点
    UpLimit = i

    i = t2_y
    while i > 0:
        if Map_List[t2_x + (i - 1) * col] != 0:
            break
        i -= 1

    if i > UpLimit:
        UpLimit = i

    if UpLimit == 0:
        return True

    i = t1_y
    while i < row - 1:
        if Map_List[t1_x + (i + 1) * col] != 0:
            break
        i += 1
    DownLimit = i

    i = t2_y
    while i < row - 1:
        if Map_List[t2_x + (i + 1) * col] != 0:
            break
        i += 1

    if i < DownLimit:
        DownLimit = i

    if DownLimit == row - 1:
        return True

    if UpLimit > DownLimit:
        return False
    else:
        for i in range(UpLimit, DownLimit + 1):
            j = LeftLine1 + 1
            for j in range(LeftLine1 + 1, RightLine2):
                if Map_List[i * col + j] != 0:
                    break
                j += 1
            if j == RightLine2:
                return True

        return False


# 检查合法算法
def Check_Algorithm(Targets):
    # 判断两个图片是否相同
    if Targets[0].element != Targets[1].element:
        play_sound("music/" + "Mistake.wav")
        return False
    else:
        if Vertical(Targets) or Horizon(Targets):
            # 播放特效音乐
            play_sound("music/" + "Hide.wav")
            return True
        else:
            play_sound("music/" + "Mistake.wav")
            return False


# 检查是否被按下
def check_event(Image_List):
    for event in pygame.event.get():
        # 如果点击右上角的X则退出
        if event.type == QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                os.execl(sys.executable, sys.executable, *sys.argv)
        # 检测鼠标事件
        if event.type == MOUSEBUTTONDOWN:
            Positon = pygame.mouse.get_pos()
            for Img in Image_List:
                geo = Img.Get_Geometry()
                x = geo[0]
                y = geo[1]
                w = geo[2]
                h = geo[3]
                # 检查是否在图片块范围内
                if Positon[0] > x and Positon[0] < x + w and Positon[1] > y and Positon[1] < y + h:
                    # 如果图片还没被消除
                    if Img.Checkstate_Able_State():
                        # ·=检查是否有点下的能力
                        if not Img.Is_Same_Click():
                            # 检查是否点自己,消除标记目标点
                            VariateObject.Targets.clear()
                            break
                        # 如果目标非空
                        if VariateObject.Targets != []:
                            # 添加点击点信息
                            VariateObject.Targets.append(Img)
                            # 检查连接合法性
                            if Check_Algorithm(VariateObject.Targets):
                                # 如果合法则隐藏图标
                                for point in VariateObject.Targets:
                                    Map_List[point.number] = 0
                                    point.number = 0
                                    point.Hide_Img()
                            else:
                                # 不合法重置图片状态
                                for point in VariateObject.Targets:
                                    point.Reset_Stats()
                            # 判断完毕重置目标点
                            VariateObject.Targets.clear()
                        else:
                            # 不为空则计入目标
                            VariateObject.Targets.append(Img)
                    break


# 背景音乐
def Music():
    pygame.mixer.music.load("music/Summer.mp3")
    # 设置音量
    pygame.mixer.music.set_volume(40)
    # 循环播放
    pygame.mixer.music.play(-1, 0)


def Music2():
    play_sound("music/" + "Win.wav")


_sound_library = {}


# 播放音效(与背景音乐可同时播放，但默认只支持wav格式)
def play_sound(path):
    global _sound_library
    sound = _sound_library.get(path)
    if sound is None:
        temp = path.replace('/', os.sep).replace('\\', os.sep)
        sound = pygame.mixer.Sound(temp)
        sound.set_volume(40)
        _sound_library[path] = sound
    sound.play()


def A():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit()


def text_objects(text, font):
    textSurface = font.render(text, True, black=(0, 0, 0))
    return textSurface, textSurface.get_rect()


def button(msg, x, y, w, h, ic, ac, gameDisplay, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    print(click)
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            action()
    ##        if action == "play":
    ##          action()
    ##        if action == "quit":
    ##          pygame.quit()
    ##          quit()
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))
    smallText = pygame.font.SysFont('comicsansms', 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurf, textRect)


# 主函数
def main():
    # 初始化
    pygame.init()
    # 创建窗口
    screen = pygame.display.set_mode((VariateObject.Screen_Width, VariateObject.Screen_Height), 0, 0)
    # 设置标题
    pygame.display.set_caption(VariateObject.Game_Title)
    # 加载鼠标样式
    # mouse_cursor = pygame.image.load(VariateObject.Mouse_Img).convert_alpha()
    # 导入图片元素
    global Map_List
    Map_List = Map_Layout()
    # 获取图片位置信息
    for i in range(0, VariateObject.Map_Sum):
        x = int(i % VariateObject.Game_Col) * VariateObject.Grid_Size + (
                VariateObject.Grid_Size - VariateObject.Ico_Size[0]) / 2
        y = int(i / VariateObject.Game_Col) * VariateObject.Grid_Size + (
                VariateObject.Grid_Size - VariateObject.Ico_Size[0]) / 2
        element = './images/ele_' + str(Map_List[i]) + '.png'
        Image_List.append(Block(screen, element, x, y, i, Map_List[i]))
    Game_Status = True
    # 播放背景音乐
    Music()
    Begin_Img = pygame.image.load(VariateObject.Begin_Img)
    screen.blit(Begin_Img, (
        (VariateObject.Screen_Width - Begin_Img.get_width()) / 2,
        (VariateObject.Screen_Height - Begin_Img.get_height()) / 2))
    font = pygame.font.SysFont("SimHei", 30)
    screen.blit(font.render("按下ESC重新开始游戏", -1, (255, 0, 0)), (0, 0))
    red = (200, 0, 0)
    green = (0, 200, 0)
    bright_red = (255, 0, 0)
    bright_green = (0, 255, 0)
    # button("GO", 150, 450, 100, 50, green, bright_green, A(),screen)
    # button("Quit", 550, 450, 100, 50, red, bright_red, A(),screen)
    pygame.display.update()
    time.sleep(2)
    # Start_time = time.time()
    while True:
        '''
        #设置鼠标图标
        x, y = pygame.mouse.get_pos()
        x -= mouse_cursor.get_width() / 2
        y -= mouse_cursor.get_height() / 2
        screen.blit(mouse_cursor, (x, y))
        '''
        # 填充背景颜色
        screen.fill(VariateObject.BackGround_Color)
        # 判断游戏是否结束
        if Game_Status:
            if Inspection_All():
                Game_Status = False
            for Img in Image_List:
                Img.Pitch_On()
            font = pygame.font.SysFont("SimHei", 30)  # 设置字体和大小
            pygame.display.update()
        else:
            # 获胜播放背景
            # play_sound("music/" + "Win.wav")
            Music2()
            # end_time = time.time()
            # print(end_time)
            # screen.blit(font.render("用时得分：" + str(end_time), -1, (0, 0, 255)), (0, 0))
            Winner = pygame.image.load(VariateObject.Win_Img)
            screen.blit(Winner, ((VariateObject.Screen_Width - Winner.get_width()) / 2,
                                 (VariateObject.Screen_Height - Winner.get_height()) / 2))
            font = pygame.font.SysFont("SimHei", 30)
            end_time = time.clock()
            end_time2 = round((end_time) / 60, 2)
            etime = str(round((end_time) / 60, 2))
            screen.blit(font.render("历史最高：" + str(lll["time"]) + "分钟", -1, (0, 255, 0)), (0, 0))
            screen.blit(font.render("用时：" + etime + "分钟", -1, (0, 255, 0)), (0, 30))
            screen.blit(font.render("即将重新开始游戏", -1, (255, 0, 0)), (400, 400))
            if (end_time2 < lll["time"]):
                lll["time"] = end_time2
            pygame.display.update()
            with open("time.dat", "w") as f_obj:
                json.dump(lll, f_obj)
            time.sleep(6)
            os.execl(sys.executable, sys.executable, *sys.argv)
        # 检查按键事件
        check_event(Image_List)
        time.sleep(0.05)


if __name__ == '__main__':
    main()

