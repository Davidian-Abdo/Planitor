"""
Generate Schedule Page - UPDATED with Template Selection & Import/Export
PROFESSIONAL VERSION: Users can choose between Excel upload or Template selection
"""
import streamlit as st
import pandas as pd
import os
import tempfile
import zipfile
import io
import json
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from frontend.components.charts.gantt_display import render_gantt_with_controls
from frontend.components.charts.progress_charts import render_schedule_metrics
from frontend.components.data_tables.schedule_table import render_schedule_table
from frontend.components.navigation.sidebar import render_project_selector
from frontend.components.auth.auth_guard import require_auth

@require_auth("write")
def show(db_session: Session, services: Dict[str, Any], user_id: int):
    """
    UPDATED Main schedule generation page with template selection option
    """
    # ✅ Use services passed from app.py
    if not services:
        st.error("❌ Services not initialized")
        return
    # ✅ Get user info from SessionManager
    session_manager = st.session_state.auth_session_manager
    user_info = _get_user_info(session_manager)
    
    st.markdown('<div class="main-header">📅 Generate Construction Schedule</div>', unsafe_allow_html=True)
    st.caption(f"User: {user_info['username']} | Project: {_get_current_project_name()}")
    
        # ✅ FIXED: Do NOT store db_session or user_id in session state
    # Database sessions are request-scoped and should not persist
    
    # Initialize session state
    _initialize_session_state()
    
    # Render navigation
    render_project_selector(db_session, user_id)
    
    # Check prerequisites
    if not _check_prerequisites():
        return
    
    # Main content - UPDATED with template selection
    _render_input_method_selection(db_session, user_id)
    
    # Results display
    if st.session_state.get('schedule_generated'):
        _render_schedule_results(db_session, user_id)


def _get_user_info(session_manager) -> Dict[str, Any]:
    """Get user information from SessionManager"""
    return {
        'id': session_manager.get_user_id(),
        'username': session_manager.get_username(),
        'role': session_manager.get_user_role(),
        'full_name': session_manager.get_username()
    }


def _get_current_project_name() -> str:
    """Get current project name safely"""
    project_config = st.session_state.get('project_config', {})
    basic_info = project_config.get('basic_info', {})
    return basic_info.get('project_name', 'No Project Selected')


def _initialize_session_state():
    """Initialize session state for schedule generation"""
    defaults = {
        'schedule_generated': False,
        'schedule_results': None,
        'current_project_id': None,
        'input_method': 'templates',  # 'templates' or 'excel'
        'selected_task_template': None,
        'selected_resource_template': None,
        'uploaded_files': {},
        'reports_folder': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _check_prerequisites() -> bool:
    """Check if all prerequisites are met for schedule generation"""
    # Check project configuration
    if 'project_config' not in st.session_state or not st.session_state.project_config.get('zones'):
        st.error("❌ Please configure your project in the Project Setup page first.")
        st.info("Go to Project Setup to define your building zones and floors.")
        return False
    
    return True


def _render_input_method_selection(db_session: Session, services: Dict[str, Any], user_id: int):
    """Render input method selection (Templates vs Excel Upload)"""
    st.subheader("🔧 Choose Input Method")
    
    # Input method selection
    input_method = st.radio(
        "Select how you want to provide scheduling data:",
        options=["📁 Use Templates (Recommended)", "📤 Upload Excel Files"],
        key="input_method_selector",
        help="Choose between using your saved templates or uploading Excel files"
    )
    
    st.session_state.input_method = 'templates' if input_method.startswith("📁") else 'excel'
    
    if st.session_state.input_method == 'templates':
        _render_template_selection(db_session,  services, user_id)
    else:
        _render_excel_upload_section(db_session,  services, user_id)
    
    # Import/Export section (moved from templates_manager)
    _render_import_export_section(services, user_id)


def _render_template_selection(db_session: Session, services: Dict[str, Any],user_id: int):
    """Render template selection interface"""
    st.markdown("---")
    st.subheader("📋 Select Templates for Scheduling")
    
    try:
        template_service = services['template_service']
        
        # Get available templates
        available_templates = template_service.get_available_templates(user_id)
        resource_templates = available_templates.get('resource_templates', [])
        task_templates = available_templates.get('task_templates', [])
        
        if not resource_templates or not task_templates:
            st.error("❌ No templates found. Please create templates in the Templates Manager first.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Task Template")
            task_template_options = {t.get('template_name', f"Template_{i}"): t for i, t in enumerate(task_templates)}
            selected_task_template_name = st.selectbox(
                "Select Task Template:",
                options=list(task_template_options.keys()),
                key="task_template_select",
                help="Choose the task template to use for scheduling"
            )
            
            if selected_task_template_name:
                st.session_state.selected_task_template = task_template_options[selected_task_template_name]
                # Display task template info
                task_template = st.session_state.selected_task_template
                st.info(f"**Tasks:** {len(task_template.get('tasks', []))} | **Disciplines:** {len(set(t.get('discipline') for t in task_template.get('tasks', [])))}")
        
        with col2:
            st.markdown("#### 👥 Resource Template")
            resource_template_options = {t.get('name', f"Resource_{i}"): t for i, t in enumerate(resource_templates)}
            selected_resource_template_name = st.selectbox(
                "Select Resource Template:",
                options=list(resource_template_options.keys()),
                key="resource_template_select",
                help="Choose the resource template to use for scheduling"
            )
            
            if selected_resource_template_name:
                st.session_state.selected_resource_template = resource_template_options[selected_resource_template_name]
                # Display resource template info
                resource_template = st.session_state.selected_resource_template
                template_metrics = template_service.get_template_metrics(user_id, 
                                                                        st.session_state.selected_task_template,
                                                                        st.session_state.selected_resource_template)
                st.info(f"**Workers:** {template_metrics.get('worker_count', 0)} | **Equipment:** {template_metrics.get('equipment_count', 0)}")
        
        # Validate template dependency
        if st.session_state.selected_task_template and st.session_state.selected_resource_template:
            validation_result = template_service.validate_template_dependency(
                user_id, 
                st.session_state.selected_task_template, 
                st.session_state.selected_resource_template
            )
            
            if not validation_result['is_valid']:
                st.warning("⚠️ Template dependency validation failed:")
                if validation_result['missing_workers']:
                    st.error(f"Missing workers: {', '.join(validation_result['missing_workers'])}")
                if validation_result['missing_equipment']:
                    st.error(f"Missing equipment: {', '.join(validation_result['missing_equipment'])}")
            else:
                st.success("✅ Template dependency validation passed!")
                
            # Show warnings
            for warning in validation_result['warnings']:
                st.warning(warning)
            
            # Schedule generation parameters
            _render_schedule_parameters(db_session, user_id, method='templates')
            
    except Exception as e:
        st.error(f"❌ Error loading templates: {e}")


def _render_excel_upload_section(db_session: Session, user_id: int):
    """Render Excel file upload interface"""
    st.markdown("---")
    st.subheader("📤 Upload Excel Files")
    
    st.info("""
    **Required Files:**
    - 📊 **Quantity Template**: Task quantities per zone/floor
    - 👥 **Resources Template**: Worker definitions and rates  
    - 🛠️ **Equipment Template**: Equipment definitions and rates
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        quantity_file = st.file_uploader(
            "Quantity Template (Excel)",
            type=["xlsx", "xls"],
            key="quantity_upload",
            help="Upload Excel file with task quantities"
        )
    
    with col2:
        resources_file = st.file_uploader(
            "Resources Template (Excel)", 
            type=["xlsx", "xls"],
            key="resources_upload",
            help="Upload Excel file with worker resources"
        )
    
    with col3:
        equipment_file = st.file_uploader(
            "Equipment Template (Excel)",
            type=["xlsx", "xls"], 
            key="equipment_upload",
            help="Upload Excel file with equipment resources"
        )
    
    # Store uploaded files
    if quantity_file:
        st.session_state.uploaded_files['quantity'] = quantity_file
    if resources_file:
        st.session_state.uploaded_files['resources'] = resources_file
    if equipment_file:
        st.session_state.uploaded_files['equipment'] = equipment_file
    
    # Check if all required files are uploaded
    required_files = ['quantity']
    missing_files = [f for f in required_files if f not in st.session_state.uploaded_files]
    
    if missing_files:
        st.error(f"❌ Missing required files: {', '.join(missing_files)}")
        return
    
    # Schedule generation parameters
    _render_schedule_parameters(db_session, user_id, method='excel')


def _render_schedule_parameters(db_session: Session, user_id: int, method: str):
    """Render schedule generation parameters"""
    st.markdown("---")
    st.subheader("⚙️ Schedule Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        optimization_level = st.selectbox(
            "Optimization Level",
            options=["Balanced", "Time-Optimized", "Cost-Optimized", "Resource-Efficient"],
            help="Choose the optimization strategy for schedule generation",
            key="optimization_level"
        )
        
        include_risk_analysis = st.checkbox(
            "Include Risk Analysis",
            value=True,
            help="Include risk factors and contingencies in scheduling",
            key="include_risk_analysis"
        )
    
    with col2:
        # Get acceleration factor from project config with fallback
        acceleration_factor = st.session_state.project_config.get(
            'advanced_settings', {}
        ).get('acceleration_factor', 1.0)
        
        acceleration_factor = st.slider(
            "Acceleration Factor",
            min_value=0.5,
            max_value=3.0,
            value=acceleration_factor,
            step=0.1,
            help="Factor to accelerate the schedule (requires more resources)",
            key="acceleration_factor"
        )
        
        generate_reports = st.checkbox(
            "Generate Detailed Reports",
            value=True,
            help="Generate comprehensive Excel reports and analysis",
            key="generate_reports"
        )
    
    # Generate schedule button
    generate_disabled = False
    if method == 'templates' and (not st.session_state.selected_task_template or not st.session_state.selected_resource_template):
        generate_disabled = True
    elif method == 'excel' and 'quantity' not in st.session_state.uploaded_files:
        generate_disabled = True
    
    if st.button("🎯 Generate Optimized Schedule", 
                 type="primary", 
                 use_container_width=True,
                 disabled=generate_disabled):
        _generate_schedule(
            db_session=db_session,
            user_id=user_id,
            method=method,
            optimization_level=optimization_level,
            acceleration_factor=acceleration_factor,
            include_risk_analysis=include_risk_analysis,
            generate_reports=generate_reports
        )


def _generate_schedule(db_session: Session, user_id: int, method: str, optimization_level: str, 
                      acceleration_factor: float, include_risk_analysis: bool, 
                      generate_reports: bool):
    """
    UPDATED: Generate schedule using either templates or Excel files
    """
    try:
        with st.spinner("🔄 Generating optimized schedule... This may take a few moments."):
            # Prepare scheduling parameters
            scheduling_params = {
                'zones_floors': st.session_state.project_config['zones'],
                'start_date': st.session_state.project_config['basic_info']['start_date'],
                'optimization_level': optimization_level,
                'acceleration_factor': acceleration_factor,
                'include_risk_analysis': include_risk_analysis,
                'work_sequences': st.session_state.get('work_sequences', []),
                'project_id': st.session_state.get('current_project_id'),
                'project_name': st.session_state.project_config['basic_info'].get('project_name', 'Unnamed Project')
            }
            
            from backend.services.scheduling_service import SchedulingService
            scheduling_service = SchedulingService(db_session)
            
            if method == 'templates':
                # Use TemplateService to convert templates to scheduler input
                from backend.services.template_service import TemplateService
                template_service = TemplateService(db_session)
                
                scheduler_input = template_service.convert_templates_to_scheduler_input(
                    user_id,
                    st.session_state.selected_task_template,
                    st.session_state.selected_resource_template,
                    st.session_state.project_config
                )
                
                schedule_results = scheduling_service.generate_schedule(
                    user_id, 
                    scheduler_input['quantity_file'],
                    scheduler_input['resources_file'], 
                    scheduler_input['equipment_file'],
                    scheduling_params
                )
            else:
                # Use uploaded Excel files
                quantity_file = st.session_state.uploaded_files['quantity']
                resources_file = st.session_state.uploaded_files.get('resources')
                equipment_file = st.session_state.uploaded_files.get('equipment')
                
                schedule_results = scheduling_service.generate_schedule(
                    user_id, quantity_file, resources_file, equipment_file, scheduling_params
                )
            
            # Store results
            st.session_state.schedule_results = schedule_results
            st.session_state.schedule_generated = True
            
            # Generate reports if requested
            if generate_reports:
                _generate_detailed_reports(schedule_results, db_session, user_id)
            
            st.success("✅ Schedule generated successfully!")
            st.balloons()
            
    except Exception as e:
        st.error(f"❌ Schedule generation failed: {str(e)}")
        import logging
        logging.error(f"Schedule generation error: {e}", exc_info=True)


def _render_import_export_section(services: Dict[str, Any],
                                  user_id: int):
    """Render import/export section (moved from templates_manager)"""
    st.markdown("---")
    st.subheader("📤 Import/Export Templates")
    
    try:
        template_service = services['template_service']
        
        col1, col2 = st.columns(2)

        # Task Templates Import/Export
        with col1:
            st.markdown("#### 📋 Task Templates")
            st.markdown("---")
            
            # Export Section
            st.markdown("**📤 Export Task Templates**")
            if st.button("📥 Generate Task Template Export", width='stretch', key="generate_task_export"):
                try:
                    task_json = template_service.export_task_templates( user_id)
                    
                    st.download_button( 
                        label="💾 Download Task Templates",
                        data=task_json,
                        file_name=f"task_templates_export_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        width='stretch',
                        key="download_task_json"
                    )
                except Exception as e:
                    st.error(f"❌ Error during export: {e}")

            # Import Section
            st.markdown("**📥 Import Task Templates**")
            task_upload = st.file_uploader("Task Template JSON", type=["json"], key="task_upload")
            if task_upload and st.button("📤 Import Task Templates", width='stretch', key="upload_tasks"):
                try:
                    if template_service.import_task_templates(user_id, task_upload):
                        st.success("✅ Task templates imported successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to import task templates")
                except Exception as e:
                    st.error(f"❌ Error during import: {e}")

        # Resource Templates Import/Export
        with col2:
            st.markdown("#### 👥 Resource Templates")
            st.markdown("---")
            
            # Export Section
            st.markdown("**📤 Export Resource Templates**")
            if st.button("📥 Generate Resource Template Export", width='stretch', key="generate_resource_export"):
                try:
                    resource_json = template_service.export_resource_templates(user_id)
                    
                    st.download_button(
                        label="💾 Download Resource Templates",
                        data=resource_json,
                        file_name=f"resource_templates_export_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        width='stretch',
                        key="download_resource_json"
                    )
                except Exception as e:
                    st.error(f"❌ Error during export: {e}")

            # Import Section
            st.markdown("**📥 Import Resource Templates**")
            resource_upload = st.file_uploader("Resource Template JSON", type=["json"], key="resource_upload")
            if resource_upload and st.button("📤 Import Resource Templates", width='stretch', key="upload_resources"):
                try:
                    if template_service.import_resource_templates(user_id, resource_upload):
                        st.success("✅ Resource templates imported successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to import resource templates")
                except Exception as e:
                    st.error(f"❌ Error during import: {e}")

    except Exception as e:
        st.error(f"❌ Error in import/export section: {e}")


def _generate_detailed_reports(schedule_results, db_session: Session, user_id: int):
    """Generate detailed reports for the schedule"""
    try:
        with st.spinner("📊 Generating detailed reports..."):
            from backend.reporting.scheduling_reporter import SchedulingReporter
            
            # Create reporter with proper dependencies
            reporter = SchedulingReporter(
                schedule_results.tasks,
                schedule_results.schedule,
                schedule_results.worker_manager,
                schedule_results.equipment_manager,
                schedule_results.calendar
            )
            
            # Generate all reports
            reports_folder = reporter.export_all_reports()
            st.session_state.reports_folder = reports_folder
            
            # Save schedule to database for history
            _save_schedule_to_database(schedule_results, db_session, user_id)
            
            st.success(f"✅ Detailed reports generated in: {reports_folder}")
            
    except Exception as e:
        st.warning(f"⚠️ Report generation completed with warnings: {e}")


def _save_schedule_to_database(schedule_results, db_session: Session, user_id: int):
    """Save generated schedule to database for history and tracking"""
    try:
        from backend.services.scheduling_service import SchedulingService
        
        scheduling_service = SchedulingService(db_session)
        
        # ✅ FIXED: Use user_id parameter instead of reading from session state
        
        # Convert schedule to saveable format
        schedule_data = {
            'project_id': st.session_state.get('current_project_id'),
            'schedule_data': _convert_schedule_to_dict(schedule_results),
            'generated_by': user_id,
            'generation_date': datetime.now()
        }
        
        scheduling_service.save_schedule(user_id, schedule_data)
        
    except Exception as e:
        # Non-critical operation - log but don't fail the whole process
        import logging
        logging.warning(f"Failed to save schedule to database: {e}")


def _convert_schedule_to_dict(schedule_results) -> Dict[str, Any]:
    """Convert schedule results to dictionary for storage"""
    return {
        'tasks': [
            {
                'id': task.id,
                'name': task.name,
                'discipline': task.discipline,
                'zone': task.zone,
                'floor': task.floor,
                'resource_type': task.resource_type,
                'allocated_crews': getattr(task, 'allocated_crews', 0),  # ✅ FIXED: Use getattr
                'allocated_equipments': getattr(task, 'allocated_equipments', {}),  # ✅ FIXED: Use getattr
                'status': getattr(task.status, 'value', 'Unknown')
            }
            for task in schedule_results.tasks
        ],
        'schedule': {
            task_id: [start.isoformat(), end.isoformat()] 
            for task_id, (start, end) in schedule_results.schedule.items()
        },
        'metadata': {
            'total_tasks': len(schedule_results.tasks),
            'generation_timestamp': datetime.now().isoformat()
        }
    }


def _render_schedule_results(db_session: Session, user_id: int):
    """Render schedule results and visualization"""
    st.markdown("---")
    st.subheader("📊 Schedule Results")
    
    # Schedule metrics
    render_schedule_metrics(st.session_state.schedule_results)
    
    # Resource Allocation Summary
    _render_allocation_summary()
    
    # Interactive Gantt Chart
    st.markdown("---")
    st.subheader("📈 Interactive Gantt Chart")
    
    # Convert schedule to DataFrame for Gantt chart
    schedule_df = _convert_schedule_to_dataframe()
    render_gantt_with_controls(schedule_df)
    
    # Schedule details table
    st.markdown("---")
    st.subheader("📋 Schedule Details")
    
    with st.expander("View Detailed Schedule with Allocations", expanded=False):
        render_schedule_table(schedule_df)
    
    # Export options
    st.markdown("---")
    _render_export_section(db_session, user_id)


def _render_allocation_summary():
    """Render resource allocation summary"""
    schedule_results = st.session_state.schedule_results
    
    if not schedule_results:
        return
    
    st.markdown("#### 👥 Resource Allocation Summary")
    
    # Crew allocations
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_tasks = len(schedule_results.tasks)
        tasks_with_allocations = sum(1 for task in schedule_results.tasks 
                                   if getattr(task, 'allocated_crews', 0) > 0)
        st.metric("Tasks with Crew Allocations", f"{tasks_with_allocations}/{total_tasks}")
    
    with col2:
        total_allocated_crews = sum(getattr(task, 'allocated_crews', 0) 
                                  for task in schedule_results.tasks)
        st.metric("Total Crews Allocated", total_allocated_crews)
    
    with col3:
        # Calculate utilization
        if hasattr(schedule_results, 'resource_utilization'):
            avg_utilization = sum(schedule_results.resource_utilization.values()) / len(schedule_results.resource_utilization) * 100
            st.metric("Average Utilization", f"{avg_utilization:.1f}%")
    
    # Equipment allocations
    st.markdown("#### 🛠️ Equipment Allocations")
    equipment_usage = {}
    for task in schedule_results.tasks:
        allocated_equipments = getattr(task, 'allocated_equipments', {})
        for equip_name, count in allocated_equipments.items():
            equipment_usage[equip_name] = equipment_usage.get(equip_name, 0) + count
    
    if equipment_usage:
        equip_cols = st.columns(3)
        for idx, (equip_name, total_count) in enumerate(equipment_usage.items()):
            with equip_cols[idx % 3]:
                st.metric(f"Total {equip_name}", total_count)


def _convert_schedule_to_dataframe() -> pd.DataFrame:
    """Convert schedule results to DataFrame with allocation data"""
    schedule_results = st.session_state.schedule_results
    
    if not schedule_results or not hasattr(schedule_results, 'tasks'):
        return pd.DataFrame()
    
    rows = []
    
    for task in schedule_results.tasks:
        if (hasattr(schedule_results, 'schedule') and 
            task.id in schedule_results.schedule):
            
            start_date, end_date = schedule_results.schedule[task.id]
            duration = (end_date - start_date).days
            
            # Get allocation data
            allocated_crews = getattr(task, 'allocated_crews', 0)
            allocated_equipments = getattr(task, 'allocated_equipments', {})
            
            rows.append({
                'TaskID': task.id,
                'TaskName': task.name,
                'Discipline': task.discipline,
                'Zone': task.zone,
                'Floor': task.floor,
                'Start': start_date,
                'End': end_date,
                'Duration': duration,
                'ResourceType': getattr(task, 'resource_type', 'Unknown'),
                'MinCrewsNeeded': getattr(task, 'min_crews_needed', 0),
                'AllocatedCrews': allocated_crews,  # ✅ ACTUAL allocation
                'MaxCrewsAllowed': getattr(task, 'max_crews_allowed', 0),  # ✅ NEW
                'AllocatedEquipment': allocated_equipments,  # ✅ ACTUAL allocation
                'Status': getattr(task.status, 'value', 'Unknown'),
                'IsCriticalPath': task.id in getattr(schedule_results, 'critical_path', [])
            })
    
    return pd.DataFrame(rows)


def _render_export_section(db_session: Session, user_id: int):
    """Render schedule export options"""
    st.subheader("📤 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.get('reports_folder') and os.path.exists(st.session_state.reports_folder):
            # Create zip of all reports
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for root, dirs, files in os.walk(st.session_state.reports_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, st.session_state.reports_folder)
                        zip_file.write(file_path, arcname)
            
            st.download_button(
                "📦 Download All Reports (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="construction_schedule_reports.zip",
                mime="application/zip",
                use_container_width=True,
                key="download_all_reports"
            )
        else:
            st.button(
                "📦 Download All Reports (ZIP)",
                disabled=True,
                help="Reports not available",
                use_container_width=True
            )
    
    with col2:
        # Export schedule as CSV
        schedule_df = _convert_schedule_to_dataframe()
        if not schedule_df.empty:
            csv_data = schedule_df.to_csv(index=False)
            
            st.download_button(
                "📄 Export Schedule (CSV)",
                data=csv_data,
                file_name="construction_schedule.csv",
                mime="text/csv",
                use_container_width=True,
                key="export_csv"
            )
        else:
            st.button(
                "📄 Export Schedule (CSV)",
                disabled=True,
                help="No schedule data available",
                use_container_width=True
            )
    
    with col3:
        # Export to Excel
        if (st.session_state.get('reports_folder') and 
            os.path.exists(st.session_state.reports_folder)):
            
            schedule_excel_path = os.path.join(
                st.session_state.reports_folder, 
                "construction_schedule.xlsx"
            )
            
            if os.path.exists(schedule_excel_path):
                with open(schedule_excel_path, 'rb') as f:
                    st.download_button(
                        "📊 Export Schedule (Excel)",
                        data=f.read(),
                        file_name="construction_schedule.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="export_excel"
                    )
            else:
                st.button(
                    "📊 Export Schedule (Excel)",
                    disabled=True,
                    help="Excel report not available",
                    use_container_width=True
                )
        else:
            st.button(
                "📊 Export Schedule (Excel)",
                disabled=True,
                help="Reports not available",
                use_container_width=True
            )