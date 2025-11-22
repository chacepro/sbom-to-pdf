from flask import Flask, render_template, request, send_file, Response
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

def format_value(value):
    """Format a value for display in PDF"""
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        if len(value) == 0:
            return "None"
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, indent=2)
    return str(value)

def create_formatted_pdf(json_data, buffer):
    """Create a formatted, readable PDF from JSON data"""
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Title
    title = json_data.get('name', 'SBOM Document')
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Document Information Section
    if 'spdxVersion' in json_data or 'SPDXID' in json_data:
        elements.append(Paragraph("Document Information", heading_style))
        
        doc_info = []
        if 'SPDXID' in json_data:
            doc_info.append(["Document ID:", format_value(json_data.get('SPDXID'))])
        if 'spdxVersion' in json_data:
            doc_info.append(["SPDX Version:", format_value(json_data.get('spdxVersion'))])
        if 'dataLicense' in json_data:
            doc_info.append(["Data License:", format_value(json_data.get('dataLicense'))])
        if 'documentNamespace' in json_data:
            doc_info.append(["Document Namespace:", format_value(json_data.get('documentNamespace'))])
        if 'comment' in json_data:
            doc_info.append(["Comment:", format_value(json_data.get('comment'))])
        
        if doc_info:
            info_table = Table(doc_info, colWidths=[2*inch, 4.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.2*inch))
    
    # Creation Info Section
    if 'creationInfo' in json_data:
        elements.append(Paragraph("Creation Information", heading_style))
        creation_info = json_data['creationInfo']
        
        creation_data = []
        if 'created' in creation_info:
            creation_data.append(["Created:", format_value(creation_info.get('created'))])
        if 'creators' in creation_info:
            creation_data.append(["Creators:", format_value(creation_info.get('creators'))])
        if 'licenseListVersion' in creation_info:
            creation_data.append(["License List Version:", format_value(creation_info.get('licenseListVersion'))])
        if 'comment' in creation_info:
            creation_data.append(["Comment:", format_value(creation_info.get('comment'))])
        
        if creation_data:
            creation_table = Table(creation_data, colWidths=[2*inch, 4.5*inch])
            creation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ]))
            elements.append(creation_table)
            elements.append(Spacer(1, 0.2*inch))
    
    # Packages Section
    if 'packages' in json_data and json_data['packages']:
        elements.append(Paragraph("Packages", heading_style))
        
        for idx, package in enumerate(json_data['packages'], 1):
            elements.append(Paragraph(f"Package {idx}: {package.get('name', 'Unknown')}", subheading_style))
            
            package_data = []
            if 'SPDXID' in package:
                package_data.append(["Package ID:", format_value(package.get('SPDXID'))])
            if 'versionInfo' in package:
                package_data.append(["Version:", format_value(package.get('versionInfo'))])
            if 'description' in package:
                package_data.append(["Description:", format_value(package.get('description'))])
            if 'summary' in package:
                package_data.append(["Summary:", format_value(package.get('summary'))])
            if 'homepage' in package:
                package_data.append(["Homepage:", format_value(package.get('homepage'))])
            if 'downloadLocation' in package:
                package_data.append(["Download Location:", format_value(package.get('downloadLocation'))])
            if 'copyrightText' in package:
                package_data.append(["Copyright:", format_value(package.get('copyrightText'))])
            if 'licenseConcluded' in package:
                package_data.append(["License Concluded:", format_value(package.get('licenseConcluded'))])
            if 'licenseDeclared' in package:
                package_data.append(["License Declared:", format_value(package.get('licenseDeclared'))])
            if 'supplier' in package:
                package_data.append(["Supplier:", format_value(package.get('supplier'))])
            if 'originator' in package:
                package_data.append(["Originator:", format_value(package.get('originator'))])
            
            if package_data:
                package_table = Table(package_data, colWidths=[2*inch, 4.5*inch])
                package_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (0, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (1, 0), (1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c8e6c9')),
                ]))
                elements.append(package_table)
                elements.append(Spacer(1, 0.15*inch))
    
    # Files Section
    if 'files' in json_data and json_data['files']:
        elements.append(PageBreak())
        elements.append(Paragraph("Files", heading_style))
        
        for idx, file_item in enumerate(json_data['files'], 1):
            elements.append(Paragraph(f"File {idx}: {file_item.get('fileName', 'Unknown')}", subheading_style))
            
            file_data = []
            if 'SPDXID' in file_item:
                file_data.append(["File ID:", format_value(file_item.get('SPDXID'))])
            if 'fileTypes' in file_item:
                file_data.append(["File Types:", format_value(file_item.get('fileTypes'))])
            if 'copyrightText' in file_item:
                file_data.append(["Copyright:", format_value(file_item.get('copyrightText'))])
            if 'licenseConcluded' in file_item:
                file_data.append(["License Concluded:", format_value(file_item.get('licenseConcluded'))])
            if 'licenseInfoInFiles' in file_item:
                file_data.append(["License Info in Files:", format_value(file_item.get('licenseInfoInFiles'))])
            if 'fileContributors' in file_item:
                file_data.append(["Contributors:", format_value(file_item.get('fileContributors'))])
            if 'comment' in file_item:
                file_data.append(["Comment:", format_value(file_item.get('comment'))])
            
            if file_data:
                file_table = Table(file_data, colWidths=[2*inch, 4.5*inch])
                file_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (0, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (1, 0), (1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#90caf9')),
                ]))
                elements.append(file_table)
                elements.append(Spacer(1, 0.15*inch))
    
    # Relationships Section
    if 'relationships' in json_data and json_data['relationships']:
        elements.append(PageBreak())
        elements.append(Paragraph("Relationships", heading_style))
        
        relationship_data = [["From", "Relationship Type", "To"]]
        for rel in json_data['relationships']:
            relationship_data.append([
                format_value(rel.get('spdxElementId', 'N/A')),
                format_value(rel.get('relationshipType', 'N/A')),
                format_value(rel.get('relatedSpdxElement', 'N/A'))
            ])
        
        if len(relationship_data) > 1:
            rel_table = Table(relationship_data, colWidths=[2*inch, 2*inch, 2.5*inch])
            rel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            elements.append(rel_table)
            elements.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(elements)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_json():
    try:
        # Check if a file was uploaded
        if 'json_file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['json_file']
        
        # Verify file is a JSON file
        if not file.filename.endswith('.json'):
            return 'Please upload a JSON file', 400
        
        # Read and parse JSON
        json_data = json.load(file)
        
        # Generate formatted PDF
        buffer = BytesIO()
        create_formatted_pdf(json_data, buffer)
        buffer.seek(0)
        
        # Send PDF as downloadable file
        return send_file(
            buffer,
            as_attachment=True,
            download_name='sbom_document.pdf',
            mimetype='application/pdf'
        )
    
    except json.JSONDecodeError:
        return 'Invalid JSON file', 400
    except Exception as e:
        return f'Error processing file: {str(e)}', 500

if __name__ == '__main__':
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    # Get host and port from environment variables, with defaults
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 3001))
    app.run(host=host, port=port, debug=debug_mode)