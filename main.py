from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageFont, ImageDraw

# To fix a warning in the App's resize method
if not hasattr(Image, 'Resampling'):  # Pillow<9.0
    Image.Resampling = Image


class App(Tk):

    def __init__(self):
        # Initialize parent class and create a window
        super().__init__()
        # Specify window's title
        self.title("Image Watermarking App")
        # Assign weight to the first column, so it would take the whole of the available space
        self.columnconfigure(0, weight=1)
        # Do the same for the first row
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)

        # Get user's screen size and scale it down
        self.panel_height = 0
        self.screen_width = self.winfo_screenwidth() // 2
        self.screen_height = self.winfo_screenheight() // 2

        # Create fixed initial geometry of the window
        self.geometry(f'{self.screen_width}x{self.screen_height}')
        self.resizable(False, False)

        # Create a frame in which all the subsequent widgets will be stored
        self.frame = ttk.Frame(self)
        # Place self.frame on the grid
        self.frame.grid()

        # Create a canvas widget to show image
        self.image_canvas = Canvas(self.frame, highlightthickness=0, bd=0,
                                   height=self.screen_height, width=self.screen_width)
        # Place freshly created Canvas on the grid
        self.image_canvas.grid(row=0)

        # Create a button widget that will launch a file dialog
        self.open_image_button = Button(self.image_canvas, text="Choose an image", command=self.open_image)
        # Create a window inside the Image canvas to temporarily store the Open Image-button in it
        self.image_canvas.create_window(self.screen_width/2, self.screen_height/2, anchor="center",
                                        window=self.open_image_button, tags="BTN")

        # Create a panel to place all the editing widgets in it, increase border distance
        self.panel = PanedWindow(self.frame, bd=5)

        # Label for watermark text's entry field
        self.text_label = Label(self.panel, text="Watermark text: ")
        self.panel.add(self.text_label)

        # Entry field for watermark text
        self.text_entry = Entry(self.panel)
        self.text_entry.insert(0, 'Watermark')
        self.panel.add(self.text_entry)

        # Label for font size's entry field
        self.font_label = Label(self.panel, text="Font size: ")
        self.panel.add(self.font_label)

        # Entry field for font size
        self.font_entry = Entry(self.panel, width=4)
        self.font_entry.insert(0, "50")
        self.panel.add(self.font_entry)

        self.color_picker = Button(self.panel, text="Color picker", command=self.choose_color)
        self.panel.add(self.color_picker)

        self.save_button = Button(self.panel, text="Save", width=20, command=lambda: self.edit_image(save=True))
        self.panel.add(self.save_button)

        # Create placeholders for images
        # Original size
        self.original = None
        # Image to display in the Canvas
        self.image = None
        # Resized version of the original image (the one for editing)
        self.resized = None

        self.rgb_color = (255, 255, 255)

        # Watermark font size
        self.font_size = 50

        # Coordinates for watermark placement
        self.x = self.screen_width // 2
        self.y = self.screen_height // 2

    def open_image(self):
        # Specify allowed filetypes
        filetypes = (
            ('image files', '*.jpg'),
            # ('All files', '*.*')
        )

        # Open file dialog
        file_path = fd.askopenfilename(title='Open a file', filetypes=filetypes)

        # Delete the Open Image-button from the Canvas
        self.image_canvas.delete("BTN")

        self.editing_panel()

        # Pass the file_path and open the image
        self.original = Image.open(file_path)

        # Resize the image to fit the window
        self.resized = self.original.resize((self.screen_width, self.screen_height-self.panel_height),
                                            Image.Resampling.LANCZOS)

        # Convert original image to a PhotoImage object
        self.image = ImageTk.PhotoImage(self.resized)

        # Place the image inside the Canvas widget
        self.image_canvas.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")

    def editing_panel(self):
        self.panel.grid(row=1, sticky="w")
        # Update window to access the panel's actual size
        self.update()

        self.panel_height = self.panel.winfo_height()
        self.image_canvas.configure(height=self.screen_height - self.panel_height)

        # Update the image after every keystroke
        self.bind("<KeyPress>", self.edit_image)
        # Update the image once a mouse button's been released
        self.bind("<ButtonRelease>", self.edit_image)
        # Move watermark
        self.bind("<B1-Motion>", self.edit_image)

    def edit_image(self, event=None, save=False):
        # Get watermark's current coordinates if not currently saving
        if event:
            self.x = event.x
            self.y = event.y

        # Get resized copy for further editing
        self.image = self.resized.copy()

        # Make sure that font size type is an integer
        try:
            self.font_size = int(self.font_entry.get())
        except ValueError:
            print("Wrong input")
        else:
            # Prevent extreme values from passing through
            if 1 <= int(self.font_entry.get()) <= 1000:
                self.font_size = int(self.font_entry.get())

        # Image is converted into editable form using
        # Draw function and assigned to draw
        draw = ImageDraw.Draw(self.image)

        # ("font type",font size)
        font = ImageFont.truetype("DroidSans.ttf", self.font_size)

        # Decide the text location, color and font
        draw.text((self.x, self.y), self.text_entry.get(), self.rgb_color, font=font)

        if save:
            self.image.save("watermarked.jpg")

        self.image = ImageTk.PhotoImage(self.image)

        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")

    # Color Picker
    def choose_color(self):

        # Save RGB value
        self.rgb_color = colorchooser.askcolor(title="Choose color")[0]


if __name__ == "__main__":
    app = App()
    app.mainloop()
