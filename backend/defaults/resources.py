from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from backend.models.domain_models import WorkerResource, EquipmentResource, BaseTask, Task
# Import models - fixed import path





workers = {
    "BétonArmé": WorkerResource(
        "BétonArmé", count=200, hourly_rate=18,
        productivity_rates={
            "GO-F-03": 5, "GO-F-05": 5, "GO-S-03": 5, "GO-S-04": 5, "GO-S-06": 5, "GO-S-07": 12, 
            "FDP-07": 5, "FDP-12": 5, "FDP-15": 5
        },
        skills=["BétonArmé"],
        max_crews={
            "GO-F-03": 25, "GO-F-05": 25, "GO-S-03": 25, "GO-S-04": 25, "GO-S-06": 25, "GO-S-07": 25, 
            "FDP-07": 25, "FDP-12": 25, "FDP-15": 25
        }
    ),

    "Ferrailleur": WorkerResource(
        "Ferrailleur", count=85, hourly_rate=18,
        productivity_rates={
            "FDP-06": 400, "FDP-11": 180, "GO-F-04": 300, "GO-S-02": 180, "GO-S-05": 300
        },
        skills=["BétonArmé"],
        max_crews={
            "FDP-06": 25, "FDP-11": 25, "GO-F-04": 25, "GO-S-02": 25, "GO-S-05": 25
        }
    ),

    "Topographe": WorkerResource(
        "Topographe", count=5, hourly_rate=18,
        productivity_rates={"PRE-01": 100, "PRE-03": 100, "TER-01": 100, "FDP-01": 100, "FDP-02": 100, "FDP-05": 100, "FDP-17": 100},
        skills=["Topographie"],
        max_crews={"PRE-01": 10, "PRE-03": 10, "TER-01": 10, "FDP-01": 10, "FDP-02": 10, "FDP-05": 10, "FDP-17": 10}
    ),

    "Maçon": WorkerResource(
        "Maçon", count=84, hourly_rate=40,
        productivity_rates={"PRE-02": 10, "SO-01": 10},
        skills=["Maçonnerie"],
        max_crews={"PRE-02": 25, "SO-01": 25}
    ),

    "Plaquiste": WorkerResource(
        "Plaquiste", count=84, hourly_rate=40,
        productivity_rates={"SO-02": 10, "SO-03": 10},
        skills=["Cloisennement", "Faux-plafond"],
        max_crews={"SO-02": 25, "SO-03": 25}
    ),

    "Étanchéiste": WorkerResource(
        "Étanchéiste", count=83, hourly_rate=40,
        productivity_rates={"SO-06": 10, "SO-07": 10},
        skills=["Etanchiété"],
        max_crews={"SO-06": 25, "SO-07": 25}
    ),

    "Carreleur-Marbrier": WorkerResource(
        "Carreleur-Marbrier", count=84, hourly_rate=40,
        productivity_rates={"SO-04": 15, "SO-05": 10},
        skills=["Carrelage", "Marbre", "Revetement"],
        max_crews={"SO-04": 15, "SO-05": 15}
    ),

    "Peintre": WorkerResource(
        "Peintre", count=8, hourly_rate=40,
        productivity_rates={"SO-08": 10, "SO-09": 25},
        skills=["Peinture"],
        max_crews={"SO-08": 15, "SO-09": 15}
    ),

    "Charpentier": WorkerResource(
        "Charpentier", count=15, hourly_rate=45,  # Increased count to cover both wood and metal work
        productivity_rates={"GO-S-08": 8, "GO-S-09": 6},
        skills=["Charpenterie", "StructureMétallique"],
        max_crews={"GO-S-08": 10, "GO-S-09": 8}
    ),

    "Soudeur": WorkerResource(
        "Soudeur", count=8, hourly_rate=50,
        productivity_rates={"GO-S-10": 6},
        skills=["Soudure"],
        max_crews={"GO-S-10": 8}
    ),

    "Ascensoriste": WorkerResource(
        "Ascensoriste", count=6, hourly_rate=55,
        productivity_rates={"SO-10": 4},
        skills=["Ascenseurs"],
        max_crews={"SO-10": 6}
    ),

    "Agent de netoyage": WorkerResource(
        "Agent de netoyage", count=15, hourly_rate=25,
        productivity_rates={"SO-11": 100},
        skills=["Nettoyage"],
        max_crews={"SO-11": 10}
    ),
    
    "ConducteurEngins": WorkerResource(
        "ConducteurEngins", count=50, hourly_rate=35,
        productivity_rates={
            "TER-02": 15, "TER-03": 20, "FDP-03": 25, "FDP-04": 15, 
            "FDP-09": 20, "FDP-10": 25, "FDP-13": 20
        },
        skills=["ConduiteEngins"],
        max_crews={
            "TER-02": 10, "TER-03": 15, "FDP-03": 10, "FDP-04": 8, 
            "FDP-09": 10, "FDP-10": 12, "FDP-13": 10
        }
    ),
    
    "OpérateurJetGrouting": WorkerResource(
        "OpérateurJetGrouting", count=12, hourly_rate=45,
        productivity_rates={"FDP-14": 15, "FDP-16": 20},
        skills=["JetGrouting"],
        max_crews={"FDP-14": 6, "FDP-16": 8}
    ),
}


# =======================
# EQUIPMENT RESOURCES
# =======================
equipment = {
    "Chargeuse": EquipmentResource(
        "Chargeuse", count=160, hourly_rate=100,
        productivity_rates={"TER-02": 120, "TER-03": 20, "GO-F-02": 40},
        type="Terrassement", max_equipment=6
    ),

    "Bulldozer": EquipmentResource(
        "Bulldozer", count=16, hourly_rate=100,
        productivity_rates={"TER-02": 200, "TER-03": 20},
        type="Terrassement", max_equipment=6
    ),

    "Pelle": EquipmentResource(
        "Pelle", count=16, hourly_rate=100,
        productivity_rates={"TER-03": 15, "FDP-03": 20},
        type="Terrassement", max_equipment=6
    ),

    "Tractopelle": EquipmentResource(
        "Tractopelle", count=16, hourly_rate=100,
        productivity_rates={"TER-02": 15, "TER-03": 200},
        type="Terrassement", max_equipment=6
    ),

    "Niveleuse": EquipmentResource(
        "Niveleuse", count=16, hourly_rate=100,
        productivity_rates={"GO-F-02": 15},
        type="Terrassement", max_equipment=6
    ),

    "Compacteur": EquipmentResource(
        "Compacteur", count=16, hourly_rate=100,
        productivity_rates={"GO-F-02": 20},
        type="Terrassement", max_equipment=6
    ),

    "Grue à tour": EquipmentResource(
        "Grue à tour", count=180, hourly_rate=150,
        productivity_rates={"GO-F-03": 10, "GO-S-03": 10, "GO-S-06": 10, "SO-01": 10, "SO-02": 10},
        type="Levage", max_equipment=8
    ),

    "Grue mobile": EquipmentResource(
        "Grue mobile", count=90, hourly_rate=150,
        productivity_rates={"FDP-06": 10, "FDP-11": 10, "GO-F-04": 10, "GO-S-02": 10},
        type="Levage", max_equipment=8
    ),

    "Nacelle": EquipmentResource(
        "Nacelle", count=16, hourly_rate=100,
        productivity_rates={"SO-06": 15, "SO-07": 15},
        type="Levage", max_equipment=6
    ),

    "Pump": EquipmentResource(
        "Pump", count=30, hourly_rate=190,
        productivity_rates={"FDP-07": 14, "FDP-12": 16, "GO-F-05": 14, "GO-S-04": 16, "GO-S-07": 16},
        type="Bétonnage", max_equipment=3
    ),

    "Camion": EquipmentResource(
        "Camion", count=9, hourly_rate=190,
        productivity_rates={"TER-03": 120, "FDP-03": 120},
        type="Transport", max_equipment=3
    ),

    "Bétonier": EquipmentResource(
        "Bétonier", count=9, hourly_rate=190,
        productivity_rates={"FDP-07": 14, "FDP-12": 16, "GO-F-05": 14, "GO-S-04": 16, "GO-S-07": 16},
        type="Bétonnage", max_equipment=3
    ),

    "Manito": EquipmentResource(
        "Manito", count=19, hourly_rate=190,
        productivity_rates={"SO-01": 14, "SO-02": 16, "SO-03": 16},
        type="Transport", max_equipment=8
    ),
    
    "Foreuse": EquipmentResource(
        "Foreuse", count=8, hourly_rate=200,
        productivity_rates={"FDP-03": 15, "FDP-13": 20, "FDP-15": 18},
        type="Fondations", max_equipment=4
    ),
    
    "Hydrofraise": EquipmentResource(
        "Hydrofraise", count=4, hourly_rate=300,
        productivity_rates={"FDP-09": 12, "FDP-10": 15},
        type="Fondations", max_equipment=2
    ),
}
