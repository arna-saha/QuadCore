# QuadCore
Problem Statement 2:
StackIt – A Minimal Q&A Forum Platform
Team Name- QuadCore
Debtanu Roy- debtanuroy82@gmail.com,
Arna Saha- arnasaha0982@gmail.com,
Anwesa Ghosh- anwesa310@gmail.com,
Dewan Habib- dewanhabib2004@gmail.com

# 🧠 StackIt - A Minimal Q&A Forum Platform: 
Website will be available at: https://quadcore-stackit-platform.onrender.com

**StackIt** is a lightweight, responsive Question-and-Answer platform built with **Flask**, designed for collaborative learning, academic discussions, and community-driven knowledge sharing.

> ✅ Built for the Odoo Hackathon '25

----

## 🚀 Features

- 🔐 **User Authentication**
  - Register, Login, Logout
  - OTP-based email verification using Gmail App Passwords

- ✍️ **Q&A System**
  - Post questions with tags
  - Submit rich text answers (Quill.js)
  - Accept best answers
  - Edit and delete support (coming soon)

- 📊 **Voting System**
  - Upvote / downvote answers
  - Score-based sorting

- 🔔 **Notification System**
  - 🔔 Bell icon with live unread counter
  - Alerts when:
    - Someone answers your question
    - You're mentioned using `@username`

- 📂 **Filtering & Pagination**
  - Filter by **Newest**, **Unanswered**, and **Popular**
  - Pagination support for smoother navigation

- 🛠 **Admin Dashboard**
  - View all users and questions
  - Delete spam/inappropriate content

---

## 📷 Screenshots

Coming soon...

---

## 🛠️ Tech Stack

| Layer         | Technology              |
|---------------|--------------------------|
| Backend       | Flask + SQLAlchemy       |
| Frontend      | Bootstrap 5 + Quill.js   |
| Database      | SQLite (easy to migrate) |
| Auth & OTP    | Flask-Login + Flask-Mail |
| Hosting       | Render                   |
| Versioning    | Git + GitHub             |

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/QuadCore.git
cd stackit-platform
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment

Create a `.env` file or edit `app.config`:

```python
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
```

Make sure to [enable 2FA and generate an App Password on Gmail](https://myaccount.google.com/apppasswords).

### 5. Run the App

```bash
python app.py
```
---

## 🌐 Deployment (Render)

- Push your repo to GitHub
- Create a new **Web Service** on [Render](https://render.com)
- Set:
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app`
- Add environment variables for mail credentials
- Done 🎉

---

## 👨‍💻 Contributors

- Debtanu Roy – [@debtanuroy](https://github.com/debtanuroy)
- Arna Saha – [@arna-saha](https://github.com/arna-saha)
- Dewan Habib - [@DewanHabib10] (https://github.com/DewanHabib10)
- Anwesa Ghosh - [@anwesa310] (https://github.com/anwesa310)

---

## 📄 License

This project is licensed under the MIT License.  
Feel free to fork and use it for your college, community, or hackathon projects!

---

## ⭐ Support the Project

If you like this project, consider giving it a ⭐ on GitHub!
