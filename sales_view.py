import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import database as db

from auth import logout_user
from data import load_data, get_filtered_data

def sales_rep_view(username):
    """Sales rep dashboard view with limited access to their own performance data"""
    # Display logo and title together
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        st.image("images/logo.png", width=80)
    with col_title:
        st.title("Sales Representative Dashboard")
    
    st.sidebar.title(f"Welcome, {st.session_state.display_name}")
    
    # Load data
    sales_data = load_data()
    
    # Filter data for the current sales rep
    # In a real app, this would be based on the user's identity
    # For this mock app, we'll use the username to filter
    rep_name = st.session_state.display_name
    rep_data = sales_data[sales_data["sales_rep"] == rep_name]
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["My Performance", "My Leads", "Product Analysis", "Regional Analysis"],
        key="sales_nav"
    )
    
    if st.sidebar.button("Logout", key="sales_logout_btn"):
        logout_user()
        st.rerun()
    
    # My Performance page
    if page == "My Performance":
        show_my_performance(rep_data, rep_name)
    
    # My Leads page
    elif page == "My Leads":
        show_my_leads(st.session_state.display_name)
    
    # Product Analysis page (limited to rep's data)
    elif page == "Product Analysis":
        show_product_analysis(rep_data, rep_name)
    
    # Regional Analysis page (limited to rep's data)
    elif page == "Regional Analysis":
        show_regional_analysis(rep_data, rep_name)

def show_my_performance(rep_data, rep_name):
    """Show sales rep's personal performance dashboard"""
    st.header(f"My Performance - {rep_name}")
    
    # KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    
    rep_revenue = rep_data["revenue"].sum()
    rep_units = rep_data["units_sold"].sum()
    rep_avg_order = rep_revenue / len(rep_data) if len(rep_data) > 0 else 0
    rep_orders = len(rep_data)
    
    col1.metric("Total Revenue", f"${rep_revenue:,.2f}")
    col2.metric("Total Units Sold", f"{rep_units:,}")
    col3.metric("Avg Order Value", f"${rep_avg_order:,.2f}")
    col4.metric("Total Orders", f"{rep_orders:,}")
    
    # Time period filter
    st.subheader("Filter by Date")
    date_range = st.date_input(
        "Select Date Range",
        value=(
            datetime.now() - timedelta(days=30),
            datetime.now()
        ),
        key="sales_date_range"
    )
    
    # Convert date_range to string format for filtering
    start_date = date_range[0].strftime("%Y-%m-%d") if len(date_range) > 0 else None
    end_date = date_range[1].strftime("%Y-%m-%d") if len(date_range) > 1 else None
    
    # Filter data based on date range
    filters = {}
    if start_date and end_date:
        filters['start_date'] = start_date
        filters['end_date'] = end_date
    
    filtered_data = get_filtered_data(rep_data, filters)
    
    # Performance trend
    st.subheader("My Revenue Trend")
    daily_revenue = filtered_data.groupby("date")["revenue"].sum().reset_index()
    daily_revenue["date"] = pd.to_datetime(daily_revenue["date"])
    daily_revenue = daily_revenue.sort_values("date")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_revenue["date"], daily_revenue["revenue"], marker='o', linestyle='-')
    ax.set_title(f"Daily Revenue Trend for {rep_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    # Product mix
    st.subheader("My Product Mix")
    product_mix = filtered_data.groupby("product")["revenue"].sum().reset_index()
    product_mix = product_mix.sort_values("revenue", ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="product", y="revenue", data=product_mix, ax=ax)
    ax.set_title(f"Product Mix for {rep_name}")
    ax.set_xlabel("Product")
    ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Regional performance
    st.subheader("My Regional Performance")
    region_mix = filtered_data.groupby("region")["revenue"].sum().reset_index()
    region_mix = region_mix.sort_values("revenue", ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="region", y="revenue", data=region_mix, ax=ax)
    ax.set_title(f"Regional Performance for {rep_name}")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Recent sales
    st.subheader("My Recent Sales")
    recent_sales = filtered_data.sort_values("date", ascending=False).head(10)
    st.dataframe(recent_sales)

def show_my_leads(rep_name):
    """Show leads assigned to the current sales rep"""
    st.header("My Leads")
    
    # Create tabs for viewing and adding leads
    tab1, tab2 = st.tabs(["View My Leads", "Add New Lead"])
    
    with tab1:
        # Get leads from session state
        leads = st.session_state.leads
        
        # Convert to DataFrame
        leads_df = pd.DataFrame(leads)
        
        # Filter for leads assigned to this rep
        if leads_df.empty:
            st.info("No leads found assigned to you.")
        else:
            # Filter leads assigned to this rep
            my_leads = leads_df[leads_df["assigned_to"] == rep_name]
            
            if my_leads.empty:
                st.info(f"No leads are currently assigned to you.")
            else:
                # Add filters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_filter = st.selectbox(
                        "Status",
                        ["All", "Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"],
                        key="my_leads_status_filter"
                    )
                
                with col2:
                    source_filter = st.selectbox(
                        "Source",
                        ["All", "Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"],
                        key="my_leads_source_filter"
                    )
                
                with col3:
                    city_filter = st.selectbox(
                        "City",
                        ["All", "Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"],
                        key="my_leads_city_filter"
                    )
                
                # Date range filter
                date_range = st.date_input(
                    "Date Range",
                    value=(
                        datetime.now() - timedelta(days=30),
                        datetime.now()
                    ),
                    key="my_leads_date_range"
                )
                
                # Apply filters
                filtered_df = my_leads.copy()
                
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df["status"] == status_filter]
                
                if source_filter != "All":
                    filtered_df = filtered_df[filtered_df["source"] == source_filter]
                
                if city_filter != "All":
                    filtered_df = filtered_df[filtered_df["city"] == city_filter]
                
                if len(date_range) >= 2:
                    start_date = date_range[0].strftime("%Y-%m-%d")
                    end_date = date_range[1].strftime("%Y-%m-%d")
                    filtered_df = filtered_df[(filtered_df["date_created"] >= start_date) & (filtered_df["date_created"] <= end_date)]
                
                # Display leads
                st.subheader(f"Showing {len(filtered_df)} leads")
                
                if filtered_df.empty:
                    st.info("No leads match your filter criteria.")
                else:
                    # Display the leads in a table
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
                
                # Lead details section
                st.subheader("Lead Details")
                
                # Select a lead to view details
                selected_lead_id = st.selectbox(
                    "Select Lead",
                    filtered_df["id"].tolist(),
                    format_func=lambda x: f"Lead #{x} - {filtered_df[filtered_df['id'] == x]['name'].values[0]}",
                    key="my_lead_select"
                )
                
                # Get the selected lead data
                selected_lead = filtered_df[filtered_df["id"] == selected_lead_id].iloc[0]
                
                # Display lead details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Customer Name:** {selected_lead['name']}")
                    st.write(f"**Phone No:** {selected_lead['phone']}")
                    st.write(f"**Date Created:** {selected_lead['date_created']}")
                
                with col2:
                    st.write(f"**Assigned To:** {selected_lead['assigned_to']}")
                    st.write(f"**ID:** {selected_lead['id']}")
                
                # Allow sales rep to update specific fields
                st.subheader("Edit Lead Information")
                
                # Editable fields
                col1, col2 = st.columns(2)
                
                with col1:
                    sector = st.text_input(
                        "Sector",
                        value=selected_lead['sector'],
                        key="edit_sector"
                    )
                    
                    city = st.selectbox(
                        "City",
                        ["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"],
                        index=["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"].index(selected_lead['city']),
                        key="edit_city"
                    )
                    
                    required_system = st.text_input(
                        "Required System",
                        value=selected_lead['required_system'],
                        key="edit_required_system"
                    )
                    
                    system_type = st.selectbox(
                        "System Type",
                        ["On Grid", "HyBrid", "OFF Grid"],
                        index=["On Grid", "HyBrid", "OFF Grid"].index(selected_lead['system_type']),
                        key="edit_system_type"
                    )
                
                with col2:
                    monthly_bill = st.text_input(
                        "Monthly Avg. Bill",
                        value=selected_lead['monthly_bill'],
                        key="edit_monthly_bill"
                    )
                    
                    status = st.selectbox(
                        "Status",
                        ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"],
                        index=["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"].index(selected_lead['status']) if selected_lead['status'] in ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"] else 0,
                        key="edit_status"
                    )
                    
                    source = st.selectbox(
                        "Source",
                        ["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"],
                        index=["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"].index(selected_lead['source']),
                        key="edit_source"
                    )
                
                remarks = st.text_area(
                    "Remarks",
                    value=selected_lead['remarks'],
                    key="edit_remarks"
                )
                
                if st.button("Save Changes", key="save_lead_changes_btn"):
                    # Update the lead in session state
                    for i, lead in enumerate(st.session_state.leads):
                        if lead["id"] == selected_lead_id:
                            # Update only the editable fields
                            st.session_state.leads[i].update({
                                "sector": sector,
                                "city": city,
                                "required_system": required_system,
                                "system_type": system_type,
                                "monthly_bill": monthly_bill,
                                "status": status,
                                "source": source,
                                "remarks": remarks
                            })
                            break
                    
                    # Save leads to database
                    db.save_leads(st.session_state.leads)
                    
                    st.success(f"Lead #{selected_lead_id} updated successfully!")
                    st.rerun()

    with tab2:
        st.subheader("Add New Lead")
        st.write("Use this form to add a new lead you've acquired directly. It will be automatically assigned to you.")
        
        # Create lead form
        col1, col2 = st.columns(2)
        
        with col1:
            lead_name = st.text_input("Customer Name", key="sales_create_lead_name")
            phone = st.text_input("Phone No", key="sales_create_phone")
            sector = st.text_input("Sector", key="sales_create_sector")
            city = st.selectbox(
                "City",
                ["Islamabad", "RawalPindi", "Taxila", "Wahcantt", "Lahore", "Karachi"],
                key="sales_create_city"
            )
            monthly_bill = st.text_input("Monthly Avg. Bill", key="sales_create_monthly_bill")
        
        with col2:
            required_system = st.text_input("Required System", key="sales_create_required_system")
            source = st.selectbox(
                "Source",
                ["Organic Search", "Paid Ads", "Social Media", "Referral", "Walk-In"],
                key="sales_create_source"
            )
            system_type = st.selectbox(
                "System Type",
                ["On Grid", "HyBrid", "OFF Grid"],
                key="sales_create_system_type"
            )
            status = st.selectbox(
                "Status",
                ["Open", "Fake Lead", "Lost", "Not Interested", "Quote Shared", "Won"],
                key="sales_create_status"
            )
            # Auto-generate customer code and display it as read-only
            next_code = db.get_next_customer_code()
            st.text_input("Customer Code", value=next_code, key="sales_create_customer_code", disabled=True)
        
        remarks = st.text_area("Remarks", key="sales_create_remarks")
        
        if st.button("Create Lead", key="sales_create_lead_btn"):
            # Validate required fields
            if not lead_name or not phone:
                st.error("Customer Name and Phone No are required fields.")
            else:
                # Show confirmation dialog
                confirmation = st.warning("Are you sure you want to create this lead?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Create Lead", key="sales_confirm_create_btn"):
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
                            "assigned_to": rep_name,  # Automatically assign to the current sales rep
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
                        
                        st.success(f"Lead '{lead_name}' created successfully and assigned to you!")
                        
                        # Force a rerun to refresh the page
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="sales_cancel_create_btn"):
                        st.rerun()

def show_product_analysis(rep_data, rep_name):
    """Show product analysis dashboard limited to the sales rep's data"""
    st.header(f"Product Analysis - {rep_name}")
    
    # Select product
    selected_product = st.selectbox(
        "Select Product",
        ["All"] + list(rep_data["product"].unique()),
        key="sales_product_select"
    )
    
    # Filter data based on selected product
    filters = {}
    if selected_product != "All":
        filters['product'] = selected_product
    
    filtered_data = get_filtered_data(rep_data, filters)
    
    # KPI metrics for the selected product
    col1, col2, col3 = st.columns(3)
    
    product_revenue = filtered_data["revenue"].sum()
    product_units = filtered_data["units_sold"].sum()
    product_avg_price = product_revenue / product_units if product_units > 0 else 0
    
    col1.metric("Total Revenue", f"${product_revenue:,.2f}")
    col2.metric("Total Units Sold", f"{product_units:,}")
    col3.metric("Avg Unit Price", f"${product_avg_price:,.2f}")
    
    # Product performance trend
    st.subheader("Performance Trend")
    product_daily_sales = filtered_data.groupby("date")["revenue"].sum().reset_index()
    product_daily_sales["date"] = pd.to_datetime(product_daily_sales["date"])
    product_daily_sales = product_daily_sales.sort_values("date")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(product_daily_sales["date"], product_daily_sales["revenue"], marker='o', linestyle='-')
    ax.set_title(f"Daily Revenue Trend for {selected_product if selected_product != 'All' else 'All Products'}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    # Product performance by region
    st.subheader("Performance by Region")
    product_region = filtered_data.groupby("region")["revenue"].sum().reset_index()
    product_region = product_region.sort_values("revenue", ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="region", y="revenue", data=product_region, ax=ax)
    ax.set_title(f"Regional Performance for {selected_product if selected_product != 'All' else 'All Products'}")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Units sold vs revenue
    st.subheader("Units Sold vs Revenue")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(filtered_data["units_sold"], filtered_data["revenue"])
    ax.set_title(f"Units Sold vs Revenue for {selected_product if selected_product != 'All' else 'All Products'}")
    ax.set_xlabel("Units Sold")
    ax.set_ylabel("Revenue ($)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

def show_regional_analysis(rep_data, rep_name):
    """Show regional analysis dashboard limited to the sales rep's data"""
    st.header(f"Regional Analysis - {rep_name}")
    
    # Select region
    selected_region = st.selectbox(
        "Select Region",
        ["All"] + list(rep_data["region"].unique()),
        key="sales_region_select"
    )
    
    # Filter data based on selected region
    filters = {}
    if selected_region != "All":
        filters['region'] = selected_region
    
    filtered_data = get_filtered_data(rep_data, filters)
    
    # KPI metrics for the selected region
    col1, col2, col3 = st.columns(3)
    
    region_revenue = filtered_data["revenue"].sum()
    region_units = filtered_data["units_sold"].sum()
    region_avg_order = region_revenue / len(filtered_data) if len(filtered_data) > 0 else 0
    
    col1.metric("Total Revenue", f"${region_revenue:,.2f}")
    col2.metric("Total Units Sold", f"{region_units:,}")
    col3.metric("Avg Order Value", f"${region_avg_order:,.2f}")
    
    # Region performance comparison
    st.subheader("My Regional Performance")
    region_performance = rep_data.groupby("region")["revenue"].sum().reset_index()
    region_performance = region_performance.sort_values("revenue", ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="region", y="revenue", data=region_performance, ax=ax)
    ax.set_title(f"Revenue by Region for {rep_name}")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Product mix by region
    st.subheader("Product Mix in Region")
    region_product_mix = filtered_data.groupby("product")["revenue"].sum().reset_index()
    region_product_mix = region_product_mix.sort_values("revenue", ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="product", y="revenue", data=region_product_mix, ax=ax)
    ax.set_title(f"Product Mix for {selected_region if selected_region != 'All' else 'All Regions'}")
    ax.set_xlabel("Product")
    ax.set_ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Time trend for region
    st.subheader("Regional Performance Over Time")
    region_time = filtered_data.groupby("date")["revenue"].sum().reset_index()
    region_time["date"] = pd.to_datetime(region_time["date"])
    region_time = region_time.sort_values("date")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(region_time["date"], region_time["revenue"], marker='o', linestyle='-')
    ax.set_title(f"Daily Revenue Trend for {selected_region if selected_region != 'All' else 'All Regions'}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
