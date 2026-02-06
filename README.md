# SOS Location SMS API

A minimal Flask API that sends your GPS location via SMS when triggered.

## Deploy to Render

**Free tier includes:** 0.5GB RAM, automatic deploys from GitHub, custom domain

### Steps:

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/sms-api.git
   git push -u origin main
   ```

2. **Go to [render.com](https://render.com)**
   - Sign up (use GitHub account)
   - Click "New +" → "Web Service"
   - Select your GitHub repo
   - Settings:
     - **Name:** sms-api (or any name)
     - **Runtime:** Python 3
     - **Build command:** `pip install -r requirements.txt`
     - **Start command:** `gunicorn app:app`
   - Click "Create Web Service"

3. **Add Environment Variables:**
   - In Render dashboard, go to **Environment**
   - Add:
     ```
     TWILIO_ACCOUNT_SID=your_account_sid
     TWILIO_AUTH_TOKEN=your_auth_token
     TWILIO_PHONE_NUMBER=+1234567890
     ```
   - Get these from [twilio.com](https://twilio.com)

4. **Done!** Your app will deploy automatically.

   Your URL will be: `https://sms-api-xxx.onrender.com`

### Use it:

Open in browser:
```
https://sms-api-xxx.onrender.com/
```

Click the red SOS button → location SMS sent to +916301664543

---

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/
