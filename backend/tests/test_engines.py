import pytest
from app.services.engines import ProblemIdentityEngine, ResurrectionEngine, InterventionMemoryEngine, ContradictionEngine, EvolutionEngine, EmergingEngine, DecisionDebtEngine, StaleMemoryEngine

def test_engine_exports():
    assert all(cls for cls in [ProblemIdentityEngine,ResurrectionEngine,InterventionMemoryEngine,ContradictionEngine,EvolutionEngine,EmergingEngine,DecisionDebtEngine,StaleMemoryEngine])

def test_identity_dna_is_structured():
    from app.services.engines import dna
    result=dna('Checkout keeps freezing on Android',platform='mobile',segment='Android users')
    assert result['product_area']=='checkout'
    assert result['platform']=='mobile'
    assert result['failure_mode']=='performance/reliability'
