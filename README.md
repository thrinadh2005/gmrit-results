# GMRIT Results Scraper - Enhanced Web Interface

A high-performance web application to scrape student exam results from GMRIT (GMR Institute of Technology) and export them to formatted Excel files with concurrent processing and advanced file management.

## Features

- 🚀 **Concurrent Scraping** - Process multiple hall tickets simultaneously (2-5 workers)
- 📊 **Real-time Performance Metrics** - Monitor speed, elapsed time, success rate
- 📁 **Complete File Management** - View, download, delete HTML/PDF/Excel files
- 🎫 **Import/Export Hall Tickets** - Save and load hall ticket lists
- 🎨 **Modern Web Interface** - Responsive design with tabbed navigation
- ⚡ **High Performance** - Up to 3x faster processing with concurrent mode
- 📱 **Mobile Friendly** - Works on all devices
- 🔄 **Real-time Updates** - Live progress tracking and status updates

## 🚀 Quick Deploy to Render

1. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/gmrit-results.git
   git push -u origin main
   ```

2. **Deploy to Render:**
   - Go to https://render.com
   - Connect GitHub
   - Select `gmrit-results` repository
   - Use: `pip install -r requirements.txt && python run.py`
   - Deploy!

**🌐 Live URL:** `https://your-app.onrender.com` with full scraping functionality

## 📋 Alternative Deployments

- **VPS:** DigitalOcean, AWS EC2 (full control)
- **Docker:** `docker build -t gmrit-scraper . && docker run -p 5000:5000 gmrit-scraper`
- **Local:** `python run.py` for development

## Usage

### Adding Hall Tickets
1. Go to **Hall Tickets** tab
2. Enter hall ticket numbers (one per line or comma-separated)
3. Click **Add Tickets** to save them
4. Use **Import/Export** for bulk operations

### Fast Scraping
1. Go to **Scraping** tab
2. Enable **Concurrent Processing** for faster results
3. Select number of workers (2-5)
4. Click **Start Scraping**
5. Monitor real-time progress and performance metrics

### File Management
1. Go to **Files** tab
2. View all HTML, PDF, and Excel files
3. Download individual files or all files as ZIP
4. Delete unwanted files or clear all of specific type

### Performance Features
- **Concurrent Mode**: Process multiple tickets simultaneously
- **Real-time Metrics**: Speed, elapsed time, active threads, success rate
- **Stop Functionality**: Stop scraping anytime
- **Auto-recovery**: Handles failed requests automatically

## Project Structure

```
gmrit-results/
├── run.py                  # Production launcher
├── app.py                  # Enhanced Flask web application
├── config.py               # Configuration settings
├── logger.py               # Logging module
├── data_manager.py         # Hall ticket data management
├── scraper.py              # Web scraping module
├── excel_generator.py      # Excel generation with formatting
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html         # Original interface
│   └── index_enhanced.html # Enhanced interface
├── data/                   # Hall ticket storage
├── html_pages/             # Scraped HTML files
├── pdfs/                   # Generated PDF results
└── README.md               # This file
```

## Requirements

- Python 3.7+
- Google Chrome (for Selenium WebDriver)
- Internet connection

## Example Hall Tickets

Format: `24341A0502`

## Performance Tips

1. **Enable Concurrent Mode** for 3x faster processing
2. **Adjust Workers** based on your system capability (2-5 workers)
3. **Monitor Metrics** to optimize performance
4. **Use Import/Export** for managing large hall ticket lists

## API Endpoints

- `GET /` - Main web interface
- `GET /api/halltickets` - Get saved hall tickets
- `POST /api/halltickets` - Add hall tickets
- `DELETE /api/halltickets/<ticket>` - Remove specific ticket
- `POST /api/scrape` - Start scraping (supports concurrent mode)
- `POST /api/stop-scraping` - Stop ongoing scraping
- `GET /api/status` - Get scraping status
- `GET /api/files` - Get all files list
- `GET /api/files/download-all` - Download all files as ZIP
- `GET /api/halltickets/export` - Export hall tickets as JSON
- `POST /api/halltickets/import` - Import hall tickets from JSON

## Notes

- This tool is for educational purposes
- Please use responsibly and respect the website's terms of service
- Concurrent processing significantly improves performance for multiple tickets
- All data is stored locally in the project directory

## License

MIT License
