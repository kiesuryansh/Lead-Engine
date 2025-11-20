"""
Lead Generation Dashboard - Real-time Monitoring & Data Viewer

A Streamlit-based web dashboard for monitoring extraction progress
and viewing extracted leads data.

Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime, timedelta
import glob
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.progress_tracker import get_tracker

# Page config
st.set_page_config(
    page_title="Lead Generation Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stProgress > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def get_data_files():
    """Get list of all extracted data CSV files"""
    data_dir = Path(__file__).parent.parent / 'data' / 'processed'
    if not data_dir.exists():
        return []

    csv_files = list(data_dir.glob('*.csv'))
    return sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)


def load_all_leads_data():
    """Load all extracted leads from CSV files"""
    files = get_data_files()

    if not files:
        return pd.DataFrame()

    dfs = []
    for file in files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            st.warning(f"Could not load {file.name}: {e}")

    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        # Remove duplicates based on company name
        if 'company_name' in combined.columns:
            combined = combined.drop_duplicates(subset=['company_name'])
        return combined

    return pd.DataFrame()


def show_header():
    """Display dashboard header"""
    st.markdown('<h1 class="main-header">🎯 Lead Generation Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")


def show_live_monitoring():
    """Display live extraction monitoring"""
    st.header("📊 Live Extraction Monitoring")

    tracker = get_tracker()

    # Get active jobs
    active_jobs = tracker.get_active_jobs()

    if active_jobs:
        st.success(f"🟢 {len(active_jobs)} Active Extraction(s)")

        for job in active_jobs:
            with st.expander(f"📍 {job['geography'].upper()} - {job['industry'].upper()}", expanded=True):
                # Get progress
                progress = tracker.get_job_progress(job['job_id'])

                if progress:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Extracted", progress['current_count'])

                    with col2:
                        st.metric("Target", progress['target_count'])

                    with col3:
                        st.metric("Progress", f"{progress['percentage']:.1f}%")

                    # Progress bar
                    st.progress(progress['percentage'] / 100)

                    if progress['current_company']:
                        st.caption(f"Currently extracting: {progress['current_company']}")

                    st.caption(f"Last update: {progress['timestamp']}")
                else:
                    st.info("Initializing extraction...")

    else:
        st.info("No active extractions. Start one to see live progress!")

    # Recent jobs
    st.subheader("🕐 Recent Extractions")

    recent_jobs = tracker.get_recent_jobs(limit=10)

    if recent_jobs:
        df = pd.DataFrame(recent_jobs)

        # Format dataframe
        df['geography'] = df['geography'].str.upper()
        df['industry'] = df['industry'].str.upper()
        df['progress'] = df.apply(lambda x: f"{x['extracted_count']}/{x['target_count']}", axis=1)

        # Status emoji
        status_emoji = {'completed': '✅', 'running': '🔄', 'failed': '❌'}
        df['status_display'] = df['status'].map(lambda x: f"{status_emoji.get(x, '❓')} {x.upper()}")

        # Display table
        st.dataframe(
            df[['geography', 'industry', 'progress', 'status_display', 'started_at']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No extraction history yet.")


def show_statistics():
    """Display extraction statistics"""
    st.header("📈 Statistics & Metrics")

    tracker = get_tracker()
    stats = tracker.get_statistics()

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Jobs",
            value=stats['total_jobs'],
            delta=None
        )

    with col2:
        st.metric(
            label="Completed Jobs",
            value=stats['completed_jobs'],
            delta=None
        )

    with col3:
        st.metric(
            label="Total Leads",
            value=f"{stats['total_leads']:,}",
            delta=None
        )

    with col4:
        completion_rate = (stats['completed_jobs'] / stats['total_jobs'] * 100) if stats['total_jobs'] > 0 else 0
        st.metric(
            label="Success Rate",
            value=f"{completion_rate:.0f}%",
            delta=None
        )

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Leads by Geography")
        if stats['by_geography']:
            geo_df = pd.DataFrame(list(stats['by_geography'].items()), columns=['Geography', 'Leads'])
            geo_df['Geography'] = geo_df['Geography'].str.upper()

            fig = px.bar(
                geo_df,
                x='Geography',
                y='Leads',
                color='Leads',
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet")

    with col2:
        st.subheader("Leads by Industry")
        if stats['by_industry']:
            ind_df = pd.DataFrame(list(stats['by_industry'].items()), columns=['Industry', 'Leads'])
            ind_df['Industry'] = ind_df['Industry'].str.upper()

            fig = px.pie(
                ind_df,
                values='Leads',
                names='Industry',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet")


def show_data_viewer():
    """Display extracted leads data viewer"""
    st.header("📋 Extracted Leads Data")

    # Load data
    df = load_all_leads_data()

    if df.empty:
        st.info("No leads data available yet. Run an extraction to populate this view.")
        return

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Companies", len(df))

    with col2:
        if 'country' in df.columns:
            st.metric("Countries", df['country'].nunique())

    with col3:
        if 'target_industry' in df.columns:
            st.metric("Industries", df['target_industry'].nunique())

    with col4:
        if 'target_geography' in df.columns:
            st.metric("Geographies", df['target_geography'].nunique())

    st.markdown("---")

    # Filters
    st.subheader("🔍 Filter Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        if 'target_geography' in df.columns:
            geographies = ['All'] + sorted(df['target_geography'].dropna().unique().tolist())
            selected_geo = st.selectbox("Geography", geographies)

    with col2:
        if 'target_industry' in df.columns:
            industries = ['All'] + sorted(df['target_industry'].dropna().unique().tolist())
            selected_ind = st.selectbox("Industry", industries)

    with col3:
        if 'country' in df.columns:
            countries = ['All'] + sorted(df['country'].dropna().unique().tolist())
            selected_country = st.selectbox("Country", countries)

    # Apply filters
    filtered_df = df.copy()

    if 'target_geography' in df.columns and selected_geo != 'All':
        filtered_df = filtered_df[filtered_df['target_geography'] == selected_geo]

    if 'target_industry' in df.columns and selected_ind != 'All':
        filtered_df = filtered_df[filtered_df['target_industry'] == selected_ind]

    if 'country' in df.columns and selected_country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == selected_country]

    st.info(f"Showing {len(filtered_df)} of {len(df)} companies")

    # Search
    search_query = st.text_input("🔎 Search company name", "")

    if search_query:
        if 'company_name' in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df['company_name'].str.contains(search_query, case=False, na=False)
            ]

    # Display data
    st.subheader(f"📊 Companies ({len(filtered_df)})")

    # Select columns to display
    display_columns = []
    if 'company_name' in filtered_df.columns:
        display_columns.append('company_name')
    if 'country' in filtered_df.columns:
        display_columns.append('country')
    if 'target_geography' in filtered_df.columns:
        display_columns.append('target_geography')
    if 'target_industry' in filtered_df.columns:
        display_columns.append('target_industry')
    if 'status' in filtered_df.columns:
        display_columns.append('status')
    if 'address' in filtered_df.columns:
        display_columns.append('address')

    if display_columns:
        st.dataframe(
            filtered_df[display_columns].head(100),  # Limit to 100 for performance
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(filtered_df.head(100), use_container_width=True, hide_index=True)

    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name=f"leads_{selected_geo}_{selected_ind}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


def show_data_files():
    """Show available data files"""
    st.header("📁 Data Files")

    files = get_data_files()

    if files:
        st.success(f"Found {len(files)} data file(s)")

        for file in files:
            with st.expander(f"📄 {file.name}"):
                stats = file.stat()
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Size", f"{stats.st_size / 1024:.1f} KB")

                with col2:
                    modified = datetime.fromtimestamp(stats.st_mtime)
                    st.metric("Modified", modified.strftime('%Y-%m-%d %H:%M'))

                with col3:
                    try:
                        df = pd.read_csv(file)
                        st.metric("Records", len(df))
                    except:
                        st.metric("Records", "N/A")

                # Preview
                try:
                    df = pd.read_csv(file)
                    st.dataframe(df.head(5), use_container_width=True)
                except Exception as e:
                    st.error(f"Could not preview: {e}")
    else:
        st.info("No data files found. Run an extraction to generate data files.")


def main():
    """Main dashboard"""
    show_header()

    # Sidebar
    with st.sidebar:
        st.title("🎯 Navigation")

        page = st.radio(
            "Select Page",
            [
                "📊 Live Monitoring",
                "📈 Statistics",
                "📋 Data Viewer",
                "📁 Data Files"
            ]
        )

        st.markdown("---")

        st.subheader("⚙️ Settings")

        # Auto-refresh
        auto_refresh = st.checkbox("Auto-refresh", value=True)

        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh interval (seconds)",
                min_value=5,
                max_value=60,
                value=10
            )

        st.markdown("---")

        st.caption("💰 Cost: $0.00")
        st.caption("⚖️ Legal: 100%")

        st.markdown("---")

        st.subheader("🚀 Quick Actions")

        if st.button("Run Extraction"):
            st.info("Run extraction from terminal:\n```bash\npython src/targeted_extraction.py --geography india --industry fmcg --count 100\n```")

    # Display selected page
    if "Live Monitoring" in page:
        show_live_monitoring()

    elif "Statistics" in page:
        show_statistics()

    elif "Data Viewer" in page:
        show_data_viewer()

    elif "Data Files" in page:
        show_data_files()

    # Auto-refresh
    if auto_refresh and "Live Monitoring" in page:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
