import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

EMAIL_SENDER       = os.environ["EMAIL_SENDER"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
EMAIL_RECIPIENT    = os.environ["EMAIL_RECIPIENT"]

now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
subject = "🔔 GOLD — LONG (HC) [TEST]"
body = (
    "TRADING SIGNAL ALERT — TEST\n"
    "========================================\n"
    "Asset      : GOLD\n"
    "Direction  : LONG\n"
    "Conviction : HC\n"
    "Entry Price: 3245.80\n"
    "TP         : 3271.04  (+$25)\n"
    "SL         : 3233.55  (-$12.50)\n"
    "R:R        : 1:2.0\n"
    "RSI        : 58.5\n"
    "Volume     : Above Average\n"
    f"Time (UTC) : {now_utc}\n"
    "========================================\n"
    "*** This is a test notification ***\n"
)

msg = MIMEMultipart()
msg["From"]    = EMAIL_SENDER
msg["To"]      = EMAIL_RECIPIENT
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

print(f"Sending test email to {EMAIL_RECIPIENT}...")

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
    print("✅ Test email sent successfully! Check your inbox.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
