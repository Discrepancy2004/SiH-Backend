from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pdfkit
from datetime import datetime
import io
import base64
import logging
import os
import tempfile
import uuid

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalCertificateGenerator:
    def __init__(self):
        # Configure wkhtmltopdf path for Windows
        self.setup_wkhtmltopdf_config()
        
        # Configure wkhtmltopdf options for professional output
        self.options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
            'disable-smart-shrinking': None,
            'dpi': 300,
            'image-quality': 100,
            'minimum-font-size': 8
        }
    
    def setup_wkhtmltopdf_config(self):
        """Configure wkhtmltopdf path for Windows"""
        import platform
        if platform.system() == 'Windows':
            # Common installation paths for wkhtmltopdf on Windows
            possible_paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Users\{}\AppData\Local\Programs\wkhtmltopdf\bin\wkhtmltopdf.exe'.format(os.getenv('USERNAME', '')),
                r'C:\wkhtmltopdf\bin\wkhtmltopdf.exe'
            ]
            
            wkhtmltopdf_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    wkhtmltopdf_path = path
                    break
            
            if wkhtmltopdf_path:
                import pdfkit
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                self.pdfkit_config = config
                logger.info(f"Found wkhtmltopdf at: {wkhtmltopdf_path}")
            else:
                logger.warning("wkhtmltopdf not found in common paths, using system PATH")
                self.pdfkit_config = None
        else:
            self.pdfkit_config = None
    
    def get_status_badge_style(self, status):
        """Return appropriate styling for status badge"""
        if not status:
            return "background: #6c757d; color: white;"
        
        status_lower = status.lower()
        if "pass" in status_lower or "success" in status_lower or "complete" in status_lower:
            return "background: linear-gradient(45deg, #28a745, #20c997); color: white; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);"
        elif "fail" in status_lower or "error" in status_lower:
            return "background: linear-gradient(45deg, #dc3545, #e74c3c); color: white; box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);"
        else:
            return "background: linear-gradient(45deg, #ffc107, #fd7e14); color: #212529; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4);"
    
    def create_certificate_html(self, data):
        """Generate professional HTML certificate"""
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        issue_date = data.get('issue_date', current_time)
        cert_id = data.get('certificate_id', f'CERT-{uuid.uuid4().hex[:8].upper()}')
        final_status = data.get('final_status', 'VERIFIED')
        status_badge_style = self.get_status_badge_style(final_status)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificate of Authenticity - {cert_id}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #2c3e50;
                    line-height: 1.6;
                    min-height: 100vh;
                    padding: 0;
                }}
                
                .certificate-container {{
                    max-width: 210mm;
                    margin: 0 auto;
                    background: #ffffff;
                    position: relative;
                    overflow: hidden;
                }}
                
                /* Decorative Elements */
                .cert-border {{
                    position: absolute;
                    top: 15px;
                    left: 15px;
                    right: 15px;
                    bottom: 15px;
                    border: 3px solid #c9a96e;
                    border-radius: 15px;
                }}
                
                .cert-border::before {{
                    content: '';
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    right: 10px;
                    bottom: 10px;
                    border: 1px solid #c9a96e;
                    border-radius: 10px;
                }}
                
                .corner-ornament {{
                    position: absolute;
                    width: 60px;
                    height: 60px;
                    background: radial-gradient(circle, #c9a96e 0%, #8b7355 100%);
                    transform: rotate(45deg);
                }}
                
                .corner-ornament.top-left {{ top: 25px; left: 25px; }}
                .corner-ornament.top-right {{ top: 25px; right: 25px; }}
                .corner-ornament.bottom-left {{ bottom: 25px; left: 25px; }}
                .corner-ornament.bottom-right {{ bottom: 25px; right: 25px; }}
                
                .corner-ornament::before {{
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 30px;
                    height: 30px;
                    background: #fff;
                    transform: translate(-50%, -50%);
                    border-radius: 50%;
                }}
                
                .watermark {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-45deg);
                    font-size: 150px;
                    font-weight: 100;
                    color: rgba(201, 169, 110, 0.05);
                    z-index: 1;
                    font-family: 'Playfair Display', serif;
                    letter-spacing: 10px;
                }}
                
                .content {{
                    position: relative;
                    z-index: 2;
                    padding: 60px 50px 40px;
                }}
                
                /* Header Section */
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                
                .company-logo {{
                    width: 120px;
                    height: 120px;
                    margin: 0 auto 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 48px;
                    font-weight: bold;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                
                .cert-title {{
                    font-family: 'Playfair Display', serif;
                    font-size: 42px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 8px;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                }}
                
                .cert-subtitle {{
                    font-size: 16px;
                    color: #7f8c8d;
                    font-weight: 300;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    margin-bottom: 30px;
                    line-height: 1.4;
                    word-wrap: break-word;
                    max-width: 100%;
                    padding: 0 20px;
                }}
                
                /* Certificate Info Bar */
                .cert-info-bar {{
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border-radius: 15px;
                    padding: 25px;
                    margin-bottom: 40px;
                    box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
                    border: 1px solid #dee2e6;
                }}
                
                .cert-info-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                }}
                
                .info-item {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 15px 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    border-left: 4px solid #667eea;
                }}
                
                .info-label {{
                    font-weight: 600;
                    color: #495057;
                    font-size: 14px;
                }}
                
                .info-value {{
                    font-weight: 700;
                    color: #212529;
                    font-size: 16px;
                }}
                
                /* Status Badge */
                .status-badge {{
                    display: inline-block;
                    padding: 8px 20px;
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    {status_badge_style}
                }}
                
                .status-checkmark {{
                    color: #28a745;
                    font-weight: bold;
                    font-size: 16px;
                    margin-right: 5px;
                }}
                
                /* Data Sections */
                .data-section {{
                    margin-bottom: 35px;
                    page-break-inside: avoid;
                }}
                
                .section-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                    padding: 15px 0;
                    border-bottom: 2px solid #e9ecef;
                }}
                
                .section-icon {{
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    margin-right: 15px;
                    font-size: 18px;
                }}
                
                .device-icon {{ background: linear-gradient(135deg, #28a745, #20c997); }}
                .process-icon {{ background: linear-gradient(135deg, #fd7e14, #f39c12); }}
                .verification-icon {{ background: linear-gradient(135deg, #dc3545, #e74c3c); }}
                .additional-icon {{ background: linear-gradient(135deg, #6f42c1, #8e44ad); }}
                
                .section-title {{
                    font-family: 'Playfair Display', serif;
                    font-size: 24px;
                    font-weight: 600;
                    color: #2c3e50;
                }}
                
                .data-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                }}
                
                .data-item {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 12px;
                    border: 1px solid #e9ecef;
                    transition: all 0.3s ease;
                }}
                
                .data-item:hover {{
                    background: #fff;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    transform: translateY(-2px);
                }}
                
                .data-label {{
                    font-size: 12px;
                    font-weight: 600;
                    color: #6c757d;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 8px;
                }}
                
                .data-value {{
                    font-size: 16px;
                    font-weight: 500;
                    color: #212529;
                    word-break: break-all;
                }}
                
                /* Certification Statement */
                .certification-statement {{
                    background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
                    border: 2px solid #28a745;
                    border-radius: 15px;
                    padding: 35px;
                    margin: 60px 0 40px 0;
                    text-align: center;
                    position: relative;
                    box-shadow: 0 8px 25px rgba(40, 167, 69, 0.15);
                    page-break-before: always;
                    page-break-after: always;
                }}
                
                
                .statement-title {{
                    font-family: 'Playfair Display', serif;
                    font-size: 28px;
                    font-weight: 700;
                    color: #155724;
                    margin-bottom: 20px;
                }}
                
                .statement-text {{
                    font-size: 16px;
                    color: #155724;
                    line-height: 1.8;
                    margin-bottom: 15px;
                }}
                
                /* Signature Section */
                .signature-section {{
                    margin-top: 50px;
                    page-break-inside: avoid;
                    page-break-before: always;
                }}
                
                .signature-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 60px;
                    margin-top: 40px;
                }}
                
                .signature-box {{
                    text-align: center;
                    position: relative;
                }}
                
                .signature-line {{
                    height: 2px;
                    background: linear-gradient(to right, #667eea, #764ba2);
                    margin: 50px 20px 15px;
                    border-radius: 2px;
                }}
                
                .signature-role {{
                    font-weight: 700;
                    font-size: 16px;
                    color: #2c3e50;
                    margin-bottom: 8px;
                }}
                
                .signature-name {{
                    font-size: 18px;
                    color: #495057;
                    margin-bottom: 5px;
                }}
                
                .signature-date {{
                    font-size: 12px;
                    color: #6c757d;
                }}
                
                /* Footer */
                .certificate-footer {{
                    margin-top: 40px;
                    padding-top: 30px;
                    border-top: 1px solid #dee2e6;
                    text-align: center;
                }}
                
                .footer-text {{
                    font-size: 11px;
                    color: #6c757d;
                    margin-bottom: 10px;
                }}
                
                .qr-code {{
                    width: 80px;
                    height: 80px;
                    margin: 20px auto 10px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }}
                
                /* Print Styles */
                @media print {{
                    body {{ background: none; }}
                    .certificate-container {{ box-shadow: none; }}
                    .certification-statement {{ 
                        page-break-before: always; 
                        page-break-after: always;
                        margin-top: 80px;
                    }}
                    .signature-section {{ 
                        page-break-before: always; 
                        margin-top: 80px;
                    }}
                }}
                
                /* Page Break Utilities for wkhtmltopdf */
                .page-break-before {{
                    page-break-before: always;
                }}
                
                .page-break-inside-avoid {{
                    page-break-inside: avoid;
                }}
            </style>
        </head>
        <body>
            <div class="certificate-container">
                <div class="cert-border"></div>
                <div class="corner-ornament top-left"></div>
                <div class="corner-ornament top-right"></div>
                <div class="corner-ornament bottom-left"></div>
                <div class="corner-ornament bottom-right"></div>
                <div class="watermark">CERTIFIED</div>
                
                <div class="content">
                    <!-- Header -->
                    <div class="header">
                        <div class="company-logo">DS</div>
                        <h1 class="cert-title">Certificate of Authenticity</h1>
                        <p class="cert-subtitle">Data Sanitization & Security Verification</p>
                    </div>
                    
                    <!-- Certificate Info Bar -->
                    <div class="cert-info-bar">
                        <div class="cert-info-grid">
                            <div class="info-item">
                                <span class="info-label">Certificate ID</span>
                                <span class="info-value">{cert_id}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Issue Date</span>
                                <span class="info-value">{issue_date}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Technician</span>
                                <span class="info-value">{data.get('technician_name', 'N/A')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Status</span>
                                <span class="status-badge"><span class="status-checkmark">✓</span>{final_status}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Device Information -->
                    <div class="data-section">
                        <div class="section-header">
                            <div class="section-icon device-icon">💾</div>
                            <h2 class="section-title">Device Information</h2>
                        </div>
                        <div class="data-grid">
                            <div class="data-item">
                                <div class="data-label">Device Type</div>
                                <div class="data-value">{data.get('device_type', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Manufacturer</div>
                                <div class="data-value">{data.get('manufacturer', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Model</div>
                                <div class="data-value">{data.get('model', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Serial Number</div>
                                <div class="data-value">{data.get('serial_number', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Asset Tag</div>
                                <div class="data-value">{data.get('asset_tag', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Capacity</div>
                                <div class="data-value">{data.get('capacity', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Interface</div>
                                <div class="data-value">{data.get('interface', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Firmware Version</div>
                                <div class="data-value">{data.get('firmware_version', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Sanitization Process -->
                    <div class="data-section">
                        <div class="section-header">
                            <div class="section-icon process-icon">🔄</div>
                            <h2 class="section-title">Sanitization Process</h2>
                        </div>
                        <div class="data-grid">
                            <div class="data-item">
                                <div class="data-label">Method Used</div>
                                <div class="data-value">{data.get('sanitization_method', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Standard Compliance</div>
                                <div class="data-value">{data.get('standard_compliance', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Number of Passes</div>
                                <div class="data-value">{data.get('number_of_passes', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Algorithm</div>
                                <div class="data-value">{data.get('algorithm', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Start Time</div>
                                <div class="data-value">{data.get('start_time', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Duration</div>
                                <div class="data-value">{data.get('duration', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Software Used</div>
                                <div class="data-value">{data.get('software_used', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Software Version</div>
                                <div class="data-value">{data.get('software_version', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Verification Results -->
                    <div class="data-section">
                        <div class="section-header">
                            <div class="section-icon verification-icon">✓</div>
                            <h2 class="section-title">Verification Results</h2>
                        </div>
                        <div class="data-grid">
                            <div class="data-item">
                                <div class="data-label">Pre-wipe Status</div>
                                <div class="data-value">{data.get('pre_wipe_verification', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Post-wipe Status</div>
                                <div class="data-value">{data.get('post_wipe_verification', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Verification Method</div>
                                <div class="data-value">{data.get('verification_method', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Sectors Processed</div>
                                <div class="data-value">{data.get('sectors_processed', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Data Remnants</div>
                                <div class="data-value">{data.get('data_remnants', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">OS Installation</div>
                                <div class="data-value">{data.get('os_installation_status', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">OS Version</div>
                                <div class="data-value">{data.get('os_version', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Boot Test</div>
                                <div class="data-value">{data.get('boot_test_result', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Additional Information -->
                    <div class="data-section">
                        <div class="section-header">
                            <div class="section-icon additional-icon">📋</div>
                            <h2 class="section-title">Additional Information</h2>
                        </div>
                        <div class="data-grid">
                            <div class="data-item">
                                <div class="data-label">Customer Name</div>
                                <div class="data-value">{data.get('customer_name', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Work Order</div>
                                <div class="data-value">{data.get('work_order', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Location</div>
                                <div class="data-value">{data.get('location', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Witness</div>
                                <div class="data-value">{data.get('witness_name', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Temperature</div>
                                <div class="data-value">{data.get('temperature', 'N/A')}</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Humidity</div>
                                <div class="data-value">{data.get('humidity', 'N/A')}</div>
                            </div>
                        </div>
                        
                        <div class="data-item" style="grid-column: 1 / -1; margin-top: 15px;">
                            <div class="data-label">Notes</div>
                            <div class="data-value">{data.get('notes', 'N/A')}</div>
                        </div>
                    </div>
                    
                    <!-- Certification Statement -->
                    <div class="certification-statement">
                        <h3 class="statement-title">Official Certification</h3>
                        <p class="statement-text">
                            This certificate verifies that the above-mentioned storage device has undergone comprehensive 
                            data sanitization procedures in full compliance with industry standards and regulatory requirements.
                        </p>
                        <p class="statement-text">
                            All confidential data has been permanently destroyed using cryptographically secure methods, 
                            rendering any previously stored information completely irrecoverable through any known forensic techniques.
                        </p>
                        <p class="statement-text">
                            <strong>This certification guarantees the complete sanitization of the specified device and 
                            confirms its readiness for secure redeployment or disposal.</strong>
                        </p>
                    </div>
                    
                    <!-- Signatures -->
                    <div class="signature-section">
                        <div class="section-header">
                            <div class="section-icon" style="background: linear-gradient(135deg, #17a2b8, #138496);">✍️</div>
                            <h2 class="section-title">Authorization</h2>
                        </div>
                        <div class="signature-grid">
                            <div class="signature-box">
                                <div class="signature-role">Certified Technician</div>
                                <div class="signature-line"></div>
                                <div class="signature-name">{data.get('technician_name', 'John Smith')}</div>
                                <div class="signature-date">Date: {data.get('technician_date', issue_date[:10])}</div>
                            </div>
                            <div class="signature-box">
                                <div class="signature-role">Quality Supervisor</div>
                                <div class="signature-line"></div>
                                <div class="signature-name">{data.get('supervisor_name', 'Jane Doe')}</div>
                                <div class="signature-date">Date: {data.get('supervisor_date', issue_date[:10])}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="certificate-footer">
                        <div class="qr-code">
                            QR CODE<br>
                            {cert_id}
                        </div>
                        <p class="footer-text">
                            This certificate contains sensitive security information. Handle in accordance with data protection policies.
                        </p>
                        <p class="footer-text">
                            Generated: {current_time} | Document ID: {cert_id} | Verification: secure-verify.com/{cert_id.lower()}
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def create_certificate(self, data):
        """Generate professional PDF certificate"""
        try:
            logger.info("Starting certificate generation...")
            html_content = self.create_certificate_html(data)
            logger.info(f"HTML content generated, length: {len(html_content)}")
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
                temp_html.write(html_content)
                temp_html_path = temp_html.name
            
            logger.info(f"Temporary HTML file created: {temp_html_path}")
            
            try:
                # Generate PDF with configuration
                logger.info("Starting PDF generation with wkhtmltopdf...")
                if self.pdfkit_config:
                    logger.info("Using configured wkhtmltopdf path")
                    pdf_data = pdfkit.from_file(temp_html_path, False, options=self.options, configuration=self.pdfkit_config)
                else:
                    logger.info("Using system PATH for wkhtmltopdf")
                    pdf_data = pdfkit.from_file(temp_html_path, False, options=self.options)
                
                logger.info(f"PDF generated successfully, size: {len(pdf_data)} bytes")
                pdf_buffer = io.BytesIO(pdf_data)
                pdf_buffer.seek(0)
                return pdf_buffer
            finally:
                # Cleanup
                if os.path.exists(temp_html_path):
                    os.unlink(temp_html_path)
                    logger.info("Temporary HTML file cleaned up")
                    
        except Exception as e:
            logger.error(f"Error creating certificate: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

# Initialize generator
cert_generator = ProfessionalCertificateGenerator()

@app.route('/generate-certificate', methods=['POST'])
def generate_certificate():
    """Generate certificate and return as base64"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        logger.info(f"Generating certificate with {len(data)} parameters")
        pdf_buffer = cert_generator.create_certificate(data)
        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'message': 'Professional certificate generated successfully',
            'pdf_base64': pdf_base64,
            'filename': f"certificate_{data.get('certificate_id', 'unknown')}.pdf",
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating certificate: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate certificate: {str(e)}'
        }), 500

@app.route('/generate-certificate-file', methods=['POST'])
def generate_certificate_file():
    """Generate and return certificate PDF file directly"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        logger.info(f"Generating certificate file with {len(data)} parameters")
        pdf_buffer = cert_generator.create_certificate(data)
        
        filename = f"certificate_{data.get('certificate_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating certificate file: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate certificate: {str(e)}'
        }), 500

@app.route('/preview-certificate', methods=['POST'])
def preview_certificate():
    """Generate certificate HTML for preview"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        html_content = cert_generator.create_certificate_html(data)
        
        return jsonify({
            'success': True,
            'html_content': html_content,
            'message': 'Professional certificate preview generated'
        })
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate preview: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Professional Certificate Generator (wkhtmltopdf)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test', methods=['POST'])
def test_endpoint():
    """Test endpoint"""
    data = request.get_json()
    return jsonify({
        'message': 'Professional Certificate API is working',
        'received_params': len(data) if data else 0,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    sample_data = {
        'certificate_id': 'CERT-2024-FLAGSHIP-001',
        'issue_date': '2024-03-15 14:30:00',
        'verification_date': '2024-03-15',
        'technician_name': 'Dr. Sarah Johnson',
        'supervisor_name': 'Michael Chen',
        'device_type': 'Enterprise SSD',
        'manufacturer': 'Samsung',
        'model': 'SSD 990 PRO',
        'serial_number': 'S6M2NG0R987654',
        'asset_tag': 'CORP-SSD-12345',
        'capacity': '2TB',
        'interface': 'NVMe PCIe 4.0',
        'firmware_version': '4B2QGXA7',
        'sanitization_method': 'Cryptographic Erase + Multi-Pass Overwrite',
        'standard_compliance': 'NIST SP 800-88 Rev. 1, DoD 5220.22-M',
        'number_of_passes': '3',
        'algorithm': 'AES-256 + Gutmann Method',
        'start_time': '2024-03-15 08:00:00',
        'duration': '2 hours 15 minutes',
        'software_used': 'SecureErase Pro Enterprise',
        'software_version': '3.2.1',
        'pre_wipe_verification': 'Confidential Data Detected',
        'post_wipe_verification': 'No Data Remnants Found',
        'verification_method': 'Hexadecimal Deep Scan + Entropy Analysis',
        'sectors_processed': '3,907,050,336',
        'data_remnants': 'None Detected (0.00%)',
        'os_installation_status': 'Windows 11 Enterprise Installed',
        'os_version': 'Windows 11 Enterprise 22H2 Build 22621',
        'boot_test_result': 'Successful - All Systems Operational',
        'final_status': 'PASSED',
        'customer_name': 'GlobalTech Industries',
        'work_order': 'WO-2024-SEC-001',
        'location': 'Secure Data Center - Building A',
        'witness_name': 'Alex Rodriguez (Security Officer)',
        'temperature': '21°C ± 1°C',
        'humidity': '45% RH ± 5%',
        'notes': 'Enterprise-grade sanitization completed with full compliance verification. Device certified for secure redeployment in production environment.'
    }
    
    print("🚀 Starting Professional Certificate Generator...")
    print("📋 Available endpoints:")
    print("   • POST /generate-certificate (base64 response)")
    print("   • POST /generate-certificate-file (direct download)")
    print("   • POST /preview-certificate (HTML preview)")
    print("   • GET /health (health check)")
    print("   • POST /api/test (test endpoint)")
    print(f"\n✨ Sample data contains {len(sample_data)} professional parameters")
    print("🎨 Features: Professional design, gradients, icons, status badges, QR code placeholder")
    print("📄 Output: High-quality PDF with premium styling\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)