#Here is the initial settings for this game
define config.menu_include_disabled = True 

label start:
    #This is the beginning video
    $ renpy.movie_cutscene("videos/1.webm")

label Scene_1:

    #Scene 1
    #The shaking effect
    transform random_shake:
        block:
            linear 0.05 xoffset 10
            linear 0.05 xoffset -10
            repeat 5    
    #Upload the background image
    image ship = "photos/1.jpg"
    #Show the background image
    scene ship
    #Shaking
    show ship at truecenter,random_shake
    pause 1.5
    #Normal
    show ship at truecenter
    #Define a character
    define robin = Character("Robin", color="#cd8b35")
    define pa1   = Character("Passenger 1", color="#357ec7")
    #Dialogue
    pa1 "罗宾"
    robin "呃，呃啊......"
    robin "我，什么，我是？呃！"
    #Shaking again
    show ship at truecenter,random_shake

    #Scene change with black screen
    scene black
    with Fade(1.0)

label Scene_2:

    #Scene 2
    #Upload the background image
    image sunrise = "photos/0.jpg"
    #Show the background image
    scene sunrise at truecenter
    with Fade(1.0)
    #robin's view
    robin "“什么，什么？我在？我是？！”"
    robin "我感到头痛难耐，记不清楚我的名字，大概是钝器伤引发的脑震荡和退行性失忆。"
    robin "也许我应该四处看看。"
    robin "我看向四周"
    #camera turn left and right (by using a long background image then turn left and right)
    transform camera_pan:
        block:
            linear 2.0 xoffset -400
            linear 2.0 xoffset 0
            linear 2.0 xoffset 400
            linear 2.0 xoffset 0
    show sunrise at camera_pan
    pause 0.1
    #stop camera movement
    show sunrise at truecenter
    #continue dialogue
    robin "舷窗，招待所般的布置，奢华的装潢，还有......一叠筹码？这是在一艘游轮上？还是一座赌场里？"
    robin "我怎么会在游轮上？我应该在......呃！"
    robin "不列！我记不起来了，我到底为什么在......"
    #Telephone
    play sound "sounds/1.ogg"
    "（响铃）"
    "一个无感情的女声"
    "“先生，您醒了？今天的早餐尚未开始供应，但赌场仍处于开放时间，您不去试试手气吗？”"
    robin "“也许，我应该带上筹码去看看。”"

label Scene_3:

    #Scene 3
    #Upload the background image
    image cor = "photos/0.jpg"
    #Show the background image
    scene cor at truecenter

    menu:
        "到右侧赌场":
            jump Scene_4
        "酒馆 (熄灯不可选)" if False:
            pass
        "回到走廊 (暂时不可选)" if False:
            pass
    
label Scene_4:

    #Scene 4
    #Upload the background image
    image cas = "photos/0.jpg"

    #Choose 
    menu:
        "1号台":
            jump Scene_5
        "2号台" if False:
            pass
        "3号台" if False:
            pass
        "4号台" if False:
            pass
        "5号台" if False:
            pass

label Scene_5:

    #Scene_5 
    #Upload the background image
    image tab = "photos/0.jpg"

    #Character
    define QL = Character("QL", color="#11DA22")
    QL "哦，先生真是闲情逸致呢，这么早就来玩吗？怎么称呼，先生？"
    robin "叫我......叫我罗宾吧。"
    QL "您想玩点什么呢？21点？德州扑克？还是简单的石头剪刀布？"
    robin "我想想，教教我规则吧。"

label Rules:

    #Rules introduction
    menu:
        "21点":
            "21点是一种比较简单的牌类游戏，玩家和庄家各自发两张牌，玩家可以选择要牌或者停牌，目标是让自己的牌点数总和尽量接近21点，但不能超过21点。"
            jump Rules
        "德州扑克":
            "德州扑克是一种比较复杂的牌类游戏，玩家和庄家各自发两张牌，玩家可以选择要牌或者停牌，目标是让自己的牌点数总和尽量接近21点，但不能超过21点。"
            jump Rules
        "石头剪刀布":
            "石头剪刀布是一种比较简单的游戏，玩家和庄家各自出一个手势，石头胜剪刀，剪刀胜布，布胜石头。"
            jump Rules
        "离开":
            jump Scene_6
            
init python:

    #Import the python game
    import subprocess
    import os
    def launch_external_python():
        script_path = os.path.join(config.gamedir, "main.py")
        subprocess.run(["python", script_path], shell=True)

label Scene_6:

    QL "那我们开始吧"

    #Run the game
    $ launch_external_python()

    robin "就到这里吧，我有点厌倦了。"
    QL "要聊聊天解乏吗，抑或是我替您点一杯？您稍后也可以到酒馆那里继续喝哦"
    robin "和我聊聊......"

    jump Scene_7

label Scene_7:

    #Choose 
    menu:
        "和我聊聊这艘船吧":
            jump Scene_8
        "和我聊聊这个赌场吧":
            jump Scene_9
        "和我聊聊这艘船的船主吧":
            jump Scene_10
        "和我聊聊这里的故事吧":
            jump Scene_11
        "离开":
            jump Scene_12

label Scene_8:
    jump Scene_7

label Scene_9:
    jump Scene_7

label Scene_10:
    jump Scene_7

label Scene_11:
    jump Scene_7

label Scene_12:
    menu:
        "到右侧赌场":
            jump Scene_6
        "酒馆":
            jump Scene_13
        "回到走廊 (暂时不可选)" if False:
            pass

label Scene_13:
    define uncle = Character("Uncle", color="#6d380f85")
    uncle "嗯，请坐，来点什么？"
    robin "来杯伏特加，不加冰。"
    uncle "新面孔，想听听情报吗。"
    robin "(排出100筹码)"
    robin "你能告诉我什么？怎么下船？或是，赌场有什么秘密吗？"
    uncle "哈，赌场的秘密怎么是我能说得清楚的。不过怎么下船我倒是可以告诉你，你有多少筹码？"
    robin "大概1000，够么？"
    uncle "不够，一张船票200黄金筹码，1黄金筹码10000筹码，新面孔，天还没亮，等你有足够筹码的时候，就来找我吧。"
    robin "等你和她们混熟点，我也可以给你搞点情报和礼物，现在，先回去睡一觉吧。"