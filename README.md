# MongoDB Testcontainers Demo

This demo illustrates a Python application using MongoDB with Testcontainers and GitHub Actions.

## 🧑‍💻 About this Demo

This project demonstrates how to:

- Build a simple Python application interacting with MongoDB Atlas.
- Automatically spin up MongoDB containers for isolated, consistent testing using Testcontainers.
- Integrate GitHub Actions to automate testing every time you push code.

## ⚙️ Technologies Used

- Python (pymongo, pytest)
- Testcontainers (with MongoDB)
- Docker
- GitHub Actions (CI/CD)

## 🚀 Running the Demo

### **Local Setup**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_db_connection.py
