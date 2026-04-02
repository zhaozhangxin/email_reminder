"""
easy_notify.py — Simple email notification tool (beginner-friendly)

======== How to Use ========

1. Send a simple email:
    email("Training done!")

2. With body text:
    email("Training done", "Accuracy 95%, took 3 hours")

3. With file attachments (images, CSV, etc.):
    email("Results ready", attachments=["result.png", "data.csv"])

4. Auto-notify when a function finishes or crashes (just add @auto_notify):
    @auto_notify("Model training")
    def train():
        ...

5. Send from command line:
    python easy_notify.py "subject" "body"
"""

from notify import send, notify_done, notify_error, on_finish


# ===================================================================
#  One function does it all: email(...)
# ===================================================================

def email(subject, body="", attachments=None, dataframes=None):
    """
    Send an email. That's it.

    Args:
        subject     -- Email title, e.g. "Training done"
        body        -- Email content (optional), e.g. "Accuracy 95%"
        attachments -- List of files to attach (optional), e.g. ["result.png"]
        dataframes  -- Dict of DataFrames (optional), e.g. {"Results": df}

    Returns:
        True = sent successfully, False = failed

    Examples:
        email("Training done")
        email("Training done", "Accuracy 95%")
        email("Results", attachments=["plot.png"])
        email("Results", dataframes={"Best config": df})
    """
    return send(subject, body=body, attachments=attachments,
                dataframes=dataframes, silent=True)


# ===================================================================
#  Decorator: @auto_notify("task name")
# ===================================================================

def auto_notify(task_name):
    """
    Put this above a function. It sends a "done" email when the function
    finishes, or an "error" email if it crashes (and re-raises the error).

    Usage:
        @auto_notify("Model training")
        def train():
            ...   # Finishes normally -> you get a "done" email
                  # Crashes          -> you get an "error" email
    """
    return on_finish(task_name)


# ===================================================================
#  Shortcut functions
# ===================================================================

def done(task_name, details=""):
    """Send a "task done" notification. e.g. done("Data cleaning")"""
    return notify_done(task_name, details=details)


def error(task_name, err=None, details=""):
    """Send a "task error" notification. e.g. error("Data cleaning", e)"""
    return notify_error(task_name, error=err, details=details)


# ===================================================================
#  Command line: python easy_notify.py "subject" "body"
# ===================================================================

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("""
+--------------------------------------------+
|     easy_notify -- Simple Email Notifier    |
+--------------------------------------------+
|                                             |
|  Command line:                              |
|    python easy_notify.py "subject"          |
|    python easy_notify.py "subject" "body"   |
|                                             |
|  In Python code:                            |
|    from easy_notify import email            |
|    email("Training done")                   |
|    email("Training done", "Accuracy 95%")   |
|    email("Results", attachments=["a.png"])  |
|                                             |
+--------------------------------------------+
""")
        sys.exit(0)

    subj = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else ""
    if email(subj, text):
        print("Sent successfully!")
    else:
        print("Failed to send. Check your network or email config.")
