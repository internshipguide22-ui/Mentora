from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from io import BytesIO
from django.conf import settings
from django.urls import reverse
from django.core.files.base import ContentFile


def generate_certificate(certificate):
    """
    Generate a certificate PDF
    
    Args:
        certificate: Certificate model instance
    
    Returns:
        Saves the certificate PDF to the certificate's file field
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Colors
    blue = HexColor('#0066cc')
    gold = HexColor('#FFD700')
    black = HexColor('#000000')

    # Add decorative border
    p.setStrokeColor(gold)
    p.setLineWidth(8)
    p.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)
    
    p.setStrokeColor(blue)
    p.setLineWidth(2)
    p.rect(0.6 * inch, 0.6 * inch, width - 1.2 * inch, height - 1.2 * inch)

    # Add certificate title
    p.setFont("Helvetica-Bold", 48)
    p.setFillColor(blue)
    p.drawCentredString(width / 2.0, height - 1.5 * inch, "Certificate of Completion")

    # Add decorative line
    p.setStrokeColor(gold)
    p.setLineWidth(2)
    p.line(2 * inch, height - 2 * inch, width - 2 * inch, height - 2 * inch)

    # Add student name
    p.setFont("Helvetica", 20)
    p.setFillColor(black)
    p.drawCentredString(width / 2.0, height - 2.8 * inch, "This is to certify that")
    
    p.setFont("Helvetica-Bold", 32)
    p.setFillColor(blue)
    student_name = certificate.enrollment.student.get_full_name() or certificate.enrollment.student.username
    p.drawCentredString(width / 2.0, height - 3.5 * inch, student_name)

    # Add course details
    p.setFont("Helvetica", 20)
    p.setFillColor(black)
    p.drawCentredString(width / 2.0, height - 4.2 * inch, "has successfully completed the course")
    
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(blue)
    p.drawCentredString(width / 2.0, height - 4.9 * inch, certificate.enrollment.course.title)

    # Add instructor name
    p.setFont("Helvetica", 16)
    p.setFillColor(black)
    instructor_name = certificate.enrollment.course.instructor.get_full_name() or certificate.enrollment.course.instructor.username
    p.drawCentredString(width / 2.0, height - 5.6 * inch, f"Instructor: {instructor_name}")

    # Add completion date
    p.setFont("Helvetica", 14)
    p.setFillColor(black)
    if certificate.enrollment.completion_date:
        completion_date = certificate.enrollment.completion_date.strftime("%B %d, %Y")
    else:
        from django.utils import timezone
        completion_date = timezone.now().strftime("%B %d, %Y")
    p.drawCentredString(width / 2.0, height - 6.2 * inch, f"Completed on {completion_date}")

    # Add certificate ID
    p.setFont("Helvetica", 10)
    p.setFillColor(HexColor('#666666'))
    p.drawCentredString(width / 2.0, 0.8 * inch, f"Certificate ID: {certificate.uuid}")
    
    # Add verification URL
    verification_url = f"{settings.SITE_URL}/certificates/verify/{certificate.uuid}/"
    p.drawCentredString(width / 2.0, 0.6 * inch, f"Verify at: {verification_url}")

    p.showPage()
    p.save()

    filename = f"certificate_{certificate.uuid}.pdf"
    certificate.file.save(filename, ContentFile(buffer.getvalue()), save=False)
    
    return certificate