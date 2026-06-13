import imaplib
import email
from email.header import decode_header
import os
import requests
import re
import socket

socket.setdefaulttimeout(30)  # fail fast instead of hanging

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KEYWORDS = [
    "sre", "site reliability", "devops", "cloud", "aws", "terraform",
    "azure devops", "ci/cd", "infrastructure", "platform engineer",
    "automation engineer", "middleware"
]


def connect():
    print("Connecting to imap.gmail.com:993 ...")
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    print("Connected. Logging in...")
    imap.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    print("Login successful.")
    return imap
