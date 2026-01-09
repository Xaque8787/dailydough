# Installation Guide for PyCharm

This guide will walk you through setting up the Internal Management System in PyCharm.

## Prerequisites

1. **Python 3.8 or higher** installed on your system
   - Download from: https://www.python.org/downloads/
   - During installation, make sure to check "Add Python to PATH"

2. **PyCharm IDE** (Community or Professional)
   - Download from: https://www.jetbrains.com/pycharm/download/

3. **Git** installed and configured
   - Your GitHub repository should already be synced

## Setup in PyCharm

### Step 1: Open Project in PyCharm

1. Open PyCharm
2. Click **File → Open**
3. Navigate to your project folder (where you cloned the repository)
4. Click **OK**

### Step 2: Configure Python Interpreter

1. Go to **File → Settings** (or **PyCharm → Preferences** on macOS)
2. Navigate to **Project: [your-project-name] → Python Interpreter**
3. Click the gear icon ⚙️ and select **Add Interpreter → Add Local Interpreter**
4. Choose **Virtualenv Environment**
5. Select **New environment**
6. Set the location (default is fine: `./venv`)
7. Choose your Python base interpreter (Python 3.8+)
8. Click **OK**

### Step 3: Install Dependencies

#### Method 1: Using PyCharm's Package Manager

1. In PyCharm, open the **Terminal** tab at the bottom
2. Make sure your virtual environment is activated (you should see `(venv)` in the prompt)
3. Run:
```bash
pip install -r requirements.txt
```

#### Method 2: Using PyCharm's UI

1. Go to **File → Settings → Project → Python Interpreter**
2. Click the **+** button
3. Search for and install each package from `requirements.txt`:
   - fastapi
   - uvicorn
   - jinja2
   - python-multipart
   - python-jose[cryptography]
   - passlib[bcrypt]
   - sqlalchemy
   - pydantic
   - pydantic-settings

### Step 4: Configure Run Configuration

1. Click **Run → Edit Configurations**
2. Click the **+** button and select **Python**
3. Configure as follows:
   - **Name:** Run Server
   - **Script path:** Click the folder icon and select `run.py`
   - **Working directory:** Should be your project root
   - **Python interpreter:** Select the venv you created
4. Click **OK**

### Step 5: Run the Application

#### Option 1: Using Run Configuration
1. Click the green play button ▶️ in the top-right
2. Or press `Shift + F10` (Windows/Linux) or `Ctrl + R` (macOS)

#### Option 2: Using Terminal
1. Open the **Terminal** tab in PyCharm
2. Run:
```bash
python run.py
```

Or:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5710 --reload
```

### Step 6: Access the Application

1. Once the server starts, you should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:5710 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

2. Open your browser and go to:
```
http://localhost:5710
```

3. You should see the **Initial Setup** page (on first run)

## First Time Setup

1. When you first access `http://localhost:5710`, you'll see the setup page
2. Create your admin account:
   - Enter a username
   - Enter a secure password
   - Click "Create Admin Account"
3. You'll be automatically logged in to the system

## Project Structure in PyCharm

```
sprinance/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app entry point
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   ├── auth/              # Authentication logic
│   ├── routes/            # Route handlers
│   ├── templates/         # Jinja2 HTML templates
│   ├── static/            # CSS & JavaScript
│   └── utils/             # Helper functions
├── data/                  # Application data
│   ├── database.db        # SQLite database (created on first run)
│   └── reports/           # Generated CSV files
├── venv/                  # Virtual environment (created by PyCharm)
├── requirements.txt       # Python dependencies
├── run.py                 # Quick start script
└── README.md             # Documentation
```

## Development Workflow

### Running with Auto-Reload

The `run.py` script and the uvicorn command both include auto-reload by default. This means:
- When you save changes to Python files, the server automatically restarts
- You don't need to manually stop and start the server
- Just refresh your browser to see changes

### Debugging in PyCharm

1. Set breakpoints by clicking in the left gutter of your code
2. Click the debug button 🐛 (or press `Shift + F9`)
3. The application will start in debug mode
4. Access the application in your browser
5. When code hits a breakpoint, PyCharm will pause execution

### Database Management

The SQLite database is stored at `data/database.db`

#### To reset the database:
1. Stop the server
2. Delete `data/database.db`
3. Restart the server
4. Go through the initial setup again

#### To view the database in PyCharm:
1. Go to **View → Tool Windows → Database**
2. Click **+** → **Data Source → SQLite**
3. Set the file to `data/database.db`
4. Click **Test Connection** then **OK**

## Troubleshooting

### Port 5710 Already in Use

If you see an error about port 5710 being in use:

**On Windows:**
```bash
netstat -ano | findstr :5710
taskkill /PID <process_id> /F
```

**On macOS/Linux:**
```bash
lsof -i :5710
kill -9 <PID>
```

### Import Errors

If you see import errors:
1. Make sure you've activated the virtual environment
2. Reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### PyCharm Not Finding Modules

1. Go to **File → Invalidate Caches → Invalidate and Restart**
2. Make sure your Python interpreter is correctly configured
3. Check that the project root is marked as "Sources Root" (right-click folder → Mark Directory as → Sources Root)

### Database Lock Errors

If you see "database is locked" errors:
1. Make sure only one instance of the app is running
2. Close any database viewers (like DB Browser for SQLite)
3. Restart the application

## Testing the Application

### Manual Testing Checklist

After setup, test these features:

1. **Authentication:**
   - [ ] Can create admin account
   - [ ] Can log in
   - [ ] Can log out

2. **Administration:**
   - [ ] Can create new users
   - [ ] Can edit users
   - [ ] Can delete users
   - [ ] Can assign admin privileges

3. **Employees:**
   - [ ] Can create employees
   - [ ] Can edit employee details
   - [ ] Can set scheduled days
   - [ ] Can configure tip requirements
   - [ ] Can view employee detail page
   - [ ] Can delete employees

4. **Daily Balance:**
   - [ ] Can enter daily financial data
   - [ ] Can add/remove working employees
   - [ ] Can enter employee tip data
   - [ ] Can save draft
   - [ ] Can finalize and generate CSV report
   - [ ] CSV file is created in data/reports/

## Next Steps

1. **Change the Secret Key:**
   - Open `app/auth/jwt_handler.py`
   - Change the `SECRET_KEY` to a secure random string

2. **Add Sample Data:**
   - Create a few test employees
   - Enter some daily balance data
   - Generate test reports

3. **Customize:**
   - Modify CSS in `app/static/css/style.css`
   - Update templates in `app/templates/`
   - Add new features as needed

## Getting Help

If you encounter issues:
1. Check the console output in PyCharm's Run window
2. Review the README.md file
3. Check Python and package versions match requirements
4. Ensure database file permissions are correct

## Security Reminder

Before deploying to production:
- [ ] Change the SECRET_KEY in `app/auth/jwt_handler.py`
- [ ] Use environment variables for sensitive configuration
- [ ] Set up HTTPS
- [ ] Configure proper authentication timeouts
- [ ] Review and update security settings
