"""Email sending functionality."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
from ..models import Student
from ..config import Config


class EmailSender:
    """Send emails with attachments."""
    
    def __init__(self):
        """Initialize email sender."""
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.from_name = Config.EMAIL_FROM_NAME
    
    def _create_connection(self):
        """Create SMTP connection."""
        if not self.email_address or not self.email_password:
            raise ValueError("Email credentials not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in .env file")
        
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.email_address, self.email_password)
        return server
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        html: bool = False
    ) -> bool:
        """
        Send an email with optional attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            attachments: List of file paths to attach
            html: If True, body is treated as HTML
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, msg_type, 'utf-8'))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    path = Path(filepath)
                    if path.exists():
                        with open(filepath, 'rb') as f:
                            attachment = MIMEApplication(f.read(), _subtype=path.suffix[1:])
                            attachment.add_header('Content-Disposition', 'attachment', filename=path.name)
                            msg.attach(attachment)
            
            # Send email
            with self._create_connection() as server:
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_certificate(self, student: Student, certificate_path: str) -> bool:
        """
        Send certificate email to a student.
        
        Args:
            student: Student object
            certificate_path: Path to the certificate PDF
        
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Certificado de Inscripción - {Config.PROGRAM_NAME}"
        
        body = f"""
        <html>
        <body>
            <h2>¡Felicitaciones {student.nombre}!</h2>
            
            <p>Tu inscripción al <strong>{Config.PROGRAM_NAME}</strong> 
            en la <strong>{Config.SCHOOL_NAME}</strong> ha sido confirmada.</p>
            
            <p>Adjunto encontrarás tu certificado de inscripción.</p>
            
            <h3>Datos de tu inscripción:</h3>
            <ul>
                <li><strong>Nombre:</strong> {student.get_full_name()}</li>
                <li><strong>DNI:</strong> {student.dni}</li>
                <li><strong>Instrumento:</strong> {student.instrumento or 'No especificado'}</li>
                <li><strong>Nivel:</strong> {student.nivel or 'No especificado'}</li>
            </ul>
            
            <p>Para cualquier consulta, no dudes en contactarnos.</p>
            
            <p>Saludos cordiales,<br>
            <strong>{Config.SCHOOL_NAME}</strong></p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=student.email,
            subject=subject,
            body=body,
            attachments=[certificate_path],
            html=True
        )
    
    def send_welcome_email(self, student: Student) -> bool:
        """
        Send welcome email to a newly registered student.
        
        Args:
            student: Student object
        
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Bienvenido/a a {Config.PROGRAM_NAME}"
        
        body = f"""
        <html>
        <body>
            <h2>¡Bienvenido/a {student.nombre}!</h2>
            
            <p>Tu inscripción al <strong>{Config.PROGRAM_NAME}</strong> 
            en la <strong>{Config.SCHOOL_NAME}</strong> ha sido recibida exitosamente.</p>
            
            <h3>Datos registrados:</h3>
            <ul>
                <li><strong>Nombre completo:</strong> {student.get_full_name()}</li>
                <li><strong>DNI:</strong> {student.dni}</li>
                <li><strong>Email:</strong> {student.email}</li>
                <li><strong>Instrumento:</strong> {student.instrumento or 'No especificado'}</li>
            </ul>
            
            <p>Tu estado actual es: <strong>{student.estado}</strong></p>
            
            <p>Recibirás una notificación cuando tu inscripción sea procesada.</p>
            
            <p>Saludos cordiales,<br>
            <strong>{Config.SCHOOL_NAME}</strong></p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=student.email,
            subject=subject,
            body=body,
            html=True
        )
    
    def send_status_update(self, student: Student) -> bool:
        """
        Send status update email to a student.
        
        Args:
            student: Student object
        
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Actualización de Estado - {Config.PROGRAM_NAME}"
        
        status_messages = {
            'Aprobado': 'Tu inscripción ha sido <strong>aprobada</strong>. ¡Felicitaciones!',
            'Rechazado': 'Tu inscripción ha sido <strong>rechazada</strong>. Por favor, contacta con la institución para más información.',
            'Pendiente': 'Tu inscripción está en estado <strong>pendiente</strong> de revisión.'
        }
        
        status_message = status_messages.get(student.estado, f'El estado de tu inscripción ha cambiado a: <strong>{student.estado}</strong>')
        
        body = f"""
        <html>
        <body>
            <h2>Actualización de Estado - {student.nombre}</h2>
            
            <p>{status_message}</p>
            
            <h3>Datos de tu inscripción:</h3>
            <ul>
                <li><strong>Nombre completo:</strong> {student.get_full_name()}</li>
                <li><strong>DNI:</strong> {student.dni}</li>
                <li><strong>Instrumento:</strong> {student.instrumento or 'No especificado'}</li>
                <li><strong>Estado:</strong> {student.estado}</li>
            </ul>
            
            {f'<p><strong>Notas:</strong> {student.notas}</p>' if student.notas else ''}
            
            <p>Para cualquier consulta, no dudes en contactarnos.</p>
            
            <p>Saludos cordiales,<br>
            <strong>{Config.SCHOOL_NAME}</strong></p>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=student.email,
            subject=subject,
            body=body,
            html=True
        )
