# AIzaSyBIUdVWpgw696EXvTdGN0aKxXqeySxCJOM
# conda activate report_gen
# conda install -c conda-forge streamlit

import streamlit as st
from generator import generate_report, create_pdf_report

# Streamlit app
st.title("Weekly Internship Report Generator")
st.write("Enter your details and work description to generate a report matching your college's format. Edit tasks and plans before downloading.")

# Input fields
institute_name = st.text_input("Institute Name", placeholder="e.g., SAL Institute of Technology and Engineering Research")
student_name = st.text_input("Student Name", placeholder="e.g., Bhalani Madhav Deepakkumar")
enrollment_number = st.text_input("Enrollment Number", placeholder="e.g., 220673107002")
organization = st.text_input("Name of Organization", placeholder="e.g., Theta Technolabs Pvt. Ltd.")
external_guide_name = st.text_input("External Guide Name", placeholder="e.g., Ajay Sukhadiya")
external_guide_contact = st.text_input("External Guide Contact Details", placeholder="e.g., Email: ajay.sukhadiya@thetatechnolabs.com")
internal_guide_name = st.text_input("Internal Faculty Guide Name", placeholder="e.g., Dr. Nimisha Patel")
prompt = st.text_area("Work Description", placeholder="e.g., Worked on developing a web application with product pages and login forms...")
hours = st.text_input("Total Working Hours", placeholder="e.g., 40")

# Initialize session state
if 'report_state' not in st.session_state:
    st.session_state.report_state = None
if 'show_edit' not in st.session_state:
    st.session_state.show_edit = False

# Generate button
if st.button("Generate Report"):
    if all([institute_name, student_name, enrollment_number, organization, external_guide_name, external_guide_contact, internal_guide_name, prompt, hours]):
        with st.spinner("Generating report content..."):
            try:
                st.session_state.report_state = generate_report(
                    institute_name,
                    student_name,
                    enrollment_number,
                    organization,
                    external_guide_name,
                    external_guide_contact,
                    internal_guide_name,
                    prompt,
                    hours
                )
                st.session_state.show_edit = True
                st.success("Report content generated! Edit below and finalize.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Please fill in all fields.")

# Editable fields
if st.session_state.show_edit and st.session_state.report_state:
    st.subheader("Edit Report Content")
    
    # Work Done
    st.write("Work Done Last Week:")
    edited_work_done = []
    for i, task in enumerate(st.session_state.report_state["work_done"], 1):
        edited_task = st.text_input(f"Task {i}", value=task, key=f"work_{i}")
        edited_work_done.append(edited_task)
    
    # Plans for Next Week
    st.write("Plans for Next Week:")
    edited_plans = []
    for i, plan in enumerate(st.session_state.report_state["plans"], 1):
        edited_plan = st.text_input(f"Plan {i}", value=plan, key=f"plan_{i}")
        edited_plans.append(edited_plan)

    # Finalize and download
    if st.button("Finalize and Download PDF"):
        with st.spinner("Creating PDF..."):
            try:
                output_file = create_pdf_report(
                    institute_name,
                    student_name,
                    enrollment_number,
                    organization,
                    external_guide_name,
                    external_guide_contact,
                    internal_guide_name,
                    edited_work_done,
                    edited_plans,
                    hours
                )
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="Download Report",
                        data=file,
                        file_name=output_file,
                        mime="application/pdf"
                    )
                st.success(f"Report generated: {output_file}")
                st.session_state.show_edit = False
                st.session_state.report_state = None
            except Exception as e:
                st.error(f"Error: {str(e)}")