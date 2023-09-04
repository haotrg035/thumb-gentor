import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
import shutil
import threading

# Function to convert an image to RGB mode
def convert_to_rgb(input_path, output_path):
    with Image.open(input_path) as img:
        rgb_img = img.convert('RGB')
        rgb_img.save(output_path, 'JPEG')

# Function to generate thumbnail images
def generate_thumbnail(input_path, output_path, size=(200, 200), quality=85, prefix='', suffix=''):
    try:
        with Image.open(input_path) as img:
            img.thumbnail(size)
            
            # Modify the output file name with prefix and suffix
            base_name, ext = os.path.splitext(os.path.basename(output_path))
            output_path = os.path.join(os.path.dirname(output_path), f"{prefix}{base_name}{suffix}{ext}")
            
            img.save(output_path, 'JPEG', quality=quality)
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# Function to process a directory and its subdirectories
def process_directory(directory, thumb_dir_name, size, quality, prefix, suffix, clear_existing, progress_var, progress_label):
    total_files = 0
    processed_files = 0
    
    for root, _, files in os.walk(directory):
        # Skip the _thumb directory
        if os.path.basename(root) == thumb_dir_name:
            continue
        thumb_dir = os.path.join(root, thumb_dir_name)
        # Clear the existing _thumb folder
        if os.path.exists(thumb_dir) and clear_existing == 1:
            shutil.rmtree(thumb_dir)
        os.makedirs(thumb_dir, exist_ok=True)
        
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                total_files += 1
                input_path = os.path.join(root, file)
                # Check if the image is in RGBA mode
                with Image.open(input_path) as img:
                    if img.mode == 'RGBA':
                        # Convert RGBA to RGB and save it
                        rgb_path = os.path.join(root, f"{os.path.splitext(file)[0]}_rgb.jpg")
                        convert_to_rgb(input_path, rgb_path)
                        # Generate the thumbnail image from the RGB version
                        thumbnail_path = os.path.join(thumb_dir, f"{os.path.splitext(file)[0]}.jpg")
                        generate_thumbnail(rgb_path, thumbnail_path, size, quality, prefix, suffix)
                        # Delete the temporary RGB file
                        os.remove(rgb_path)
                    elif img.mode == 'P':
                        rgb_path = os.path.join(root, f"{os.path.splitext(file)[0]}_rgb.jpg")
                        convert_to_rgb(input_path, rgb_path)
                        thumbnail_path = os.path.join(thumb_dir, f"{os.path.splitext(file)[0]}.jpg")
                        generate_thumbnail(rgb_path, thumbnail_path, size, quality, prefix, suffix)
                        os.remove(rgb_path)
                    else:
                        # Generate the thumbnail image
                        thumbnail_path = os.path.join(thumb_dir, f"{os.path.splitext(file)[0]}.jpg")
                        generate_thumbnail(input_path, thumbnail_path, size, quality, prefix, suffix)
                processed_files += 1
                progress_value = int(processed_files / total_files * 100)
                progress_var.set(progress_value)
                progress_label.config(text=f"Thumbnails Processed: {processed_files}/{total_files}")

# Function to validate numeric input
def validate_numeric_input(P):
    if P == "":
        return True
    try:
        float(P)
        return True
    except ValueError:
        return False

# Function to start generating thumbnails
def start_thumbnail_generation():
    directory = selected_directory.get()
    width = entry_width.get()
    height = entry_height.get()
    quality = entry_quality.get()
    prefix = entry_prefix.get()
    suffix = entry_suffix.get()
    clear_existing = clear_existing_var.get()
    str_thumb_dir_name = entry_thumb_dir_name.get()
    
    # Check if any of the input fields are empty
    if not directory or not width or not height or not quality:
        messagebox.showerror("Error", "Please fill in all input fields.")
        return
    
    # Check if the entered directory exists
    if not os.path.exists(directory):
        messagebox.showerror("Error", "The selected directory does not exist.")
        return

    thumbnail_size = (int(width), int(height))
    thumbnail_quality = int(quality)
    
    progress_var.set(0)
    processing_thread = threading.Thread(target=process_directory, args=(directory, str_thumb_dir_name, thumbnail_size, thumbnail_quality, prefix, suffix, clear_existing, progress_var, progress_label))
    processing_thread.start()

    def check_progress():
        if processing_thread.is_alive():
            root.after(100, check_progress)
        else:
            messagebox.showinfo("Complete", "Thumbnail generation complete.")
    
    root.after(100, check_progress)

# Create a Tkinter root window
root = tk.Tk()
root.title("Thumb Gentor")
root.geometry("370x460")
root.resizable(False, False)  # Make the window not resizable

# Frame for directory selection
frame_directory = ttk.Frame(root)
frame_directory.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

label_directory = ttk.Label(frame_directory, text="Select a directory:")
label_directory.grid(row=0, column=0, sticky=tk.W, columnspan=2)

selected_directory = tk.StringVar()
entry_directory = ttk.Entry(frame_directory, textvariable=selected_directory,width=200)
entry_directory.grid(row=1, column=1, padx=5, pady=0, sticky=tk.W)

def browse_directory():
    directory = filedialog.askdirectory(title="Select a directory containing images")
    if directory:
        selected_directory.set(directory)

button_browse = ttk.Button(frame_directory, text="Browse", command=browse_directory)
button_browse.grid(row=1, column=0, padx=0, pady=5)

# Frame for thumbnail settings
frame_settings = ttk.Frame(root)
frame_settings.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Entry fields for thumbnail dir name
label_thumb_dir = ttk.Label(frame_settings, text="Thumbnail folder:")
label_thumb_dir.grid(row=2, column=0, sticky=tk.W)
entry_thumb_dir_name = ttk.Entry(frame_settings)
entry_thumb_dir_name.grid(row=2, column=1, padx=15, pady=5)
entry_thumb_dir_name.insert(0, "_thumb")
# Checkbox to clear existing _thumb directories
clear_existing_var = tk.IntVar()
clear_existing_var.set(1)
clear_existing_checkbox = ttk.Checkbutton(frame_settings, text="Clear Existing Thumbnail Directories", variable=clear_existing_var)
clear_existing_checkbox.grid(row=3, column=0, padx=0, pady=5)

# Entry fields for prefix and suffix
label_prefix = ttk.Label(frame_settings, text="File prefix:")
label_prefix.grid(row=4, column=0, sticky=tk.W)
entry_prefix = ttk.Entry(frame_settings)
entry_prefix.grid(row=4, column=1, padx=15, pady=5)

label_suffix = ttk.Label(frame_settings, text="File suffix:")
label_suffix.grid(row=5, column=0, sticky=tk.W)
entry_suffix = ttk.Entry(frame_settings)
entry_suffix.grid(row=5, column=1, padx=15, pady=5)

# Entry validation for numeric input
validate_numeric = root.register(validate_numeric_input)
entry_width = ttk.Entry(frame_settings, validate="key", validatecommand=(validate_numeric, "%P"))
entry_height = ttk.Entry(frame_settings, validate="key", validatecommand=(validate_numeric, "%P"))
entry_quality = ttk.Entry(frame_settings, validate="key", validatecommand=(validate_numeric, "%P"))

label_width = ttk.Label(frame_settings, text="Width (px):")
label_width.grid(row=8, column=0, sticky=tk.W)

entry_width = ttk.Entry(frame_settings)
entry_width.grid(row=8, column=1, padx=15, pady=5)

label_height = ttk.Label(frame_settings, text="Height (px):")
label_height.grid(row=9, column=0, sticky=tk.W)

entry_height = ttk.Entry(frame_settings)
entry_height.grid(row=9, column=1, padx=15, pady=5)

label_quality = ttk.Label(frame_settings, text="Quality (%):")
label_quality.grid(row=10, column=0, sticky=tk.W)

entry_quality = ttk.Entry(frame_settings)
entry_quality.grid(row=10, column=1, padx=15, pady=5)

# Set default values for width, height, and quality
entry_width.insert(0, "200")
entry_height.insert(0, "200")
entry_quality.insert(0, "85")

# Progress bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=10, pady=10)

# Frame for buttons
frame_buttons = ttk.Frame(root)
frame_buttons.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

button_generate = ttk.Button(frame_buttons, text="Generate!", command=start_thumbnail_generation)
button_generate.pack(pady=5)

# Progress bar label
progress_label = ttk.Label(frame_buttons, text="Images Processed: 0/0")
progress_label.pack(pady=5)

# Run the GUI main loop
root.mainloop()
