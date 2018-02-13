from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from tkcolorpicker import askcolor
from xml.etree.ElementTree import ElementTree, Element, SubElement
import numpy as np
import nbpsolver

def decrease():
    xmin, xmax, ymin, ymax = ax.axis()
    xmin, xmax, ymin, ymax = xmin / 1.5, xmax / 1.5, ymin / 1.5, ymax / 1.5
    ax.axis([xmin, xmax, ymin, ymax])
    canvas.show()


def increase():
    xmin, xmax, ymin, ymax = ax.axis()
    xmin, xmax, ymin, ymax = xmin * 1.5, xmax * 1.5, ymin * 1.5, ymax * 1.5
    ax.axis([xmin, xmax, ymin, ymax])
    canvas.show()


def set_color():
    global current_color
    x = askcolor(current_color, page1)[1]
    if x: current_color = x


def mouse_move(event):
    if not event.inaxes:
        return
    x, y = event.xdata, event.ydata
    label_x.config(text=" x = " + '{0:8.3f}'.format(x))
    label_y.config(text=" y = " + '{0:8.3f}'.format(y))


def update_entrysize(x):
    entry_size.delete(0, END)
    entry_size.insert(0, str(x))


def openXmlDialog():
    filename = filedialog.askopenfilename(initialdir=".", title="Select config file",
                                          filetypes=[("xml files", "*.xml"), ("all files", "*.*")])
    if filename is None or len(filename) == 0:
        return
    load_xml(filename)


def saveXmlDialog():
    filename = filedialog.asksaveasfilename(initialdir=".", title="Select config file to save",
                                            filetypes=[("xml files", "*.xml")],defaultextension='.xml')
    if filename is None or filename == '':
        return
    save_xml(filename)


def get_slider_size():
    return scale_size.get()


def get_color():
    return current_color


def add_object(x, y, size, color):
    circle = Circle((x, y), size, color=color)
    ax.add_artist(circle)
    canvas.show()
    circles.append({'x':x, 'y':y, 's':size, 'c':color})


def mouse_click(event):
    if not event.inaxes: return
    if event.button != 1: return
    x, y = event.xdata, event.ydata
    add_circle_on_mouse_click(x, y)


def add_circle_on_mouse_click(x, y):
    size = get_slider_size()
    color = get_color()
    add_object(x, y, size, color)


def set_working_area(xmin, xmax, ymin, ymax):
    ax.axis([xmin, xmax, ymin, ymax])
    canvas.show()


def load_xml(path):
    global current_color
    circles.clear()
    ax.cla()
    tree = ElementTree()
    tree.parse(path)
    root = tree.getroot()
    e = root.find('area')
    if e is not None:
        xmin = e.get('xmin')
        xmax = e.get('xmax')
        ymin = e.get('ymin')
        ymax = e.get('ymax')
        set_working_area(float(xmin), float(xmax), float(ymin), float(ymax))
    e = root.find('slider')
    if e is not None:
        value = e.get('value')
        scale_size.set(float(value))
    e = root.find('color')
    if e is not None:
        value = e.get('value')
        current_color = value
    elist = root.findall('items/item')
    if elist is not None:
        for e in elist:
            x = e.get('x')
            y = e.get('y')
            s = e.get('size')
            c = e.get('color')
            add_object(float(x), float(y), float(s), c)


def save_xml(path):
    root = Element('root')
    xmin, xmax, ymin, ymax = ax.axis()
    area = SubElement(root, 'area', xmin=str(xmin), xmax=str(xmax), ymin=str(ymin), ymax=str(ymax))
    slider = SubElement(root, 'slider', value=str(get_slider_size()))
    color = SubElement(root, 'color', value=str(get_color()))
    items = SubElement(root, 'items')
    for e in circles:
        item = SubElement(items, 'item', x=str(e['x']), y=str(e['y']), size=str(e['s']), color=str(e['c']))
    tree = ElementTree(root)
    tree.write(path, method='xml')

def exec_method():
    method = RB.get()
    eTime = time_size_v.get()
    nbpsolver.nbpsolver(method,circles,eTime)

if __name__ == '__main__':

    # ---------------------------------------------------------------------
    root = Tk()
    #root.geometry('1024x768')
    root.geometry('600x800')
    root.resizable(0, 0)
    # ---------------------------------------------------------------------
    current_color = '#FF0000'
    circles = []
    # ---------------------------------------------------------------------
    frame_top = Frame(root)

    nb = ttk.Notebook(frame_top)
    page1 = ttk.Frame(nb)
    page2 = ttk.Frame(nb)
    nb.add(page1, text='Edit')
    nb.add(page2, text='Model')

    # for x in range(2):
    #   Grid.columnconfigure(page1, x, weight=1)
    # for y in range(3):
    #   Grid.rowconfigure(page1, y, weight=1)

    label_x = Label(page1, text="",  relief="sunken", bg="white", anchor="w")
    label_y = Label(page1, text="",  relief="sunken", bg="white", anchor="w")
    label_x.grid(row=0, column=0, sticky=W+E)
    label_y.grid(row=1, column=0, sticky=W+E)

    button_color = Button(page1, text='Choose Color', command=set_color)
    button_color.grid(row=2, column=0, sticky=W+E+N+S)#, sticky=W+E+N+S)

    scale_size = Scale(page1, from_=1, to=100, orient=HORIZONTAL, resolution=0.1, relief='sunken', bg='white',
                       command=update_entrysize)
    scale_size.grid(row=0, column=1, rowspan=2, sticky=W+E)

    entrysize_v = DoubleVar()
    entry_size = Entry(page1, bg='white', textvariable=entrysize_v)
    entry_size.bind("<Return>", lambda event: scale_size.set(entrysize_v.get()))
    entry_size.grid(row=2, column=1, sticky=N+S)
    entry_size.insert(0, str(scale_size.get()))

    RB  = IntVar()
    RB1 = Radiobutton(page2, text="SciPy ODEINT", variable=RB, value=1).grid(row=0, column=0, sticky=W)
    RB2 = Radiobutton(page2, text="Verlet", variable=RB, value=2).grid(row=1, column=0, sticky=W)
    RB3 = Radiobutton(page2, text="Verlet+Multi Threading", variable=RB, value=3).grid(row=2, column=0, sticky=W)
    RB4 = Radiobutton(page2, text="Verlet+Multi Processing", variable=RB, value=4).grid(row=0, column=1, sticky=W, padx=20)
    RB5 = Radiobutton(page2, text="Verlet+OpenCL", variable=RB, value=5).grid(row=1, column=1, sticky=W, padx=20)
    RB6 = Radiobutton(page2, text="Verlet+Cython", variable=RB, value=6).grid(row=2, column=1, sticky=W, padx=20)
    RB.set(1)
    time_size_v = DoubleVar()
    time_size_v.set(1000)
    time_size = Entry(page2, bg='white', textvariable=time_size_v).grid(row=3, column=0, sticky=W, padx=5,pady=10)
    exec_button = Button(page2, text='Execute method', command=exec_method).grid(row=4, column=0, sticky=W, padx=5)

    Grid.rowconfigure(root, 0, weight=1)
    Grid.columnconfigure(root, 0, weight=1)
    frame_top.grid(row=0, column=0, sticky=W+E+N+S)

    Grid.rowconfigure(frame_top, 0, weight=1)
    Grid.columnconfigure(frame_top, 0, weight=1)
    #nb.pack(expand=1, fill='both')
    nb.grid(row=0, column=0, sticky=W+E+N+S)
    # ---------------------------------------------------------------------

    frame_bottom = Frame(root)
    button_decrease = Button(frame_bottom, text='-', command=decrease)
    #button_decrease.pack(side='left')
    button_decrease.grid(row=1, column=0, sticky=W+E+N+S)
    button_increase = Button(frame_bottom, text='+', command=increase)
    #button_increase.pack(side='left')
    button_increase.grid(row=1, column=1, sticky=W+E+N+S)

    fig = Figure()  # figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.axis([-100, 100, -100, 100])

    canvas = FigureCanvasTkAgg(fig, master=frame_bottom)
    canvas.show()
    #canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    Grid.rowconfigure(root, 1, weight=1)
    Grid.columnconfigure(root, 0, weight=1)
    frame_bottom.grid(row=1, column=0, sticky=W+E+N+S)

    Grid.rowconfigure(frame_bottom, 0, weight=1)
    Grid.columnconfigure(frame_bottom, 0, weight=1)
    Grid.rowconfigure(frame_bottom, 1, weight=1)
    Grid.columnconfigure(frame_bottom, 1, weight=1)
    Grid.rowconfigure(frame_bottom, 2, weight=1)
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, sticky=W+E+N+S)

    button_xml_load = Button(frame_bottom, text=" Load XML ", command=openXmlDialog)
    button_xml_load.grid(row=2, column=0, sticky=W+E+N+S)
    button_xml_save = Button(frame_bottom, text=" Save XML ", command=saveXmlDialog)
    button_xml_save.grid(row=2, column=1, sticky=W+E+N+S)

    # ---------------------------------------------------------------------

    canvas.mpl_connect('motion_notify_event', mouse_move)
    canvas.mpl_connect('button_press_event', mouse_click)
    root.mainloop()
