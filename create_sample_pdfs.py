#!/usr/bin/env python3
"""
Create sample PDF files for testing multi-PDF analysis
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import random

def create_financial_report_pdf(filename, company_name, year):
    """Create a sample financial report PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"<b>{company_name} Annual Report {year}</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Financial data
    revenue = random.randint(50000, 500000)
    profit = random.randint(5000, 50000)
    employees = random.randint(50, 1000)
    
    content = f"""
    <b>Executive Summary</b><br/>
    This report presents the financial performance of {company_name} for the year {year}.<br/><br/>
    
    <b>Key Financial Metrics:</b><br/>
    • Total Revenue: ${revenue:,}<br/>
    • Net Profit: ${profit:,}<br/>
    • Number of Employees: {employees}<br/>
    • Profit Margin: {(profit/revenue)*100:.1f}%<br/><br/>
    
    <b>Performance Analysis:</b><br/>
    The company showed {'strong' if profit > 20000 else 'moderate'} performance this year.
    Revenue {'increased' if revenue > 200000 else 'remained stable'} compared to previous years.<br/><br/>
    
    <b>Future Projections:</b><br/>
    Based on current trends, we project {random.randint(5, 25)}% growth in the next fiscal year.
    """
    
    story.append(Paragraph(content, styles['Normal']))
    doc.build(story)
    print(f"✅ Created {filename}")

def create_sales_report_pdf(filename, quarter, year):
    """Create a sample sales report PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph(f"<b>Sales Report Q{quarter} {year}</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Sales data
    units_sold = random.randint(1000, 10000)
    avg_price = random.randint(50, 500)
    total_sales = units_sold * avg_price
    
    content = f"""
    <b>Quarterly Sales Summary</b><br/>
    Report for Q{quarter} {year}<br/><br/>
    
    <b>Sales Metrics:</b><br/>
    • Units Sold: {units_sold:,}<br/>
    • Average Unit Price: ${avg_price}<br/>
    • Total Sales: ${total_sales:,}<br/>
    • Sales Growth: {random.randint(-10, 30):+}%<br/><br/>
    
    <b>Regional Performance:</b><br/>
    • North Region: {random.randint(20, 40)}% of total sales<br/>
    • South Region: {random.randint(25, 45)}% of total sales<br/>
    • East Region: {random.randint(15, 35)}% of total sales<br/>
    • West Region: {random.randint(10, 30)}% of total sales<br/><br/>
    
    <b>Product Categories:</b><br/>
    • Category A: {random.randint(30, 60)}% of sales<br/>
    • Category B: {random.randint(20, 40)}% of sales<br/>
    • Category C: {random.randint(10, 30)}% of sales<br/>
    """
    
    story.append(Paragraph(content, styles['Normal']))
    doc.build(story)
    print(f"✅ Created {filename}")

def main():
    """Create sample PDFs for testing"""
    print("📄 Creating sample PDF files for testing...")
    
    try:
        # Create financial reports
        create_financial_report_pdf("company_report_2023.pdf", "TechCorp Inc", 2023)
        create_financial_report_pdf("company_report_2024.pdf", "TechCorp Inc", 2024)
        
        # Create sales reports  
        create_sales_report_pdf("sales_q1_2024.pdf", 1, 2024)
        create_sales_report_pdf("sales_q2_2024.pdf", 2, 2024)
        
        print(f"\n✅ Created 4 sample PDF files")
        print("📋 Now you can test with:")
        print("   python test_multi_pdf_analysis.py")
        
    except ImportError:
        print("❌ Missing reportlab library")
        print("📦 Install with: pip install reportlab")
        print("\n💡 Alternative: Download sample PDFs manually:")
        print("   - Find any PDF files online")
        print("   - Place them in this directory") 
        print("   - Run: python test_multi_pdf_analysis.py")

if __name__ == "__main__":
    main() 