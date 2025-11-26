"""
PROFESSIONAL Work Sequence Configuration Page - FIXED Implementation
"""
import streamlit as st
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def show(db_session: Session, user_id: int):
    """Work sequence configuration - FIXED implementation"""
    try:
        st.title("⚙️ Configuration des Séquences de Travail")
        st.markdown("Définissez l'ordre d'exécution des travaux par corps d'état et par zone")

        # Get current project
        current_project_id = st.session_state.get('current_project_id')
        current_project_name = st.session_state.get('current_project_name')

        if not current_project_id:
            st.warning("⚠️ Veuillez d'abord sélectionner un projet")
            return

        st.info(f"**Projet actuel:** {current_project_name}")

        # Initialize services
        try:
            from backend.services.project_service import ProjectService
            from backend.services.zone_sequence_service import ZoneSequenceService
            from backend.services.user_task_service import UserTaskService
            
            project_service = ProjectService(db_session)
            zone_service = ZoneSequenceService(db_session)
            task_service = UserTaskService(db_session)
        except Exception as e:
            st.error(f"❌ Erreur d'initialisation des services: {e}")
            return

        # Get project data 
        project = project_service.get_project(user_id,current_project_id)
        if not project:
            st.error("❌ Projet non trouvé")
            return

        # Get project zones
        zones = project.get('zones', {})
        if not zones:
            st.warning("""
            ⚠️ Aucune zone configurée pour ce projet.
            
            **Pour configurer les séquences:**
            1. Allez dans **Configuration Projet**
            2. Définissez les zones et étages
            3. Revenez sur cette page
            """)
            return

        available_zones = list(zones.keys())
        st.success(f"✅ {len(available_zones)} zone(s) disponible(s): {', '.join(available_zones)}")

        # Get available disciplines from user tasks
        tasks = task_service.get_user_task_templates(user_id)
        disciplines = list(set(task.get('discipline', 'Général') for task in tasks if task.get('included', True)))
        
        if not disciplines:
            st.warning("""
            ⚠️ Aucun corps d'état trouvé.
            
            **Pour configurer les séquences:**
            1. Allez dans **Gestion Templates** → **Bibliothèque Tâches**
            2. Chargez les tâches par défaut ou créez vos propres tâches
            3. Revenez sur cette page
            """)
            return

        # Main configuration interface
        st.header("🎯 Configuration des Séquences")

        # Get existing configuration
        existing_config = zone_service.get_zone_sequence_config(current_project_id, user_id)
        
        # Initialize session state if needed
        if 'zone_sequence_config' not in st.session_state:
            st.session_state.zone_sequence_config = existing_config

        # Discipline selector
        selected_discipline = st.selectbox(
            "Sélectionnez un Corps d'État à configurer",
            disciplines,
            key="discipline_selector"
        )

        if selected_discipline:
            _render_discipline_configuration(
                zone_service, current_project_id, user_id, 
                selected_discipline, available_zones
            )

        # Configuration overview
        st.header("📊 Vue d'Ensemble de la Configuration")
        _render_configuration_overview(zone_service, current_project_id, user_id)

        # Actions section
        st.header("⚡ Actions")
        _render_actions_section(zone_service, current_project_id, user_id, available_zones, disciplines)

    except Exception as e:
        logger.error(f"❌ Error in zone sequence page: {e}")
        st.error("❌ Erreur lors du chargement de la configuration des séquences")
        st.info("🔄 Veuillez rafraîchir la page ou contacter le support")

def _render_discipline_configuration(zone_service, project_id, user_id, discipline, available_zones):
    """Render configuration for a specific discipline"""
    st.subheader(f"🧩 Configuration pour: {discipline}")
    
    # Get current sequence for this discipline
    current_config = st.session_state.zone_sequence_config
    discipline_sequence = current_config.get(discipline, [])
    
    # Display current groups
    if discipline_sequence:
        st.write("**Groupes actuels:**")
        for i, group in enumerate(discipline_sequence):
            with st.expander(f"Groupe {i+1}: {len(group)} zone(s)", expanded=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Zones:** {', '.join(group)}")
                
                with col2:
                    # Edit group
                    if st.button("✏️", key=f"edit_{discipline}_{i}"):
                        st.session_state[f'editing_{discipline}_{i}'] = True
                
                with col3:
                    # Delete group (if not the only one)
                    if len(discipline_sequence) > 1:
                        if st.button("🗑️", key=f"delete_{discipline}_{i}"):
                            discipline_sequence.pop(i)
                            if zone_service.update_zone_sequence(project_id, user_id, discipline, discipline_sequence):
                                st.success("✅ Groupe supprimé!")
                                st.rerun()
    
    # Add new group section
    st.subheader("➕ Ajouter un Nouveau Groupe")
    new_group_zones = st.multiselect(
        f"Sélectionnez les zones pour le nouveau groupe ({discipline})",
        available_zones,
        key=f"new_group_{discipline}"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Ajouter le Groupe", key=f"add_{discipline}", width="stretch"):
            if new_group_zones:
                # Initialize if needed
                if discipline not in st.session_state.zone_sequence_config:
                    st.session_state.zone_sequence_config[discipline] = []
                
                # Add new group
                st.session_state.zone_sequence_config[discipline].append(new_group_zones)
                
                # Save to database
                if zone_service.update_zone_sequence(
                    project_id, user_id, discipline, 
                    st.session_state.zone_sequence_config[discipline]
                ):
                    st.success("✅ Nouveau groupe ajouté!")
                    st.rerun()
            else:
                st.error("❌ Veuillez sélectionner au moins une zone")
    
    with col2:
        if st.button("💾 Sauvegarder Configuration", key=f"save_{discipline}", width="stretch"):
            if zone_service.update_zone_sequence(
                project_id, user_id, discipline, 
                st.session_state.zone_sequence_config.get(discipline, [])
            ):
                st.success("✅ Configuration sauvegardée!")

def _render_configuration_overview(zone_service, project_id, user_id):
    """Render configuration overview"""
    config = st.session_state.zone_sequence_config
    
    if not config:
        st.info("📝 Aucune configuration de séquence définie. Ajoutez des groupes pour commencer.")
        return
    
    # Create overview cards
    cols = st.columns(min(3, len(config)))
    
    for i, (discipline, sequence) in enumerate(config.items()):
        col_idx = i % 3
        with cols[col_idx]:
            with st.container():
                st.markdown(f"**{discipline}**")
                st.write(f"**Groupes:** {len(sequence)}")
                total_zones = sum(len(group) for group in sequence)
                st.write(f"**Zones totales:** {total_zones}")
                st.progress(min(1.0, len(sequence) / 5))  # Progress indicator

def _render_actions_section(zone_service, project_id, user_id, available_zones, disciplines):
    """Render actions section"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Réinitialiser", width="stretch"):
            if zone_service.reset_zone_sequence(project_id, user_id):
                st.session_state.zone_sequence_config = {}
                st.success("✅ Configuration réinitialisée!")
                st.rerun()
    
    
    with col3:
        if st.button("📥 Exporter JSON", width="stretch"):
            export_data = zone_service.export_zone_sequence(project_id, user_id)
            if export_data:
                import json
                st.download_button(
                    label="💾 Télécharger",
                    data=json.dumps(export_data, indent=2, ensure_ascii=False),
                    file_name="configuration_sequences.json",
                    mime="application/json",
                    width="stretch"
                )
    
    # Validation
    if st.session_state.zone_sequence_config:
        validation_result = _validate_configuration(st.session_state.zone_sequence_config, available_zones)
        
        if validation_result['warnings']:
            with st.expander("⚠️ Avertissements de Configuration", expanded=True):
                for warning in validation_result['warnings']:
                    st.warning(warning)
        
        if validation_result['errors']:
            with st.expander("❌ Erreurs de Configuration", expanded=True):
                for error in validation_result['errors']:
                    st.error(error)

def _validate_configuration(config: dict, available_zones: list) -> dict:
    """Validate zone sequence configuration"""
    errors = []
    warnings = []
    
    for discipline, sequence in config.items():
        # Check if sequence is empty
        if not sequence:
            warnings.append(f"La discipline '{discipline}' a une séquence vide")
            continue
            
        # Check each group
        used_zones = set()
        for i, group in enumerate(sequence):
            if not group:
                errors.append(f"Groupe {i+1} de '{discipline}' est vide")
                continue
                
            for zone in group:
                if zone not in available_zones:
                    errors.append(f"Zone '{zone}' dans le groupe {i+1} de '{discipline}' n'existe pas")
                used_zones.add(zone)
        
        # Check for unused zones
        unused_zones = set(available_zones) - used_zones
        if unused_zones:
            warnings.append(f"Zones non utilisées dans '{discipline}': {', '.join(unused_zones)}")
    
    return {'errors': errors, 'warnings': warnings}