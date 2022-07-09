import pytest
import numpy as np

from concreteproperties.material import Concrete, Steel
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.stress_strain_profile import (
    ConcreteLinear,
    RectangularStressBlock,
    SteelElasticPlastic,
)

import sectionproperties.pre.library.concrete_sections as sp_cs

# generate list of angles to test
thetas = np.linspace(start=-np.pi, stop=np.pi, num=31)

# define material properties
concrete = Concrete(
    name="40 MPa Concrete",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=32.8e3),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=40,
        alpha=0.85,
        gamma=0.77,
        ultimate_strain=0.003,
    ),
    alpha_squash=0.85,
    flexural_tensile_strength=0.6 * np.sqrt(40),
    colour="lightgrey",
)

steel = Steel(
    name="500 MPa Steel",
    density=7.85e-6,
    yield_strength=500,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=500,
        elastic_modulus=200e3,
        fracture_strain=0.05,
    ),
    colour="grey",
)


@pytest.mark.parametrize("theta", thetas)
def test_stress_equilibrium_rectangle(theta):
    # reference geometry
    geom = sp_cs.concrete_rectangular_section(
        b=300,
        d=900,
        dia_top=16,
        n_top=3,
        dia_bot=24,
        n_bot=3,
        n_circle=4,
        cover=30,
        area_top=200,
        area_bot=450,
        conc_mat=concrete,
        steel_mat=steel,
    )

    sec = ConcreteSection(geom.rotate_section(angle=theta, use_radians=True))
    cracked = sec.calculate_cracked_properties()

    # list of normal forces
    normal_forces = [-1e3, 0, 1e3, 1e5]
    m_star = 10e6

    for nf in normal_forces:
        # check section equilibirum for uncracked stress
        uncr_stress = sec.calculate_uncracked_stress(n=nf, mx=m_star)
        force = 0
        moment = 0

        for cf in uncr_stress.concrete_forces:
            force += cf[0]
            moment += cf[0] * cf[1]

        for sf in uncr_stress.steel_forces:
            force += sf[0]
            moment += sf[0] * sf[1]

        assert pytest.approx(force, abs=1e-8) == nf
        assert pytest.approx(moment, rel=1e-3) == m_star

        # check section equilibirum for cracked stress
        cr_stress = sec.calculate_cracked_stress(
            cracked_results=cracked, n=nf, m=m_star
        )
        force = 0
        moment = 0

        for cf in cr_stress.concrete_forces:
            force += cf[0]
            moment += cf[0] * cf[1]

        for sf in cr_stress.steel_forces:
            force += sf[0]
            moment += sf[0] * sf[1]

        assert pytest.approx(force, abs=1e-8) == nf
        assert pytest.approx(moment, rel=5e-3) == m_star

    # check section equilibirum for ultimate stress
    ultimate = sec.ultimate_bending_capacity()
    ult_stress = sec.calculate_ultimate_stress(ultimate_results=ultimate)
    force = 0
    moment = 0

    for cf in ult_stress.concrete_forces:
        force += cf[0]
        moment += cf[0] * cf[1]

    for sf in ult_stress.steel_forces:
        force += sf[0]
        moment += sf[0] * sf[1]

    assert pytest.approx(force, abs=20) == 0
    assert pytest.approx(moment, rel=1e-4) == ultimate.mv


# list of normal forces
normal_forces = [-1e3, 0, 1e3, 1e5, 1e6]


@pytest.mark.parametrize("nf", normal_forces)
def test_stress_equilibrium_circular(nf):
    # reference geometry
    geom = sp_cs.concrete_circular_section(
        d=750,
        n=64,
        dia=24,
        n_bar=12,
        n_circle=4,
        area_conc=np.pi * 750 * 750 / 4,
        area_bar=450,
        cover=50,
        conc_mat=concrete,
        steel_mat=steel,
    )

    sec = ConcreteSection(geom)
    cracked = sec.calculate_cracked_properties()
    m_star = 100e6

    # check section equilibirum for uncracked stress
    uncr_stress = sec.calculate_uncracked_stress(n=nf, mx=m_star)
    force = 0
    moment = 0

    for cf in uncr_stress.concrete_forces:
        force += cf[0]
        moment += cf[0] * cf[1]

    for sf in uncr_stress.steel_forces:
        force += sf[0]
        moment += sf[0] * sf[1]

    assert pytest.approx(force, abs=1e-8) == nf
    assert pytest.approx(moment, rel=1e-3) == m_star

    # check section equilibirum for cracked stress
    cr_stress = sec.calculate_cracked_stress(cracked_results=cracked, n=nf, m=m_star)
    force = 0
    moment = 0

    for cf in cr_stress.concrete_forces:
        force += cf[0]
        moment += cf[0] * cf[1]

    for sf in cr_stress.steel_forces:
        force += sf[0]
        moment += sf[0] * sf[1]

    assert pytest.approx(force, abs=1e-8) == nf
    assert pytest.approx(moment, rel=5e-3) == m_star

    # check section equilibirum for ultimate stress
    ultimate = sec.ultimate_bending_capacity()
    ult_stress = sec.calculate_ultimate_stress(ultimate_results=ultimate)
    force = 0
    moment = 0

    for cf in ult_stress.concrete_forces:
        force += cf[0]
        moment += cf[0] * cf[1]

    for sf in ult_stress.steel_forces:
        force += sf[0]
        moment += sf[0] * sf[1]

    # assert pytest.approx(force, abs=20) == 0
    assert pytest.approx(moment, rel=1e-4) == ultimate.mv


@pytest.mark.parametrize("theta", thetas)
def test_stress_equilibrium_tee(theta):
    # reference geometry
    geom = sp_cs.concrete_tee_section(
        b=450,
        d=1200,
        b_f=1800,
        d_f=200,
        dia_top=16,
        n_top=12,
        dia_bot=24,
        n_bot=4,
        n_circle=4,
        cover=30,
        area_top=200,
        area_bot=450,
        conc_mat=concrete,
        steel_mat=steel,
    )

    sec = ConcreteSection(geom.rotate_section(angle=theta, use_radians=True))
    cracked = sec.calculate_cracked_properties()

    # list of normal forces
    normal_forces = [-1e3, 0, 1e3, 1e5]
    m_star = 10e6

    for nf in normal_forces:
        # check section equilibirum for uncracked stress
        uncr_stress = sec.calculate_uncracked_stress(n=nf, mx=m_star)
        force = 0
        moment = 0

        for cf in uncr_stress.concrete_forces:
            force += cf[0]
            moment += cf[0] * cf[1]

        for sf in uncr_stress.steel_forces:
            force += sf[0]
            moment += sf[0] * sf[1]

        assert pytest.approx(force, abs=1e-8) == nf
        assert pytest.approx(moment, rel=1e-3) == m_star

        # check section equilibirum for cracked stress
        cr_stress = sec.calculate_cracked_stress(
            cracked_results=cracked, n=nf, m=m_star
        )
        force = 0
        moment = 0

        for cf in cr_stress.concrete_forces:
            force += cf[0]
            moment += cf[0] * cf[1]

        for sf in cr_stress.steel_forces:
            force += sf[0]
            moment += sf[0] * sf[1]

        assert pytest.approx(force, abs=1e-8) == nf
        assert pytest.approx(moment, rel=5e-3) == m_star

    # check section equilibirum for ultimate stress
    ultimate = sec.ultimate_bending_capacity()
    ult_stress = sec.calculate_ultimate_stress(ultimate_results=ultimate)
    force = 0
    moment = 0

    for cf in ult_stress.concrete_forces:
        force += cf[0]
        moment += cf[0] * cf[1]

    for sf in ult_stress.steel_forces:
        force += sf[0]
        moment += sf[0] * sf[1]

    assert pytest.approx(force, abs=20) == 0
    assert pytest.approx(moment, rel=1e-4) == ultimate.mv