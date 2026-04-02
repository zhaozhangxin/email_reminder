"""
notify.py — General-purpose email notification tool

Usage 1: Call functions directly
    from notify import send, notify_done, notify_error, notify_progress

Usage 2: Send results (DataFrame / images / file attachments)
    from notify import send
    send("Results", body="Training done", dataframes={"Best config": df}, attachments=["result.png"])

Usage 3: Decorator (auto-send email when function finishes or crashes)
    from notify import on_finish

    @on_finish("Model training")
    def train():
        ...

Usage 4: Quick send from command line
    python notify.py "subject" "body"
"""

import os
import smtplib
import traceback
import functools
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

# ── Email Configuration ──────────────────────────────────────────────────────
_SMTP_HOST = 'smtp.gmail.com'
_SMTP_PORT = 465
_SENDER    = 'your-gmail@gmail.com'          # <-- Replace with your Gmail
_PASSWORD  = 'xxxx xxxx xxxx xxxx'           # <-- Replace with your 16-char App Password
_RECIPIENT = 'your-email@example.com'        # <-- Replace with where you want to receive


# ── Core Send Function ───────────────────────────────────────────────────────
def send(subject: str,
         body: str = '',
         dataframes: dict = None,
         attachments: list = None,
         silent: bool = False) -> bool:
    """
    Send an email with optional DataFrame tables and file attachments.

    Args:
        subject:     Email subject line
        body:        Plain text body
        dataframes:  dict[title, pd.DataFrame], embedded as HTML tables
                     e.g. {"Best results": df1, "All trials": df2}
        attachments: List of file paths to attach
                     e.g. ["result.csv", "plot.png"]
        silent:      If True, print warning on failure instead of raising
    """
    msg = MIMEMultipart('mixed')
    msg['From']    = _SENDER
    msg['To']      = _RECIPIENT
    msg['Subject'] = subject

    # ── Body: plain text + DataFrame HTML tables ─────────────────────────────
    html_parts = []
    if body:
        html_parts.append(f'<pre style="font-family:monospace">{body}</pre>')

    if dataframes:
        for title, df in dataframes.items():
            try:
                table_html = df.to_html(
                    border=1, index=True, float_format=lambda x: f'{x:.4f}',
                    classes='dataframe',
                )
                html_parts.append(
                    f'<h3 style="font-family:sans-serif">{title}</h3>'
                    f'<style>.dataframe {{border-collapse:collapse; font-size:13px}}'
                    f'.dataframe td, .dataframe th {{padding:4px 8px; border:1px solid #ccc}}'
                    f'.dataframe tr:nth-child(even) {{background:#f5f5f5}}</style>'
                    f'{table_html}'
                )
            except Exception as e:
                html_parts.append(f'<p>[Table "{title}" render failed: {e}]</p>')

    html_body = '<html><body>' + '\n'.join(html_parts) + '</body></html>'
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # ── Attachments ──────────────────────────────────────────────────────────
    for path in (attachments or []):
        if not os.path.exists(path):
            print(f'[notify] Warning: attachment not found, skipping: {path}')
            continue
        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].lower()
        try:
            if ext in ('.png', '.jpg', '.jpeg', '.gif'):
                with open(path, 'rb') as f:
                    part = MIMEImage(f.read())
                part.add_header('Content-Disposition', 'attachment', filename=filename)
            else:
                with open(path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(part)
        except Exception as e:
            print(f'[notify] Warning: failed to process attachment "{filename}": {e}')

    # ── Send ─────────────────────────────────────────────────────────────────
    try:
        with smtplib.SMTP_SSL(_SMTP_HOST, _SMTP_PORT) as server:
            server.login(_SENDER, _PASSWORD)
            server.sendmail(_SENDER, _RECIPIENT, msg.as_string())
        print(f'[notify] Email sent: {subject}')
        return True
    except Exception as e:
        errmsg = f'[notify] Failed to send email: {e}'
        if silent:
            print(errmsg)
            return False
        raise


# ── Shortcut Functions ───────────────────────────────────────────────────────
def notify_done(task: str, details: str = '', silent: bool = True) -> bool:
    """Send a task completion notification."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'[Done] {task} — {now}'
    body = f'{task} completed\nTime: {now}\n\n{details}' if details else f'{task} completed\nTime: {now}'
    return send(subject, body, silent=silent)


def notify_error(task: str, error: Exception = None, details: str = '',
                 silent: bool = True) -> bool:
    """Send an error/crash notification with traceback."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'[Error] {task} — {now}'
    tb = traceback.format_exc() if error is not None else ''
    body = '\n\n'.join(filter(None, [
        f'{task} encountered an error\nTime: {now}',
        details,
        f'Exception:\n{tb}' if tb and tb.strip() != 'NoneType: None' else '',
    ]))
    return send(subject, body, silent=silent)


def notify_progress(task: str, message: str, silent: bool = True) -> bool:
    """Send a progress update."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'[Progress] {task} — {now}'
    return send(subject, f'{message}\n\nTime: {now}', silent=silent)


# ── Decorator ────────────────────────────────────────────────────────────────
def on_finish(task: str, notify_on_error: bool = True, notify_on_success: bool = True,
              silent: bool = True):
    """
    Decorator: sends a "done" email when the function finishes normally,
    or an "error" email if it raises an exception (and re-raises it).

    Example:
        @on_finish("Model training")
        def train():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = datetime.now()
            try:
                result = func(*args, **kwargs)
                if notify_on_success:
                    elapsed = (datetime.now() - start).total_seconds()
                    notify_done(task, f'Elapsed: {elapsed:.1f}s', silent=silent)
                return result
            except Exception as e:
                if notify_on_error:
                    notify_error(task, e, silent=silent)
                raise
        return wrapper
    return decorator


# ── Command Line Entry ───────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python notify.py "subject" ["body"]')
        sys.exit(1)
    subject = sys.argv[1]
    body    = sys.argv[2] if len(sys.argv) > 2 else ''
    send(subject, body)
