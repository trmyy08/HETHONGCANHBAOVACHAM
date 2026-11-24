# -*- coding: utf-8 -*-
"""
inference_engine.py
Dong co doi sanh luat va tong hop bang chung cho he thong canh bao va cham.

Quy trinh:
    1. Tien xu ly  : tu du lieu cam bien tho tinh ra cac su kien dan xuat
                     (TTC, khoang cach an toan, ty le khoang cach...)
    2. Doi sanh    : duyet toan bo co so luat, thu thap cac luat khop
    3. Giai xung dot: chon luat thang theo (do uu tien, muc nghiem trong, do tin cay)
    4. Giai trinh  : xuat chuoi suy dien dan den ket luan
"""

from typing import Dict, Any, List, Tuple

from config import (
    G, BRAKE_EFFICIENCY, ROAD_FRICTION, REACTION_TIME,
    TTC_DANGER, TTC_WARNING, DR_DANGER, DR_WARNING,
    ABSOLUTE_MIN_DISTANCE, NEGLIGIBLE_SPEED_KMH, MAX_SENSOR_RANGE,
    LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER, LEVEL_ORDER, LEVEL_ACTION,
    BASELINE_DANGER_DISTANCE, BASELINE_WARNING_DISTANCE,
)
from knowledge_base import RULE_BASE, Rule


# ---------------------------------------------------------------------------
# BUOC 1: TIEN XU LY - SINH CAC SU KIEN DAN XUAT
# ---------------------------------------------------------------------------
def tinh_khoang_cach_an_toan(toc_do_ms: float, he_so_bam: float,
                             thoi_gian_phan_ung: float) -> float:
    """
    Khoang cach an toan toi thieu = quang duong phan ung + quang duong phanh.

        d_an_toan = v * t_phan_ung + v^2 / (2 * a_hieu_dung)
        a_hieu_dung = he_so_bam * g * hieu_suat_phanh
    """
    a_hieu_dung = he_so_bam * G * BRAKE_EFFICIENCY
    quang_duong_phan_ung = toc_do_ms * thoi_gian_phan_ung
    quang_duong_phanh = (toc_do_ms ** 2) / (2 * a_hieu_dung) if a_hieu_dung > 0 else float("inf")
    return quang_duong_phan_ung + quang_duong_phanh


def tinh_ttc(khoang_cach: float, toc_do_tuong_doi_ms: float) -> float:
    """Time To Collision. Tra ve vo cung neu khong tiep can."""
    if toc_do_tuong_doi_ms <= 0.01:
        return float("inf")
    return khoang_cach / toc_do_tuong_doi_ms


def tien_xu_ly(mau: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuyen 1 mau du lieu cam bien tho thanh tap su kien (facts) day du
    de dong co suy dien doi sanh voi co so luat.
    """
    toc_do_xe_kmh = mau["toc_do_xe_kmh"]
    toc_do_vat_kmh = mau["toc_do_vat_the_kmh"]
    khoang_cach = mau["khoang_cach"]

    toc_do_xe_ms = toc_do_xe_kmh / 3.6
    toc_do_vat_ms = toc_do_vat_kmh / 3.6
    toc_do_tuong_doi_ms = toc_do_xe_ms - toc_do_vat_ms

    he_so_bam = ROAD_FRICTION[mau["tinh_trang_duong"]]
    thoi_gian_phan_ung = REACTION_TIME[mau["trang_thai_tai_xe"]]

    khoang_cach_an_toan = tinh_khoang_cach_an_toan(
        toc_do_xe_ms, he_so_bam, thoi_gian_phan_ung
    )
    ttc = tinh_ttc(khoang_cach, toc_do_tuong_doi_ms)
    ty_le = khoang_cach / khoang_cach_an_toan if khoang_cach_an_toan > 0 else 99.0

    facts: Dict[str, Any] = {
        # --- su kien goc tu cam bien ---
        "t": mau["t"],
        "khoang_cach": khoang_cach,
        "toc_do_xe_kmh": toc_do_xe_kmh,
        "toc_do_vat_the_kmh": toc_do_vat_kmh,
        "tinh_trang_duong": mau["tinh_trang_duong"],
        "trang_thai_tai_xe": mau["trang_thai_tai_xe"],
        "loai_vat_the": mau["loai_vat_the"],
        "cam_bien_hoat_dong": mau["cam_bien_hoat_dong"],
        "gia_toc_tuong_doi": mau.get("gia_toc_tuong_doi", 0.0),

        # --- su kien dan xuat ---
        "toc_do_xe_ms": toc_do_xe_ms,
        "toc_do_tuong_doi_ms": toc_do_tuong_doi_ms,
        "toc_do_tuong_doi_kmh": toc_do_tuong_doi_ms * 3.6,
        "dang_tiep_can": toc_do_tuong_doi_ms > 0.01,
        "he_so_bam_duong": he_so_bam,
        "thoi_gian_phan_ung": thoi_gian_phan_ung,
        "khoang_cach_an_toan": khoang_cach_an_toan,
        "ty_le_khoang_cach": ty_le,
        "ty_le_phan_tram": ty_le * 100,
        "ttc": ttc,

        # --- hang so nguong, de in ra trong cau giai thich ---
        "nguong_ttc_nguy_hiem": TTC_DANGER,
        "nguong_ttc_canh_bao": TTC_WARNING,
        "nguong_toi_thieu": ABSOLUTE_MIN_DISTANCE,
        "nguong_toc_do_bo_qua": NEGLIGIBLE_SPEED_KMH,
        "tam_do_toi_da": MAX_SENSOR_RANGE,
    }
    return facts


# ---------------------------------------------------------------------------
# BUOC 2 + 3: DOI SANH VA GIAI QUYET XUNG DOT
# ---------------------------------------------------------------------------
def suy_dien_tien(facts: Dict[str, Any]) -> Tuple[List[Rule], Dict[str, Any], List[str]]:
    """Suy dien tien theo co che agenda va Working Memory.

    Pha 1: cac luat tac nghiep R01-R22 doc su kien cam bien va dua su kien
           ``kich_hoat_<ma_luat>`` vao bo nho lam viec.
    Pha 2: M01-M03 tong hop bang chung nguy hiem/canh bao/an toan de giai thich.
           Cac bang chung nay khong tham gia chon ket luan cuoi.
    Pha 3: lap den khi khong con bang chung moi (fixed point).

    Ket luan cuoi duoc chon truc tiep tu cac luat tac nghiep R01-R22 bang
    chien luoc giai xung dot.
    """
    wm = dict(facts)  # Working Memory: su kien goc + su kien dan xuat
    agenda: List[Rule] = []
    trace: List[str] = []

    # Nap cac luat co the kich hoat vao agenda theo thu tu uu tien.
    pending = sorted(RULE_BASE, key=lambda r: (-r.uu_tien, r.id))
    while pending:
        rule = pending.pop(0)
        if rule.kiem_tra(wm):
            agenda.append(rule)
            wm[f"kich_hoat_{rule.id}"] = True
            trace.append(f"{rule.id}: dieu kien dung -> them kich_hoat_{rule.id}")

    # Cac luat tong hop (meta-rules) tao su kien moi tu ket qua luat tac nghiep.
    # Vong lap tiep tuc den khi khong con su kien moi.
    # M01-M03 chi tao cac nhan bang chung de trace giai thich.
    # M04-M06 bi loai bo vi khong duoc luat tac nghiep nao su dung va
    # khong anh huong den ket luan cuoi; khong gia lap suy dien nhieu tang.
    meta_rules = [
        ("M01", lambda w: any(r.ket_luan == LEVEL_DANGER for r in agenda),
         "co_bang_chung_nguy_hiem"),
        ("M02", lambda w: any(r.ket_luan == LEVEL_WARNING for r in agenda),
         "co_bang_chung_canh_bao"),
        ("M03", lambda w: any(r.ket_luan == LEVEL_SAFE for r in agenda),
         "co_bang_chung_an_toan"),
    ]
    changed = True
    so_vong = 0
    while changed:
        so_vong += 1
        changed = False
        for ma, dieu_kien, fact_moi in meta_rules:
            if not wm.get(fact_moi, False) and dieu_kien(wm):
                wm[fact_moi] = True
                trace.append(f"{ma}: suy ra {fact_moi}")
                changed = True

    wm["so_vong_suy_dien"] = so_vong
    return agenda, wm, trace


def doi_sanh(facts: Dict[str, Any]) -> List[Rule]:
    """Tuong thich API cu: tra ve tap luat tac nghiep duoc kich hoat."""
    agenda, _, _ = suy_dien_tien(facts)
    return agenda


def giai_quyet_xung_dot(cac_luat_khop: List[Rule]) -> Rule:
    """
    Chien luoc giai xung dot 3 tang:
        1. Do uu tien cao hon thang
        2. Cung uu tien -> muc canh bao nghiem trong hon thang (an toan la tren het)
        3. Van bang nhau -> do tin cay cao hon thang
    """
    return max(
        cac_luat_khop,
        key=lambda r: (r.uu_tien, LEVEL_ORDER[r.ket_luan], r.do_tin_cay),
    )


# ---------------------------------------------------------------------------
# BUOC 4: SUY DIEN HOAN CHINH + GIAI TRINH
# ---------------------------------------------------------------------------
def suy_dien(mau: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suy dien muc canh bao cho 1 mau du lieu cam bien.
    Tra ve dict gom muc canh bao, luat thang, toan bo tap xung dot va chuoi giai trinh.
    """
    facts = tien_xu_ly(mau)
    cac_luat_khop, working_memory, trace_tien = suy_dien_tien(facts)
    luat_thang = giai_quyet_xung_dot(cac_luat_khop)

    # Chuoi giai trinh: cac luat khop, sap xep giam dan theo uu tien
    cac_luat_khop_sorted = sorted(
        cac_luat_khop,
        key=lambda r: (-r.uu_tien, -LEVEL_ORDER[r.ket_luan]),
    )
    giai_trinh = [
        {
            "ma_luat": r.id,
            "nhom": r.nhom,
            "ket_luan": r.ket_luan,
            "uu_tien": r.uu_tien,
            "do_tin_cay": r.do_tin_cay,
            "dien_giai": r.dien_giai(facts),
            "la_luat_thang": (r.id == luat_thang.id),
        }
        for r in cac_luat_khop_sorted
    ]

    return {
        "t": facts["t"],
        "khoang_cach": facts["khoang_cach"],
        "toc_do_xe_kmh": facts["toc_do_xe_kmh"],
        "toc_do_vat_the_kmh": facts["toc_do_vat_the_kmh"],
        "ttc": facts["ttc"],
        "khoang_cach_an_toan": facts["khoang_cach_an_toan"],
        "ty_le_khoang_cach": facts["ty_le_khoang_cach"],
        "muc_canh_bao": luat_thang.ket_luan,
        "luat_thang": luat_thang.id,
        "do_tin_cay": luat_thang.do_tin_cay,
        "hanh_dong": LEVEL_ACTION[luat_thang.ket_luan],
        "so_luat_khop": len(cac_luat_khop),
        "co_xung_dot": len({r.ket_luan for r in cac_luat_khop}) > 1,
        "giai_trinh": giai_trinh,
        "facts": facts,
        "working_memory": working_memory,
        "trace_suy_dien_tien": trace_tien,
        "so_vong_suy_dien": working_memory["so_vong_suy_dien"],
    }


def in_giai_trinh(kq: Dict[str, Any], chi_tiet: bool = True) -> str:
    """Xuat chuoi suy dien duoi dang van ban de dua vao bao cao."""
    dong = []
    dong.append(f"  t = {kq['t']:.2f}s | d = {kq['khoang_cach']:.1f} m | "
                f"v = {kq['toc_do_xe_kmh']:.1f} km/h | "
                f"TTC = {kq['ttc']:.2f}s | "
                f"d/d_an_toan = {kq['ty_le_khoang_cach']:.2f}")
    dong.append(f"  => KET LUAN: {kq['muc_canh_bao']} (luat {kq['luat_thang']}, "
                f"do tin cay {kq['do_tin_cay']:.2f})")
    if chi_tiet:
        dong.append("  Tong hop bang chung M01-M03 (phuc vu giai thich):")
        for buoc in kq["trace_suy_dien_tien"]:
            dong.append(f"     [FC] {buoc}")
        dong.append(f"  So luat khop: {kq['so_luat_khop']}"
                    + ("  [CO XUNG DOT - da giai quyet bang do uu tien]" if kq["co_xung_dot"] else ""))
        for g in kq["giai_trinh"]:
            dau = ">>" if g["la_luat_thang"] else "  "
            dong.append(f"   {dau} [{g['ma_luat']}|ut={g['uu_tien']}|{g['ket_luan']}] {g['dien_giai']}")
    return "\n".join(dong)


# ---------------------------------------------------------------------------
# BO LOC ON DINH - XU LY NHIEU CAM BIEN NHAT THOI
# ---------------------------------------------------------------------------
def loc_on_dinh(chuoi_muc: List[str], so_mau_xac_nhan: int = 3) -> List[str]:
    """
    Loai bo cac 'nhap nhay' canh bao do nhieu hoac mat tin hieu cam bien
    trong 1-2 mau roi tro lai binh thuong.

    Nguyen tac:
        - Mot muc canh bao chi duoc cong nhan neu duy tri du so_mau_xac_nhan mau
          lien tiep. Neu khong, giu lai muc da duoc cong nhan truoc do.
        - Rieng muc NGUY HIEM duoc cong nhan NGAY LAP TUC (khong cho xac nhan),
          vi tre mot phan muoi giay cung co the khien canh bao vo nghia.
    """
    if not chuoi_muc:
        return []

    ket_qua = []
    muc_on_dinh = chuoi_muc[0]
    i = 0
    n = len(chuoi_muc)

    while i < n:
        muc_hien_tai = chuoi_muc[i]

        if muc_hien_tai == muc_on_dinh:
            ket_qua.append(muc_on_dinh)
            i += 1
            continue

        # Nguy hiem: cong nhan ngay, khong cho xac nhan
        if muc_hien_tai == LEVEL_DANGER:
            muc_on_dinh = LEVEL_DANGER
            ket_qua.append(muc_on_dinh)
            i += 1
            continue

        # Cac muc khac: dem so mau lien tiep cung muc
        j = i
        while j < n and chuoi_muc[j] == muc_hien_tai:
            j += 1
        do_dai = j - i

        if do_dai >= so_mau_xac_nhan:
            muc_on_dinh = muc_hien_tai          # du dai -> cong nhan
            ket_qua.extend([muc_on_dinh] * do_dai)
        else:
            ket_qua.extend([muc_on_dinh] * do_dai)  # qua ngan -> coi la nhieu
        i = j

    return ket_qua


# ---------------------------------------------------------------------------
# MO HINH DOI CHUNG: CHI DUNG NGUONG KHOANG CACH CO DINH
# ---------------------------------------------------------------------------
def suy_dien_nguong_co_dinh(mau: Dict[str, Any],
                            nguong_nguy_hiem: float = BASELINE_DANGER_DISTANCE,
                            nguong_canh_bao: float = BASELINE_WARNING_DISTANCE) -> str:
    """
    Mo hinh doi chung (baseline) de so sanh trong bao cao:
    chi dua tren khoang cach, KHONG xet toc do.
    Day la cach lam don gian nhat ma nhieu he canh bao gia re dang dung.
    """
    if not mau["cam_bien_hoat_dong"]:
        return LEVEL_WARNING
    d = mau["khoang_cach"]
    if d < nguong_nguy_hiem:
        return LEVEL_DANGER
    if d < nguong_canh_bao:
        return LEVEL_WARNING
    return LEVEL_SAFE
