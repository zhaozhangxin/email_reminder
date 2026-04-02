"""
notify.py — 通用邮件通知工具

用法一：直接调用函数
    from notify import send, notify_done, notify_error, notify_progress

用法二：发送结果（DataFrame / 图片 / 文件附件）
    from notify import send
    send("结果", body="训练完成", dataframes={"最优配置": df}, attachments=["result.png"])

用法三：装饰器（函数结束/报错时自动发邮件）
    from notify import on_finish

    @on_finish("模型训练")
    def train():
        ...

用法四：命令行快速发送
    python notify.py "主题" "正文"
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

# ── 邮箱配置 ──────────────────────────────────────────────────────────────────
_SMTP_HOST = 'smtp.gmail.com'
_SMTP_PORT = 465
_SENDER    = 'your-gmail@gmail.com'          # <-- Replace with your Gmail
_PASSWORD  = 'xxxx xxxx xxxx xxxx'           # <-- Replace with your 16-char App Password
_RECIPIENT = 'your-email@example.com'        # <-- Replace with where you want to receive


# ── 核心发送函数 ───────────────────────────────────────────────────────────────
def send(subject: str,
         body: str = '',
         dataframes: dict = None,
         attachments: list = None,
         silent: bool = False) -> bool:
    """
    发送邮件，支持 DataFrame 内嵌表格和文件附件。

    参数:
        subject:     邮件主题
        body:        正文（纯文本）
        dataframes:  dict[标题, pd.DataFrame]，以 HTML 表格嵌入正文
                     例: {"最优结果": df1, "所有试验": df2}
        attachments: 文件路径列表，作为附件发送
                     例: ["result.csv", "plot.png"]
        silent:      True 时发送失败不抛异常，只打印警告
    """
    msg = MIMEMultipart('mixed')
    msg['From']    = _SENDER
    msg['To']      = _RECIPIENT
    msg['Subject'] = subject

    # ── 正文：纯文本 + DataFrame HTML 表格 ────────────────────────────────────
    html_parts = []
    if body:
        # 纯文本转 HTML（保留换行）
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
                html_parts.append(f'<p>[表格 "{title}" 渲染失败: {e}]</p>')

    html_body = '<html><body>' + '\n'.join(html_parts) + '</body></html>'
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # ── 附件 ──────────────────────────────────────────────────────────────────
    for path in (attachments or []):
        if not os.path.exists(path):
            print(f'[notify] ⚠️ 附件不存在，跳过: {path}')
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
            print(f'[notify] ⚠️ 附件 "{filename}" 处理失败: {e}')

    # ── 发送 ──────────────────────────────────────────────────────────────────
    try:
        with smtplib.SMTP_SSL(_SMTP_HOST, _SMTP_PORT) as server:
            server.login(_SENDER, _PASSWORD)
            server.sendmail(_SENDER, _RECIPIENT, msg.as_string())
        print(f'[notify] ✅ 邮件已发送: {subject}')
        return True
    except Exception as e:
        errmsg = f'[notify] ⚠️ 邮件发送失败: {e}'
        if silent:
            print(errmsg)
            return False
        raise


# ── 常用快捷函数 ───────────────────────────────────────────────────────────────
def notify_done(task: str, details: str = '', silent: bool = True) -> bool:
    """任务完成通知。"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'[完成] {task} — {now}'
    body = f'{task} 已完成\n时间: {now}\n\n{details}' if details else f'{task} 已完成\n时间: {now}'
    return send(subject, body, silent=silent)


def notify_error(task: str, error: Exception = None, details: str = '',
                 silent: bool = True) -> bool:
    """错误/崩溃通知，自动附上 traceback。"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'[错误] {task} — {now}'
    tb = traceback.format_exc() if error is not None else ''
    body = '\n\n'.join(filter(None, [
        f'{task} 运行出错\n时间: {now}',
        details,
        f'异常信息:\n{tb}' if tb and tb.strip() != 'NoneType: None' else '',
    ]))
    return send(subject, body, silent=silent)


def notify_progress(task: str, message: str, silent: bool = True) -> bool:
    """进度汇报。"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = f'[进度] {task} — {now}'
    return send(subject, f'{message}\n\n时间: {now}', silent=silent)


# ── 装饰器 ────────────────────────────────────────────────────────────────────
def on_finish(task: str, notify_on_error: bool = True, notify_on_success: bool = True,
              silent: bool = True):
    """
    装饰器：函数正常结束时发"完成"邮件，抛异常时发"错误"邮件（并重新抛出）。

    示例:
        @on_finish("EBV 分类器训练")
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
                    notify_done(task, f'耗时: {elapsed:.1f} 秒', silent=silent)
                return result
            except Exception as e:
                if notify_on_error:
                    notify_error(task, e, silent=silent)
                raise
        return wrapper
    return decorator


# ── 命令行入口 ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('用法: python notify.py "主题" ["正文"]')
        sys.exit(1)
    subject = sys.argv[1]
    body    = sys.argv[2] if len(sys.argv) > 2 else ''
    send(subject, body)
