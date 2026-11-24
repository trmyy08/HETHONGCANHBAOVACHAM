import sys
import statistics

from config import MSSV_LIST, LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER, LEVEL_ACTION
from knowledge_base import RULE_BASE, thong_ke_co_so_luat
from sensor_simulator import DANH_SACH_KICH_BAN
from inference_engine import suy_dien, in_giai_trinh
from experiment import (
    chay_toan_bo, chay_mot_kich_ban, xuat_csv_tong_hop, xuat_csv_du_lieu_tho,
)

GACH = "=" * 86
GACH_NHO = "-" * 86


def in_tieu_de():
    print(GACH)
    print("DE TAI 36 - MO PHONG HE THONG CANH BAO VA CHAM")
    print("Ky thuat AI trong tam: He luat IF-THEN, doi sanh luat + tong hop bang chung + nguong canh bao")
    print(GACH)
    tk = thong_ke_co_so_luat()
    print(f"Co so tri thuc : {tk['tong_so_luat']} luat IF-THEN, chia 6 nhom chuc nang")
    print(f"MSSV su dung   : {', '.join(MSSV_LIST)}")
    print(f"So kich ban    : {len(DANH_SACH_KICH_BAN)} (yeu cau toi thieu 3)")
    print(f"Muc canh bao   : {LEVEL_SAFE} / {LEVEL_WARNING} / {LEVEL_DANGER}")
    print(GACH, "\n")


def demo_giai_trinh():
    """In chuoi suy dien chi tiet tai cac thoi diem chuyen muc canh bao."""
    kb = DANH_SACH_KICH_BAN[0]
    r = chay_mot_kich_ban(kb, MSSV_LIST[0])
    print(f"DEMO GIAI TRINH SUY DIEN - {r['ma_kich_ban']}: {r['ten_kich_ban']}")
    print(f"MSSV {r['mssv']} | {r['kich_ban'].mo_ta}\n")

    muc_truoc = None
    for mau, kq, muc in zip(r["du_lieu"], r["ket_qua_suy_dien"], r["muc_luat"]):
        if muc != muc_truoc:
            print(GACH_NHO)
            print(f"CHUYEN MUC: {muc_truoc or 'khoi dau'} -> {muc}")
            print(in_giai_trinh(kq, chi_tiet=True))
            print(f"  Hanh dong: {LEVEL_ACTION[muc]}")
            muc_truoc = muc
    print(GACH_NHO, "\n")


def in_bang_tong_hop(tat_ca):
    print("BANG 1. KET QUA THEO TUNG KICH BAN (trung binh tren 5 MSSV)")
    print(GACH_NHO)
    print(f"{'KB':<5}{'Ten kich ban':<34}{'Toi han':>9}{'CB luat':>9}"
          f"{'Som(s)':>8}{'CB nguong':>11}{'Som(s)':>8}")
    print(GACH_NHO)

    bang = []
    for kb in DANH_SACH_KICH_BAN:
        nhom = [r for r in tat_ca if r["ma_kich_ban"] == kb.ma]

        def tb(khoa):
            gt = [r[khoa] for r in nhom if r[khoa] is not None and r[khoa] != float("inf")]
            return statistics.mean(gt) if gt else None

        d = {
            "ma": kb.ma, "ten": kb.ten,
            "toi_han": tb("t_toi_han"),
            "cb_luat": tb("t_canh_bao_luat"),
            "som_luat": tb("du_bao_truoc_luat"),
            "cb_nguong": tb("t_canh_bao_nguong"),
            "som_nguong": tb("du_bao_truoc_nguong"),
        }
        bang.append(d)

        def f(x):
            return "  --  " if x is None else f"{x:.2f}"

        print(f"{d['ma']:<5}{d['ten'][:33]:<34}{f(d['toi_han']):>9}{f(d['cb_luat']):>9}"
              f"{f(d['som_luat']):>8}{f(d['cb_nguong']):>11}{f(d['som_nguong']):>8}")
    print(GACH_NHO)
    print("Toi han  : thoi diem khong con tranh duoc va cham du phanh het suc")
    print("Som(s)   : thoi gian canh bao phat ra TRUOC moc toi han (cang lon cang tot)")
    print("Gia tri am nghia la canh bao phat ra KHI DA QUA MUON\n")
    return bang


def in_so_sanh_mo_hinh(tat_ca):
    nguy_co = [r for r in tat_ca if r["ma_kich_ban"] != "KB6"]
    an_toan = [r for r in tat_ca if r["ma_kich_ban"] == "KB6"]

    def tong_hop(khoa):
        gt = [r[khoa] for r in nguy_co if r[khoa] is not None]
        return statistics.mean(gt), min(gt), sum(1 for x in gt if x <= 0)

    tb_l, min_l, tre_l = tong_hop("du_bao_truoc_luat")
    tb_n, min_n, tre_n = tong_hop("du_bao_truoc_nguong")

    # Bao dong gia = moi mau trong kich ban an toan bi gan CANH BAO hoac NGUY HIEM.
    bao_dong_gia_l = sum(
        r["phan_bo_luat"][LEVEL_WARNING] + r["phan_bo_luat"][LEVEL_DANGER]
        for r in an_toan
    )
    bao_dong_gia_n = sum(
        r["phan_bo_nguong"][LEVEL_WARNING] + r["phan_bo_nguong"][LEVEL_DANGER]
        for r in an_toan
    )

    so_luot = len(nguy_co)
    so_kb_nguy_co = len({r["ma_kich_ban"] for r in nguy_co})
    print(f"BANG 2. SO SANH HAI MO HINH TREN {so_luot} LUOT CHAY CO NGUY CO "
          f"({so_kb_nguy_co} KB x {len(MSSV_LIST)} MSSV)")
    print(GACH_NHO)
    print(f"{'Tieu chi':<48}{'Luat':>16}{'Nguong co dinh':>20}")
    print(GACH_NHO)
    print(f"{'Thoi gian canh bao som trung binh (s)':<48}{tb_l:>16.2f}{tb_n:>20.2f}")
    print(f"{'Thoi gian canh bao som thap nhat (s)':<48}{min_l:>16.2f}{min_n:>20.2f}")
    print(f"{('So luot canh bao QUA MUON (<= 0s) / ' + str(so_luot)):<48}{tre_l:>16d}{tre_n:>20d}")
    print(f"{'So mau canh bao gia (CB + nguy hiem) o KB6':<48}{bao_dong_gia_l:>16d}{bao_dong_gia_n:>20d}")
    print(GACH_NHO, "\n")
    return {
        "tb_luat": tb_l, "min_luat": min_l, "tre_luat": tre_l,
        "tb_nguong": tb_n, "min_nguong": min_n, "tre_nguong": tre_n,
        "bao_dong_gia_luat": bao_dong_gia_l, "bao_dong_gia_nguong": bao_dong_gia_n,
    }


def in_thong_ke_suy_dien(tat_ca):
    tong_mau = sum(r["so_mau"] for r in tat_ca)
    tong_xung_dot = sum(r["so_mau_xung_dot"] for r in tat_ca)
    luat_tb = statistics.mean(r["so_luat_khop_tb"] for r in tat_ca)
    da_dung = sorted({l for r in tat_ca for l in r["cac_luat_da_dung"]})
    tung_khop = sorted({l for r in tat_ca for l in r["cac_luat_tung_khop"]})

    print("BANG 3. THONG KE HOAT DONG CUA DONG CO SUY DIEN")
    print(GACH_NHO)
    print(f"Tong so mau cam bien da xu ly        : {tong_mau}")
    print(f"So mau co nhieu luat cho ket luan khac nhau (xung dot): "
          f"{tong_xung_dot} ({100*tong_xung_dot/tong_mau:.1f}%)")
    print(f"So luat khop trung binh moi mau      : {luat_tb:.2f}")
    print(f"So luat tung khop dieu kien          : {len(tung_khop)}/{len(RULE_BASE)}")
    print(f"So luat tung THANG trong giai xung dot: {len(da_dung)}/{len(RULE_BASE)}")
    print(f"Danh sach luat tung thang            : {', '.join(da_dung)}")
    print(GACH_NHO, "\n")
    return {"tong_mau": tong_mau, "tong_xung_dot": tong_xung_dot,
            "luat_tb": luat_tb, "da_dung": da_dung, "tung_khop": tung_khop}


def main():
    in_tieu_de()

    if "--demo" in sys.argv:
        demo_giai_trinh()
        return

    print("Dang chay mo phong...\n")
    tat_ca = chay_toan_bo()

    in_bang_tong_hop(tat_ca)
    in_so_sanh_mo_hinh(tat_ca)
    in_thong_ke_suy_dien(tat_ca)

    p1 = xuat_csv_tong_hop(tat_ca)
    p2 = xuat_csv_du_lieu_tho(tat_ca)
    print(f"Da xuat: {p1}")
    print(f"Da xuat: {p2}")

    if "--no-plot" not in sys.argv:
        from visualize import ve_tat_ca
        duong_dan, _ = ve_tat_ca(tat_ca)
        for p in duong_dan:
            print(f"Da xuat: {p}")

    print("\nHoan tat.")


if __name__ == "__main__":
    main()
