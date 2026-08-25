from core.capacity import capacity_engine
from schemas.vision import BodyComposition, SWRCategory
from services.vision.landmarks import Landmark, calculate_shoulder_waist_ratio


def _make_landmarks(
    l_sh_x=0.3, r_sh_x=0.7,
    l_hp_x=0.4, r_hp_x=0.6,
    y_sh=0.3, y_hp=0.6,
):
    blank = Landmark(x=0.5, y=0.5, z=0.0, visibility=0.9)
    lms = [blank] * 33
    lms[11] = Landmark(x=l_sh_x, y=y_sh, z=0.0, visibility=0.9)
    lms[12] = Landmark(x=r_sh_x, y=y_sh, z=0.0, visibility=0.9)
    lms[23] = Landmark(x=l_hp_x, y=y_hp, z=0.0, visibility=0.9)
    lms[24] = Landmark(x=r_hp_x, y=y_hp, z=0.0, visibility=0.9)
    return lms


def test_swr_category_enum_values():
    assert SWRCategory.OVERFAT.value == "overfat"
    assert SWRCategory.BALANCED.value == "balanced"
    assert SWRCategory.ATHLETIC.value == "athletic"


def test_body_composition_defaults():
    bc = BodyComposition()

    assert bc.shoulder_width_px == 0.0
    assert bc.waist_width_px == 0.0
    assert bc.shoulder_waist_ratio == 1.1
    assert bc.swr_category == SWRCategory.BALANCED
    assert bc.v_taper_ratio is None
    assert bc.confidence == 0.0


def test_swr_calculation_athletic():
    lms = _make_landmarks(l_sh_x=0.2, r_sh_x=0.8, l_hp_x=0.4, r_hp_x=0.6)

    shoulder_px, waist_px, swr, category = calculate_shoulder_waist_ratio(lms, 640, 480)

    assert shoulder_px > 0
    assert waist_px > 0
    assert swr > 1.2
    assert category == SWRCategory.ATHLETIC


def test_swr_calculation_overfat():
    lms = _make_landmarks(l_sh_x=0.4, r_sh_x=0.6, l_hp_x=0.2, r_hp_x=0.8)

    _, _, swr, category = calculate_shoulder_waist_ratio(lms, 640, 480)

    assert swr < 1.0
    assert category == SWRCategory.OVERFAT


def test_swr_division_by_zero_guard():
    lms = _make_landmarks(l_hp_x=0.5, r_hp_x=0.5)

    _, waist_px, swr, category = calculate_shoulder_waist_ratio(lms, 640, 480)

    assert waist_px == 0.0
    assert swr == 1.1
    assert category == SWRCategory.BALANCED


def test_capacity_swr_adjustment():
    bc_overfat = BodyComposition(swr_category=SWRCategory.OVERFAT, is_valid_person=True)
    bc_athletic = BodyComposition(swr_category=SWRCategory.ATHLETIC, is_valid_person=True)
    bc_balanced = BodyComposition(swr_category=SWRCategory.BALANCED, is_valid_person=True)

    assert capacity_engine._swr_adjustment(bc_overfat) == -0.05
    assert capacity_engine._swr_adjustment(bc_athletic) == 0.05
    assert capacity_engine._swr_adjustment(bc_balanced) == 0.0


def test_swr_weight_multiplier():
    bc_athletic = BodyComposition(swr_category=SWRCategory.ATHLETIC)
    bc_balanced = BodyComposition(swr_category=SWRCategory.BALANCED)

    assert capacity_engine.swr_weight_multiplier(bc_athletic) == 1.1
    assert capacity_engine.swr_weight_multiplier(bc_balanced) == 1.0
    assert capacity_engine.swr_weight_multiplier(None) == 1.0
