from MainFrame.Resources.lib import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class graphLoader:
    def __init__(self, canvas):
        self.canvas = canvas

    def plot_pie_chart(self):
        labels = ['Active', 'Resigned']
        sizes = [60, 40]
        colors = ['lightgreen', 'lightcoral']
        explode = (0.1, 0)

        self.canvas.axes.pie(sizes, explode=explode, labels=labels, colors=colors,
                             autopct='%1.1f%%', shadow=True, startangle=140)
        self.canvas.axes.axis('equal')

        self.canvas.axes.set_facecolor('none')
        self.canvas.figure.patch.set_alpha(0)
        self.canvas.setStyleSheet("background-color: transparent;")
        self.canvas.draw()