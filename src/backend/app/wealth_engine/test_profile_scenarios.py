"""Test Profile Scenarios - Demonstrates different user types"""
from adaptive_profile_manager import AdaptiveProfileManager, AdaptiveUserProfile, EmploymentStatus, LifeGoal

def run_scenarios():
    """Run different user scenarios"""
    manager = AdaptiveProfileManager()
    
    print("="*70)
    print("ADAPTIVE PROFILE MANAGER - USER SCENARIOS")
    print("="*70)
    
    # Scenario 1: Bad credit, gig economy (YOU currently)
    print("\n1️⃣  SCENARIO: Bad Credit + Gig Economy")
    print("-"*70)
    
    profile1 = manager.create_profile(
        user_id='user_gig_bad_credit',
        credit_score=520,
        monthly_income=800,
        employment_status=EmploymentStatus.GIG_ECONOMY,
        total_debt=2000,
        high_interest_debt=1500,
        current_capital=45,
        risk_tolerance='moderate',
        primary_goal=LifeGoal.DEBT_ELIMINATION
    )
    
    report1 = manager.generate_report('user_gig_bad_credit')
    print(f"Credit: {report1['credit_tier']} | Employment: {report1['employment']}")
    print(f"Capital: {report1['current_capital']} | Debt: £2,000")
    print(f"Available strategies: {report1['available_strategies']}")
    print(f"✅ Recommended rule: {report1['recommended_rule']}")
    print(f"   → Focus: Debt payoff first, build emergency fund")
    
    # Simulate improvement
    print("\n   [6 months later: Credit improves, debt paid down]")
    profile1, changes = manager.update_profile('user_gig_bad_credit', {
        'credit_score': 620,
        'total_debt': 500,
        'high_interest_debt': 0,
        'current_capital': 300
    })
    print(f"   🔄 Change detected: {changes}")
    print(f"   New rule recommendation: {manager.get_recommended_rule(profile1)}")
    
    # Scenario 2: Good credit, stable job
    print("\n2️⃣  SCENARIO: Good Credit + Stable Employment")
    print("-"*70)
    
    profile2 = manager.create_profile(
        user_id='user_stable_good',
        credit_score=720,
        monthly_income=3500,
        employment_status=EmploymentStatus.FULL_TIME_STABLE,
        total_debt=0,
        high_interest_debt=0,
        current_capital=2500,
        risk_tolerance='aggressive',
        primary_goal=LifeGoal.WEALTH_BUILDING
    )
    
    report2 = manager.generate_report('user_stable_good')
    print(f"Credit: {report2['credit_tier']} | Employment: {report2['employment']}")
    print(f"Capital: {report2['current_capital']}")
    print(f"Available strategies: {report2['available_strategies']}")
    print(f"✅ Recommended rule: {report2['recommended_rule']}")
    print(f"   → Focus: Growth, can use credit arbitrage, leverage")
    
    # Scenario 3: Student, starting out
    print("\n3️⃣  SCENARIO: Student, Just Starting")
    print("-"*70)
    
    profile3 = manager.create_profile(
        user_id='user_student',
        credit_score=0,  # No history
        monthly_income=600,
        employment_status=EmploymentStatus.STUDENT,
        total_debt=0,
        high_interest_debt=0,
        current_capital=15,
        risk_tolerance='conservative',
        primary_goal=LifeGoal.EMERGENCY_FUND
    )
    
    report3 = manager.generate_report('user_student')
    print(f"Credit: {report3['credit_tier']} | Employment: {report3['employment']}")
    print(f"Capital: {report3['current_capital']}")
    print(f"Available strategies: {report3['available_strategies']}")
    print(f"✅ Recommended rule: {report3['recommended_rule']}")
    print(f"   → Focus: Build credit, start savings habit, tiny amounts")
    
    # Scenario 4: Near retirement
    print("\n4️⃣  SCENARIO: Near Retirement (Age 60)")
    print("-"*70)
    
    profile4 = manager.create_profile(
        user_id='user_retirement',
        credit_score=780,
        monthly_income=2000,  # Pension + part-time
        employment_status=EmploymentStatus.PART_TIME_VARIABLE,
        total_debt=0,
        high_interest_debt=0,
        current_capital=8000,
        risk_tolerance='conservative',
        primary_goal=LifeGoal.RETIREMENT
    )
    
    report4 = manager.generate_report('user_retirement')
    print(f"Credit: {report4['credit_tier']} | Employment: {report4['employment']}")
    print(f"Capital: {report4['current_capital']}")
    print(f"Available strategies: {report4['available_strategies']}")
    print(f"✅ Recommended rule: {report4['recommended_rule']}")
    print(f"   → Focus: Capital preservation, income generation")
    
    # Scenario 5: Windfall recipient
    print("\n5️⃣  SCENARIO: Unexpected Windfall (£5,000)")
    print("-"*70)
    
    profile5 = manager.create_profile(
        user_id='user_windfall',
        credit_score=650,
        monthly_income=1800,
        employment_status=EmploymentStatus.FULL_TIME_NEW,
        total_debt=3000,  # Still has debt
        high_interest_debt=800,
        current_capital=5200,  # Just got windfall
        risk_tolerance='moderate',
        primary_goal=LifeGoal.WEALTH_BUILDING
    )
    
    report5 = manager.generate_report('user_windfall')
    print(f"Credit: {report5['credit_tier']} | Employment: {report5['employment']}")
    print(f"Capital: {report5['current_capital']}")
    print(f"✅ Recommended rule: {report5['recommended_rule']}")
    print(f"   ⚠️  WARNING: Has high-interest debt (£800)")
    print(f"   → Suggestion: Pay off debt first (£800), then invest remainder")
    
    # Crossed threshold
    print("\n   [Windfall crossed £5,000 threshold!]")
    print(f"   New strategies unlocked: momentum_trading, options, private_credit")
    
    # Summary table
    print("\n" + "="*70)
    print("SUMMARY: RULE RECOMMENDATIONS BY PROFILE")
    print("="*70)
    
    scenarios = [
        ('Gig + Bad Credit', 'debt_first_70_30', 'Pay debt, build safety net'),
        ('Stable + Good Credit', '10_90', 'Maximize growth'),
        ('Student', '90_10', 'Build habits, stay safe'),
        ('Near Retirement', '60_40', 'Preserve capital'),
        ('Windfall (has debt)', 'debt_first_70_30', 'Debt first, then diversify')
    ]
    
    for name, rule, focus in scenarios:
        print(f"{name:25} | {rule:20} | {focus}")
    
    print("\n" + "="*70)
    print("The system automatically adapts to:")
    print("  ✓ Credit score changes")
    print("  ✓ Employment status changes")
    print("  ✓ Capital threshold crossings")
    print("  ✓ Debt payoff milestones")
    print("  ✓ Risk tolerance updates")
    print("="*70)

if __name__ == "__main__":
    run_scenarios()
