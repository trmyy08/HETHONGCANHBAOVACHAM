# -*- coding: utf-8 -*-
"""
visualize.py
Sinh cac bieu do truc quan phuc vu bao cao.

Cac hinh duoc xuat ra thu muc results/:
    H1_dien_bien_kich_ban.png   - dien bien khoang cach + muc canh bao, 6 kich ban
    H2_ttc_theo_thoi_gian.png   - TTC va nguong canh bao
    H3_so_sanh_du_bao.png       - so sanh thoi gian du bao truoc giua 2 mo hinh
    H4_ban_do_quyet_dinh.png    - ban do quyet dinh tren mat phang (toc do, khoang cach)
    H5_phan_bo_theo_mssv.png    - phan bo muc canh bao theo tung MSSV
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from config import (
    MSSV_LIST, LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER,
    TTC_DANGER, TTC_WARNING, BASELINE_DANGER_DISTANCE, BASELINE_WARNING_DISTANCE,
)
from sensor_simulator import DANH_SACH_KICH_BAN
from inference_engine import suy_dien
from experiment import chay_mot_kich_ban, THU_MUC_KET_QUA

MAU = {
    LEVEL_SAFE:    "#2E933C",
    LEVEL_WARNING: "#E8A33D",
    LEVEL_DANGER:  "#C9342B",
}

plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 160,
    "font.size": 9,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def _to_mau(chuoi_muc):
    return [MAU[m] for m in chuoi_muc]


# ---------------------------------------------------------------------------
# HINH 1: DIEN BIEN 6 KICH BAN
# ---------------------------------------------------------------------------
def hinh_dien_bien(ket_qua_mot_mssv, mssv):
    fig, axes = plt.subplots(2, 4, figsize=(17, 7))
    for ax, r in zip(axes.ravel(), ket_qua_mot_mssv):
        t = [m["t"] for m in r["du_lieu"]]
        d = [m["khoang_cach"] for m in r["du_lieu"]]
        d_at = [k["khoang_cach_an_toan"] for k in r["ket_qua_suy_dien"]]

        ax.scatter(t, d, c=_to_mau(r["muc_luat"]), s=7, zorder=3)
        ax.plot(t, d_at, "--", color="#3E5C76", lw=1.3,
                label="Khoang cach an toan toi thieu", zorder=2)

        if r["t_toi_han"] != float("inf"):
            ax.axvline(r["t_toi_han"], color="black", ls=":", lw=1.4,
                       label="Moc toi han (khong con tranh duoc)")
        if r["t_canh_bao_luat"] is not None:
            ax.axvline(r["t_canh_bao_luat"], color="#E8A33D", lw=1.2, alpha=0.8)

        ax.set_title(f"{r['ma_kich_ban']}: {r['ten_kich_ban']}\n"
                     f"{r['kich_ban'].toc_do_xe_kmh:.0f} km/h, "
                     f"d0 = {r['kich_ban'].khoang_cach_dau:.0f} m, "
                     f"duong {r['kich_ban'].tinh_trang_duong}", fontsize=8.5)
        ax.set_xlabel("Thoi gian (s)")
        ax.set_ylabel("Khoang cach (m)")
        ax.legend(fontsize=6.5, loc="upper right")

    chu_thich = [Patch(facecolor=MAU[k], label=k) for k in
                 (LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER)]
    fig.legend(handles=chu_thich, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.015))
    fig.suptitle(f"Hinh 1. Dien bien khoang cach va muc canh bao qua 8 kich ban "
                 f"(du lieu sinh theo MSSV {mssv})", fontsize=11, y=1.0)
    fig.tight_layout()
    duong_dan = os.path.join(THU_MUC_KET_QUA, "H1_dien_bien_kich_ban.png")
    fig.savefig(duong_dan, bbox_inches="tight")
    plt.close(fig)
    return duong_dan


# ---------------------------------------------------------------------------
# HINH 2: TTC THEO THOI GIAN
# ---------------------------------------------------------------------------
def hinh_ttc(ket_qua_mot_mssv, mssv):
    fig, ax = plt.subplots(figsize=(10, 5))
    mau_duong = plt.cm.viridis(np.linspace(0, 0.9, len(ket_qua_mot_mssv)))
    for r, c in zip(ket_qua_mot_mssv, mau_duong):
        t = [m["t"] for m in r["du_lieu"]]
        ttc = [min(k["ttc"], 15) for k in r["ket_qua_suy_dien"]]
        ax.plot(t, ttc, lw=1.6, color=c, label=f"{r['ma_kich_ban']} - {r['ten_kich_ban']}")

    ax.axhline(TTC_WARNING, color=MAU[LEVEL_WARNING], ls="--", lw=1.5)
    ax.axhline(TTC_DANGER, color=MAU[LEVEL_DANGER], ls="--", lw=1.5)
    ax.axhspan(0, TTC_DANGER, color=MAU[LEVEL_DANGER], alpha=0.10)
    ax.axhspan(TTC_DANGER, TTC_WARNING, color=MAU[LEVEL_WARNING], alpha=0.10)
    ax.axhspan(TTC_WARNING, 15, color=MAU[LEVEL_SAFE], alpha=0.07)
    ax.text(0.15, TTC_DANGER - 0.35, f"Nguong NGUY HIEM = {TTC_DANGER}s",
            color=MAU[LEVEL_DANGER], fontsize=8)
    ax.text(0.15, TTC_WARNING + 0.2, f"Nguong CANH BAO = {TTC_WARNING}s",
            color="#9A6B1E", fontsize=8)

    ax.set_ylim(0, 15)
    ax.set_xlabel("Thoi gian (s)")
    ax.set_ylabel("TTC - thoi gian den khi va cham (s)")
    ax.set_title(f"Hinh 2. Dien bien TTC va cac nguong canh bao (MSSV {mssv})")
    ax.legend(fontsize=7.5, loc="upper right")
    fig.tight_layout()
    duong_dan = os.path.join(THU_MUC_KET_QUA, "H2_ttc_theo_thoi_gian.png")
    fig.savefig(duong_dan)
    plt.close(fig)
    return duong_dan


# ---------------------------------------------------------------------------
# HINH 3: SO SANH THOI GIAN DU BAO TRUOC
# ---------------------------------------------------------------------------
def hinh_so_sanh(tat_ca):
    ma_kb = [kb.ma for kb in DANH_SACH_KICH_BAN if kb.ma != "KB6"]
    luat, nguong = [], []
    for ma in ma_kb:
        nhom = [r for r in tat_ca if r["ma_kich_ban"] == ma]
        gt_luat = [r["du_bao_truoc_luat"] for r in nhom if r["du_bao_truoc_luat"] is not None]
        gt_ng = [r["du_bao_truoc_nguong"] for r in nhom if r["du_bao_truoc_nguong"] is not None]
        luat.append(float(np.mean(gt_luat)) if gt_luat else 0.0)
        nguong.append(float(np.mean(gt_ng)) if gt_ng else 0.0)

    x = np.arange(len(ma_kb))
    w = 0.36
    fig, ax = plt.subplots(figsize=(10, 5))
    b1 = ax.bar(x - w / 2, luat, w, label="He suy dien theo luat (toc do + khoang cach)",
                color="#2E6F9E")
    b2 = ax.bar(x + w / 2, nguong, w, label="Nguong khoang cach co dinh (doi chung)",
                color="#B0B7BE")
    ax.bar_label(b1, fmt="%.2f", fontsize=8)
    ax.bar_label(b2, fmt="%.2f", fontsize=8)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels(ma_kb)
    ax.set_ylabel("Thoi gian du bao truoc (giay)")
    ax.set_title("Hinh 3. Thoi gian canh bao som truoc moc toi han\n"
                 "(trung binh tren 5 MSSV; gia tri am nghia la canh bao khi da khong con tranh duoc)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    duong_dan = os.path.join(THU_MUC_KET_QUA, "H3_so_sanh_du_bao.png")
    fig.savefig(duong_dan)
    plt.close(fig)
    return duong_dan, dict(zip(ma_kb, zip(luat, nguong)))


# ---------------------------------------------------------------------------
# HINH 4: BAN DO QUYET DINH TREN MAT PHANG (TOC DO, KHOANG CACH)
# ---------------------------------------------------------------------------
def hinh_ban_do_quyet_dinh():
    toc_do = np.linspace(5, 120, 120)
    khoang_cach = np.linspace(1, 120, 120)
    luoi = np.zeros((len(khoang_cach), len(toc_do)))
    luoi_ng = np.zeros_like(luoi)

    from config import LEVEL_ORDER
    from inference_engine import suy_dien_nguong_co_dinh

    for i, d in enumerate(khoang_cach):
        for j, v in enumerate(toc_do):
            mau = {
                "t": 0.0, "khoang_cach": float(d), "khoang_cach_that": float(d),
                "toc_do_xe_kmh": float(v), "toc_do_vat_the_kmh": 0.0,
                "gia_toc_tuong_doi": 0.0, "tinh_trang_duong": "kho",
                "trang_thai_tai_xe": "binh_thuong", "loai_vat_the": "xe_phia_truoc",
                "cam_bien_hoat_dong": True, "da_va_cham": False,
            }
            luoi[i, j] = LEVEL_ORDER[suy_dien(mau)["muc_canh_bao"]]
            luoi_ng[i, j] = LEVEL_ORDER[suy_dien_nguong_co_dinh(mau)]

    from matplotlib.colors import ListedColormap
    cmap = ListedColormap([MAU[LEVEL_SAFE], MAU[LEVEL_WARNING], MAU[LEVEL_DANGER]])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, Z, ten in zip(
        axes, [luoi_ng, luoi],
        ["(a) Nguong khoang cach co dinh\n(chi xet khoang cach)",
         "(b) He suy dien theo luat\n(ket hop toc do + khoang cach)"],
    ):
        ax.pcolormesh(toc_do, khoang_cach, Z, cmap=cmap, vmin=0, vmax=2, shading="auto")
        ax.set_xlabel("Toc do xe chu (km/h)")
        ax.set_title(ten, fontsize=9.5)
        ax.grid(False)
    axes[0].set_ylabel("Khoang cach den vat the (m)")
    axes[0].axhline(BASELINE_WARNING_DISTANCE, color="white", lw=0.8, ls="--")
    axes[0].axhline(BASELINE_DANGER_DISTANCE, color="white", lw=0.8, ls="--")

    chu_thich = [Patch(facecolor=MAU[k], label=k) for k in
                 (LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER)]
    fig.legend(handles=chu_thich, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Hinh 4. Ban do quyet dinh: muc canh bao theo toc do va khoang cach "
                 "(vat the dung yen, duong kho)", fontsize=11)
    fig.tight_layout()
    duong_dan = os.path.join(THU_MUC_KET_QUA, "H4_ban_do_quyet_dinh.png")
    fig.savefig(duong_dan, bbox_inches="tight")
    plt.close(fig)
    return duong_dan


# ---------------------------------------------------------------------------
# HINH 5: PHAN BO MUC CANH BAO THEO MSSV
# ---------------------------------------------------------------------------
def hinh_phan_bo_mssv(tat_ca):
    nhan = [m[-4:] for m in MSSV_LIST]
    an_toan, canh_bao, nguy_hiem = [], [], []
    for mssv in MSSV_LIST:
        nhom = [r for r in tat_ca if r["mssv"] == mssv]
        tong = sum(r["so_mau"] for r in nhom)
        an_toan.append(100 * sum(r["phan_bo_luat"][LEVEL_SAFE] for r in nhom) / tong)
        canh_bao.append(100 * sum(r["phan_bo_luat"][LEVEL_WARNING] for r in nhom) / tong)
        nguy_hiem.append(100 * sum(r["phan_bo_luat"][LEVEL_DANGER] for r in nhom) / tong)

    x = np.arange(len(nhan))
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.bar(x, an_toan, 0.55, label=LEVEL_SAFE, color=MAU[LEVEL_SAFE])
    ax.bar(x, canh_bao, 0.55, bottom=an_toan, label=LEVEL_WARNING, color=MAU[LEVEL_WARNING])
    day = [a + b for a, b in zip(an_toan, canh_bao)]
    ax.bar(x, nguy_hiem, 0.55, bottom=day, label=LEVEL_DANGER, color=MAU[LEVEL_DANGER])

    for i in range(len(nhan)):
        ax.text(i, an_toan[i] / 2, f"{an_toan[i]:.0f}%", ha="center", color="white", fontsize=8)
        ax.text(i, day[i] + nguy_hiem[i] / 2, f"{nguy_hiem[i]:.0f}%", ha="center",
                color="white", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels([f"...{n}" for n in nhan])
    ax.set_xlabel("MSSV (4 so cuoi)")
    ax.set_ylabel("Ty le mau (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Hinh 5. Phan bo muc canh bao tren toan bo 8 kich ban, theo tung MSSV")
    ax.legend(fontsize=8, ncol=3)
    fig.tight_layout()
    duong_dan = os.path.join(THU_MUC_KET_QUA, "H5_phan_bo_theo_mssv.png")
    fig.savefig(duong_dan)
    plt.close(fig)
    return duong_dan


def ve_tat_ca(tat_ca):
    os.makedirs(THU_MUC_KET_QUA, exist_ok=True)
    mssv_dai_dien = MSSV_LIST[0]
    kq_dai_dien = [r for r in tat_ca if r["mssv"] == mssv_dai_dien]
    duong_dan = []
    duong_dan.append(hinh_dien_bien(kq_dai_dien, mssv_dai_dien))
    duong_dan.append(hinh_ttc(kq_dai_dien, mssv_dai_dien))
    p3, bang_so_sanh = hinh_so_sanh(tat_ca)
    duong_dan.append(p3)
    duong_dan.append(hinh_ban_do_quyet_dinh())
    duong_dan.append(hinh_phan_bo_mssv(tat_ca))
    return duong_dan, bang_so_sanh
