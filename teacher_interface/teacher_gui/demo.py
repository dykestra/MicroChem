""" Demo simple script to spin up a GUI instance """

from ttkthemes import themed_tk as tk
from TeacherInterfaceGUI import *

root = tk.ThemedTk()
gui = TeacherInterfaceGUI(root)
root.mainloop()