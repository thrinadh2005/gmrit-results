"""
GMRIT Results Scraper - Web Frontend
Flask web application for the GMRIT results scraper with enhanced features
"""
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import sys
import threading
import time
import json
import zipfile
# Import scraper with fallbacks - prioritize real Selenium scraper
try:
    from scraper import scrape_student_results
except (ImportError, Exception):
    try:
        from scraper_render import scrape_student_results
    except (ImportError, Exception):
        try:
            from scraper_simple import scrape_student_results
        except (ImportError, Exception):
            # Last resort - create simple fallback
            def scrape_student_results(hall_ticket, output_dir='html_pages'):
                return {
                    'success': False,
                    'hall_ticket': hall_ticket,
                    'error': 'Scraper not available - deployment issue'
                }
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import HTML_DIR, PDF_DIR, OUTPUT_DIR, EXCEL_FILE
from logger import logger
from data_manager import DataManager
from excel_generator import ExcelGenerator

app = Flask(__name__)

# Global variable to track scraping status
scraping_status = {
    'is_running': False,
    'progress': 0,
    'current_ticket': '',
    'total_tickets': 0,
    'success_count': 0,
    'failed_count': 0,
    'message': '',
    'logs': [],
    'start_time': None,
    'elapsed_time': 0,
    'concurrent_mode': False,
    'active_threads': 0
}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index_enhanced.html')

@app.route('/api/halltickets')
def get_halltickets():
    """Get all saved hall tickets"""
    tickets = DataManager.list_halltickets()
    return jsonify({'tickets': tickets})

@app.route('/api/halltickets', methods=['POST'])
def add_halltickets():
    """Add hall tickets"""
    data = request.get_json()
    tickets = data.get('tickets', [])
    
    added = []
    already_exists = []
    
    for ticket in tickets:
        ticket = ticket.strip()
        if ticket:
            if DataManager.add_hallticket(ticket):
                added.append(ticket)
            else:
                already_exists.append(ticket)
    
    return jsonify({
        'success': True,
        'added': added,
        'already_exists': already_exists
    })

@app.route('/api/halltickets/<ticket>', methods=['DELETE'])
def remove_hallticket(ticket):
    """Remove a specific hall ticket"""
    DataManager.remove_hallticket(ticket)
    return jsonify({'success': True})

@app.route('/api/halltickets', methods=['DELETE'])
def clear_halltickets():
    """Clear all hall tickets"""
    DataManager.clear_halltickets()
    return jsonify({'success': True})

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'success': False, 'message': 'Scraping already in progress'})
    
    data = request.get_json()
    concurrent_mode = data.get('concurrent', False)
    max_workers = data.get('max_workers', 3)
    
    tickets = DataManager.list_halltickets()
    if not tickets:
        return jsonify({'success': False, 'message': 'No hall tickets to process'})
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_in_background, args=(tickets, concurrent_mode, max_workers))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Scraping started', 'concurrent': concurrent_mode})

def scrape_single_ticket(ticket, output_dir):
    """Scrape a single ticket using the new scraper function"""
    try:
        result = scrape_student_results(ticket, output_dir)
        # Convert result format to match expected structure
        return {
            'success': result.get('success', False),
            'ticket': ticket,
            'error': result.get('error', 'Unknown error'),
            'html_file': result.get('html_file'),
            'message': result.get('message', '')
        }
    except Exception as e:
        return {'success': False, 'ticket': ticket, 'error': str(e)}

def scrape_in_background(tickets, concurrent_mode=False, max_workers=3):
    """Run scraping in background thread"""
    global scraping_status
    
    scraping_status.update({
        'is_running': True,
        'progress': 0,
        'current_ticket': '',
        'total_tickets': len(tickets),
        'success_count': 0,
        'failed_count': 0,
        'message': 'Initializing scraper...',
        'logs': [],
        'start_time': datetime.now().isoformat(),
        'elapsed_time': 0,
        'concurrent_mode': concurrent_mode,
        'active_threads': 0
    })
    
    try:
        if concurrent_mode and len(tickets) > 1:
            # Concurrent scraping
            scraping_status['message'] = f'Starting concurrent scraping with {max_workers} workers...'
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(scrape_single_ticket, ticket, OUTPUT_DIR): ticket for ticket in tickets}
                scraping_status['active_threads'] = len(futures)
                
                completed = 0
                for future in as_completed(futures):
                    ticket = futures[future]
                    completed += 1
                    
                    scraping_status.update({
                        'progress': int((completed / len(tickets)) * 100),
                        'current_ticket': ticket,
                        'message': f'Processing {completed}/{len(tickets)}: {ticket}',
                        'active_threads': len([f for f in futures if not f.done()])
                    })
                    
                    try:
                        result = future.result(timeout=120)  # 2 minute timeout per ticket
                        if result['success']:
                            scraping_status['success_count'] += 1
                            scraping_status['logs'].append(f"✓ Success: {ticket}")
                        else:
                            scraping_status['failed_count'] += 1
                            error_msg = f"✗ Failed: {ticket} - {result.get('error', 'Unknown error')}"
                            scraping_status['logs'].append(error_msg)
                    except Exception as e:
                        scraping_status['failed_count'] += 1
                        scraping_status['logs'].append(f"✗ Timeout/Error: {ticket} - {str(e)}")
        else:
            # Sequential scraping using simple scraper
            for i, ticket in enumerate(tickets, 1):
                scraping_status.update({
                    'progress': int((i - 1) / len(tickets) * 100),
                    'current_ticket': ticket,
                    'message': f'Processing {i}/{len(tickets)}: {ticket}'
                })
                
                result = scrape_single_ticket(ticket, OUTPUT_DIR)
                
                if result['success']:
                    scraping_status['success_count'] += 1
                    scraping_status['logs'].append(f"✓ Success: {ticket}")
                else:
                    scraping_status['failed_count'] += 1
                    error_msg = f"✗ Failed: {ticket} - {result.get('error', 'Unknown error')}"
                    scraping_status['logs'].append(error_msg)
        
        # Generate Excel
        scraping_status['message'] = 'Generating Excel file...'
        generator = ExcelGenerator()
        excel_data = generator.process_all_html_files()
        
        if excel_data:
            generator.generate_excel(excel_data)
            scraping_status['logs'].append(f"✓ Excel generated: {EXCEL_FILE}")
        
        # Calculate elapsed time
        if scraping_status['start_time']:
            try:
                start_time = datetime.fromisoformat(scraping_status['start_time'])
                scraping_status['elapsed_time'] = (datetime.now() - start_time).total_seconds()
            except (ValueError, TypeError):
                pass
        
        scraping_status.update({
            'is_running': False,
            'progress': 100,
            'message': 'Scraping completed successfully',
            'active_threads': 0
        })
        
    except Exception as e:
        scraping_status.update({
            'is_running': False,
            'message': f'Error: {str(e)}',
            'active_threads': 0
        })
        scraping_status['logs'].append(f"✗ Error: {str(e)}")

@app.route('/api/status')
def get_status():
    """Get current scraping status with calculated metrics"""
    global scraping_status
    
    # Calculate additional timing metrics if scraping is running
    if scraping_status['is_running'] and scraping_status['start_time']:
        try:
            start_time = datetime.fromisoformat(scraping_status['start_time'])
            now = datetime.now()
            elapsed = (now - start_time).total_seconds()
            scraping_status['elapsed_time'] = round(elapsed, 1)
            
            # Calculate estimate
            processed = scraping_status['success_count'] + scraping_status['failed_count']
            if processed > 0:
                avg_time = elapsed / processed
                remaining = scraping_status['total_tickets'] - processed
                scraping_status['estimated_remaining'] = round(avg_time * remaining, 1)
            else:
                scraping_status['estimated_remaining'] = None
        except (ValueError, TypeError):
            pass
            
    return jsonify(scraping_status)

@app.route('/api/summary')
def get_summary():
    """Get results summary"""
    # Check saved hall tickets
    tickets = DataManager.list_halltickets()
    
    # Check existing files
    html_count = len([f for f in os.listdir(HTML_DIR) if f.endswith('_page_source.html')]) if os.path.exists(HTML_DIR) else 0
    pdf_count = len([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]) if os.path.exists(PDF_DIR) else 0
    
    excel_info = None
    if os.path.exists(EXCEL_FILE):
        size = os.path.getsize(EXCEL_FILE) / 1024
        excel_info = {
            'exists': True,
            'path': EXCEL_FILE,
            'size_kb': round(size, 1),
            'modified': datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE)).strftime('%Y-%m-%d %H:%M:%S')
        }
    else:
        excel_info = {'exists': False}
    
    return jsonify({
        'hall_tickets': len(tickets),
        'html_files': html_count,
        'pdf_files': pdf_count,
        'excel': excel_info,
        'scraping_status': scraping_status
    })

@app.route('/api/files')
def get_files():
    """Get list of all files"""
    files = {
        'html_files': [],
        'pdf_files': [],
        'excel_file': None
    }
    
    # HTML files
    if os.path.exists(HTML_DIR):
        html_files = [f for f in os.listdir(HTML_DIR) if f.endswith('_page_source.html')]
        for f in html_files:
            file_path = os.path.join(HTML_DIR, f)
            files['html_files'].append({
                'name': f,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                'ticket': f.replace('_page_source.html', '')
            })
    
    # PDF files
    if os.path.exists(PDF_DIR):
        pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
        for f in pdf_files:
            file_path = os.path.join(PDF_DIR, f)
            files['pdf_files'].append({
                'name': f,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                'ticket': f.replace('_results.pdf', '')
            })
    
    # Excel file
    if os.path.exists(EXCEL_FILE):
        files['excel_file'] = {
            'name': os.path.basename(EXCEL_FILE),
            'size': os.path.getsize(EXCEL_FILE),
            'modified': datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE)).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    return jsonify(files)

@app.route('/api/files/<file_type>/<filename>')
def download_file(file_type, filename):
    """Download specific file"""
    if file_type == 'html':
        file_path = os.path.join(HTML_DIR, filename)
    elif file_type == 'pdf':
        file_path = os.path.join(PDF_DIR, filename)
    elif file_type == 'excel':
        file_path = EXCEL_FILE
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/files/<file_type>/<filename>', methods=['DELETE'])
def delete_file(file_type, filename):
    """Delete specific file"""
    if file_type == 'html':
        file_path = os.path.join(HTML_DIR, filename)
    elif file_type == 'pdf':
        file_path = os.path.join(PDF_DIR, filename)
    elif file_type == 'excel' and filename == 'gmrit_results.xlsx':
        file_path = EXCEL_FILE
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/files/clear/<file_type>', methods=['DELETE'])
def clear_files(file_type):
    """Clear all files of specific type"""
    try:
        if file_type == 'html':
            if os.path.exists(HTML_DIR):
                files = [f for f in os.listdir(HTML_DIR) if f.endswith('_page_source.html')]
                for f in files:
                    os.remove(os.path.join(HTML_DIR, f))
        elif file_type == 'pdf':
            if os.path.exists(PDF_DIR):
                files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
                for f in files:
                    os.remove(os.path.join(PDF_DIR, f))
        elif file_type == 'excel':
            if os.path.exists(EXCEL_FILE):
                os.remove(EXCEL_FILE)
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/download-all')
def download_all_files():
    """Download all files as ZIP"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add HTML files
        if os.path.exists(HTML_DIR):
            for f in os.listdir(HTML_DIR):
                if f.endswith('_page_source.html'):
                    zip_file.write(os.path.join(HTML_DIR, f), f'html_pages/{f}')
        
        # Add PDF files
        if os.path.exists(PDF_DIR):
            for f in os.listdir(PDF_DIR):
                if f.endswith('.pdf'):
                    zip_file.write(os.path.join(PDF_DIR, f), f'pdfs/{f}')
        
        # Add Excel file
        if os.path.exists(EXCEL_FILE):
            zip_file.write(EXCEL_FILE, os.path.basename(EXCEL_FILE))
    
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'gmrit_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    )

@app.route('/api/halltickets/export')
def export_halltickets():
    """Export hall tickets as text file"""
    tickets = DataManager.list_halltickets()
    
    # Create text format
    text_content = f"# GMRIT Hall Tickets\n"
    text_content += f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text_content += f"# Total Tickets: {len(tickets)}\n\n"
    
    for ticket in tickets:
        text_content += f"{ticket}\n"
    
    # Create response
    from flask import Response
    response = Response(text_content, mimetype='text/plain')
    response.headers['Content-Disposition'] = f'attachment; filename=hall_tickets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    return response

@app.route('/api/halltickets/import', methods=['POST'])
def import_halltickets():
    """Import hall tickets from text or JSON"""
    try:
        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'})
            
            if file.filename.endswith('.txt'):
                # Read text file
                text_content = file.read().decode('utf-8')
                tickets = []
                for line in text_content.split('\n'):
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        tickets.append(line)
            elif file.filename.endswith('.json'):
                # Read JSON file
                import json
                data = json.loads(file.read().decode('utf-8'))
                tickets = data.get('hall_tickets', [])
            else:
                return jsonify({'success': False, 'message': 'Unsupported file format. Use .txt or .json'})
        else:
            # Handle JSON data (existing functionality)
            data = request.get_json()
            tickets = data.get('hall_tickets', [])
        
        if not isinstance(tickets, list):
            return jsonify({'success': False, 'message': 'Invalid data format'})
        
        added = []
        already_exists = []
        
        for ticket in tickets:
            ticket = str(ticket).strip()
            if ticket and DataManager.add_hallticket(ticket):
                added.append(ticket)
            elif ticket:
                already_exists.append(ticket)
        
        return jsonify({
            'success': True,
            'added': added,
            'already_exists': already_exists,
            'message': f'Imported {len(added)} new tickets'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Import failed: {str(e)}'})

@app.route('/api/halltickets/import-upload', methods=['POST'])
def import_halltickets_upload():
    """Handle file upload for import"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    try:
        if file.filename.endswith('.txt'):
            # Process text file
            text_content = file.read().decode('utf-8')
            tickets = []
            for line in text_content.split('\n'):
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    tickets.append(line)
            
            # Add tickets to data manager
            added = []
            already_exists = []
            
            for ticket in tickets:
                ticket = str(ticket).strip()
                if ticket and DataManager.add_hallticket(ticket):
                    added.append(ticket)
                elif ticket:
                    already_exists.append(ticket)
            
            return jsonify({
                'success': True,
                'added': added,
                'already_exists': already_exists,
                'message': f'Imported {len(added)} new tickets from {file.filename}'
            })
        else:
            return jsonify({'success': False, 'message': 'Only .txt files are supported for file upload'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Import failed: {str(e)}'})

@app.route('/api/stop-scraping', methods=['POST'])
def stop_scraping():
    """Stop ongoing scraping process"""
    global scraping_status
    if scraping_status['is_running']:
        scraping_status.update({
            'is_running': False,
            'message': 'Scraping stopped by user',
            'active_threads': 0
        })
        return jsonify({'success': True, 'message': 'Scraping stopped'})
    return jsonify({'success': False, 'message': 'No scraping in progress'})

@app.route('/api/excel/download')
def download_excel():
    """Download the generated Excel file"""
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    return jsonify({'error': 'Excel file not found'}), 404

@app.route('/api/generate-excel', methods=['POST'])
def generate_excel():
    """Generate Excel from existing HTML files"""
    try:
        generator = ExcelGenerator()
        excel_data = generator.process_all_html_files()
        
        if excel_data:
            generator.generate_excel(excel_data)
            return jsonify({
                'success': True,
                'message': f'Excel generated with {len(excel_data)} student records'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data found. Run scraping first or check HTML files.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating Excel: {str(e)}'
        })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Starting GMRIT Results Scraper Web Interface...")
    print("Open http://localhost:5000 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
