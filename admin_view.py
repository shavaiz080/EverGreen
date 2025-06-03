import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
import local_db as db
import random
from auth import logout_user, get_user_info
from data import load_data, get_filtered_data

# Initialize session state for leads if it doesn't exist
if 'leads' not in st.session_state:
    st.session_state.leads = db.load_leads()
    
# Initialize next lead ID if it doesn't exist
if 'next_lead_id' not in st.session_state:
    st.session_state.next_lead_id = db.get_next_lead_id()
    
# Initialize form_submit_success flag if it doesn't exist
if 'form_submit_success' not in st.session_state:
    st.session_state.form_submit_success = False

# Initialize users list if it doesn't exist
if 'users' not in st.session_state:
    st.session_state.users = db.load_users()

def admin_view():
    """Admin dashboard view with full access to all data and analytics"""
    # Display logo and title together
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        st.image("images/logo.png", width=80)
    with col_title:
        st.title("Admin Dashboard")
    
    # Display notification if exists
    if st.session_state.notification:
        if st.session_state.notification["type"] == "success":
            st.success(st.session_state.notification["message"])
        elif st.session_state.notification["type"] == "error":
            st.error(st.session_state.notification["message"])
        elif st.session_state.notification["type"] == "warning":
            st.warning(st.session_state.notification["message"])
        elif st.session_state.notification["type"] == "info":
            st.info(st.session_state.notification["message"])
        
        # Clear notification after displaying
        st.session_state.notification = None
    
    st.sidebar.title(f"Welcome, {st.session_state.display_name}")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard Overview", "Leads", "Leads Management", "User Accounts"],
        key="admin_nav"
    )
    
    if st.sidebar.button("Logout", key="logout_btn"):
        logout_user()
        st.rerun()
    
    # Dashboard Overview page
    if page == "Dashboard Overview":
        show_dashboard_overview()
    
    # Leads page
    elif page == "Leads":
        show_leads()
    
    # Leads Management page
    elif page == "Leads Management":
        show_leads_management()
    
    # User Accounts page
    elif page == "User Accounts":
        show_user_accounts()

def show_dashboard_overview():
    """Show dashboard overview with key metrics and charts"""
    st.header("Dashboard Overview")
    
    # Get actual leads data from session state
    leads = st.session_state.leads
    leads_df = pd.DataFrame(leads) if leads else pd.DataFrame()
    
    # Create top-level metrics
    st.subheader("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    
    # Calculate KPIs
    total_leads = len(leads) if leads else 0
    won_leads = len([lead for lead in leads if lead.get("status") == "Won"]) if leads else 0
    conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Display KPIs
    col1.metric(
        "Total Leads", 
        f"{total_leads}",
        "Total Opportunities"
    )
    col2.metric(
        "Won Deals", 
        f"{won_leads}",
        "Successfully Converted"
    )
    col3.metric(
        "Conversion Rate", 
        f"{conversion_rate:.1f}%",
        "Success Rate"
    )
    
    # Lead Analysis Section
    st.subheader("Lead Analysis")
    chart1, chart2 = st.columns(2)
    
    with chart1:
        st.markdown("### Lead Status Distribution")
        if leads:
            # Create status distribution
            status_counts = pd.DataFrame(leads).groupby('status').size().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            # Create a bar chart
            fig = plt.figure(figsize=(10, 6))
            plt.barh(status_counts['Status'], status_counts['Count'])
            plt.title('Lead Status Distribution')
            plt.xlabel('Number of Leads')
            
            # Customize colors based on status
            colors = ['#FFA500', '#FFD700', '#32CD32', '#FF6B6B', '#4169E1']
            plt.barh(status_counts['Status'], status_counts['Count'], color=colors[:len(status_counts)])
            
            st.pyplot(fig)
            plt.close()
    
    with chart2:
        st.markdown("### Sales Team Performance")
        if leads:
            sales_performance = pd.DataFrame(leads)
            if 'assigned_to' in sales_performance.columns:
                sales_stats = sales_performance.groupby('assigned_to').agg({
                    'id': 'count',
                    'status': lambda x: sum(x == 'Won')
                }).reset_index()
                
                sales_stats.columns = ['Sales Rep', 'Total Leads', 'Won Deals']
                sales_stats['Success Rate'] = (sales_stats['Won Deals'] / sales_stats['Total Leads'] * 100).round(1)
                st.dataframe(sales_stats.style.highlight_max(axis=0, color='#90EE90'))
    
    # Sales Performance Analysis
    st.subheader("Sales Team Performance Analysis")
    if leads:
        sales_df = pd.DataFrame(leads)
        if 'assigned_to' in sales_df.columns:
            # Create three columns for different metrics
            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                st.markdown("### Lead Assignment vs Closure Rate")
                # Calculate leads assigned and closed for each sales rep
                sales_metrics = sales_df.groupby('assigned_to').agg({
                    'id': 'count',  # Total leads assigned
                    'status': lambda x: sum(x == 'Won')  # Leads closed/won
                }).reset_index()
                
                sales_metrics.columns = ['Sales Rep', 'Assigned', 'Closed']
                sales_metrics['Conversion Rate'] = (sales_metrics['Closed'] / sales_metrics['Assigned'] * 100).round(1)
                
                # Create a bar chart comparing assigned vs closed leads
                fig = plt.figure(figsize=(10, 6))
                x = range(len(sales_metrics['Sales Rep']))
                width = 0.35
                
                plt.bar(x, sales_metrics['Assigned'], width, label='Assigned', color='#FFA500')
                plt.bar([i + width for i in x], sales_metrics['Closed'], width, label='Closed', color='#32CD32')
                
                plt.xlabel('Sales Representatives')
                plt.ylabel('Number of Leads')
                plt.title('Lead Assignment vs Closure by Sales Rep')
                plt.xticks([i + width/2 for i in x], sales_metrics['Sales Rep'], rotation=45)
                plt.legend()
                
                st.pyplot(fig)
                plt.close()
            
            with metric_col2:
                st.markdown("### Conversion Rate by Sales Rep")
                # Create a horizontal bar chart for conversion rates
                fig = plt.figure(figsize=(10, 6))
                plt.barh(sales_metrics['Sales Rep'], sales_metrics['Conversion Rate'])
                plt.xlabel('Conversion Rate (%)')
                plt.title('Lead Conversion Rate by Sales Rep')
                
                # Add percentage labels on the bars
                for i, v in enumerate(sales_metrics['Conversion Rate']):
                    plt.text(v, i, f'{v}%', va='center')
                
                st.pyplot(fig)
                plt.close()
            
            # Average Time to Close Analysis
            st.markdown("### Average Time to Close Analysis")
            if 'created_at' in sales_df.columns and 'closed_at' in sales_df.columns:
                # Convert datetime columns
                sales_df['created_at'] = pd.to_datetime(sales_df['created_at'])
                sales_df['closed_at'] = pd.to_datetime(sales_df['closed_at'])
                
                # Calculate time to close for won leads
                won_leads = sales_df[sales_df['status'] == 'Won'].copy()
                won_leads['time_to_close'] = (won_leads['closed_at'] - won_leads['created_at']).dt.days
                
                # Group by sales rep and calculate average time to close
                time_metrics = won_leads.groupby('assigned_to')['time_to_close'].agg([
                    ('avg_days', 'mean'),
                    ('min_days', 'min'),
                    ('max_days', 'max')
                ]).round(1).reset_index()
                
                # Create a column chart for average time to close
                fig = plt.figure(figsize=(10, 6))
                plt.bar(time_metrics['assigned_to'], time_metrics['avg_days'], color='#4169E1')
                plt.xlabel('Sales Representatives')
                plt.ylabel('Average Days to Close')
                plt.title('Average Time to Close by Sales Rep')
                plt.xticks(rotation=45)
                
                # Add average days labels on top of bars
                for i, v in enumerate(time_metrics['avg_days']):
                    plt.text(i, v, f'{v:.1f}d', ha='center', va='bottom')
                
                st.pyplot(fig)
                plt.close()
                
                # Display detailed metrics table
                st.markdown("### Detailed Performance Metrics")
                metrics_table = pd.merge(sales_metrics, time_metrics, left_on='Sales Rep', right_on='assigned_to')
                metrics_table = metrics_table[['Sales Rep', 'Assigned', 'Closed', 'Conversion Rate', 
                                             'avg_days', 'min_days', 'max_days']]
                metrics_table.columns = ['Sales Rep', 'Total Leads', 'Won Deals', 'Success Rate (%)', 
                                       'Avg Days to Close', 'Min Days', 'Max Days']
                st.dataframe(metrics_table.style.highlight_max(axis=0, color='#90EE90'))
    
    # Add follow-up reminders if any leads are pending follow-up
    pending_followup = [lead for lead in leads if lead.get('status') == 'Follow Up']
    if pending_followup:
        st.subheader("⚠️ Follow-up Reminders")
        for lead in pending_followup[:3]:  # Show top 3 follow-ups
            st.warning(
                f"Follow up required for {lead.get('customer_name', 'N/A')} - "
                f"Last contact: {lead.get('last_contact_date', 'Not available')}"
            )
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Lead Sources")
        if not leads_df.empty and "source" in leads_df.columns:
            # Get actual lead sources data
            source_counts = leads_df["source"].value_counts()
            sources = source_counts.index.tolist()
            values = source_counts.values.tolist()
            
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(values, labels=sources, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.info("No lead source data available yet.")
    
    with col2:
        st.subheader("Lead Status")
        if not leads_df.empty and "status" in leads_df.columns:
            # Get actual lead status data
            status_counts = leads_df["status"].value_counts()
            statuses = status_counts.index.tolist()
            counts = status_counts.values.tolist()
            
            fig, ax = plt.subplots(figsize=(8, 8))
            sns.barplot(x=statuses, y=counts, ax=ax)
            ax.set_title("Leads by Status")
            ax.set_xlabel("Status")
            ax.set_ylabel("Count")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("No lead status data available yet.")
    
    # Recent activity - generate based on actual leads
    st.subheader("Recent Activity")
    
    # Generate activity data based on most recent leads
    activities = []
    
    # Sort leads by creation date if available, otherwise use the first 5
    recent_leads = sorted(leads, key=lambda x: x.get("created_at", ""), reverse=True)[:5] if leads else []
    
    for i, lead in enumerate(recent_leads):
        # Create a timestamp (use current time minus random minutes for demo)
        timestamp = (datetime.now() - timedelta(minutes=random.randint(10, 300))).strftime("%Y-%m-%d %H:%M")
        user = lead.get("assigned_to", "Unassigned")
        action = f"Created new lead: {lead.get('name', 'Unknown')}"
        
        activities.append({
            "timestamp": timestamp,
            "user": user,
            "action": action
        })
    
    if activities:
        activity_df = pd.DataFrame(activities)
        st.dataframe(activity_df, use_container_width=True)
    else:
        st.info("No recent activity available yet.")

def get_sales_users_list():
    """Get a list of sales users for dropdowns"""
    users = db.load_users()
    # Start with Unassigned option
    user_list = ["Unassigned"]
    # Add active users with sales role
    for user in users:
        if user["status"] == "Active" and user["role"] == "sales":
            user_list.append(user["name"])
    return user_list

def get_assigned_to_index(user_list, assigned_to):
    """Helper function to safely get the index of assigned_to in the user list"""
    try:
        return user_list.index(assigned_to)
    except ValueError:
        return 0  # Default to first item (Unassigned) if not found

def show_leads():
    """Show leads dashboard with list of leads and filters"""
    st.header("Leads")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"],
            key="leads_status_filter"
        )
    
    with col2:
        source_filter = st.selectbox(
            "Source",
            ["All", "Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"],
            key="leads_source_filter"
        )
    
    with col3:
        city_filter = st.selectbox(
            "City",
            ["All", "Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"],
            key="leads_city_filter"
        )
        
    with col4:
        assigned_filter = st.selectbox(
            "Assigned To",
            ["All"] + get_sales_users_list(),
            key="leads_assigned_filter"
        )
    
    # Date range filter
    date_range = st.date_input(
        "Date Range",
        value=(
            datetime.now() - timedelta(days=30),
            datetime.now()
        ),
        key="leads_date_range"
    )
    
    # Get leads from session state
    leads = st.session_state.leads
    
    leads_df = pd.DataFrame(leads)
    
    # Apply filters
    filtered_df = leads_df.copy() if not leads_df.empty else pd.DataFrame()
    
    if not filtered_df.empty:
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["status"] == status_filter]
        
        if source_filter != "All":
            filtered_df = filtered_df[filtered_df["source"] == source_filter]
        
        if city_filter != "All":
            filtered_df = filtered_df[filtered_df["city"] == city_filter]
            
        if assigned_filter != "All":
            filtered_df = filtered_df[filtered_df["assigned_to"] == assigned_filter]
        
        if len(date_range) >= 2:
            start_date = date_range[0].strftime("%Y-%m-%d")
            end_date = date_range[1].strftime("%Y-%m-%d")
            filtered_df = filtered_df[(filtered_df["date_created"] >= start_date) & (filtered_df["date_created"] <= end_date)]
    
    # Display leads
    if filtered_df.empty:
        st.info("No leads found. Create some leads in the Leads Management section.")
    else:
        st.subheader(f"Showing {len(filtered_df)} leads")
        
        # Add action buttons for each lead
        # Add action column to the dataframe
        filtered_df["actions"] = None
        
        # Ensure customer_code column exists (for backward compatibility)
        if "customer_code" not in filtered_df.columns:
            filtered_df["customer_code"] = "N/A"
        
        # Reorder columns to show customer_code near the beginning
        cols = filtered_df.columns.tolist()
        # Remove customer_code from current position
        if "customer_code" in cols:
            cols.remove("customer_code")
        # Insert customer_code after name
        name_index = cols.index("name") if "name" in cols else 0
        cols.insert(name_index + 1, "customer_code")
        # Apply the new column order
        filtered_df = filtered_df[cols]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Action section
        st.subheader("Lead Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if not filtered_df.empty:
                selected_lead_id = st.selectbox(
                    "Select Lead",
                    filtered_df["id"].tolist(),
                    format_func=lambda x: f"Lead #{x} - {filtered_df[filtered_df['id'] == x]['name'].values[0]}",
                    key="lead_action_select"
                )
            else:
                st.warning("No leads available to select")
                selected_lead_id = None
        
        with col2:
            action = st.selectbox(
                "Action",
                ["Edit", "Delete"],
                key="lead_action_type"
            )
        
        if selected_lead_id is not None:
            if action == "Edit":
                st.subheader(f"Edit Lead #{selected_lead_id}")
                
                # Get the selected lead data
                selected_lead = filtered_df[filtered_df["id"] == selected_lead_id].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    lead_name = st.text_input("Customer Name", value=selected_lead["name"], key="quick_edit_name")
                    phone = st.text_input("Phone No", value=selected_lead["phone"], key="quick_edit_phone")
                    sector = st.text_input("Sector", value=selected_lead["sector"], key="quick_edit_sector")
                    city = st.selectbox(
                        "City",
                        ["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"],
                        index=["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"].index(selected_lead["city"]) if selected_lead["city"] in ["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"] else 0,
                        key="quick_edit_city"
                    )
                    monthly_bill = st.number_input("Monthly Avg. Bill", min_value=0, value=int(selected_lead["monthly_bill"]), key="quick_edit_monthly_bill")
                
                with col2:
                    required_system = st.text_input("Required System", value=selected_lead["required_system"], key="quick_edit_required_system")
                    source = st.selectbox(
                        "Source",
                        ["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"],
                        index=["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"].index(selected_lead["source"]) if selected_lead["source"] in ["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"] else 0,
                        key="quick_edit_source"
                    )
                    system_type = st.selectbox(
                        "System Type",
                        ["On Grid", "HyBrid", "OFF Grid"],
                        index=["On Grid", "HyBrid", "OFF Grid"].index(selected_lead["system_type"]) if selected_lead["system_type"] in ["On Grid", "HyBrid", "OFF Grid"] else 0,
                        key="quick_edit_system_type"
                    )
                    status = st.selectbox(
                        "Status",
                        ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"],
                        index=["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"].index(selected_lead["status"]) if selected_lead["status"] in ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"] else 0,
                        key="quick_edit_status"
                    )
                    assigned_to = st.selectbox(
                        "Assigned To",
                        get_sales_users_list(),
                        index=get_assigned_to_index(get_sales_users_list(), selected_lead["assigned_to"]),
                        key="quick_edit_assigned_to"
                    )
                    customer_code = st.text_input("Customer Code", value=selected_lead.get("customer_code", ""), key="quick_edit_customer_code")
                
                remarks = st.text_area("Remarks", value=selected_lead.get("remarks", ""), key="quick_edit_remarks")
                
                if st.button("Save Changes", key="quick_edit_save_btn"):
                    # Update the lead in session state
                    for i, lead in enumerate(st.session_state.leads):
                        if lead["id"] == selected_lead_id:
                            # Update lead with new values
                            st.session_state.leads[i].update({
                                "name": lead_name,
                                "phone": phone,
                                "sector": sector,
                                "city": city,
                                "monthly_bill": monthly_bill,
                                "required_system": required_system,
                                "system_type": system_type,
                                "status": status,
                                "source": source,
                                "assigned_to": assigned_to,
                                "customer_code": customer_code,
                                "remarks": remarks
                            })
                            break
                    
                    # Save leads to database
                    db.save_leads(st.session_state.leads)
                    
                    st.session_state.notification = {"type": "success", "message": f"Lead #{selected_lead_id} updated successfully!"}
                    st.rerun()
            
            elif action == "Delete":
                st.warning(f"Are you sure you want to delete Lead #{selected_lead_id} - {filtered_df[filtered_df['id'] == selected_lead_id]['name'].values[0]}?")
                
                if st.button("Confirm Delete", key="confirm_delete_lead_btn"):
                    # Remove the lead from session state
                    st.session_state.leads = [lead for lead in st.session_state.leads if lead["id"] != selected_lead_id]
                    
                    # Save leads to database
                    db.save_leads(st.session_state.leads)
                    
                    st.session_state.notification = {"type": "success", "message": f"Lead #{selected_lead_id} deleted successfully!"}
                    st.rerun()
    
    # Export option
    if not filtered_df.empty:
        if st.button("Export to CSV", key="leads_export_btn"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="leads_export.csv",
                mime="text/csv",
                key="leads_download_btn"
            )

def show_leads_management():
    """Show leads management dashboard with lead creation and editing"""
    st.header("Leads Management")
    
    # Create tabs for different actions
    tab1, tab2, tab3 = st.tabs(["Create Lead", "Edit Lead", "Assign Leads"])
    
    with tab1:
        st.subheader("Create New Lead")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lead_name = st.text_input("Customer Name", key="create_lead_name")
            phone = st.text_input("Phone No", key="create_phone")
            sector = st.text_input("Sector", key="create_sector")
            city = st.selectbox(
                "City",
                ["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"],
                key="create_city"
            )
            monthly_bill = st.number_input("Monthly Avg. Bill", min_value=0, key="create_monthly_bill")
        
        with col2:
            required_system = st.text_input("Required System", key="create_required_system")
            source = st.selectbox(
                "Source",
                ["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"],
                key="create_source"
            )
            system_type = st.selectbox(
                "System Type",
                ["On Grid", "HyBrid", "OFF Grid"],
                key="create_system_type"
            )
            status = st.selectbox(
                "Status",
                ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"],
                key="create_status"
            )
            assigned_to = st.selectbox(
                "Assigned To",
                ["Unassigned"] + get_sales_users_list(),
                index=get_assigned_to_index(["Unassigned"] + get_sales_users_list(), "Unassigned"),
                key="create_assigned_to"
            )
            # Auto-generate customer code and display it as read-only
            next_code = db.get_next_customer_code()
            st.text_input("Customer Code", value=next_code, key="create_customer_code", disabled=True)
        
        remarks = st.text_area("Remarks", key="create_remarks")
        
        if st.button("Create Lead", key="create_lead_btn"):
            # Validate required fields
            if not lead_name or not phone:
                st.error("Customer Name and Phone No are required fields.")
            else:
                # Show confirmation dialog
                confirmation = st.warning("Are you sure you want to create this lead?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Create Lead", key="confirm_create_btn"):
                        # Create a new lead with the form data
                        new_lead = {
                            "id": st.session_state.next_lead_id,
                            "name": lead_name,
                            "phone": phone,
                            "sector": sector,
                            "city": city,
                            "monthly_bill": monthly_bill,
                            "required_system": required_system,
                            "system_type": system_type,
                            "status": status,
                            "source": source,
                            "assigned_to": assigned_to,
                            "customer_code": next_code,  # Use the auto-generated code
                            "remarks": remarks,
                            "date_created": datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        # Add the new lead to the session state
                        st.session_state.leads.append(new_lead)
                        
                        # Increment the next lead ID
                        st.session_state.next_lead_id += 1
                        
                        # Save leads to database
                        db.save_leads(st.session_state.leads)
                        
                        st.session_state.notification = {"type": "success", "message": f"Lead '{lead_name}' created successfully!"}
                        
                        # Use a callback to reset the form
                        if "create_lead_btn" not in st.session_state:
                            st.session_state.create_lead_btn = False
                        
                        # Force a rerun to refresh the page
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_create_btn"):
                        st.rerun()
    
    with tab2:
        st.subheader("Edit Lead")
        
        if not st.session_state.leads:
            st.info("No leads available to edit. Please create some leads first.")
        else:
            # Create a dropdown to select a lead to edit
            lead_options = {lead["id"]: f"Lead #{lead['id']} - {lead['name']}" for lead in st.session_state.leads}
            selected_lead_id = st.selectbox(
                "Select Lead to Edit",
                options=list(lead_options.keys()),
                format_func=lambda x: lead_options[x],
                key="edit_lead_select"
            )
            
            # Find the selected lead
            selected_lead = next((lead for lead in st.session_state.leads if lead["id"] == selected_lead_id), None)
            
            if selected_lead:
                col1, col2 = st.columns(2)
                
                with col1:
                    lead_name = st.text_input("Customer Name", value=selected_lead["name"], key="edit_lead_name")
                    phone = st.text_input("Phone No", value=selected_lead["phone"], key="edit_phone")
                    sector = st.text_input("Sector", value=selected_lead["sector"], key="edit_sector")
                    city = st.selectbox(
                        "City",
                        ["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"],
                        index=["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"].index(selected_lead["city"]) if selected_lead["city"] in ["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"] else 0,
                        key="edit_city"
                    )
                    monthly_bill = st.number_input("Monthly Avg. Bill", min_value=0, value=int(selected_lead["monthly_bill"]), key="edit_monthly_bill")
                
                with col2:
                    required_system = st.text_input("Required System", value=selected_lead["required_system"], key="edit_required_system")
                    source = st.selectbox(
                        "Source",
                        ["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"],
                        index=["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"].index(selected_lead["source"]) if selected_lead["source"] in ["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"] else 0,
                        key="edit_source"
                    )
                    system_type = st.selectbox(
                        "System Type",
                        ["On Grid", "HyBrid", "OFF Grid"],
                        index=["On Grid", "HyBrid", "OFF Grid"].index(selected_lead["system_type"]) if selected_lead["system_type"] in ["On Grid", "HyBrid", "OFF Grid"] else 0,
                        key="edit_system_type"
                    )
                    status = st.selectbox(
                        "Status",
                        ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"],
                        index=["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"].index(selected_lead["status"]) if selected_lead["status"] in ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"] else 0,
                        key="edit_status"
                    )
                    assigned_to = st.selectbox(
                        "Assigned To",
                        ["Unassigned"] + get_sales_users_list(),
                        index=get_assigned_to_index(["Unassigned"] + get_sales_users_list(), selected_lead["assigned_to"]),
                        key="edit_assigned_to"
                    )
                    customer_code = st.text_input("Customer Code", value=selected_lead.get("customer_code", ""), key="edit_customer_code")
                
                remarks = st.text_area("Remarks", value=selected_lead.get("remarks", ""), key="edit_remarks")
                
                if st.button("Update Lead", key="update_lead_btn"):
                    # Update the lead in session state
                    for i, lead in enumerate(st.session_state.leads):
                        if lead["id"] == selected_lead_id:
                            # Update lead with new values
                            st.session_state.leads[i].update({
                                "name": lead_name,
                                "phone": phone,
                                "sector": sector,
                                "city": city,
                                "monthly_bill": monthly_bill,
                                "required_system": required_system,
                                "system_type": system_type,
                                "status": status,
                                "source": source,
                                "assigned_to": assigned_to,
                                "customer_code": customer_code,
                                "remarks": remarks
                            })
                            break
                    
                    # Save leads to database
                    db.save_leads(st.session_state.leads)
                    
                    st.session_state.notification = {"type": "success", "message": f"Lead #{selected_lead_id} updated successfully!"}
                    st.rerun()
    
    with tab3:
        st.subheader("Bulk Lead Assignment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "New", "Contacted", "Qualified", "Proposal", "Closed Won", "Closed Lost"],
                key="bulk_status_filter"
            )
        
        with col2:
            assign_to = st.selectbox(
                "Assign To",
                ["Unassigned"] + get_sales_users_list(),
                index=get_assigned_to_index(["Unassigned"] + get_sales_users_list(), "Unassigned"),
                key="bulk_assign_to"
            )
        
        # Generate sample leads based on filter
        filtered_leads = []
        for i in range(1, 6):
            status = "New" if status_filter == "All" else status_filter
            filtered_leads.append({
                "id": i,
                "name": f"Lead {i}",
                "company": f"Company {i}",
                "status": status,
                "current_owner": random.choice(get_sales_users_list())
            })
        
        filtered_leads_df = pd.DataFrame(filtered_leads)
        
        # Display leads with checkboxes
        st.dataframe(filtered_leads_df, use_container_width=True)
        
        if st.button("Assign Selected Leads", key="bulk_assign_btn"):
            st.session_state.notification = {"type": "success", "message": f"Selected leads assigned to {assign_to} successfully!"}

def show_user_accounts():
    """Show user accounts management dashboard"""
    st.header("User Accounts")
    
    # Create tabs for different actions
    tab1, tab2 = st.tabs(["User List", "Create User"])
    
    with tab1:
        st.subheader("User List")
        
        # Get users from session state
        users = st.session_state.users
        
        users_df = pd.DataFrame(users)
        st.dataframe(users_df, use_container_width=True)
        
        # User actions
        st.subheader("User Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            user_to_edit = st.selectbox(
                "Select User",
                [f"{user['name']} ({user['username']})" for user in users],
                key="user_to_edit"
            )
            selected_user_index = [f"{user['name']} ({user['username']})" for user in users].index(user_to_edit)
            selected_user = users[selected_user_index]
        
        with col2:
            action = st.selectbox(
                "Action",
                ["Edit", "Delete", "Deactivate", "Reset Password"],
                key="user_action"
            )
        
        if action == "Edit":
            st.subheader(f"Edit User: {selected_user['name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username", value=selected_user['username'], key="edit_user_username")
                full_name = st.text_input("Full Name", value=selected_user['name'], key="edit_user_name")
                email = st.text_input("Email", value=selected_user['email'], key="edit_user_email")
            
            with col2:
                role = st.selectbox(
                    "Role",
                    ["admin", "sales"],
                    index=0 if selected_user['role'] == "admin" else 1,
                    key="edit_user_role"
                )
                status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=0 if selected_user['status'] == "Active" else 1,
                    key="edit_user_status"
                )
                new_password = st.text_input("New Password (leave blank to keep current)", type="password", key="edit_user_password")
            
            if st.button("Save Changes", key="save_user_changes_btn"):
                # Update the user in session state
                update_data = {
                    "username": username,
                    "name": full_name,
                    "email": email,
                    "role": role,
                    "status": status
                }
                
                # Only update password if a new one was provided
                if new_password:
                    update_data["password"] = new_password
                
                for i, user in enumerate(st.session_state.users):
                    if user["id"] == selected_user["id"]:
                        # Update user with new values
                        st.session_state.users[i].update(update_data)
                        break
                
                # Save users to database
                db.save_users(st.session_state.users)
                
                st.session_state.notification = {"type": "success", "message": f"User '{full_name}' updated successfully!"}
                st.rerun()
        
        elif action == "Delete":
            if selected_user['username'] == "admin":
                st.error("Cannot delete the admin user!")
            else:
                st.warning(f"Are you sure you want to delete user '{selected_user['name']}'? This action cannot be undone.")
                
                if st.button("Confirm Delete", key="confirm_delete_user_btn"):
                    # Remove the user from session state
                    st.session_state.users = [user for user in st.session_state.users if user["id"] != selected_user["id"]]
                    
                    # Save users to database
                    db.save_users(st.session_state.users)
                    
                    st.session_state.notification = {"type": "success", "message": f"User '{selected_user['name']}' deleted successfully!"}
                    st.rerun()
        
        elif action == "Deactivate":
            if selected_user['username'] == "admin":
                st.error("Cannot deactivate the admin user!")
            else:
                new_status = "Inactive" if selected_user['status'] == "Active" else "Active"
                action_text = "deactivate" if new_status == "Inactive" else "activate"
                
                st.warning(f"Are you sure you want to {action_text} user '{selected_user['name']}'?")
                
                if st.button(f"Confirm {action_text.capitalize()}", key="confirm_status_change_btn"):
                    # Update the user status in session state
                    for i, user in enumerate(st.session_state.users):
                        if user["id"] == selected_user["id"]:
                            # Update user status
                            st.session_state.users[i]["status"] = new_status
                            break
                    
                    # Save users to database
                    db.save_users(st.session_state.users)
                    
                    st.session_state.notification = {"type": "success", "message": f"User '{selected_user['name']}' {action_text}d successfully!"}
                    st.rerun()
        
        elif action == "Reset Password":
            st.subheader(f"Reset Password for: {selected_user['name']}")
            
            new_password = st.text_input("New Password", type="password", key="reset_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_reset_password")
            
            if st.button("Reset Password", key="reset_password_btn"):
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif not new_password:
                    st.error("Password cannot be empty!")
                else:
                    # Update the user's password in session state
                    for i, user in enumerate(st.session_state.users):
                        if user["id"] == selected_user["id"]:
                            st.session_state.users[i]["password"] = new_password
                            break
                    
                    # Save users to database
                    db.save_users(st.session_state.users)
                    
                    st.session_state.notification = {"type": "success", "message": f"Password for '{selected_user['name']}' reset successfully!"}
                    st.rerun()
    
    with tab2:
        st.subheader("Create New User")
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", key="new_username")
            full_name = st.text_input("Full Name", key="new_full_name")
            email = st.text_input("Email", key="new_email")
        
        with col2:
            role = st.selectbox(
                "Role",
                ["admin", "sales"],
                key="new_role"
            )
            password = st.text_input("Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="new_confirm_password")
        
        if st.button("Create User", key="create_user_btn"):
            if password == confirm_password:
                # Create a new user with the form data
                new_user = {
                    "id": len(st.session_state.users) + 1,
                    "username": username,
                    "name": full_name,
                    "email": email,
                    "role": role,
                    "status": "Active",
                    "password": password
                }
                
                # Add the new user to the session state
                st.session_state.users.append(new_user)
                
                # Save users to database
                db.save_users(st.session_state.users)
                
                st.session_state.notification = {"type": "success", "message": f"User '{username}' created successfully!"}
                st.rerun()
            else:
                st.session_state.notification = {"type": "error", "message": "Passwords do not match!"}

if __name__ == "__main__":
    admin_view()
