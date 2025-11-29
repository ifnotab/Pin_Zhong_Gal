label start:
    #This is the beginning video
    $ renpy.movie_cutscene("videos/1.webm")
    
    #The first scene
    #Upload the background image
    image ship = "photos/0.jpg"
    #Show the background image
    scene ship
    show ship at truecenter
    #Define a character
    define robin = Character("Robin", color="#cd8b35")
    define pa1   = Character("Passenger 1", color="#357ec7")
    #Dialogue
    pa1 "罗宾"
    robin "呃，呃啊......"
    robin "我，什么，我是？呃！"