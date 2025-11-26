"""
Forms for customizing construction task templates
"""
import streamlit as st
from typing import Dict, Any, Optional, List

def render_task_customization_form(default_task: Any, existing_customization: Dict = None) -> Optional[Dict]:
    """
    Render form for customizing a task template
    
    Args:
        default_task: Default task to customize
        existing_customization: Existing customization data
        
    Returns:
        Customized task data or None if cancelled
    """
    st.subheader("✏️ Personnalisation de Tâche")
    
    with st.form(key="task_customization_form"):
        # Basic Information
        col1, col2 = st.columns(2)
        
        with col1:
            task_name = st.text_input(
                "Nom de la Tâche*",
                value=existing_customization.get('name') if existing_customization else getattr(default_task, 'name', ''),
                help="Nom personnalisé pour cette tâche"
            )
            
            discipline = st.text_input(
                "Corps d'État*",
                value=existing_customization.get('discipline') if existing_customization else getattr(default_task, 'discipline', ''),
                help="Discipline de construction (ex: BétonArmé, Maçonnerie)"
            )
        
        with col2:
            sub_discipline = st.text_input(
                "Sous-Discipline",
                value=existing_customization.get('sub_discipline') if existing_customization else getattr(default_task, 'sub_discipline', 'General'),
                help="Sous-catégorie de la discipline"
            )
            
            resource_type = st.selectbox(
                "Type de Ressource*",
                options=['worker', 'equipment', 'material', 'hybrid'],
                index=['worker', 'equipment', 'material', 'hybrid'].index(
                    existing_customization.get('resource_type') if existing_customization 
                    else getattr(default_task, 'resource_type', 'worker')
                )
            )
        
        # Duration and Resources
        st.markdown("---")
        st.subheader("⏱️ Durée et Ressources")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            base_duration = st.number_input(
                "Durée de Base (Jours)*",
                min_value=0.5,
                max_value=100.0,
                step=0.5,
                value=existing_customization.get('base_duration') if existing_customization else getattr(default_task, 'base_duration', 1),
                help="Durée estimée en jours ouvrables"
            )
        
        with col2:
            min_crews = st.number_input(
                "Équipes Minimum",
                min_value=1,
                max_value=20,
                value=existing_customization.get('min_crews_needed') if existing_customization else getattr(default_task, 'min_crews_needed', 1),
                help="Nombre minimum d'équipes requises"
            )
        
        with col3:
            included = st.checkbox(
                "Inclure dans les Planning",
                value=existing_customization.get('included') if existing_customization else getattr(default_task, 'included', True),
                help="Inclure cette tâche dans la génération des plannings"
            )
        
        # Equipment Needs
        st.markdown("**Équipement Requis**")
        equipment_data = existing_customization.get('min_equipment_needed') if existing_customization else getattr(default_task, 'min_equipment_needed', {})
        
        if equipment_data:
            for equip_name, quantity in equipment_data.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text_input(f"Équipement", value=equip_name, key=f"equip_name_{equip_name}", disabled=True)
                with col2:
                    new_quantity = st.number_input(f"Quantité", min_value=0, value=quantity, key=f"equip_qty_{equip_name}")
                    equipment_data[equip_name] = new_quantity
        
        # Task Dependencies
        st.markdown("---")
        st.subheader("🔗 Dépendances")
        
        predecessors = st.text_area(
            "Tâches Prédécesseurs",
            value=", ".join(existing_customization.get('predecessors') if existing_customization else getattr(default_task, 'predecessors', [])),
            help="Liste des IDs des tâches précédentes (séparées par des virgules)"
        )
        
        # Advanced Options
        with st.expander("⚙️ Options Avancées"):
            col1, col2 = st.columns(2)
            
            with col1:
                weather_sensitive = st.checkbox(
                    "Sensible à la Météo",
                    value=existing_customization.get('weather_sensitive') if existing_customization else getattr(default_task, 'weather_sensitive', False)
                )
                
                delay = st.number_input(
                    "Délai de Début (Jours)",
                    min_value=0,
                    value=existing_customization.get('delay') if existing_customization else getattr(default_task, 'delay', 0)
                )
            
            with col2:
                quality_gate = st.checkbox(
                    "Point de Contrôle Qualité",
                    value=existing_customization.get('quality_gate') if existing_customization else getattr(default_task, 'quality_gate', False)
                )
                
                repeat_on_floor = st.checkbox(
                    "Répéter par Étage",
                    value=existing_customization.get('repeat_on_floor') if existing_customization else getattr(default_task, 'repeat_on_floor', True)
                )
        
        # Customization Notes
        customization_notes = st.text_area(
            "Notes de Personnalisation",
            value=existing_customization.get('customization_notes', '') if existing_customization else '',
            help="Notes sur les modifications apportées à la tâche par défaut"
        )
        
        # Form Actions
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submit_button = st.form_submit_button("💾 Sauvegarder la Personnalisation")
        
        if submit_button:
            if not task_name or not discipline:
                st.error("❌ Les champs marqués d'un * sont obligatoires")
                return None
            
            # Parse predecessors
            predecessor_list = [p.strip() for p in predecessors.split(',')] if predecessors else []
            
            customized_task = {
                'base_task_id': getattr(default_task, 'id', ''),
                'name': task_name,
                'discipline': discipline,
                'sub_discipline': sub_discipline,
                'resource_type': resource_type,
                'task_type': existing_customization.get('task_type') if existing_customization else getattr(default_task, 'task_type', 'worker'),
                'base_duration': base_duration,
                'min_crews_needed': min_crews,
                'min_equipment_needed': equipment_data,
                'predecessors': predecessor_list,
                'repeat_on_floor': repeat_on_floor,
                'delay': delay,
                'weather_sensitive': weather_sensitive,
                'quality_gate': quality_gate,
                'included': included,
                'customization_notes': customization_notes
            }
            
            return customized_task
    
    return None