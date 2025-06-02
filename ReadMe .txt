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
