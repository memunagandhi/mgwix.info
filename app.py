# MGWix Portfolio — mgwix.info
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os, json, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# ── GOOGLE SHEETS ─────────────────────────────────────────────
def save_to_sheet(row):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        sheet_id   = os.environ.get('SHEET_ID')
        if not creds_json or not sheet_id:
            print("Google Sheets env vars missing")
            return False
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        creds  = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(sheet_id).sheet1
        sheet.append_row(row)
        print(f"Sheet row saved: {row}")
        return True
    except Exception as e:
        print(f"Sheet error: {e}")
        return False

# ── EMAIL NOTIFICATION ────────────────────────────────────────
def send_email_notification(name, email, service, message):
    try:
        smtp_email = os.environ.get('SMTP_EMAIL')
        smtp_pass  = os.environ.get('SMTP_PASSWORD')
        to_email   = os.environ.get('NOTIFY_EMAIL', smtp_email)
        if not smtp_email or not smtp_pass:
            print("SMTP env vars missing")
            return False
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚀 New Portfolio Inquiry from {name}"
        msg['From']    = smtp_email
        msg['To']      = to_email
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0a0f0d;color:#f0ece4;padding:32px;border-radius:12px;">
          <h2 style="color:#00C49A;margin-bottom:4px;">New Contact Form Submission</h2>
          <p style="color:#9a9490;margin-top:0;">mgwix.info Portfolio</p>
          <hr style="border-color:#1e2e29;margin:24px 0;">
          <table style="width:100%;">
            <tr><td style="padding:8px 0;color:#9a9490;width:100px;">Name</td><td style="color:#f0ece4;font-weight:600;">{name}</td></tr>
            <tr><td style="padding:8px 0;color:#9a9490;">Email</td><td style="color:#00C49A;">{email}</td></tr>
            <tr><td style="padding:8px 0;color:#9a9490;">Service</td><td style="color:#f0ece4;">{service}</td></tr>
          </table>
          <hr style="border-color:#1e2e29;margin:24px 0;">
          <p style="color:#9a9490;margin-bottom:8px;">Message:</p>
          <p style="color:#f0ece4;background:#111;padding:16px;border-radius:8px;border-left:3px solid #00C49A;">{message}</p>
          <p style="color:#6b6762;font-size:12px;margin-top:32px;">Sent from mgwix.info contact form</p>
        </div>"""
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_email, smtp_pass)
            server.sendmail(smtp_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ── ROUTES ────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    print("=== CONTACT FORM SUBMITTED ===")
    try:
        data    = request.get_json()
        name    = data.get('name','').strip()
        email   = data.get('email','').strip()
        service = data.get('service','').strip()
        message = data.get('message','').strip()
        budget  = data.get('budget','').strip()
        ts      = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        save_to_sheet([ts, name, email, service, budget, message])
        send_email_notification(name, email, service, message)

        return jsonify({'success': True, 'message': "Thank you! I'll get back to you within 24 hours."})
    except Exception as e:
        print(f"Contact error: {e}")
        return jsonify({'success': True, 'message': "Thank you! I'll be in touch soon."})

if __name__ == '__main__':
    app.run(debug=False)
