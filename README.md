# CCT211H5-Twelve-Clicks-of-Christmas-Tkinter

Twelve Clicks of Christmas is a Tkinter-based interactive advent calendar that combines creativity,
nostalgia, and personalization. The application allows users to design their own digital calendar by adding
messages, images, and captions behind twelve themed windows / doors. Each door opens with a simple
click, revealing surprises that can only be unlocked on a specific date, storing personalized content
persistently in an SQLite database. Once complete, users can export a viewer-only version to share with
others, perfect for a warm, customizable holiday gift. The project emphasizes user-friendly design, data
persistence, and creative engagement through an intuitive, multi-window Python interface.


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

This approach guarantees alignment with the Tkinter GUI and CRUD persistence requirements while
showcasing strong software organization and usability.
