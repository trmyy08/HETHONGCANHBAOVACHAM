MSSV_LIST = [
    "051206001878",
    "052206009774",
    "051206004603",
    "075206003273",
    "070306004031",
]
G = 9.81                 
BRAKE_EFFICIENCY = 0.85  
ROAD_FRICTION = {
    "kho":     0.80,   
    "am":      0.60,   
    "uot":     0.45, 
    "tron":    0.30,  
}

REACTION_TIME = {
    "tinh_tao":    0.80,
    "binh_thuong": 1.20,
    "met_moi":     1.80,
    "mat_tap_trung": 2.50,
}

TTC_DANGER = 1.5   
TTC_WARNING = 3.0 

DR_DANGER = 0.60   
DR_WARNING = 1.00  

ABSOLUTE_MIN_DISTANCE = 2.0

NEGLIGIBLE_SPEED_KMH = 5.0

LEVEL_SAFE = "AN TOAN"
LEVEL_WARNING = "CANH BAO"
LEVEL_DANGER = "NGUY HIEM"

LEVEL_ORDER = {LEVEL_SAFE: 0, LEVEL_WARNING: 1, LEVEL_DANGER: 2}

LEVEL_ACTION = {
    LEVEL_SAFE:    "Giu nguyen hanh trinh. Khong co canh bao.",
    LEVEL_WARNING: "Canh bao am thanh ngat quang + den vang. Tai xe nen nha chan ga.",
    LEVEL_DANGER:  "Canh bao am thanh lien tuc + den do + rung vo lang. Kich hoat ho tro phanh khan cap (AEB).",
}


SENSOR_RATE_HZ = 20        
DISTANCE_NOISE_STD = 0.25  
SPEED_NOISE_STD = 0.40      
DROPOUT_PROB = 0.01         
MAX_SENSOR_RANGE = 150.0    

BASELINE_DANGER_DISTANCE = 10.0
BASELINE_WARNING_DISTANCE = 25.0
