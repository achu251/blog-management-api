import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_invoice_pdf(username: str, plan_name: str, price: float, start_date: datetime, end_date: datetime, transaction_id: str) -> str:
    # Ensure the directory exists
    invoices_dir = os.path.join("media", "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    filename = f"invoice_{transaction_id}.pdf"
    filepath = os.path.join(invoices_dir, filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Draw the invoice content
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "INVOICE")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Billed To: {username}")
    c.drawString(50, height - 120, f"Transaction ID: {transaction_id}")
    
    c.drawString(50, height - 160, f"Plan: {plan_name}")
    c.drawString(50, height - 180, f"Price: ${price:.2f}")
    
    c.drawString(50, height - 220, f"Start Date: {start_date.strftime('%Y-%m-%d')}")
    c.drawString(50, height - 240, f"End Date: {end_date.strftime('%Y-%m-%d')}")
    
    c.drawString(50, height - 300, "Thank you for subscribing to Blog Management API!")
    
    c.save()
    
    return f"/media/invoices/{filename}"
