CATEGORIES={
 'recurring':'Repeated observations of a known problem',
 'successful_intervention':'A measured intervention with successful outcome',
 'failed_intervention':'A measured intervention with failure or no measurable change',
 'partial_intervention':'An intervention that helps one segment/platform but not another',
 'resurrection':'A previously quieter problem returns after intervention',
 'false_similarity':'Semantically similar feedback with different failure modes',
 'contradiction':'Historical conclusion conflicts with current evidence',
 'evolution':'A problem changes failure mode, platform or user goal over time',
 'unrelated':'Feedback that should remain separate from a tempting match',
 'new_problem':'A problem with no historical match',
}
SCENARIOS={}
TEMPLATES={
 'recurring':('Known checkout issue appears again on the same platform.','SAME_PROBLEM'),
 'successful_intervention':('Historical intervention produced the expected improvement.','SUCCESS'),
 'failed_intervention':('A previously attempted fix produced no measurable improvement.','FAILURE_OR_NO_CHANGE'),
 'partial_intervention':('An intervention improved one segment but not another.','PARTIAL_SUCCESS'),
 'resurrection':('A previously quieter problem returns after an intervention.','RESURRECTED_PROBLEM'),
 'false_similarity':('Feedback shares vocabulary with an existing problem but has a different failure mode.','SEPARATE_PROBLEM'),
 'contradiction':('Historical evidence suggested resolution but current evidence conflicts.','CONTRADICTION'),
 'evolution':('The problem changes failure mode, platform or user goal over time.','EVOLVED_PROBLEM'),
 'unrelated':('Feedback looks superficially similar but belongs to a different product area.','UNRELATED'),
 'new_problem':('Feedback has no supported historical match.','NEW_PROBLEM'),
}
for category,description in CATEGORIES.items():
    template,expected=TEMPLATES[category]
    for i in range(1,11):
        sid=f'{category}_{i:02d}'
        SCENARIOS[sid]={
            'category':category,
            'description':description,
            'input':f'Synthetic evaluation case {i}: {template}',
            'expected_behavior':{
                'classification':expected,
                'resurrection':category=='resurrection',
                'contradiction':category=='contradiction',
                'separate_match':category in {'false_similarity','unrelated'},
                'new_problem':category=='new_problem',
            },
            'data_source':'synthetic_evaluation',
        }
SCENARIOS['mobile_checkout_resurrection']={
    'category':'hero',
    'description':'Mobile checkout intervention followed by renewed Android complaints.',
    'input':'Checkout still fails on Android after the mobile navigation redesign.',
    'expected_behavior':{
        'classification':'RESURRECTED_PROBLEM','resurrection':True,'contradiction':True,
        'partial_outcome':True,'evidence':True,'historical_intervention':True,'memory_difference':True,
    },
    'data_source':'synthetic_demo',
}
