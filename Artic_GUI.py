#Import python libraries
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import os
import pandas as pd
import subprocess
import re
import threading

# Create Tk object 
window = tk.Tk() 
  
# Set the window title 
window.title('Artic Pipeline GUI')

# Set window size
width = 800
height = 850

window.geometry(f"{width}x{height}")
window.resizable(False,False)

icon = PhotoImage(file = 'Icon.png')
 
# Setting window icon
window.iconphoto(False, icon)

window.configure(bg='white')

#Open File Explorer to select input folder path
def input_data(button):
    global input_data_directory
    global filenames
    if button == True:
        input_data_directory = filedialog.askdirectory(parent=window,title='Select a folder')
        inputDataPath.delete(0,tk.END)
        input_data_directory = input_data_directory.replace('\\','/')
        inputDataPath.insert(0,input_data_directory)
    elif button == False:
        input_data_directory = inputDataPath.get()
    filenames = os.listdir(input_data_directory)
    filename_selection.delete(0,tk.END)
    for val in filenames:
        filename_selection.insert(tk.END, val)

def select_all():
    filename_selection.select_set(0, END)

def deselect_all():
    filename_selection.selection_clear(0, END)

#Open File Explorer to select output folder path
def output_data(button):
    global output_data_directory
    if button == True:
        output_data_directory = filedialog.askdirectory(parent=window,title='Select a folder')
        outputDataPath.delete(0,tk.END)
        output_data_directory = output_data_directory.replace('\\','/')
        outputDataPath.insert(0,output_data_directory)
    elif button == False:
        output_data_directory = outputDataPath.get()

#Open File Explorer to select sample sheet file path
def read_samplesheet_file(button):
    global barcode_path
    if button == True:
        barcode_path = filedialog.askopenfilename(title="Select a file", filetypes=(("CSV Files","*.csv"), ("All Files","*.*")))
        barcodePath.delete(0,tk.END)
        barcode_path = barcode_path.replace('\\','/')
        barcodePath.insert(0,barcode_path)
    elif button == False:
        barcode_path = barcodePath.get()

#Pass command to terminal
def run():
    threadValue = thread_entry.get()

    if pipelineVar.get() == 1:
        pipeline = "nanopolish"
    elif pipelineVar.get() == 2:
        pipeline = "medaka"

    #Change thread value in pipeline bash script
    with open('peace_1.sh', 'r') as file:
        filedata = file.read()
    file.close()
    indexes = [x for x, v in enumerate(filedata) if v == '\n']
    string_start = filedata.index('threads=')
    indexes.append(string_start)
    indexes.sort()
    string_stop = indexes[indexes.index(string_start) + 1]
    filedata = filedata.replace(filedata[string_start:string_stop],f'threads={threadValue}')

    with open('peace_1.sh', 'w') as file :
        file.write(filedata)
    file.close()

    #Create dataframe from sample sheet
    df = pd.read_csv(barcode_path)
    df.set_index("barcode", drop=True, inplace=True)
    prefix_dict = df.to_dict(orient="index")

    #Create list of folders to process based on selection using listbox
    new_filenames=[]
    selected = filename_selection.curselection()
    for idx in range(len(filenames)):
        if idx not in selected:
            new_filenames.append(filename_selection.get(idx))

    i = 1
    final_file_list = []

    #Confirm that barcode is in the name of all folders to be run
    for filename in new_filenames:
        if 'barcode' in filename:
            final_file_list.append(filename)

    for filename in final_file_list:
        inputDirectory = os.path.join(input_data_directory,filename)
        inputDirectory = inputDirectory.replace('\\','/')  
        outputDirectory = os.path.join(output_data_directory,filename)
        outputDirectory = outputDirectory.replace('\\','/')

        #Find digits in filename and read corresponding ID from sample sheet dictionary  
        tmp = re.findall(r'\d+', filename)
        res = list(map(int, tmp))
        num = ''
        for i in res:
            num += str(i)
        num = int(num)
        prefix = prefix_dict[num]['sample']

        statusTmp = f"Processing Folder {i} of {len(final_file_list)}..."  
        statusText.set(statusTmp)

        subprocess.run(["./peace_1.sh",pipeline,inputDirectory,outputDirectory,prefix,inputDirectory[-2:]])
        i += 1

    #Write all consensus sequences to one file
    for filename in final_file_list:
        tmp = re.findall(r'\d+', filename)
        res = list(map(int, tmp))
        num = ''
        for i in res:
            num += str(i)
        num = int(num)
        tmp = prefix_dict[num]['sample']
        tmp = f'{tmp}.consensus.fasta'
        src = input_data_directory + '/' + filename + '/' + prefix_dict[num]['sample'] + '/' + tmp
        print(src)
        with open(src, 'r') as f:
            data = f.read()
        f.close()
        with open(f'{input_data_directory}/AllConsensusSequences.fasta', 'a') as f:
            f.write(data)
        f.close()

    statusText.set("Done")
        
def changeOnHover(widget, colorOnHover, colorOnLeave, button):
    if button == False:
        widget.bind("<Enter>", func=lambda e: widget.config(highlightbackground=colorOnHover))

        widget.bind("<Leave>", func=lambda e: widget.config(highlightbackground=colorOnLeave))

    elif button == True:
        widget.bind("<Enter>", func=lambda e: widget.config(bg=colorOnHover))

        widget.bind("<Leave>", func=lambda e: widget.config(bg=colorOnLeave))

def light_mode():
    backgroundLabel["bg"] = "white"
    backgroundLabel["image"] = lightbackgroundImage
    Imagelabel["bg"] = "white"
    inputLabel["bg"] = "white"
    filenameselectionLabel["bg"] = "white"
    outputLabel["bg"] = "white"
    barcodeLabel["bg"] = "white"
    threadLabel["bg"] = "white"
    pipelineLabel["bg"] = "white"
    nanopolishLabel["bg"] = "white"
    nanopolishButton["bg"] = "white"
    medakaLabel["bg"] = "white"
    medakaButton["bg"] = "white"
    inputDataPath["bg"],inputDataPath["fg"] = "white", "black"
    filename_selection["bg"], filename_selection["fg"] = "white", "black"
    outputDataPath["bg"], outputDataPath["fg"] = "white", "black"
    barcodePath["bg"], barcodePath["fg"] = "white", "black"
    thread_entry["bg"], thread_entry["fg"] ="white", "black"
    input_button["bg"],input_button["fg"] = "white", "black"
    select_button["bg"],select_button["fg"] = "white", "black"
    deselect_button["bg"],deselect_button["fg"] = "white", "black"
    output_button["bg"],output_button["fg"] = "white", "black"
    barcode_button["bg"],barcode_button["fg"] = "white", "black"
    run_button["bg"],run_button["fg"] = "white", "black"
    statusbar["bg"],statusbar["fg"] = "white", "black"

def dark_mode():
    backgroundLabel["bg"] = "#404040"
    backgroundLabel["image"] = darkbackgroundImage
    Imagelabel["bg"] = "#404040"
    inputLabel["bg"] = "#404040"
    filenameselectionLabel["bg"] = "#404040"
    outputLabel["bg"] = "#404040"
    barcodeLabel["bg"] = "#404040"
    threadLabel["bg"] = "#404040"
    pipelineLabel["bg"] = "#404040"
    nanopolishLabel["bg"] = "#404040"
    nanopolishButton["bg"] = "#404040"
    medakaLabel["bg"] = "#404040"
    medakaButton["bg"] = "#404040"
    inputDataPath["bg"],inputDataPath["fg"] = "#3B3B3B", "white"
    filename_selection["bg"], filename_selection["fg"] = "#3B3B3B", "white"
    outputDataPath["bg"], outputDataPath["fg"] = "#3B3B3B", "white"
    barcodePath["bg"], barcodePath["fg"] = "#3B3B3B", "white"
    thread_entry["bg"], thread_entry["fg"] = "#3B3B3B", "white"
    input_button["bg"],input_button["fg"] = "#3B3B3B", "white"
    select_button["bg"],select_button["fg"] = "#3B3B3B", "white"
    deselect_button["bg"],deselect_button["fg"] = "#3B3B3B", "white"
    output_button["bg"],output_button["fg"] = "#3B3B3B", "white"
    barcode_button["bg"],barcode_button["fg"] = "#3B3B3B", "white"
    run_button["bg"],run_button["fg"] = "#3B3B3B", "white"
    statusbar["bg"],statusbar["fg"] = "#3B3B3B", "white"

def open_help():
    subprocess.Popen(["notepad.exe", "README.md"])
    
    
menubar = tk.Menu(window)

selectFolderMenu = tk.Menu(menubar,tearoff=0)
colorThemeMenu = tk.Menu(menubar,tearoff=0)

fileMenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=fileMenu)
fileMenu.add_cascade(label="Select Data Path", menu=selectFolderMenu)
fileMenu.add_cascade(label="Color Theme", menu=colorThemeMenu)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=window.quit)

selectFolderMenu.add_command(label="Input Data Folder",command=lambda:input_data(button=True))
selectFolderMenu.add_command(label="Output Data Folder",command=lambda:output_data(button=True))
selectFolderMenu.add_command(label="Sample Sheet File",command=lambda:read_samplesheet_file(button=True))

colorThemeMenu.add_command(label="Light",command=lambda:light_mode())
colorThemeMenu.add_command(label="Dark",command=lambda:dark_mode())

editmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda:window.focus_get().event_generate('<<Cut>>'))
editmenu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda:window.focus_get().event_generate('<<Copy>>'))
editmenu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda:window.focus_get().event_generate('<<Paste>>'))


helpmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="User Manual",command=lambda:open_help())


window.config(menu=menubar)

lightbackgroundImage = tk.PhotoImage(file = "LightBackground.png")
darkbackgroundImage = tk.PhotoImage(file = "DarkBackground.png")
  
# Set background image
backgroundLabel = Label(window, image = lightbackgroundImage)
backgroundLabel.place(x = 0, y = 0)

# Insert image in window
image = Image.open("Image.png")
image = image.resize((400, 100), Image.ANTIALIAS)
label_image = ImageTk.PhotoImage(image)

Imagelabel = tk.Label(image=label_image,bg="white")
Imagelabel.image = label_image
Imagelabel.place(x=(width/2)-200, y=20)
  
inputLabel = tk.Label(window, text="Input Data Path",font=('Verdana',14),bg="white")
inputLabel.place(x=30, y=160)  

#Entry box for input folder path
inputDataPath = tk.Entry(highlightthickness=2,borderwidth=0,highlightcolor= "#2696FF",highlightbackground="#D1D1D1",font=('Verdana',14))
inputDataPath.place(x=30, y=200,width=700, height=30)
changeOnHover(inputDataPath, "#696A6B", "#D1D1D1", False)
inputDataPath.bind("<Return>",func=lambda e: input_data(button=False))

#Browse button for input folder path
input_button = tk.Button(window,text='...',bg="white",command=lambda:input_data(button=True))
input_button.place(x=740, y=200,width = 30, height = 30)
#changeOnHover(input_button, "#D9F2FF", "white", True)

filenameselectionLabel = tk.Label(window, text="Select Folders to Remove from List",font=('Verdana',14),bg="white")
filenameselectionLabel.place(x=30, y=260) 

listboxFrame = tk.Frame(window,bg="white")
listboxFrame.place(x=380,y=260)

scrollbar = Scrollbar(listboxFrame)
scrollbar.pack(side = RIGHT, fill = BOTH)

#Listbox for selection of folders to remove from list of folders to be processed
filename_selection = tk.Listbox(listboxFrame, selectmode=tk.MULTIPLE, height=4,width=29,font=('Verdana',14),highlightcolor="#2696FF",selectbackground="#2696FF", yscrollcommand = scrollbar.set)
filename_selection.pack()

scrollbar.config(command = filename_selection.yview)

select_button = tk.Button(window, text='Select All', font=('Verdana',12), bg="white", command=lambda:select_all())
select_button.place(x=30,y=310)
#changeOnHover(select_button, "#D9F2FF", "white", True)

deselect_button = tk.Button(window, text='Deselect All', font=('Verdana',12), bg="white", command=lambda:deselect_all())
deselect_button.place(x=150,y=310)
#changeOnHover(deselect_button, "#D9F2FF", "white", True)

outputLabel = tk.Label(window, text="Output Data Path",font=('Verdana',14),bg="white")
outputLabel.place(x=30, y=380)

#Entry box for output folder path
outputDataPath = tk.Entry(highlightthickness=2,borderwidth=0,highlightcolor= "#2696FF",highlightbackground="#D1D1D1",font=('Verdana',14))
outputDataPath.place(x=30, y=420, width=700, height=30)
changeOnHover(outputDataPath, "#696A6B", "#D1D1D1", False)
outputDataPath.bind("<Return>",func=lambda e: output_data(button=False))

#Browse button for output folder path
output_button = tk.Button(window,text='...',bg="white",command=lambda:output_data(button=True))
output_button.place(x=740, y=420, width = 30, height = 30)
#changeOnHover(output_button, "#D9F2FF", "white", True)

barcodeLabel = tk.Label(window, text="Sample Sheet (CSV)",font=('Verdana',14),bg="white")
barcodeLabel.place(x=30, y=480)

#Entry box for sample sheet file path
barcodePath = tk.Entry(highlightthickness=2,borderwidth=0,highlightcolor= "#2696FF",highlightbackground="#D1D1D1",font=('Verdana',14))
barcodePath.place(x=30, y=520, width=700, height=30)
changeOnHover(barcodePath, "#696A6B", "#D1D1D1", False)
barcodePath.bind("<Return>",func=lambda e: read_samplesheet_file(button=False))

#Browse button for sample sheet file path
barcode_button = tk.Button(window,text='...',bg="white",command=lambda:read_samplesheet_file(button=True))
barcode_button.place(x=740, y=520, width = 30, height = 30)
#changeOnHover(barcode_button, "#D9F2FF", "white", True)

threadLabel = tk.Label(window, text="Threads",font=('Verdana',14),bg="white")
threadLabel.place(x=30, y=580)

#Entry box for number of threads
thread_entry = tk.Entry(highlightthickness=2,borderwidth=0,highlightcolor= "#2696FF",highlightbackground="#D1D1D1",font=('Verdana',14))
thread_entry.place(x=30, y=620,width=700, height=30)
changeOnHover(thread_entry, "#696A6B", "#D1D1D1", False)

pipelineLabel = tk.Label(window, text="Pipeline",font=('Verdana',14),bg="white")
pipelineLabel.place(x=30, y=680)

#Radiobuttons to select desired pipeline
pipelineVar = tk.IntVar()
nanopolishButton = tk.Radiobutton(window, text="", variable=pipelineVar, value=1, font=('Verdana',14), bg="white", fg="#2696FF")
nanopolishButton.place(x=40, y=720)

nanopolishLabel = tk.Label(window, text="Nanopolish",font=('Verdana',14),bg="white")
nanopolishLabel.place(x=70, y=720)

medakaButton = tk.Radiobutton(window, text="", variable=pipelineVar, value=2, font=('Verdana',14), bg="white", fg="#2696FF")
medakaButton.place(x=210, y=720)

medakaLabel = tk.Label(window, text="Medaka",font=('Verdana',14),bg="white")
medakaLabel.place(x=240, y=720)

# Run button
run_button = tk.Button(window,text='Run',font=('Verdana',14),command=lambda:threading.Thread(target=run).start(),bg="white")
run_button.place(x=600, y=750, width = 100, height = 50)
#changeOnHover(run_button, "#D9F2FF", "white", True)


# Status bar
statusText = tk.StringVar()
statusText.set("")
statusbar = tk.Label(window, textvariable=statusText, bd=1, relief=tk.SUNKEN, anchor=tk.W,bg="white")
statusbar.pack(side=tk.BOTTOM, fill=tk.X)


window.mainloop()