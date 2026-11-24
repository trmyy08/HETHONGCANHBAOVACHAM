# -*- coding: utf-8 -*-
"""
config.py
Tham so cau hinh cho He thong canh bao va cham (Forward Collision Warning - FCW).

De tai 36 - Mo phong he thong canh bao va cham
Mon: Tri tue nhan tao
"""

# ---------------------------------------------------------------------------
# 1. DANH SACH MSSV CUA NHOM (dung lam seed sinh du lieu cam bien)
#    Nguon: file DATASET.docx do giang vien cung cap
# ---------------------------------------------------------------------------
MSSV_LIST = [
    "051206001878",
    "052206009774",
    "051206004603",
    "075206003273",
    "070306004031",
]

# ---------------------------------------------------------------------------
# 2. HANG SO VAT LY
# ---------------------------------------------------------------------------
G = 9.81                 # gia toc trong truong (m/s^2)
BRAKE_EFFICIENCY = 0.85  # hieu suat phanh thuc te so voi ly thuyet

# He so bam duong theo dieu kien mat duong
ROAD_FRICTION = {
    "kho":     0.80,   # duong kho, nhua tot
    "am":      0.60,   # duong am sau mua
    "uot":     0.45,   # duong uot, dang mua
    "tron":    0.30,   # duong tron truot (dau, bun)
}

# Thoi gian phan ung cua tai xe (giay)
REACTION_TIME = {
    "tinh_tao":    0.80,
    "binh_thuong": 1.20,
    "met_moi":     1.80,
    "mat_tap_trung": 2.50,
}

# ---------------------------------------------------------------------------
# 3. NGUONG CANH BAO (threshold) - trai tim cua he suy dien
#    TTC = Time To Collision (thoi gian den khi va cham, giay)
#    DR  = Distance Ratio = khoang cach do duoc / khoang cach an toan toi thieu
# ---------------------------------------------------------------------------
TTC_DANGER = 1.5    # TTC <= 1.5s  -> NGUY HIEM
TTC_WARNING = 3.0   # TTC <= 3.0s  -> CANH BAO

DR_DANGER = 0.60    # con < 60% khoang cach an toan -> NGUY HIEM
DR_WARNING = 1.00   # con < 100% khoang cach an toan -> CANH BAO

# Khoang cach vat ly toi thieu (m) - duoi nguong nay luon nguy hiem
ABSOLUTE_MIN_DISTANCE = 2.0

# Toc do duoi nguong nay coi nhu xe gan nhu dung, khong canh bao
NEGLIGIBLE_SPEED_KMH = 5.0

# ---------------------------------------------------------------------------
# 4. CAC MUC CANH BAO
# ---------------------------------------------------------------------------
LEVEL_SAFE = "AN TOAN"
LEVEL_WARNING = "CANH BAO"
LEVEL_DANGER = "NGUY HIEM"

LEVEL_ORDER = {LEVEL_SAFE: 0, LEVEL_WARNING: 1, LEVEL_DANGER: 2}

LEVEL_ACTION = {
    LEVEL_SAFE:    "Giu nguyen hanh trinh. Khong co canh bao.",
    LEVEL_WARNING: "Canh bao am thanh ngat quang + den vang. Tai xe nen nha chan ga.",
    LEVEL_DANGER:  "Canh bao am thanh lien tuc + den do + rung vo lang. Kich hoat ho tro phanh khan cap (AEB).",
}

# ---------------------------------------------------------------------------
# 5. THAM SO CAM BIEN MO PHONG
# ---------------------------------------------------------------------------
SENSOR_RATE_HZ = 20          # tan so lay mau cua radar (lan/giay)
DISTANCE_NOISE_STD = 0.25    # do lech chuan nhieu do khoang cach (m)
SPEED_NOISE_STD = 0.40       # do lech chuan nhieu do toc do (km/h)
DROPOUT_PROB = 0.01          # xac suat mat tin hieu cam bien tai 1 mau
MAX_SENSOR_RANGE = 150.0     # tam do toi da cua radar (m)

# Nguong cua mo hinh doi chung "khoang cach co dinh" (m)
BASELINE_DANGER_DISTANCE = 10.0
BASELINE_WARNING_DISTANCE = 25.0
