from dataclasses import dataclass
from typing import Callable, Dict, Any, List

from config import (
    LEVEL_SAFE, LEVEL_WARNING, LEVEL_DANGER,
    TTC_DANGER, TTC_WARNING, DR_DANGER, DR_WARNING,
    ABSOLUTE_MIN_DISTANCE, NEGLIGIBLE_SPEED_KMH,
)


@dataclass
class Rule:
    id: str
    nhom: str
    dieu_kien: Callable[[Dict[str, Any]], bool]
    ket_luan: str
    uu_tien: int
    do_tin_cay: float
    giai_thich: str

    def kiem_tra(self, facts: Dict[str, Any]) -> bool:
        try:
            return bool(self.dieu_kien(facts))
        except (KeyError, TypeError, ZeroDivisionError):
            return False

    def dien_giai(self, facts: Dict[str, Any]) -> str:
        """Thay cac bien trong cau giai thich bang gia tri thuc te."""
        try:
            return self.giai_thich.format(**facts)
        except (KeyError, IndexError, ValueError):
            return self.giai_thich

RULE_BASE: List[Rule] = [

    Rule(
        id="R01", nhom="Loc tinh huong",
        dieu_kien=lambda f: not f["cam_bien_hoat_dong"],
        ket_luan=LEVEL_WARNING, uu_tien=100, do_tin_cay=0.50,
        giai_thich="Cam bien mat tin hieu tai thoi diem {t:.2f}s. "
                   "He thong khong du du lieu de ket luan, phat canh bao muc trung gian de an toan.",
    ),
    Rule(
        id="R02", nhom="Loc tinh huong",
        dieu_kien=lambda f: f["khoang_cach"] > f["tam_do_toi_da"],
        ket_luan=LEVEL_SAFE, uu_tien=95, do_tin_cay=0.95,
        giai_thich="Khong phat hien vat the trong tam do radar ({tam_do_toi_da:.0f} m). "
                   "Phia truoc trong, khong canh bao.",
    ),
    Rule(
        id="R03", nhom="Loc tinh huong",
        dieu_kien=lambda f: f["toc_do_xe_kmh"] < NEGLIGIBLE_SPEED_KMH
                            and f["khoang_cach"] >= ABSOLUTE_MIN_DISTANCE,
        ket_luan=LEVEL_SAFE, uu_tien=90, do_tin_cay=0.90,
        giai_thich="Toc do xe chi {toc_do_xe_kmh:.1f} km/h (duoi nguong {nguong_toc_do_bo_qua:.0f} km/h), "
                   "xe gan nhu dung yen nen bo qua canh bao.",
    ),

    Rule(
        id="R04", nhom="Khoang cach tuyet doi",
        dieu_kien=lambda f: f["khoang_cach"] < ABSOLUTE_MIN_DISTANCE,
        ket_luan=LEVEL_DANGER, uu_tien=88, do_tin_cay=1.00,
        giai_thich="Khoang cach {khoang_cach:.2f} m nho hon nguong vat ly toi thieu "
                   "{nguong_toi_thieu:.1f} m. Nguy hiem bat ke toc do.",
    ),

    Rule(
        id="R05", nhom="Ket hop toc do - khoang cach",
        dieu_kien=lambda f: f["dang_tiep_can"] and f["ttc"] <= TTC_DANGER,
        ket_luan=LEVEL_DANGER, uu_tien=80, do_tin_cay=0.98,
        giai_thich="TTC = {ttc:.2f}s <= nguong nguy hiem {nguong_ttc_nguy_hiem:.1f}s "
                   "(khoang cach {khoang_cach:.1f} m, toc do tuong doi {toc_do_tuong_doi_kmh:.1f} km/h).",
    ),
    Rule(
        id="R06", nhom="Ket hop toc do - khoang cach",
        dieu_kien=lambda f: f["ty_le_khoang_cach"] < DR_DANGER,
        ket_luan=LEVEL_DANGER, uu_tien=78, do_tin_cay=0.95,
        giai_thich="Khoang cach thuc te chi dat {ty_le_phan_tram:.0f}% khoang cach an toan toi thieu "
                   "({khoang_cach:.1f} m so voi {khoang_cach_an_toan:.1f} m can co).",
    ),
    Rule(
        id="R07", nhom="Ket hop toc do - khoang cach",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["ttc"] <= TTC_WARNING
                            and f["ty_le_khoang_cach"] < DR_WARNING,
        ket_luan=LEVEL_DANGER, uu_tien=76, do_tin_cay=0.90,
        giai_thich="Dong thoi vi pham ca hai tieu chi: TTC = {ttc:.2f}s va khoang cach chi dat "
                   "{ty_le_phan_tram:.0f}% muc an toan. Hai yeu to cong huong nen nang len muc nguy hiem.",
    ),
    Rule(
        id="R08", nhom="Ket hop toc do - khoang cach",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and TTC_DANGER < f["ttc"] <= TTC_WARNING,
        ket_luan=LEVEL_WARNING, uu_tien=60, do_tin_cay=0.92,
        giai_thich="TTC = {ttc:.2f}s nam trong khoang canh bao "
                   "({nguong_ttc_nguy_hiem:.1f}s - {nguong_ttc_canh_bao:.1f}s).",
    ),
    Rule(
        id="R09", nhom="Ket hop toc do - khoang cach",
        dieu_kien=lambda f: DR_DANGER <= f["ty_le_khoang_cach"] < DR_WARNING,
        ket_luan=LEVEL_WARNING, uu_tien=58, do_tin_cay=0.88,
        giai_thich="Khoang cach {khoang_cach:.1f} m thap hon khoang cach an toan "
                   "{khoang_cach_an_toan:.1f} m nhung chua duoi nguong nguy hiem.",
    ),

    Rule(
        id="R10", nhom="Dieu kien moi truong",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["he_so_bam_duong"] <= 0.45
                            and f["ttc"] <= TTC_DANGER * 1.5,
        ket_luan=LEVEL_DANGER, uu_tien=74, do_tin_cay=0.93,
        giai_thich="Mat duong {tinh_trang_duong} (he so bam {he_so_bam_duong:.2f}) lam quang duong phanh "
                   "tang manh; voi TTC = {ttc:.2f}s he thong nang som len muc nguy hiem.",
    ),
    Rule(
        id="R11", nhom="Dieu kien moi truong",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["he_so_bam_duong"] <= 0.60
                            and f["ttc"] <= TTC_WARNING * 1.3,
        ket_luan=LEVEL_WARNING, uu_tien=56, do_tin_cay=0.85,
        giai_thich="Duong {tinh_trang_duong} nen mo rong vung canh bao: TTC = {ttc:.2f}s da du de canh bao som.",
    ),
    Rule(
        id="R12", nhom="Dieu kien moi truong",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["thoi_gian_phan_ung"] >= 1.8
                            and f["ttc"] <= TTC_WARNING * 1.2,
        ket_luan=LEVEL_WARNING, uu_tien=55, do_tin_cay=0.82,
        giai_thich="Tai xe o trang thai '{trang_thai_tai_xe}' (thoi gian phan ung {thoi_gian_phan_ung:.1f}s) "
                   "nen he thong canh bao som hon binh thuong.",
    ),
    Rule(
        id="R13", nhom="Dieu kien moi truong",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["thoi_gian_phan_ung"] >= 2.5
                            and f["ttc"] <= TTC_DANGER * 1.6,
        ket_luan=LEVEL_DANGER, uu_tien=72, do_tin_cay=0.90,
        giai_thich="Tai xe mat tap trung (phan ung {thoi_gian_phan_ung:.1f}s) trong khi TTC chi con "
                   "{ttc:.2f}s: khong con du thoi gian phan ung thu cong.",
    ),

    Rule(
        id="R14", nhom="Loai vat the",
        dieu_kien=lambda f: f["loai_vat_the"] == "vat_can_tinh"
                            and f["dang_tiep_can"]
                            and f["ttc"] <= TTC_WARNING * 1.2,
        ket_luan=LEVEL_DANGER, uu_tien=70, do_tin_cay=0.90,
        giai_thich="Vat can dung yen phia truoc (TTC = {ttc:.2f}s): vat the khong tu di chuyen "
                   "nen toan bo viec tranh va cham phu thuoc xe chu.",
    ),
    Rule(
        id="R15", nhom="Loai vat the",
        dieu_kien=lambda f: f["loai_vat_the"] == "nguoi_di_bo"
                            and f["dang_tiep_can"]
                            and f["ttc"] <= TTC_WARNING * 1.5,
        ket_luan=LEVEL_DANGER, uu_tien=71, do_tin_cay=0.92,
        giai_thich="Phat hien nguoi di bo trong quy dao voi TTC = {ttc:.2f}s. "
                   "Doi tuong de bi ton thuong nen ap dung nguong nghiem ngat nhat.",
    ),
    Rule(
        id="R16", nhom="Loai vat the",
        dieu_kien=lambda f: f["loai_vat_the"] == "xe_cat_ngang"
                            and f["dang_tiep_can"]
                            and f["ttc"] <= TTC_WARNING,
        ket_luan=LEVEL_DANGER, uu_tien=69, do_tin_cay=0.88,
        giai_thich="Xe cat ngang dau xe voi TTC = {ttc:.2f}s, quy dao giao nhau nen khong the tranh bang danh lai.",
    ),
    Rule(
        id="R17", nhom="Xu huong",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["gia_toc_tuong_doi"] > 1.5
                            and f["ttc"] <= TTC_WARNING,
        ket_luan=LEVEL_DANGER, uu_tien=68, do_tin_cay=0.87,
        giai_thich="Toc do tiep can dang tang nhanh ({gia_toc_tuong_doi:.2f} m/s^2) - "
                   "xe truoc phanh gap. TTC {ttc:.2f}s se rut ngan rat nhanh.",
    ),
    Rule(
        id="R18", nhom="Xu huong",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["gia_toc_tuong_doi"] > 0.5
                            and f["ttc"] <= TTC_WARNING * 1.6,
        ket_luan=LEVEL_WARNING, uu_tien=54, do_tin_cay=0.80,
        giai_thich="Khoang cach dang thu hep dan ({gia_toc_tuong_doi:.2f} m/s^2), can theo doi.",
    ),
    Rule(
        id="R19", nhom="Xu huong",
        dieu_kien=lambda f: not f["dang_tiep_can"] and f["ty_le_khoang_cach"] >= DR_WARNING,
        ket_luan=LEVEL_SAFE, uu_tien=40, do_tin_cay=0.90,
        giai_thich="Xe phia truoc dang chay nhanh hon hoac bang xe chu, khoang cach khong thu hep.",
    ),

    Rule(
        id="R20", nhom="Mac dinh",
        dieu_kien=lambda f: f["dang_tiep_can"] and f["ttc"] > TTC_WARNING
                            and f["ty_le_khoang_cach"] >= DR_WARNING,
        ket_luan=LEVEL_SAFE, uu_tien=20, do_tin_cay=0.95,
        giai_thich="TTC = {ttc:.2f}s va khoang cach dat {ty_le_phan_tram:.0f}% muc an toan, "
                   "ca hai tieu chi deu vuot nguong an toan.",
    ),
    Rule(
        id="R21", nhom="Mac dinh",
        dieu_kien=lambda f: True,
        ket_luan=LEVEL_SAFE, uu_tien=1, do_tin_cay=0.70,
        giai_thich="Khong luat canh bao nao duoc kich hoat, mac dinh ket luan an toan.",
    ),
    Rule(
        id="R22", nhom="Mac dinh",
        dieu_kien=lambda f: f["dang_tiep_can"]
                            and f["ttc"] <= TTC_DANGER * 0.6,
        ket_luan=LEVEL_DANGER, uu_tien=85, do_tin_cay=1.00,
        giai_thich="TTC chi con {ttc:.2f}s - va cham gan nhu chac chan neu khong can thiep ngay lap tuc.",
    ),
]


def thong_ke_co_so_luat() -> Dict[str, int]:
    """Thong ke so luat theo nhom va theo ket luan."""
    tk = {"tong_so_luat": len(RULE_BASE)}
    for r in RULE_BASE:
        tk["nhom_" + r.nhom.replace(" ", "_")] = tk.get("nhom_" + r.nhom.replace(" ", "_"), 0) + 1
        tk["ket_luan_" + r.ket_luan.replace(" ", "_")] = tk.get("ket_luan_" + r.ket_luan.replace(" ", "_"), 0) + 1
    return tk
