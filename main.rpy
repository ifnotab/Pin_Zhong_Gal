label start:
    #This is the beginning video
    $ renpy.movie_cutscene("videos/1.webm")

    #Scene 1
    #The shaking effect
    transform random_shake:
        block:
            linear 0.05 xoffset 10
            linear 0.05 xoffset -10
            repeat 5    
    #Upload the background image
    image ship = "photos/0.jpg"
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

    #Scene 3
    #Upload the background image
    image cor = "photos/0.jpg"
    #Show the background image
    scene cor at truecenter

    menu:
        "正中到右侧赌场":
            "1"
        "左侧酒馆" if False:
            pass