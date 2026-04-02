# easy_notify

Send yourself email notifications from Python in **one line of code**. Perfect for knowing when your training is done or your script crashes — without staring at the terminal.

```python
from easy_notify import email
email("Training done!", "Accuracy: 95.2%")
```

No complex setup. No extra libraries. Just Gmail + two Python files.

---

## Table of Contents

- [Step 1: Get a Gmail App Password](#step-1-get-a-gmail-app-password)
- [Step 2: Configure notify.py](#step-2-configure-notifypy)
- [Step 3: Test It](#step-3-test-it)
- [How to Add Email Notifications to Your Code](#how-to-add-email-notifications-to-your-code)
  - [The Easiest Way: Get Notified When Your Code Crashes](#the-easiest-way-get-notified-when-your-code-crashes)
  - [Send a Simple Email](#send-a-simple-email)
  - [Send with Attachments](#send-with-attachments)
  - [Send a DataFrame as a Table](#send-a-dataframe-as-a-table)
  - [Send from Command Line (No Coding)](#send-from-command-line-no-coding)
- [Copy-Paste Templates](#copy-paste-templates)
- [Troubleshooting](#troubleshooting)

---

## Step 1: Get a Gmail App Password

You need a **16-character App Password** from Gmail (not your regular Gmail password).

### 1.1 Turn on 2-Step Verification

1. Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Find **"2-Step Verification"** and click on it
3. Follow the prompts to turn it on (you'll need your phone)

> If 2-Step Verification is already on, skip to 1.2.

### 1.2 Generate an App Password

1. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. You may need to sign in again
3. Under **"App name"**, type anything (e.g. `notify`)
4. Click **"Create"**
5. Google will show a **16-character password** like `abcd efgh ijkl mnop`
6. **Copy it and save it somewhere** — you won't be able to see it again

---

## Step 2: Configure notify.py

Open `notify.py` and edit the configuration section at the top (around line 34). You only need to change **3 lines**:

```python
_SMTP_HOST = 'smtp.gmail.com'
_SMTP_PORT = 465
_SENDER    = 'your-gmail@gmail.com'        # <-- Your Gmail address
_PASSWORD  = 'abcd efgh ijkl mnop'         # <-- The 16-char App Password from Step 1
_RECIPIENT = 'whoever-you-want@email.com'  # <-- Where to receive notifications
```

| Field | What to fill in |
|---|---|
| `_SENDER` | Your Gmail address |
| `_PASSWORD` | The 16-character App Password (spaces are fine) |
| `_RECIPIENT` | Where you want to receive notifications. Can be the same Gmail, or a different email (e.g. your school/work email) |

Save the file. **You never need to touch this again.**

---

## Step 3: Test It

Open a terminal and run:

```bash
python easy_notify.py "Test" "If you got this, it works!"
```

Check your inbox. If you see the email, everything is set up correctly.

---

## How to Add Email Notifications to Your Code

### The Easiest Way: Get Notified When Your Code Crashes

> **This is probably what you want.** You have a Python script that takes a long time to run. You want to walk away and get an email if it crashes — with the full error message.

**You only need to add 3 lines to your existing code.** Here's a before/after example:

#### Before (your original code):

```python
# my_script.py

import pandas as pd

data = pd.read_csv("big_dataset.csv")
results = some_long_computation(data)
results.to_csv("output.csv")
print("Done!")
```

#### After (with email notification):

```python
# my_script.py

import pandas as pd
from easy_notify import email          # <-- ADD THIS LINE (1/3)

try:                                   # <-- ADD THIS LINE (2/3)
    data = pd.read_csv("big_dataset.csv")
    results = some_long_computation(data)
    results.to_csv("output.csv")
    email("Script finished!", "Results saved to output.csv")

except Exception as e:                 # <-- ADD THIS LINE (3/3)
    email("Script CRASHED!", f"Error:\n{e}")
    raise                              # This re-raises the error so you can still see it in terminal
```

**What this does:**
- `try:` = "try running the code below"
- `except Exception as e:` = "if anything goes wrong, catch the error and call it `e`"
- `raise` = "after sending the email, still show the error in terminal as usual"

**That's it.** If your script crashes at 3 AM, you'll wake up to an email with the exact error message.

> **Important:** After adding `try:`, you need to **indent all your original code by 4 spaces** (select all, press Tab in most editors). The code under `try:` and `except` must be indented. This is how Python knows which code is "inside" the try block.

---

### A Simpler Alternative: `@auto_notify`

If the `try/except` approach feels complex, there's an even simpler way — but it requires your code to be inside a function. Just add **2 lines**:

```python
from easy_notify import auto_notify    # <-- ADD THIS

@auto_notify("My Script")             # <-- ADD THIS
def main():
    # All your existing code goes here (indented by 4 spaces)
    data = pd.read_csv("big_dataset.csv")
    results = some_long_computation(data)
    results.to_csv("output.csv")

main()                                 # <-- Call the function
```

**What this does:**
- `@auto_notify("My Script")` watches the function below it
- If the function finishes normally, you get a **"Done"** email
- If the function crashes, you get an **"Error"** email with the full error message
- Either way, you'll know what happened

---

### Send a Simple Email

```python
from easy_notify import email

# Just a subject
email("Training done!")

# Subject + body
email("Training done", "Final accuracy: 95.2%\nTotal epochs: 50")
```

### Send with Attachments

Attach any files — images, CSVs, PDFs, etc.

```python
email("Results ready",
      body="See attached plots and data",
      attachments=["loss_curve.png", "results.csv"])
```

### Send a DataFrame as a Table

If you use pandas, you can embed DataFrames directly in the email as nicely formatted tables:

```python
import pandas as pd

results = pd.DataFrame({
    "Model":    ["ResNet", "ViT", "MLP"],
    "Accuracy": [0.95, 0.93, 0.87],
    "Loss":     [0.12, 0.18, 0.35],
})

email("Experiment results",
      dataframes={"Model Comparison": results})
```

### Send from Command Line (No Coding)

You can send emails directly from the terminal without writing any Python:

```bash
# Subject only
python easy_notify.py "Job finished"

# Subject + body
python easy_notify.py "Job finished" "Processed 10,000 samples, no errors"
```

---

## Copy-Paste Templates

Pick the template that fits your situation. **Copy it, paste it into your script, and change the parts in `ALL_CAPS`.**

### Template 1: "Email me if my code crashes"

```python
from easy_notify import email

try:
    # =====================
    # YOUR CODE GOES HERE
    # (indent everything by 4 spaces)
    # =====================
    pass  # <-- delete this line and put your code here

    email("YOUR_TASK_NAME finished!", "Everything went well.")

except Exception as e:
    email("YOUR_TASK_NAME CRASHED!", f"Error:\n{e}")
    raise
```

### Template 2: "Email me when done, with results attached"

```python
from easy_notify import email

try:
    # YOUR CODE HERE
    pass

    email("YOUR_TASK_NAME finished!",
          body="See attached results",
          attachments=["YOUR_OUTPUT_FILE.csv", "YOUR_PLOT.png"])

except Exception as e:
    email("YOUR_TASK_NAME CRASHED!", f"Error:\n{e}")
    raise
```

### Template 3: "Just wrap my whole script with auto-notify"

```python
from easy_notify import auto_notify

@auto_notify("YOUR_TASK_NAME")
def main():
    # YOUR ENTIRE SCRIPT GOES HERE
    # (indent everything by 4 spaces)
    pass  # <-- delete this line and put your code here

main()
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `SMTPAuthenticationError` | Double-check your App Password. Make sure 2-Step Verification is ON. |
| `Connection timed out` | Your network may block port 465. Try a different network (e.g. home WiFi vs university). |
| `ModuleNotFoundError: No module named 'notify'` | Make sure `notify.py` and `easy_notify.py` are in the **same folder** as your script. |
| Email lands in spam | Open spam folder, find the email, click "Not Spam". Future emails will go to inbox. |
| `IndentationError` | All code inside `try:` and `except:` must be indented by 4 spaces. Select your code and press Tab. |
| `pandas` error with dataframes | Install pandas first: `pip install pandas`. Only needed if you use the `dataframes=` feature. |

---

## File Structure

```
your_project/
  notify.py          # Core engine (edit your email config here, Step 2)
  easy_notify.py     # Beginner-friendly interface (you use this in your code)
  your_script.py     # Your code that imports easy_notify
```

You only need `notify.py` + `easy_notify.py`. Copy them into any project folder and you're good to go.
