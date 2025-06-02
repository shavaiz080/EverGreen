# Role-Based Sales Dashboard

A Streamlit web application that provides role-based dashboards for sales data visualization and analysis.

## Features

- **Role-based access control**: Different views for administrators and sales representatives
- **Interactive dashboards**: Filter and analyze sales data with dynamic charts
- **Admin dashboard**: Complete overview of all sales data, performance metrics, and analytics
- **Sales rep dashboard**: Personalized view of individual performance metrics

## Project Structure

- `app.py`: Main application entry point
- `auth.py`: Authentication module for user login and role management
- `data.py`: Data handling module for loading and filtering sales data
- `views.py`: Dashboard view router
- `admin_view.py`: Admin dashboard views and components
- `sales_view.py`: Sales representative dashboard views and components

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit application:
   ```
   streamlit run app.py
   ```
2. Open your browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

## Demo Accounts

- **Admin User**:
  - Username: admin
  - Password: admin123

- **Sales Representative**:
  - Username: sales1
  - Password: sales123
  - Name: John Doe

- **Sales Representative**:
  - Username: sales2
  - Password: sales456
  - Name: Jane Smith

## Customization

- To add real data, modify the `data.py` file to connect to your database or data source
- To add more users, update the `USERS` dictionary in `auth.py`
- To add more dashboard views, create new functions in the appropriate view files

## Deployment Options

### Option 1: Deploy on Streamlit Cloud (Recommended)

1. **Create a GitHub repository**:
   - Create a new repository on GitHub
   - Push your code to the repository using Git:
     ```
     git init
     git add .
     git commit -m "Initial commit"
     git remote add origin <your-github-repo-url>
     git push -u origin main
     ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository, branch (main), and set the main file path to `app.py`
   - Click "Deploy"
   - Share the generated URL with your friends

### Option 2: Deploy on Heroku

1. **Install Heroku CLI**:
   - Download and install from [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login to Heroku and create app**:
   ```
   heroku login
   heroku create evergreen-dashboard
   ```

3. **Push to Heroku**:
   ```
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```

4. **Open the app**:
   ```
   heroku open
   ```

### Option 3: Deploy on PythonAnywhere

1. Create an account on [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload your project files
3. Set up a web app with the command: `streamlit run app.py`
4. Share your PythonAnywhere URL

## Important Notes for Deployment

- **Data Persistence**: The app currently uses local JSON files for data storage. When deployed to platforms like Streamlit Cloud or Heroku, any changes to data will be temporary and reset when the app restarts.
- **Authentication**: For a production environment, consider implementing stronger authentication mechanisms.
- **Environment Variables**: Store sensitive information like passwords in environment variables.
