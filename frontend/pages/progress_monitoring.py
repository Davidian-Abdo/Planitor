"""
PROFESSIONAL Progress Monitoring
Clean implementation with dependency injection
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session

from frontend.components.navigation.sidebar import render_project_selector
from frontend.components.data_tables.progress_table import render_progress_table

def show(db_session: Session, user_id: int):
    """
    Professional progress monitoring with dependency injection
    
    Args:
        db_session: Database session for backend operations
        user_id: Current user ID for data isolation
    """
    # Professional page setup
    st.title("📈 Progress Monitoring")
    
    # User context
    session_manager = st.session_state.session_manager
    st.caption(f"User: {session_manager.get_username()} | Project: {_get_current_project_name()}")
    
    # Initialize session state
    _initialize_session_state()
    
    # ✅ FIXED: Do NOT store db_session or user_id in session state
    # Database sessions are request-scoped and should not persist
    
    # Professional navigation
    render_project_selector(db_session, user_id)
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📊 Current Status", "📈 Analysis"])
    
    with tab1:
        _render_upload_section(db_session, user_id)
    
    with tab2:
        _render_status_section(db_session)
    
    with tab3:
        _render_analysis_section(db_session)

def _get_current_project_name() -> str:
    """Get current project name professionally"""
    project_config = st.session_state.get('project_config', {})
    return project_config.get('basic_info', {}).get('project_name', 'No Project Selected')

def _initialize_session_state():
    """Initialize session state professionally"""
    defaults = {
        'progress_data': None,
        'monitoring_analysis': None,
        'reference_schedule': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def _render_upload_section(db_session: Session, user_id: int):
    """Render professional data upload section"""
    st.header("📤 Upload Progress Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        _render_progress_upload(db_session, user_id)
    
    with col2:
        _render_reference_setup()

def _render_progress_upload(db_session: Session, user_id: int):
    """Render progress file upload professionally"""
    st.subheader("Progress Report Upload")
    
    uploaded_file = st.file_uploader(
        "Upload Progress Report",
        type=['xlsx', 'csv'],
        help="Upload your progress tracking data (Excel or CSV format)",
        key="progress_upload"
    )
    
    if uploaded_file:
        progress_data = _process_uploaded_file(uploaded_file, db_session)
        if progress_data is not None:
            st.session_state.progress_data = progress_data
            st.success("✅ Progress data uploaded successfully!")
            
            # Save data professionally
            _save_progress_data(progress_data, db_session, user_id)
            
            # Show preview
            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(progress_data.head(), use_container_width=True)

def _process_uploaded_file(uploaded_file, db_session: Session) -> Optional[pd.DataFrame]:
    """Process uploaded file professionally"""
    try:
        # Try backend service first
        try:
            from backend.services.file_processing_service import FileProcessingService
            file_service = FileProcessingService(db_session)
            return file_service.process_progress_file(uploaded_file)
        except ImportError:
            # Fallback processing
            return _process_file_fallback(uploaded_file)
            
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
        return None

def _process_file_fallback(uploaded_file) -> Optional[pd.DataFrame]:
    """Professional fallback file processing"""
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        required_cols = ['Date', 'TaskID', 'Progress']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {missing_cols}")
            return None
        
        # Professional data cleaning
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Progress'] = pd.to_numeric(df['Progress'], errors='coerce')
        
        # Data quality check
        invalid_data = df[df['Progress'].isna() | (df['Progress'] < 0) | (df['Progress'] > 100)]
        if not invalid_data.empty:
            st.warning(f"⚠️ Found {len(invalid_data)} rows with invalid progress values")
        
        st.success(f"✅ Processed {len(df)} progress records")
        return df
        
    except Exception as e:
        st.error(f"❌ File processing error: {e}")
        return None

def _save_progress_data(progress_data: pd.DataFrame, db_session: Session, user_id: int):
    """Save progress data professionally"""
    try:
        from backend.services.monitoring_service import MonitoringService
        
        monitoring_service = MonitoringService(db_session)
        success = monitoring_service.save_progress_updates(
            user_id=user_id,
            progress_data=progress_data,
            project_id=st.session_state.get('current_project_id')
        )
        
        if success:
            st.info("💾 Progress data saved to database")
        else:
            st.warning("⚠️ Progress data processed but not saved to database")
            
    except Exception as e:
        st.warning(f"⚠️ Database save warning: {e}")

def _render_reference_setup():
    """Render reference schedule setup"""
    st.subheader("Reference Schedule")
    
    if st.session_state.get('schedule_results'):
        st.success("✅ Using generated schedule as reference")
        st.session_state.reference_schedule = _convert_schedule_to_monitoring_format(
            st.session_state.schedule_results
        )
    else:
        st.warning("⚠️ No schedule available")
        # Allow manual reference upload
        ref_file = st.file_uploader(
            "Upload Reference Schedule",
            type=['xlsx', 'csv'],
            key="ref_upload"
        )
        if ref_file:
            st.session_state.reference_schedule = _process_reference_file(ref_file)

def _convert_schedule_to_monitoring_format(schedule_results) -> pd.DataFrame:
    """Convert schedule to monitoring format professionally"""
    try:
        rows = []
        for task in schedule_results.tasks:
            if hasattr(schedule_results, 'schedule') and task.id in schedule_results.schedule:
                start_date, end_date = schedule_results.schedule[task.id]
                rows.append({
                    'TaskID': task.id,
                    'TaskName': task.name,
                    'Discipline': task.discipline,
                    'Start': start_date,
                    'End': end_date,
                    'PlannedProgress': 0,
                    'Status': 'Planned'
                })
        
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error converting schedule: {e}")
        return pd.DataFrame()

def _process_reference_file(uploaded_file) -> pd.DataFrame:
    """Process reference file professionally"""
    try:
        if uploaded_file.name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file)
        else:
            return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error processing reference file: {e}")
        return pd.DataFrame()

def _render_status_section(db_session: Session):
    """Render current status section"""
    st.header("📊 Current Project Status")
    
    if st.session_state.progress_data is None:
        st.info("📭 Upload progress data to view current status")
        return
    
    # Get current status professionally
    from backend.services.monitoring_service import MonitoringService
    
    monitoring_service = MonitoringService(db_session)
    current_status = monitoring_service.calculate_current_status(
        st.session_state.progress_data,
        st.session_state.reference_schedule
    )
    
    # Professional status metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_progress = current_status.get('overall_progress', 0)
        st.metric("Overall Progress", f"{overall_progress:.1f}%")
    
    with col2:
        completed = current_status.get('completed_tasks', 0)
        total = current_status.get('total_tasks', 1)
        st.metric("Tasks Completed", f"{completed}/{total}")
    
    with col3:
        deviation = current_status.get('schedule_deviation', 0)
        st.metric("Schedule Deviation", f"{deviation:.1f} days")
    
    with col4:
        perf_index = current_status.get('performance_index', 0)
        st.metric("Performance Index", f"{perf_index:.2f}")
    
    # Recent updates
    st.subheader("🕒 Recent Progress Updates")
    if st.session_state.progress_data is not None:
        recent_data = st.session_state.progress_data.sort_values('Date', ascending=False).head(10)
        render_progress_table(recent_data)

def _render_analysis_section(db_session: Session):
    """Render progress analysis section"""
    st.header("📈 Progress Analysis")
    
    if st.session_state.progress_data is None or st.session_state.reference_schedule is None:
        st.info("📭 Upload progress data and reference schedule for analysis")
        return
    
    # Generate analysis
    if st.button("🔄 Generate Progress Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing progress data..."):
            from backend.services.monitoring_service import MonitoringService
            
            monitoring_service = MonitoringService(db_session)
            analysis_results = monitoring_service.analyze_progress(
                st.session_state.progress_data,
                st.session_state.reference_schedule
            )
            
            st.session_state.monitoring_analysis = analysis_results
            
            if analysis_results:
                st.success("✅ Progress analysis completed!")
    
    # Display results
    if st.session_state.monitoring_analysis:
        _display_analysis_results()

def _display_analysis_results():
    """Display analysis results professionally"""
    analysis = st.session_state.monitoring_analysis
    
    # S-Curve analysis
    if 'analysis_df' in analysis:
        st.subheader("📈 S-Curve Analysis")
        from frontend.components.charts.progress_charts import render_progress_dashboard
        render_progress_dashboard(analysis['analysis_df'])
    
    # Performance metrics
    if 'performance_metrics' in analysis:
        st.subheader("🎯 Performance Metrics")
        metrics = analysis['performance_metrics']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Schedule Performance", f"{metrics.get('spi', 0):.2f}")
            st.metric("Cost Performance", f"{metrics.get('cpi', 0):.2f}")
        
        with col2:
            st.metric("Planned Value", f"${metrics.get('pv', 0):,.0f}")
            st.metric("Earned Value", f"${metrics.get('ev', 0):,.0f}")