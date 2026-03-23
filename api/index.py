"""
Vercel Serverless Function for GMRIT Results Scraper
Simplified version for cloud deployment
"""
import json
from flask import Flask, request, jsonify, send_file
import os
from datetime import datetime

app = Flask(__name__)

# Mock data storage for Vercel (in production, use Vercel KV or external database)
HALL_TICKETS = []

@app.route('/')
def index():
    """Serve the web interface"""
    try:
        with open('templates/index_enhanced.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Template not found", 404

@app.route('/api/halltickets')
def get_halltickets():
    """Get all saved hall tickets"""
    return jsonify({'tickets': HALL_TICKETS})

@app.route('/api/halltickets', methods=['POST'])
def add_halltickets():
    """Add hall tickets"""
    data = request.get_json()
    tickets = data.get('tickets', [])
    
    added = []
    already_exists = []
    
    for ticket in tickets:
        ticket = ticket.strip()
        if ticket and ticket not in HALL_TICKETS:
            HALL_TICKETS.append(ticket)
            added.append(ticket)
        elif ticket:
            already_exists.append(ticket)
    
    return jsonify({
        'success': True,
        'added': added,
        'already_exists': already_exists
    })

@app.route('/api/halltickets/<ticket>', methods=['DELETE'])
def remove_hallticket(ticket):
    """Remove a specific hall ticket"""
    if ticket in HALL_TICKETS:
        HALL_TICKETS.remove(ticket)
    return jsonify({'success': True})

@app.route('/api/halltickets', methods=['DELETE'])
def clear_halltickets():
    """Clear all hall tickets"""
    global HALL_TICKETS
    HALL_TICKETS = []
    return jsonify({'success': True})

@app.route('/api/halltickets/export')
def export_halltickets():
    """Export hall tickets as text file"""
    text_content = "# GMRIT Hall Tickets\n"
    text_content += f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text_content += f"# Total Tickets: {len(HALL_TICKETS)}\n\n"
    
    for ticket in HALL_TICKETS:
        text_content += f"{ticket}\n"
    
    response = app.response_class(
        response=text_content,
        status=200,
        mimetype='text/plain'
    )
    response.headers['Content-Disposition'] = f'attachment; filename=hall_tickets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    return response

@app.route('/api/status')
def get_status():
    """Get current status"""
    return jsonify({
        'is_running': False,
        'progress': 0,
        'current_ticket': '',
        'total_tickets': 0,
        'success_count': 0,
        'failed_count': 0,
        'message': 'Ready to scrape (Note: Full scraping requires local deployment)',
        'logs': [],
        'start_time': None,
        'elapsed_time': 0,
        'concurrent_mode': False,
        'active_threads': 0
    })

@app.route('/api/summary')
def get_summary():
    """Get results summary"""
    return jsonify({
        'hall_tickets': len(HALL_TICKETS),
        'html_files': 0,
        'pdf_files': 0,
        'excel': {'exists': False},
        'scraping_status': {
            'is_running': False,
            'message': 'Full scraping requires local deployment due to browser requirements'
        }
    })

@app.route('/api/files')
def get_files():
    """Get list of all files"""
    return jsonify({
        'html_files': [],
        'pdf_files': [],
        'excel_file': None
    })

# Disable scraping endpoints for Vercel (they won't work in serverless environment)
@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Scraping not available on Vercel"""
    return jsonify({
        'success': False, 
        'message': 'Scraping requires local deployment with Chrome browser. Please deploy locally for full functionality.'
    })

if __name__ == '__main__':
    app.run(debug=True)
