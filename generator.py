import os
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from typing import TypedDict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

# Set Google API key for Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Define state for LangGraph
class ReportState(TypedDict):
    institute_name: str
    student_name: str
    enrollment_number: str
    organization: str
    external_guide_name: str
    external_guide_contact: str
    internal_guide_name: str
    prompt: str
    work_done: list
    plans: list
    hours: str
    output_file: str

# Helper function to generate text with Gemini
def generate_text(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating text: {str(e)}"

# Step 1: Generate work done
def generate_work_done(state: ReportState) -> ReportState:
    prompt = f"Based on this work description: {state['prompt']}, generate a list of 2-3 concise tasks completed last week for a college internship report. Each task should be one sentence."
    work_text = generate_text(prompt)
    tasks = [task.strip() for task in work_text.split('\n') if task.strip()]
    state["work_done"] = tasks[:3]  # Limit to 3 tasks
    return state

# Step 2: Generate plans for next week
def generate_plans(state: ReportState) -> ReportState:
    prompt = f"Based on this work description: {state['prompt']}, generate a list of 2-3 concise tasks planned for next week for a college internship report. Each task should be one sentence."
    plans_text = generate_text(prompt)
    plans = [plan.strip() for plan in plans_text.split('\n') if plan.strip()]
    state["plans"] = plans[:3]  # Limit to 3 plans
    return state

# Function to create PDF report
def create_pdf_report(
    institute_name: str,
    student_name: str,
    enrollment_number: str,
    organization: str,
    external_guide_name: str,
    external_guide_contact: str,
    internal_guide_name: str,
    work_done: list,
    plans: list,
    hours: str
) -> str:
    output_file = f"report_{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        name='TitleCustom',
        fontSize=14,
        leading=16,
        alignment=1,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        name='SubtitleCustom',
        fontSize=12,
        leading=14,
        alignment=1,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        name='BodyCustom',
        fontSize=10,
        leading=12,
        spaceAfter=8
    )
    table_label_style = ParagraphStyle(
        name='TableLabelCustom',
        fontSize=10,
        leading=12,
        spaceBefore=8,
        spaceAfter=4
    )

    # Institute Header
    story.append(Paragraph(institute_name.upper(), title_style))
    story.append(Paragraph("Ahmedabad, Gujarat", subtitle_style))
    story.append(Paragraph("Ph: 07967129000 Website: www.ljku.edu.in", subtitle_style))
    story.append(Paragraph("Student's Weekly Report of Internship", title_style))
    story.append(Spacer(1, 12))

    # Student and Organization Details (Table)
    details_data = [
        ["Student Name:", student_name],
        ["Enrollment Number:", enrollment_number],
        ["Name of Organization:", organization],
        ["External Guide Name:", external_guide_name],
        ["External Guide Contact Details:", external_guide_contact],
        ["Internal Faculty Guide Name:", internal_guide_name]
    ]
    details_table = Table(details_data, colWidths=[150, 350])
    details_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 12))

    # Work Done
    story.append(Paragraph("Work done in last Week with description:", table_label_style))
    for i, task in enumerate(work_done, 1):
        story.append(Paragraph(f"{i}. {task}", body_style))
    story.append(Spacer(1, 8))

    # Plans for Next Week
    story.append(Paragraph("Plans for next week:", table_label_style))
    for i, plan in enumerate(plans, 1):
        story.append(Paragraph(f"{i}. {plan}", body_style))
    story.append(Spacer(1, 8))

    # Total Working Hours
    story.append(Paragraph(f"Total Working Hrs: {hours}", body_style))
    story.append(Spacer(1, 8))

    # Signature
    story.append(Paragraph("Signature of Student: ____________________", body_style))
    story.append(Spacer(1, 12))

    # Performance Rating
    story.append(Paragraph("The above entries are correct and the admin of work done by Trainee is", body_style))
    rating_data = [
        ["Excellent", "Very Good", "Good", "Fair", "Below Average", "Poor"],
        ["", "", "", "", "", ""]
    ]
    rating_table = Table(rating_data, colWidths=[80] * 6)
    rating_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(rating_table)
    story.append(Spacer(1, 12))

    # Guide Signatures
    story.append(Paragraph("Signature of External Guide with Company Seal: ____________________", body_style))
    story.append(Paragraph("Date: ____________________", body_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Signature of Internal Guide: ____________________", body_style))
    story.append(Paragraph("Date: ____________________", body_style))

    # Build PDF
    doc.build(story)
    return output_file

# Define LangGraph workflow
workflow = StateGraph(ReportState)
workflow.add_node("generate_work_done", generate_work_done)
workflow.add_node("generate_plans", generate_plans)

# Define edges
workflow.set_entry_point("generate_work_done")
workflow.add_edge("generate_work_done", "generate_plans")
workflow.add_edge("generate_plans", END)

# Compile workflow
app = workflow.compile()

# Function to run the report generator
def generate_report(
    institute_name: str,
    student_name: str,
    enrollment_number: str,
    organization: str,
    external_guide_name: str,
    external_guide_contact: str,
    internal_guide_name: str,
    prompt: str,
    hours: str
) -> ReportState:
    initial_state = ReportState(
        institute_name=institute_name,
        student_name=student_name,
        enrollment_number=enrollment_number,
        organization=organization,
        external_guide_name=external_guide_name,
        external_guide_contact=external_guide_contact,
        internal_guide_name=internal_guide_name,
        prompt=prompt,
        work_done=[],
        plans=[],
        hours=hours,
        output_file=""
    )
    result = app.invoke(initial_state)
    return result
