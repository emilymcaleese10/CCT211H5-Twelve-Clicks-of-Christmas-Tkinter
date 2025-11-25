# CCT211H5-Twelve-Clicks-of-Christmas-Tkinter

Twelve Clicks of Christmas is a Tkinter-based interactive advent calendar that combines creativity,
nostalgia, and personalization. The application allows users to design their own digital calendar by adding
messages, images, and captions behind twelve themed windows / doors.

# 🛠️ How to run the program

To make your calendar, open the project folder containing `main.py`.

## 1. Creating and Editing Your Calendar (The Editor)

The `main.py` file is the **Editing file**, used to customize the calendar's messages and images.

### A. Launching the Editor

1.  **Open a Terminal/Command Prompt** and navigate to the project directory.
2.  Run the main program:
    ```bash
    python main.py
    ```

### B. Editing Calendar

1.  The program will first ask: **"WHO IS YOUR ADVENT CALENDAR FOR?"**
2.  Enter the recipient's name (e.g., "Sarah") and click **SAVE**. This name will appear on the calendar viewer.

3.  After saving the name, you will see the **Edit Calendar** page with **12 doors** (representing December 13th through 24th).
2.  **Click on any door** (e.g., DOOR 5) to open the editor for that day.
3.  In the **Door Editor** screen you can add messages and images.
4.  Click **SAVE** at the bottom to store the message and image path in the database. You will then return to the main doors page.

## 2. Exporting the Calendar (Creating the Gift)

Once you are done setting up all 12 doors, you need to **Export** the calendar.

1.  On the **Edit Calendar** page, click the **Export** button in the top-left corner.
2.  The program will create a new, timestamped folder (e.g., `12 Clicks Export 24_11_2025 - 13_30_00`) in your chosen location.
3.  The program will attempt to use PyInstaller to create a standalone executable (`RUN.exe` or `RUN.app`), but will also provide batch/shell scripts (`windows.bat` or `mac.sh`) for direct running.

## 3. Running the Calendar (The Viewer)

The recipient uses the `RUN.exe` or `RUN.app` file to open the calendar.

1.  The recipient should open the **exported calendar folder**.
2.  They should run the calendar using one of the following methods:
    * **If a standalone executable was built:** Run `RUN.exe` (Windows) or `RUN.app` (macOS).
    * **If not, or if using a script:** Double-click `windows.bat` (Windows) or run `mac.sh` (macOS/Linux) in the terminal.
    * **Direct Python run:** If they have Python installed, they can run `python viewer.py`.
3.  The **Viewer App** will open, greeting the recipient by name.
4.  Click **OPEN** to see the 12 doors.
5.  **Opening a Door:**
    * If the current system date is **on or after** the unlock date (Dec 13th for Door 1, Dec 24th for Door 12), they can click the door to see your message and image.
    * If the date is too early, they will receive a message saying **"Not available! Come back later on door's date."**

# This project fulfills all project requirements:
● Multiple Windows: The program will include separate windows for editing, viewing, and analytics
(e.g., EditorApp, ViewerApp, AnalyticsWindow).
● Multiple Classes: The codebase will be object-oriented, with distinct classes such as App, Door,
SqliteRepo, EditorWindow, and ViewerWindow.
● Data Entry: The editor interface allows users to input and modify messages, images, captions, and
unlock dates for each day.
● Persistence: All data (messages, media paths, captions, unlock dates) will be stored in a local SQLite
database, ensuring that content remains available between sessions.
● Interactivity: Each “door” will open with a click, revealing daily surprises that are date-locked to
their assigned day, demonstrating logic-driven interactivity.
● Export System: The editor will include an Export Viewer function that packages the data and a
view-only interface for recipients to open their advent calendar in read-only mode.
