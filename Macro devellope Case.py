import time
import keyboard
from pynput.mouse import Button, Controller

# Initialize the mouse controller
mouse = Controller()

def on_triggered():
    # 1. Left click at the current cursor position
    for _ in range(50):
        mouse.click(Button.left, 1)
        time.sleep(0.2)
        
        # 2. Press Enter
        keyboard.send('enter')
        time.sleep(0.2)
        
        # 3. Press Right Arrow 3 times cleanly using a loop
        for _ in range(3):
            keyboard.send('right')
        
        # 4. Tap the Up Arrow key
        keyboard.send('up')
        time.sleep(0.1)
        

# Register F4 as the global macro trigger
keyboard.add_hotkey("f4", on_triggered)

print("=== Macro Active ===")
print("Press 'F4' to Click -> Enter -> Right x3 -> Up")
print("Press 'ESC' to exit the program...")

# Keep the script running in the background
keyboard.wait("esc")
