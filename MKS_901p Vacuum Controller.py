import time
from tkinter import *
from tkinter import messagebox
from mks_901p import MKS_901p

def recordingButtonPressed():
    global recording
    global outputFile
    global startTime
    
    if recording:
        outputFile.close()
        recordButton.config(text="Record", background="green")
        
    else:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        outputFile = open('PLog-' + timestr, 'w')
        outputFile.write("Time (ms), Pressure (torr)\n")
        recordButton.config(text="Stop", background="red")
        startTime = int(round(time.time() * 1000))
        
    recording = not recording  

def updatePressure():
    
    pressure = mks_901p.getPressure()
    
    pressureLabel.config(text = pressure)
    pressureUnitLabel.config(text = mks_901p.units)
    spinnerLabel.config(text = mks_901p.nextSpinner())
        
    if recording:
        millis = int(round(time.time() * 1000)) - startTime
        outputFile.write("{}, {}\n".format(millis, mks_901p.pressureSciNote))
    
    masterWindow.after(250, updatePressure)
    
 
masterWindow = Tk()
masterWindow.title("MKS 901p Vacuum Controller") #pressure gauge name - search up "MKS901P vacuum gauge" for more info
masterWindow.geometry("400x200")
masterWindow.configure(background="black")
masterWindow.resizable(False, False) #Don't allow resizing in the x or y direction

recordButton = Button(masterWindow, text="Record", width=10, command=recordingButtonPressed, background="green")
recordButton.place(x = 140, y = 150 , width=120, height=25)

pressureLabel = Label(masterWindow, text="", background="black", foreground="blue", font=(None, 70))
pressureLabel.place(x = 0, y = 10, width=400, height=100)
pressureUnitLabel = Label(masterWindow, text="", background="black", foreground="blue", font=(None, 35))
pressureUnitLabel.place(x = 0, y = 100, width=400, height=35)
spinnerLabel = Label(masterWindow, text="", background="black", foreground="white", font=(None, 20), anchor=W)
spinnerLabel.place(x = 20, y = 157, width=10, height=10)

recording = False

try:
    mks_901p = MKS_901p()
    
except Exception as e:
    masterWindow.withdraw()
    messagebox.showerror("Error", repr(e))
    exit()

mks_901p.dumpConfig()
masterWindow.after(0, updatePressure)
masterWindow.mainloop()
