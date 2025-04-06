import streamlit as st
from datetime import datetime
from database import init_db, add_employee, delete_employee, get_employees, add_task, get_summary

init_db()

st.set_page_config(page_title="Task Manager", layout="wide")
st.title("Task Manager - Admin Panel")

departments = ["Web Development", "Accountant", "Social Media", "Artificial Intelligence", "HR", "Marketing"]
department = st.sidebar.selectbox("Select Department", departments)

st.header(f"📂 Department: {department}")



with st.sidebar.expander("👥 Manage Employees"):
    st.subheader("Add Employee")
    passkey = st.text_input("Enter Admin Passkey", type="password", key="add_pass")
    emp_id = st.number_input("Employee ID", step=1, format="%d", key="emp_id")
    name = st.text_input("Employee Name", key="emp_name")
    phone = st.text_input("Phone Number", key="emp_phone")
    email = st.text_input("Email", key="emp_email")
    join_date = st.date_input("Joining Date", key="emp_join_date")

    if st.button("Add", key="add_button"):
        if passkey == "admin123":
            if add_employee(emp_id, name, phone, email, department, join_date.strftime("%Y-%m-%d")):
                st.success("Employee added successfully!")
            else:
                st.error("ID or Email already exists.")
        else:
            st.error("Incorrect passkey!")

    st.subheader("Delete Employee")
    emp_list = get_employees(department)
    emp_names = [f"{emp[1]} (ID: {emp[0]})" for emp in emp_list]
    emp_ids = [emp[0] for emp in emp_list]
    if emp_list:
        selected = st.selectbox("Select Employee", emp_names, key="delete_employee")
        selected_id = emp_ids[emp_names.index(selected)]
        del_pass = st.text_input("Confirm Passkey to Delete", type="password", key="del_pass")
        if st.button("Delete", key="delete_button"):
            if del_pass == "admin123":
                delete_employee(selected_id)
                st.warning("Employee deleted.")
            else:
                st.error("Wrong passkey.")
    else:
        st.info("No employees in this department.")

#
with st.expander("📝 Assign Today's Task"):
    st.subheader("Assign Task")
    today = datetime.now().strftime("%Y-%m-%d")
    st.markdown(f"**Today's Date:** `{today}`")

    emp_list = get_employees(department)
    if emp_list:
        emp_names = [f"{emp[1]} (ID: {emp[0]})" for emp in emp_list]
        selected = st.selectbox("Select Employee", emp_names, key="assign_task_employee")
        selected_id = emp_list[emp_names.index(selected)][0]
        task_desc = st.text_area("Task Description")

        if st.button("Assign Task"):
            add_task(selected_id, task_desc, is_done=False)
            st.success("Task assigned for today.")

        if st.button("Mark as Completed"):
            add_task(selected_id, task_desc, is_done=True)
            st.success("Marked as completed.")

        if st.button("Mark as Incomplete"):
            add_task(selected_id, task_desc, is_done=False)
            st.info("Marked as incomplete.")
    else:
        st.info("Add employees to assign tasks.")

# 

with st.expander("📊 Monthly Task Summary"):
    st.subheader(f"Last 1 Month Summary for {department}")
    data = get_summary(department)

    if data:
        from pandas import DataFrame
        df = DataFrame(data, columns=["Employee", "Joining Date", "Task Date", "Task", "Status"])
        df["Status"] = df["Status"].apply(lambda x: "✅" if x == 1 else "❌")
        st.dataframe(df)
    else:
        st.info("No tasks found in the past month.")
