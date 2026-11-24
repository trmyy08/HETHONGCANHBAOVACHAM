import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any

from config import (
    SENSOR_RATE_HZ, DISTANCE_NOISE_STD, SPEED_NOISE_STD,
    DROPOUT_PROB, MAX_SENSOR_RANGE,
)
@dataclass
class KichBan:
    ma: str
    ten: str
    mo_ta: str
    toc_do_xe_kmh: float         
    toc_do_vat_the_kmh: float     
    khoang_cach_dau: float        
    gia_toc_vat_the: float        
    thoi_diem_phanh: float = 0.0  
    gia_toc_xe: float = 0.0     
    tinh_trang_duong: str = "kho"
    trang_thai_tai_xe: str = "binh_thuong"
    loai_vat_the: str = "xe_phia_truoc"
    thoi_luong: float = 10.0      

DANH_SACH_KICH_BAN: List[KichBan] = [
    KichBan(
        ma="KB1", ten="Do thi - xe truoc phanh gap",
        mo_ta="Di trong noi do 40 km/h, bam sau xe truoc 30 m o cung toc do. "
              "Den giay thu 2 xe truoc phanh gap vi den do. Day la tinh huong "
              "va cham lien hoan pho bien nhat trong do thi.",
        toc_do_xe_kmh=40, toc_do_vat_the_kmh=40, khoang_cach_dau=30,
        gia_toc_vat_the=-4.5, thoi_diem_phanh=2.0, tinh_trang_duong="kho",
        trang_thai_tai_xe="binh_thuong",
    ),
    KichBan(
        ma="KB2", ten="Quoc lo - toc do trung binh",
        mo_ta="Chay 70 km/h tren quoc lo, cach xe tai phia truoc 55 m. Xe tai chay "
              "65 km/h roi giam toc tu giay thu 2.5 khi vao khu dan cu.",
        toc_do_xe_kmh=70, toc_do_vat_the_kmh=65, khoang_cach_dau=55,
        gia_toc_vat_the=-3.0, thoi_diem_phanh=2.5, tinh_trang_duong="kho",
        trang_thai_tai_xe="binh_thuong",
    ),
    KichBan(
        ma="KB3", ten="Cao toc - vat can dung yen",
        mo_ta="Chay 100 km/h tren cao toc, phia truoc 140 m la xe chet may dung yen "
              "trong lan. Toc do tiep can khong doi va rat lon, toan bo trach nhiem "
              "tranh va cham thuoc ve xe chu.",
        toc_do_xe_kmh=100, toc_do_vat_the_kmh=0, khoang_cach_dau=140,
        gia_toc_vat_the=0.0, tinh_trang_duong="kho",
        trang_thai_tai_xe="binh_thuong", loai_vat_the="vat_can_tinh",
    ),
    KichBan(
        ma="KB4", ten="Troi mua - duong uot",
        mo_ta="Chay 60 km/h duoi troi mua (he so bam chi 0.45 so voi 0.80 khi kho), "
              "cach xe truoc 70 m. Xe truoc giam toc tu giay thu 2. Quang duong "
              "phanh dai gan gap doi so voi duong kho.",
        toc_do_xe_kmh=60, toc_do_vat_the_kmh=55, khoang_cach_dau=70,
        gia_toc_vat_the=-2.5, thoi_diem_phanh=2.0, tinh_trang_duong="uot",
        trang_thai_tai_xe="binh_thuong",
    ),
    KichBan(
        ma="KB5", ten="Tai xe mat tap trung",
        mo_ta="Chay 80 km/h, tai xe nhin dien thoai nen thoi gian phan ung len toi "
              "2.5s thay vi 1.2s. Xe truoc chay 75 km/h roi phanh tu giay thu 2. "
              "Kiem tra kha nang canh bao som bu cho do tre cua con nguoi.",
        toc_do_xe_kmh=80, toc_do_vat_the_kmh=75, khoang_cach_dau=100,
        gia_toc_vat_the=-3.0, thoi_diem_phanh=2.0, tinh_trang_duong="kho",
        trang_thai_tai_xe="mat_tap_trung",
    ),
    KichBan(
        ma="KB6", ten="Giu khoang cach an toan (doi chung am)",
        mo_ta="Chay 60 km/h, giu deu khoang cach 60 m voi xe truoc cung toc do. "
              "Kich ban nay khong co nguy co va cham, dung de kiem tra he thong "
              "co bao dong gia hay khong.",
        toc_do_xe_kmh=60, toc_do_vat_the_kmh=60, khoang_cach_dau=60,
        gia_toc_vat_the=0.0, tinh_trang_duong="kho",
        trang_thai_tai_xe="tinh_tao",
    ),
    KichBan(
        ma="KB7", ten="Nguoi di bo bang qua duong",
        mo_ta="Chay 50 km/h trong do thi, phia truoc 85 m co nguoi di bo bang qua duong. "
              "Doi tuong de bi ton thuong nen he thong ap dung nguong nghiem ngat nhat.",
        toc_do_xe_kmh=50, toc_do_vat_the_kmh=0, khoang_cach_dau=85,
        gia_toc_vat_the=0.0, tinh_trang_duong="kho",
        trang_thai_tai_xe="binh_thuong", loai_vat_the="nguoi_di_bo",
    ),
    KichBan(
        ma="KB8", ten="Xe cat ngang tai giao lo",
        mo_ta="Chay 60 km/h den giao lo, mot xe may cat ngang dau xe o cu ly 85 m. "
              "Quy dao giao nhau nen khong the tranh bang cach danh lai.",
        toc_do_xe_kmh=60, toc_do_vat_the_kmh=0, khoang_cach_dau=85,
        gia_toc_vat_the=0.0, tinh_trang_duong="am",
        trang_thai_tai_xe="binh_thuong", loai_vat_the="xe_cat_ngang",
    ),
]


# ---------------------------------------------------------------------------
# GAN MSSV VAO THAM SO
# ---------------------------------------------------------------------------
def seed_tu_mssv(mssv: str) -> int:
    """Chuyen MSSV thanh seed nguyen cho bo sinh so ngau nhien."""
    return int(mssv) % (2 ** 31)


def he_so_lech_tu_mssv(mssv: str, chi_so: int) -> float:
    """
    Sinh he so lech trong khoang [0.88, 1.12] tu mot nhom chu so cua MSSV.
    Nho vay moi sinh vien co bo du lieu rieng nhung van cung ban chat vat ly.
    """
    chuoi = mssv[-6:]
    gia_tri = int(chuoi[chi_so % len(chuoi)]) + int(chuoi[(chi_so + 3) % len(chuoi)])
    # gia_tri nam trong [0, 18] -> anh xa ve [0.88, 1.12]
    return 0.88 + (gia_tri / 18.0) * 0.24


def ca_bien_kich_ban(kb: KichBan, mssv: str) -> KichBan:
    """Tao ban the cua kich ban da duoc ca bien theo MSSV."""
    return KichBan(
        ma=kb.ma,
        ten=kb.ten,
        mo_ta=kb.mo_ta,
        toc_do_xe_kmh=round(kb.toc_do_xe_kmh * he_so_lech_tu_mssv(mssv, 0), 1),
        toc_do_vat_the_kmh=round(kb.toc_do_vat_the_kmh * he_so_lech_tu_mssv(mssv, 1), 1),
        khoang_cach_dau=round(kb.khoang_cach_dau * he_so_lech_tu_mssv(mssv, 2), 1),
        gia_toc_vat_the=round(kb.gia_toc_vat_the * he_so_lech_tu_mssv(mssv, 4), 2),
        thoi_diem_phanh=kb.thoi_diem_phanh,
        gia_toc_xe=kb.gia_toc_xe,
        tinh_trang_duong=kb.tinh_trang_duong,
        trang_thai_tai_xe=kb.trang_thai_tai_xe,
        loai_vat_the=kb.loai_vat_the,
        thoi_luong=kb.thoi_luong,
    )
def sinh_du_lieu(kb: KichBan, mssv: str, co_nhieu: bool = True) -> List[Dict[str, Any]]:
    """
    Mo phong dong hoc 2 xe va xuat chuoi mau cam bien o tan so SENSOR_RATE_HZ.

    Mo hinh dong hoc (roi rac theo buoc dt):
        v(t+dt) = max(0, v(t) + a*dt)
        x(t+dt) = x(t) + v(t)*dt + 0.5*a*dt^2
        khoang_cach = x_vat_the - x_xe
    """
    rng = random.Random(seed_tu_mssv(mssv) + int(kb.ma[-1]))
    dt = 1.0 / SENSOR_RATE_HZ
    so_mau = int(kb.thoi_luong * SENSOR_RATE_HZ)

    v_xe = kb.toc_do_xe_kmh / 3.6
    v_vat = kb.toc_do_vat_the_kmh / 3.6
    x_xe = 0.0
    x_vat = kb.khoang_cach_dau

    du_lieu: List[Dict[str, Any]] = []
    v_tuong_doi_truoc = v_xe - v_vat

    for i in range(so_mau):
        t = i * dt
        khoang_cach_that = x_vat - x_xe

        # --- da va cham thi dung mo phong ---
        if khoang_cach_that <= 0:
            du_lieu.append({
                "t": round(t, 3),
                "khoang_cach": 0.0,
                "khoang_cach_that": 0.0,
                "toc_do_xe_kmh": round(v_xe * 3.6, 2),
                "toc_do_vat_the_kmh": round(v_vat * 3.6, 2),
                "gia_toc_tuong_doi": 0.0,
                "tinh_trang_duong": kb.tinh_trang_duong,
                "trang_thai_tai_xe": kb.trang_thai_tai_xe,
                "loai_vat_the": kb.loai_vat_the,
                "cam_bien_hoat_dong": True,
                "da_va_cham": True,
            })
            break

        # --- mo phong nhieu va mat tin hieu cua cam bien ---
        cam_bien_ok = True
        d_do = khoang_cach_that
        v_do = v_xe * 3.6
        v_vat_do = v_vat * 3.6

        if co_nhieu:
            if rng.random() < DROPOUT_PROB:
                cam_bien_ok = False
            # nhieu do khoang cach tang dan theo cu ly (dac trung cua radar)
            he_so_cu_ly = 1.0 + khoang_cach_that / MAX_SENSOR_RANGE
            d_do = max(0.0, khoang_cach_that + rng.gauss(0, DISTANCE_NOISE_STD * he_so_cu_ly))
            v_do = max(0.0, v_xe * 3.6 + rng.gauss(0, SPEED_NOISE_STD))
            v_vat_do = max(0.0, v_vat * 3.6 + rng.gauss(0, SPEED_NOISE_STD))

        # --- gia toc tuong doi (toc do tiep can dang tang hay giam) ---
        v_tuong_doi = v_xe - v_vat
        gia_toc_tuong_doi = (v_tuong_doi - v_tuong_doi_truoc) / dt if i > 0 else 0.0
        v_tuong_doi_truoc = v_tuong_doi

        du_lieu.append({
            "t": round(t, 3),
            "khoang_cach": round(d_do, 3),
            "khoang_cach_that": round(khoang_cach_that, 3),
            "toc_do_xe_kmh": round(v_do, 2),
            "toc_do_vat_the_kmh": round(v_vat_do, 2),
            "gia_toc_tuong_doi": round(gia_toc_tuong_doi, 3),
            "tinh_trang_duong": kb.tinh_trang_duong,
            "trang_thai_tai_xe": kb.trang_thai_tai_xe,
            "loai_vat_the": kb.loai_vat_the,
            "cam_bien_hoat_dong": cam_bien_ok,
            "da_va_cham": False,
        })

        # --- cap nhat dong hoc ---
        # vat the phia truoc chi bat dau phanh khi da qua thoi_diem_phanh
        a_vat = kb.gia_toc_vat_the if t >= kb.thoi_diem_phanh else 0.0
        if v_vat <= 0.0:
            a_vat = 0.0

        x_xe += v_xe * dt + 0.5 * kb.gia_toc_xe * dt * dt
        x_vat += max(0.0, v_vat * dt + 0.5 * a_vat * dt * dt)
        v_xe = max(0.0, v_xe + kb.gia_toc_xe * dt)
        v_vat = max(0.0, v_vat + a_vat * dt)

    return du_lieu


def sinh_toan_bo(mssv: str, co_nhieu: bool = True) -> Dict[str, Dict[str, Any]]:
    """Sinh du lieu cho toan bo 6 kich ban ung voi 1 MSSV."""
    ket_qua = {}
    for kb_goc in DANH_SACH_KICH_BAN:
        kb = ca_bien_kich_ban(kb_goc, mssv)
        ket_qua[kb.ma] = {
            "kich_ban": kb,
            "du_lieu": sinh_du_lieu(kb, mssv, co_nhieu=co_nhieu),
        }
    return ket_qua
