from app.main import app

def test_required_routes_exist():
    routes={getattr(r,'path','') for r in app.routes}
    required={
        '/api/v1/health','/api/v1/dashboard/overview','/api/v1/feedback','/api/v1/feedback/{feedback_id}','/api/v1/analyze','/api/v1/problems','/api/v1/problems/{problem_id}','/api/v1/problems/{problem_id}/timeline','/api/v1/problems/{problem_id}/evolution','/api/v1/problems/{problem_id}/evidence','/api/v1/problems/{problem_id}/memory','/api/v1/interventions','/api/v1/interventions/check','/api/v1/outcomes','/api/v1/problems/resurrected','/api/v1/problems/emerging','/api/v1/contradictions','/api/v1/replay','/api/v1/evaluation/run','/api/v1/evaluation/results','/api/v1/demo/reset','/api/v1/demo/seed','/api/v1/memory/retain','/api/v1/memory/recall','/api/v1/memory/reflect'}
    assert required <= routes
