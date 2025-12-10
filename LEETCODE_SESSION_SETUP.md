# LeetCode Session Setup Guide

## How to Get Your LeetCode Session ID

### Step 1: Login to LeetCode
1. Go to [leetcode.com](https://leetcode.com)
2. Login to your account

### Step 2: Open Browser DevTools
- **Chrome/Edge:** Press `F12` or `Ctrl+Shift+I`
- **Firefox:** Press `F12` or `Ctrl+Shift+I`

### Step 3: Find Your Session Cookie
1. Click on the **Application** tab (Chrome) or **Storage** tab (Firefox)
2. In the left sidebar, expand **Cookies**
3. Click on `https://leetcode.com`
4. Find the cookie named **`LEETCODE_SESSION`**
5. Copy the **Value** (it's a long string)

### Step 4: Enter in Dashboard
1. Go to your MAANG Tracker dashboard
2. Navigate to **Settings** or **LeetCode Integration**
3. Paste your:
   - **Username:** Your LeetCode username
   - **Session ID:** The LEETCODE_SESSION value you copied

### Example:
```
Username: arnold-1324
Session ID: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Why This Method?

✅ **No SOCKS proxy needed** - Direct API calls  
✅ **More reliable** - No automated login issues  
✅ **Secure** - Session stored locally  
✅ **Simple** - Just copy & paste  

## Session Validity

- Sessions typically last **30 days**
- If you logout from LeetCode, you'll need a new session
- The system will notify you if your session expires

## Troubleshooting

**"Invalid session" error?**
- Make sure you copied the entire LEETCODE_SESSION value
- Try logging out and back into LeetCode
- Get a fresh session ID

**Can't find the cookie?**
- Make sure you're logged into LeetCode
- Try refreshing the page
- Check you're looking at `https://leetcode.com` cookies (not other domains)

## Security Note

Your session ID is like a password - keep it private! It's stored locally in:
```
config/leetcode_session.json
```

Never share this file or commit it to version control.
