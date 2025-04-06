import tkinter as tk
from tkinter import simpledialog, filedialog
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

try:
    def get_graph_dimensions():
        root = tk.Tk()
        root.withdraw()
        xmin = simpledialog.askfloat("Input", "Enter minimum x value:", parent=root, minvalue=0, maxvalue=100, initialvalue=0)
        xmax = simpledialog.askfloat("Input", "Enter maximum x value:", parent=root, minvalue=xmin + 1, maxvalue=100, initialvalue=10)
        ymin = simpledialog.askfloat("Input", "Enter minimum y value:", parent=root, minvalue=0, maxvalue=100, initialvalue=0)
        ymax = simpledialog.askfloat("Input", "Enter maximum y value:", parent=root, minvalue=ymin + 1, maxvalue=100, initialvalue=10)
        return xmin, xmax, ymin, ymax

    def ask_for_image():
        root = tk.Tk()
        root.withdraw()
        use_image = simpledialog.askstring("Use Image", "Do you want to use an image for tracing? (yes/no)", parent=root)
        return (use_image.lower() == "yes") or (use_image.lower() == "y")

    xmin, xmax, ymin, ymax = get_graph_dimensions()
    use_image = ask_for_image()

    image_path = None
    if use_image:
        root = tk.Tk()
        root.withdraw()
        image_path = filedialog.askopenfilename(title="Select an Image File", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not image_path:
            print("No image selected. Exiting...")
            exit()
        img = Image.open(image_path)
        img = img.convert("RGBA")

    drawing = False
    points = []
    snap_to_grid = False

    def on_press(event):
        global drawing
        drawing = True

    def on_release(event):
        global drawing
        drawing = False

    def on_move(event):
        if drawing and event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            if snap_to_grid:
                x = round(x)
                y = round(y)
            points.append((x, y))
            ax.plot(x, y, 'bo', markersize=1)
            fig.canvas.draw()

    fig, ax = plt.subplots()
    ax.set_title("Draw a shape with the mouse. Close the window to calculate area.")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal')

    if use_image:
        ax.imshow(np.array(img), extent=[xmin, xmax, ymin, ymax], aspect='auto', alpha=0.5)

    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('button_release_event', on_release)
    fig.canvas.mpl_connect('motion_notify_event', on_move)

    plt.show()

    if np.linalg.norm(np.array(points[0]) - np.array(points[-1])) > 1e-2:
        points.append(points[0])

    points = np.array(points)
    x_vals = points[:, 0]
    y_vals = points[:, 1]

    def vertical_slice_area(x):
        intersections = []
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            if x1 == x2:
                continue
            if (x1 <= x <= x2) or (x2 <= x <= x1):
                t = (x - x1) / (x2 - x1)
                y = y1 + t * (y2 - y1)
                intersections.append(y)
        if len(intersections) < 2:
            return 0
        intersections.sort()
        return intersections[-1] - intersections[0]

    def integrate_area(fx, a, b, n=10000):
        h = (b - a) / n
        total = 0.5 * (fx(a) + fx(b))
        for i in range(1, n):
            x = a + i * h
            total += fx(x)
        return h * total

    area = integrate_area(vertical_slice_area, xmin, xmax)

    plt.figure()
    if use_image:
        plt.imshow(np.array(img), extent=[xmin, xmax, ymin, ymax], aspect='auto', alpha=0.5)
    plt.fill(points[:, 0], points[:, 1], alpha=0.3, color='orange')
    plt.plot(points[:, 0], points[:, 1], 'b-', linewidth=1)
    plt.title(f"Estimated Area: {area:.2f}")
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.axis('equal')
    plt.show()

except Exception as e:
    print(f"An error occurred: {str(e)}")
