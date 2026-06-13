import imaplib
import email
from email.header import decode_header
import os
import requests
import re

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KEYWORDS = [
    "sre", "site reliability", "devops", "cloud", "aws", "terraform",
    "azure devops", "ci/cd", "infrastructure", "platform engineer",
    "automation engineer", "middleware"
]

PROCESSED_LABEL = "JobAlertsProcessed"


def connect():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    return imap


def decode_subject(raw_subject):
    decoded, encoding = decode_header(raw_subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })


def main():
    imap = connect()
    imap.select("INBOX")

    # Search unread LinkedIn job alert emails
    status, messages = imap.search(
        None, '(UNSEEN FROM "jobalerts-noreply@linkedin.com")'
    )

    if status != "OK":
        print("Search failed")
        return

    msg_ids = messages[0].split()
    if not msg_ids:
        print("No new job alerts")
        return

    matched = []

    for msg_id in msg_ids:
        status, msg_data = imap.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = decode_subject(msg["Subject"] or "")

        subject_lower = subject.lower()
        if any(kw in subject_lower for kw in KEYWORDS):
            matched.append(subject)

        # Mark as read regardless (avoid reprocessing)
        imap.store(msg_id, '+FLAGS', '\\Seen')

    if matched:
        lines = ["<b>New Job Alerts (SRE/DevOps/Cloud)</b>", ""]
        for s in matched:
            lines.append(f"• {s}")
        send_telegram("\n".join(lines))
        print(f"Sent {len(matched)} matches")
    else:
        print(f"Checked {len(msg_ids)} emails, no keyword matches")

    imap.logout()

if __name__ == "__main__":
    main()
