Monthly Extremes Report for WeeWX Belchertown

A custom report page for New Belchertown WeeWX Skin that displays historical monthly temperature extremes from your weather station's NOAA data.

Features
📊 Monthly Records — Absolute minimum and maximum temperatures for each month (with years)
📈 Summary Statistics — Overall extremes and temperature range
🗓️ Multi-Year Aggregation — Combines data from all available historical years
🔄 Automatic Updates — Python script regenerates data weekly via cron
🌙 Dark Mode — Full support for light/dark themes
📱 Responsive Design — Works on desktop, tablet, and mobile
⚡ Fast — Uses static JSON, no live calculations in browser
How It Works
NOAA Files (2020-2026)
        ↓
  Python Script
   (Weekly Cron)
        ↓
  extremes.json (Static)
        ↓
  HTML Report Page
        ↓
  Display to Users
Components
generate_extremes.py — Server-side script
Reads all NOAA files (NOAA-YYYY-MM.txt)
Calculates monthly extremes across all years
Generates static JSON file
Runs automatically every Sunday via cron
records-mensili.html — Report page
Loads JSON (instant, no lag)
Displays table with 12 months
Shows statistics cards
Integrates with Belchertown styling
Integration — Menu link
Added via nav-menu-custom.inc
No core files modified (upgrade-safe)
Installation
Prerequisites
WeeWX 5.x with New Belchertown skin
Python 3.6+
Web server (nginx/Apache) serving WeeWX files
Step 1: Copy Files
bash
# Copy Python script
cp generate_extremes.py /var/www/html/weewx/

# Create pages directory if needed
mkdir -p /var/www/html/weewx/pages

# Copy HTML report
cp records-mensili.html /var/www/html/weewx/pages/
Step 2: Generate Initial JSON
bash
cd /var/www/html/weewx/
python3 generate_extremes.py

Expected output:

✓ JSON generato: /var/www/html/weewx/extremes-2020-2025.json
  Mesi processati: 12
Step 3: Configure Cron (Weekly Update)
bash
crontab -e

Add this line to run every Sunday at midnight:

cron
0 0 * * 0 cd /var/www/html/weewx && python3 generate_extremes.py >> /var/log/weewx-extremes.log 2>&1

Verify it was added:

bash
crontab -l | grep generate_extremes
Step 4: Set File Permissions
bash
chmod 644 /var/www/html/weewx/extremes-2020-2025.json
chmod 644 /var/www/html/weewx/pages/records-mensili.html
chmod 755 /var/www/html/weewx/generate_extremes.py
Step 5: Add to Belchertown Menu
bash
# Copy menu template
cp /etc/weewx/skins/new-belchertown/nav-menu-custom.inc.example \
   /etc/weewx/skins/new-belchertown/nav-menu-custom.inc

Edit nav-menu-custom.inc and add this line after the "About" menu item:

html
<li class="menu-item menu-item-5${" current-menu-item" if $page == "records-mensili" else ""}"><a href="$relative_url/pages/records-mensili.html" itemprop="url"><span itemprop="name">Monthly Extremes</span></a></li>
Step 6: Sync to Public Server (if applicable)

If your WeeWX server differs from your web server:

bash
rsync -av /var/www/html/weewx/extremes-2020-2025.json root@webserver:/var/www/html/ecowitt_new/
rsync -av /var/www/html/weewx/pages/records-mensili.html root@webserver:/var/www/html/ecowitt_new/pages/
Customization
Language Translation

The HTML filename and labels can be translated. For example, to Spanish:

Rename records-mensili.html to records-extremos.html
Edit nav-menu-custom.inc:
html
   <span itemprop="name">Registros Mensuales</span>
Update URLs in the script if needed
JSON Output Location

The script outputs to:

/var/www/html/weewx/extremes-2020-2025.json

If you need a different location, edit generate_extremes.py:

python
OUTPUT_FILE = Path("/your/custom/path/extremes.json")
Styling Customization

The report uses standard CSS variables from Belchertown. To customize colors, add to your Custom CSS file in Belchertown settings:

css
table th {
    background-color: var(--your-color);
}
Troubleshooting
JSON file not generated
bash
# Run script manually to see errors
cd /var/www/html/weewx/
python3 generate_extremes.py

Check:

NOAA files exist in /var/www/html/weewx/noaa/NOAA-*.txt
Python 3 is installed: python3 --version
Write permissions on directory: ls -ld /var/www/html/weewx/
Cron not executing
bash
# Check cron was added
crontab -l

# Check cron log
tail -f /var/log/weewx-extremes.log

# Test manually
cd /var/www/html/weewx && python3 generate_extremes.py
Report page shows 404

Verify paths are correct:

records-mensili.html exists in /var/www/html/weewx/pages/
JSON file is accessible at /weewx/extremes-2020-2025.json
Check browser console (F12) for fetch errors
Wrong URL in HTML

The HTML expects paths relative to /weewx/. If Belchertown is at a different path, edit records-mensili.html:

javascript
const EXTREMES_JSON = '/your-path/extremes-2020-2025.json';
Data Processing
Input
All NOAA-*.txt files in /var/www/html/weewx/noaa/
Format: Standard WeeWX NOAA monthly summaries
Processing
Extracts daily HIGH and LOW temperatures
Aggregates by month across all years
Calculates absolute min/max and averages
Output JSON Format
json
[
  {
    "month": "January",
    "month_idx": 1,
    "min_temp": -5.1,
    "min_year": 2021,
    "max_temp": 15.4,
    "max_year": 2025,
    "avg_min": 1.2,
    "avg_max": 9.8,
    "years_count": 5
  },
  ...
]
Performance
Data Processing: ~100ms (runs weekly, not on each page view)
Page Load: <500ms (static JSON, no database queries)
Browser Rendering: Instant (pre-calculated stats)
Browser Support
Chrome/Edge 90+
Firefox 88+
Safari 14+
Mobile browsers (iOS Safari, Chrome Mobile)
Files
.
├── generate_extremes.py      # Python script to generate JSON
├── records-mensili.html      # Report page (rename as needed)
└── README.md                 # This file
License

MIT License - Feel free to modify and distribute.

Contributing

Found a bug? Have a suggestion? Please open an issue or submit a pull request.

Development

To modify the report:

Test generate_extremes.py locally:
bash
   python3 generate_extremes.py
Edit records-mensili.html in a browser for styling
Test in dark mode: Press Shift + Cmd/Ctrl + L in browser dev tools
Support
WeeWX Docs: https://weewx.io/
Belchertown Wiki: https://github.com/uajqq/weewx-belchertown-new/wiki
WeeWX Forum: https://github.com/weewx/weewx/discussions
Changelog
v1.0.0 (2026-09-12)
Initial release
Monthly extremes report
Cron-based weekly updates
Dark mode support
Responsive design

Created for: https://www.pnmeteo.it/ecowitt_new/
WeeWX Skin: New Belchertown 2.1.1
