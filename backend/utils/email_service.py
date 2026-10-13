import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(to_email: str, subject: str, body: str, html_body: str = None):
    """Send an email using Gmail SMTP"""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("Email credentials not configured. Skipping email send.")
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Add plain text body
        msg.attach(MIMEText(body, "plain"))
        
        # Add HTML body if provided
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
        
        # Connect to SMTP server and send
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def send_check_in_reminder(email: str, name: str, time_of_day: str):
    """Send a dose reminder email"""
    subject = f"Regrowth OS - {time_of_day.capitalize()} Dose Reminder"
    body = f"Hi {name},\n\nThis is your reminder to apply your {time_of_day} dose of Minoxidil + Finasteride.\n\nStay consistent for best results!\n\nBest,\nRegrowth OS Team"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #4F46E5; color: white; padding: 20px; text-align: center;">
                <h1>Regrowth OS</h1>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9;">
                <h2>Hi {name},</h2>
                <p>This is your reminder to apply your <strong>{time_of_day}</strong> dose of Minoxidil + Finasteride.</p>
                <p>Stay consistent for best results!</p>
                <div style="background-color: #4F46E5; color: white; padding: 10px; text-align: center; border-radius: 5px; margin-top: 20px;">
                    <a href="#" style="color: white; text-decoration: none;">Log Your Dose Now</a>
                </div>
            </div>
        </body>
    </html>
    """
    return send_email(email, subject, body, html_body)

def send_streak_achievement_email(email: str, name: str, streak_days: int, badge_name: str):
    """Send a streak achievement email"""
    subject = f"Congratulations! You've earned the '{badge_name}' badge!"
    body = f"Hi {name},\n\nAmazing work! You've maintained a {streak_days}-day streak and earned the '{badge_name}' badge.\n\nKeep up the great work!\n\nBest,\nRegrowth OS Team"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #10B981; color: white; padding: 20px; text-align: center;">
                <h1>🎉 Achievement Unlocked!</h1>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9;">
                <h2>Hi {name},</h2>
                <p>Amazing work! You've maintained a <strong>{streak_days}-day streak</strong> and earned the <strong>'{badge_name}'</strong> badge.</p>
                <p>Keep up the great work!</p>
            </div>
        </body>
    </html>
    """
    return send_email(email, subject, body, html_body)

def send_refill_reminder(email: str, name: str, days_remaining: int):
    """Send a bottle refill reminder"""
    subject = f"Refill Alert: Only {days_remaining} days of medicine remaining"
    body = f"Hi {name},\n\nYour medicine bottle is running low. You have approximately {days_remaining} days of treatment remaining.\n\nOrder your refill now to avoid missing doses.\n\nOrder at: manmatters.com\n\nBest,\nRegrowth OS Team"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #EF4444; color: white; padding: 20px; text-align: center;">
                <h1>Refill Alert</h1>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9;">
                <h2>Hi {name},</h2>
                <p>Your medicine bottle is running low. You have approximately <strong>{days_remaining} days</strong> of treatment remaining.</p>
                <p>Order your refill now to avoid missing doses.</p>
                <div style="background-color: #4F46E5; color: white; padding: 10px; text-align: center; border-radius: 5px; margin-top: 20px;">
                    <a href="https://manmatters.com" style="color: white; text-decoration: none;">Order Now at Man Matters</a>
                </div>
            </div>
        </body>
    </html>
    """
    return send_email(email, subject, body, html_body)
