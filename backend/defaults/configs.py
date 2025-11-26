


acceleration = {
    "Terrassement": {
        "factor": 3.0, 
        "max_crews": 5, 
        "constraints": ["space_availability", "equipment_limits"]
    },
    "FondationsProfondes": {
        "factor": 2.0, 
        "max_crews": 4, 
        "constraints": ["curing_time", "sequential_work", "specialized_equipment"]
    },
    "GrosŒuvre": {
        "factor": 1.5, 
        "max_crews": 3, 
        "constraints": ["curing_time", "structural_sequence"]
    },
    "SecondŒuvre": {
        "factor": 1.2, 
        "max_crews": 4, 
        "constraints": ["space_limitation", "trade_coordination"]
    },
    "default": {
        "factor": 1.0, 
        "max_crews": 2, 
        "constraints": ["quality_requirements"]
    }
}


cross_floor_links= {
    # Deep foundations to superstructure
    "GO-F-01": ["FDP-08", "FDP-12", "FDP-17"],
    
    # Structural dependencies
    "GO-S-04": ["GO-S-07"],  # Columns (F+1) depend on Slab (F)
    "GO-S-05": ["GO-S-07"],  # Plancher prep depends on previous slab
    "GO-S-07": ["GO-S-04"],  # Slab depends on columns from same level
    
    # Quality gates for deep foundations
    "FDP-05": ["FDP-04"],  # Geotechnical control after cleaning
    "FDP-08": ["FDP-07"],  # Core testing after concreting
    "FDP-17": ["FDP-08"],  # Integrity testing after core tests
}

QUALITY_GATES = {
    "PRE-01": "Site Establishment Approval",
    "TER-01": "Earthworks Approval", 
    "FDP-05": "Geotechnical Control - Bottom of Excavation",
    "FDP-08": "Deep Foundations Quality Control",
    "FDP-17": "Integrity Testing Approval",
    "GO-F-01": "Shallow Foundations Approval",
    "GO-S-01": "Structural Works Approval",
    "SO-01": "Enclosed Building Status",
}

SHIFT_CONFIG = {
    "default": 1.0,
    "Terrassement": 2.0,
    "FondationsProfondes": 1.8,
    "GrosŒuvre": 1.5,
    "SecondŒuvre": 1.0,
}