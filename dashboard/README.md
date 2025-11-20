# 📊 Lead Generation Dashboard

Real-time web dashboard for monitoring lead extraction progress and viewing extracted data.

## Features

### 📊 Live Monitoring
- Real-time extraction progress tracking
- Active job status
- Current company being extracted
- Progress bars and percentages
- Recent extraction history

### 📈 Statistics & Metrics
- Total jobs and completion rate
- Total leads extracted
- Breakdown by geography
- Breakdown by industry
- Interactive charts and visualizations

### 📋 Data Viewer
- View all extracted leads
- Filter by geography, industry, country
- Search by company name
- Sort and paginate data
- Download filtered results as CSV

### 📁 Data Files Manager
- View all generated data files
- File statistics (size, modification date, record count)
- Preview file contents
- Quick access to exports

## Quick Start

### 1. Install Dependencies

```bash
pip install streamlit plotly altair pyyaml
```

### 2. Start Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically at: **http://localhost:8501**

### 3. Run Extraction with Monitoring

In a separate terminal, run:

```bash
python src/targeted_extraction_monitored.py --geography india --industry fmcg --count 100
```

### 4. Watch Live Progress

The dashboard will automatically show:
- Real-time progress updates (auto-refreshes every 10 seconds)
- Companies being extracted
- Progress bars and percentages
- Final results when complete

## Dashboard Pages

### 📊 Live Monitoring

Shows active extractions with:
- Geography and industry
- Current progress (extracted/target)
- Progress percentage
- Current company being processed
- Recent extraction jobs

**Auto-refresh**: Enable in sidebar (default: 10 seconds)

### 📈 Statistics

Displays aggregate metrics:
- Total jobs (all time)
- Completed jobs
- Total leads extracted
- Success rate
- Bar chart by geography
- Pie chart by industry

### 📋 Data Viewer

Interactive data table with:
- **Filters**: Geography, Industry, Country
- **Search**: Find companies by name
- **Display**: Up to 100 rows at a time
- **Download**: Export filtered data to CSV

**Columns shown:**
- Company Name
- Country
- Target Geography
- Target Industry
- Status
- Address (if available)

### 📁 Data Files

File management:
- List all CSV files in `data/processed/`
- File statistics (size, date, records)
- Preview first 5 rows
- Quick access to download

## Usage Examples

### Monitor Live Extraction

1. Start dashboard:
```bash
streamlit run dashboard/app.py
```

2. In another terminal, start extraction:
```bash
python src/targeted_extraction_monitored.py --geography singapore --industry ecommerce --count 50
```

3. Watch live progress in dashboard at **📊 Live Monitoring** page

### View Extracted Data

1. Go to **📋 Data Viewer** page
2. Select filters:
   - Geography: India
   - Industry: FMCG
   - Country: India
3. Search for specific company
4. Click **Download** to export filtered data

### Check Statistics

1. Go to **📈 Statistics** page
2. View:
   - Total leads extracted
   - Breakdown by geography (bar chart)
   - Breakdown by industry (pie chart)
   - Completion rates

## Configuration

### Auto-Refresh Settings

In the sidebar:
- Toggle **Auto-refresh** on/off
- Adjust **Refresh interval** (5-60 seconds)

Default: 10 seconds (recommended for live monitoring)

### Dashboard Port

Change port if 8501 is busy:
```bash
streamlit run dashboard/app.py --server.port 8502
```

### Theme

Streamlit supports light/dark themes:
- Click ⋮ (menu) → Settings → Theme
- Or create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## Data Storage

### Progress Database

Progress data stored in: **`data/extraction_progress.db`** (SQLite)

Tables:
- `extraction_jobs` - Job metadata
- `progress_updates` - Real-time progress log
- `leads_summary` - Quick lead summaries for stats

### Extracted Data

CSV files stored in: **`data/processed/`**

Format: `targeted_leads_YYYYMMDD_HHMMSS.csv`

## Troubleshooting

### Dashboard won't start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Fix**:
```bash
pip install streamlit plotly altair pyyaml
```

### No live progress showing

**Issue**: Extraction running but dashboard shows "No active extractions"

**Fix**:
- Make sure you're using `targeted_extraction_monitored.py` (not `targeted_extraction.py`)
- Check that `data/extraction_progress.db` exists
- Enable auto-refresh in dashboard sidebar

### Data not showing in viewer

**Issue**: "No leads data available yet"

**Fix**:
- Check that CSV files exist in `data/processed/`
- Run an extraction to generate data
- Refresh the dashboard page

### Dashboard is slow

**Issue**: Dashboard takes long to load data

**Fix**:
- Large CSV files can slow loading
- Dashboard shows max 100 rows per view
- Use filters to reduce data shown
- Consider archiving old CSV files

## Advanced Features

### Custom Database Path

Change progress database location:

```python
# In targeted_extraction_monitored.py
tracker = ProgressTracker(db_path="custom/path/progress.db")
```

### Remote Dashboard

Run dashboard on server and access remotely:

```bash
streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501
```

Access at: `http://your-server-ip:8501`

**Security**: Use authentication if exposing publicly

### Embedding Dashboard

Embed in iframe:
```html
<iframe src="http://localhost:8501" width="100%" height="800px"></iframe>
```

## API Access

Access progress data programmatically:

```python
from core.progress_tracker import get_tracker

tracker = get_tracker()

# Get statistics
stats = tracker.get_statistics()
print(f"Total leads: {stats['total_leads']}")

# Get active jobs
active = tracker.get_active_jobs()
for job in active:
    print(f"{job['geography']} - {job['extracted_count']}/{job['target_count']}")

# Get recent leads
recent = tracker.get_recent_leads(limit=10)
for lead in recent:
    print(lead['company_name'])
```

## Screenshots

### Live Monitoring
```
🎯 Lead Generation Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Live Extraction Monitoring
🟢 1 Active Extraction(s)

📍 INDIA - FMCG
   Extracted: 45    Target: 100    Progress: 45.0%
   ████████████░░░░░░░░░░░░░░ 45%
   Currently extracting: ABC Foods Pvt Ltd
   Last update: 2024-01-15T14:23:45
```

### Statistics
```
📈 Statistics & Metrics

Total Jobs: 25    Completed: 23    Total Leads: 2,450    Success Rate: 92%

[Bar Chart: Leads by Geography]
[Pie Chart: Leads by Industry]
```

### Data Viewer
```
📋 Extracted Leads Data

Total Companies: 2,450    Countries: 15    Industries: 5    Geographies: 4

🔍 Filter Data
Geography: [India ▼]    Industry: [FMCG ▼]    Country: [India ▼]

Showing 250 of 2,450 companies

📊 Companies (250)
┌─────────────────────────────────┬─────────┬──────────┬──────────┐
│ Company Name                    │ Country │ Geography│ Industry │
├─────────────────────────────────┼─────────┼──────────┼──────────┤
│ ABC Foods Pvt Ltd              │ India   │ INDIA    │ FMCG     │
│ XYZ Beverages Limited          │ India   │ INDIA    │ FMCG     │
...
```

## Cost

**Dashboard**: ✅ Free
**Hosting**: ✅ Free (run locally)
**Cloud Hosting**: ✅ Free tier available (Streamlit Cloud)

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect GitHub repo
4. Set main file: `dashboard/app.py`
5. Deploy!

**Result**: Public dashboard at `https://your-app.streamlit.app`

### Deploy to Local Server

```bash
# Install as service (Linux systemd)
sudo tee /etc/systemd/system/lead-dashboard.service > /dev/null <<EOF
[Unit]
Description=Lead Generation Dashboard
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Lead-Engine
ExecStart=/usr/bin/streamlit run dashboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable lead-dashboard
sudo systemctl start lead-dashboard
```

## Support

### Issues
- Progress not updating → Check auto-refresh is enabled
- Data not loading → Verify CSV files exist
- Slow performance → Reduce data file sizes

### Questions
- Check main README.md
- See docs/SETUP.md
- Review docs/TARGETED_EXTRACTION.md

---

**Enjoy monitoring your lead generation in real-time! 📊**
