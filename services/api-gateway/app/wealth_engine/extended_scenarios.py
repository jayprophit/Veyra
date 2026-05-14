from adaptive_profile_manager import AdaptiveProfileManager, AdaptiveUserProfile, EmploymentStatus, LifeGoal

def run_extended_scenarios():
    manager = AdaptiveProfileManager()
    scenarios = []
    
    # Business Owner
    p6 = manager.create_profile(
        user_id='business_owner',
        credit_score=700,
        monthly_income=4000,
        employment_status=EmploymentStatus.SELF_EMPLOYED,
        total_debt=5000,
        high_interest_debt=0,
        current_capital=3000,
        risk_tolerance='aggressive',
        primary_goal=LifeGoal.WEALTH_BUILDING
    )
    scenarios.append(('Business Owner', manager.get_recommended_rule(p6)))
    
    # Single Parent
    p7 = manager.create_profile(
        user_id='single_parent',
        credit_score=640,
        monthly_income=2200,
        employment_status=EmploymentStatus.PART_TIME_VARIABLE,
        total_debt=800,
        high_interest_debt=0,
        current_capital=400,
        risk_tolerance='conservative',
        primary_goal=LifeGoal.EMERGENCY_FUND
    )
    scenarios.append(('Single Parent', manager.get_recommended_rule(p7)))
    
    # High Earner
    p8 = AdaptiveUserProfile(
        user_id='high_earner',
        credit_score=780,
        monthly_income=8000,
        employment_status=EmploymentStatus.FULL_TIME_STABLE,
        total_debt=0,
        high_interest_debt=0,
        current_capital=50000,
        risk_tolerance='aggressive',
        primary_goal=LifeGoal.WEALTH_BUILDING
    )
    manager.profiles['high_earner'] = p8
    scenarios.append(('High Earner', manager.get_recommended_rule(p8)))
    
    print('='*50)
    print('EXTENDED SCENARIOS')
    print('='*50)
    for name, rule in scenarios:
        print(f'{name:20} | {rule}')

if __name__ == '__main__':
    run_extended_scenarios()