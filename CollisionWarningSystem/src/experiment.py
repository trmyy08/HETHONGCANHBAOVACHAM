# -*- coding: utf-8 -*-
"""
experiment.py
Chay mo phong, do cac chi so danh gia va so sanh giua hai mo hinh:
    (A) He suy dien theo luat, ket hop TOC DO + KHOANG CACH  (de xuat cua nhom)
    (B) Nguong khoang cach co dinh, KHONG xet toc do          (doi chung)
"""

import csv
import os
import statistics
from typing import List, Dict, Any

from config import (
    MSSV_LIST, G, BRAKE_EFFICIENCY, ROAD_FRICTION,
    LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER, LEVEL_ORDER, SENSOR_RATE_HZ,
)
from sensor_simulator import DANH_SACH_KICH_BAN, ca_bien_kich_ban, sinh_du_lieu
from inference_engine import suy_dien, suy_dien_nguong_co_dinh, loc_on_dinh

THU_MUC_KET_QUA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
THU_MUC_DU_LIEU = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


# ---------------------------------------------------------------------------
# MOC THOI GIAN TOI HAN (ground truth de danh gia canh bao som hay muon)
# ---------------------------------------------------------------------------
def tim_moc_toi_han(du_lieu: List[Dict[str, Any]], tinh_trang_duong: str) -> float:
    """Tim moc mat kha nang tranh va cham neu xe chu phanh toi da ngay lap tuc.

    Dung khoang cach dung tuong doi: xe chu va vat the deu co quang duong dung
    rieng. Moc toi han xay ra khi khoang cach thuc te khong con du bu cho chenhlech
    quang duong dung. Day la mo hinh 1D ly tuong hoa, khong thay the thu nghiem xe.
    """
    a_ego = max(0.1, ROAD_FRICTION[tinh_trang_duong] * G * BRAKE_EFFICIENCY)
    # Gia dinh vat the cung co kha nang giam toc voi he so bam mat duong nhu xe chu.
    a_lead = a_ego
    for mau in du_lieu:
        v_ego = max(0.0, mau["toc_do_xe_kmh"] / 3.6)
        v_lead = max(0.0, mau["toc_do_vat_the_kmh"] / 3.6)
        d_stop_ego = (v_ego ** 2) / (2.0 * a_ego)
        d_stop_lead = (v_lead ** 2) / (2.0 * a_lead)
        d_required = max(0.0, d_stop_ego - d_stop_lead)
        if mau["khoang_cach_that"] <= d_required:
            return mau["t"]
    return float("inf")


# ---------------------------------------------------------------------------
# CHAY 1 KICH BAN VOI 1 MSSV
# ---------------------------------------------------------------------------
def chay_mot_kich_ban(kb_goc, mssv: str) -> Dict[str, Any]:
    kb = ca_bien_kich_ban(kb_goc, mssv)
    du_lieu = sinh_du_lieu(kb, mssv, co_nhieu=True)

    ket_qua_suy_dien = [suy_dien(m) for m in du_lieu]
    # Chuoi ket luan tho, truoc khi loc nhieu
    muc_luat_tho = [k["muc_canh_bao"] for k in ket_qua_suy_dien]
    muc_nguong_tho = [suy_dien_nguong_co_dinh(m) for m in du_lieu]
    # Ap dung bo loc on dinh cho CA HAI mo hinh de so sanh cong bang
    ket_qua_nguong = loc_on_dinh(muc_nguong_tho)

    t_toi_han = tim_moc_toi_han(du_lieu, kb.tinh_trang_duong)
    co_va_cham = any(m["da_va_cham"] for m in du_lieu)

    def thoi_diem_dau_tien(chuoi_muc, muc):
        """Thoi diem dau tien dat DEN muc do (CANH BAO tinh ca truong hop
        he nhay thang len NGUY HIEM)."""
        nguong = LEVEL_ORDER[muc]
        for i, m in enumerate(chuoi_muc):
            if LEVEL_ORDER[m] >= nguong:
                return du_lieu[i]["t"]
        return None

    muc_luat = loc_on_dinh(muc_luat_tho)

    t_cb_luat = thoi_diem_dau_tien(muc_luat, LEVEL_WARNING)
    t_nh_luat = thoi_diem_dau_tien(muc_luat, LEVEL_DANGER)
    t_cb_nguong = thoi_diem_dau_tien(ket_qua_nguong, LEVEL_WARNING)
    t_nh_nguong = thoi_diem_dau_tien(ket_qua_nguong, LEVEL_DANGER)

    def thoi_gian_du_bao_truoc(t_cb):
        if t_cb is None or t_toi_han == float("inf"):
            return None
        return round(t_toi_han - t_cb, 2)

    def dem(chuoi):
        return {
            LEVEL_SAFE: chuoi.count(LEVEL_SAFE),
            LEVEL_WARNING: chuoi.count(LEVEL_WARNING),
            LEVEL_DANGER: chuoi.count(LEVEL_DANGER),
        }

    so_mau_xung_dot = sum(1 for k in ket_qua_suy_dien if k["co_xung_dot"])
    so_luat_khop_tb = statistics.mean(k["so_luat_khop"] for k in ket_qua_suy_dien)
    cac_luat_da_dung = sorted({k["luat_thang"] for k in ket_qua_suy_dien})
    cac_luat_tung_khop = sorted({g["ma_luat"] for k in ket_qua_suy_dien for g in k["giai_trinh"]})

    return {
        "mssv": mssv,
        "ma_kich_ban": kb.ma,
        "ten_kich_ban": kb.ten,
        "kich_ban": kb,
        "du_lieu": du_lieu,
        "ket_qua_suy_dien": ket_qua_suy_dien,
        "muc_luat": muc_luat,
        "muc_nguong": ket_qua_nguong,
        "t_toi_han": t_toi_han,
        "co_va_cham": co_va_cham,
        "t_canh_bao_luat": t_cb_luat,
        "t_nguy_hiem_luat": t_nh_luat,
        "t_canh_bao_nguong": t_cb_nguong,
        "t_nguy_hiem_nguong": t_nh_nguong,
        "du_bao_truoc_luat": thoi_gian_du_bao_truoc(t_cb_luat),
        "du_bao_truoc_nguong": thoi_gian_du_bao_truoc(t_cb_nguong),
        "phan_bo_luat": dem(muc_luat),
        "phan_bo_nguong": dem(ket_qua_nguong),
        "so_mau": len(du_lieu),
        "so_mau_xung_dot": so_mau_xung_dot,
        "so_luat_khop_tb": round(so_luat_khop_tb, 2),
        "cac_luat_da_dung": cac_luat_da_dung,
        "cac_luat_tung_khop": cac_luat_tung_khop,
    }


# ---------------------------------------------------------------------------
# CHAY TOAN BO THI NGHIEM
# ---------------------------------------------------------------------------
def chay_toan_bo() -> List[Dict[str, Any]]:
    tat_ca = []
    for mssv in MSSV_LIST:
        for kb in DANH_SACH_KICH_BAN:
            tat_ca.append(chay_mot_kich_ban(kb, mssv))
    return tat_ca


# ---------------------------------------------------------------------------
# XUAT FILE
# ---------------------------------------------------------------------------
def xuat_csv_tong_hop(tat_ca: List[Dict[str, Any]]) -> str:
    os.makedirs(THU_MUC_KET_QUA, exist_ok=True)
    duong_dan = os.path.join(THU_MUC_KET_QUA, "tong_hop_ket_qua.csv")
    with open(duong_dan, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "MSSV", "Kich ban", "Ten kich ban", "Toc do xe (km/h)",
            "Toc do vat the (km/h)", "Khoang cach dau (m)", "Tinh trang duong",
            "Trang thai tai xe", "Moc toi han (s)", "Co va cham",
            "T canh bao - Luat (s)", "T nguy hiem - Luat (s)",
            "Du bao truoc - Luat (s)",
            "T canh bao - Nguong (s)", "T nguy hiem - Nguong (s)",
            "Du bao truoc - Nguong (s)",
            "So mau AN TOAN", "So mau CANH BAO", "So mau NGUY HIEM",
            "So mau xung dot", "So luat khop TB",
        ])
        for r in tat_ca:
            kb = r["kich_ban"]
            w.writerow([
                r["mssv"], r["ma_kich_ban"], r["ten_kich_ban"],
                kb.toc_do_xe_kmh, kb.toc_do_vat_the_kmh, kb.khoang_cach_dau,
                kb.tinh_trang_duong, kb.trang_thai_tai_xe,
                "inf" if r["t_toi_han"] == float("inf") else r["t_toi_han"],
                "Co" if r["co_va_cham"] else "Khong",
                r["t_canh_bao_luat"], r["t_nguy_hiem_luat"], r["du_bao_truoc_luat"],
                r["t_canh_bao_nguong"], r["t_nguy_hiem_nguong"], r["du_bao_truoc_nguong"],
                r["phan_bo_luat"][LEVEL_SAFE], r["phan_bo_luat"][LEVEL_WARNING],
                r["phan_bo_luat"][LEVEL_DANGER],
                r["so_mau_xung_dot"], r["so_luat_khop_tb"],
            ])
    return duong_dan


def xuat_csv_du_lieu_tho(tat_ca: List[Dict[str, Any]]) -> str:
    """Xuat toan bo chuoi mau cam bien kem ket luan, de nop kem bao cao."""
    os.makedirs(THU_MUC_DU_LIEU, exist_ok=True)
    duong_dan = os.path.join(THU_MUC_DU_LIEU, "du_lieu_cam_bien.csv")
    with open(duong_dan, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "MSSV", "Kich ban", "t (s)", "Khoang cach do (m)", "Khoang cach that (m)",
            "Toc do xe (km/h)", "Toc do vat the (km/h)", "TTC (s)",
            "Khoang cach an toan (m)", "Ty le d/d_an_toan",
            "Muc canh bao (Luat)", "Luat thang", "Muc canh bao (Nguong co dinh)",
        ])
        for r in tat_ca:
            for mau, kq, muc_ng in zip(r["du_lieu"], r["ket_qua_suy_dien"], r["muc_nguong"]):
                w.writerow([
                    r["mssv"], r["ma_kich_ban"], mau["t"],
                    mau["khoang_cach"], mau["khoang_cach_that"],
                    mau["toc_do_xe_kmh"], mau["toc_do_vat_the_kmh"],
                    "inf" if kq["ttc"] == float("inf") else round(kq["ttc"], 3),
                    round(kq["khoang_cach_an_toan"], 2),
                    round(kq["ty_le_khoang_cach"], 3),
                    kq["muc_canh_bao"], kq["luat_thang"], muc_ng,
                ])
    return duong_dan
