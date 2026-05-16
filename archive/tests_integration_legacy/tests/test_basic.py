"""Basic tests for Veyra."""
import pytest


def test_imports():
    """Test that all modules can be imported."""
    from src.backend.app.wealth_engine.escalation_sim import EscalationSim
    from src.backend.app.wealth_engine.report_exporter import ReportExporter
    
    sim = EscalationSim()
    exporter = ReportExporter()
    assert sim is not None
    assert exporter is not None


def test_escalation_sim():
    """Test wealth escalation simulation."""
    
    sim = EscalationSim()
    result = sim.simulate(20, 100, 5)
    
    assert result is not None
    assert "final" in result
    assert "contributed" in result
    assert "gain" in result
    assert "milestones" in result
    assert result["final"] > 0
    assert result["contributed"] > 0


def test_report_exporter():
    """Test report export functionality."""
    
    exporter = ReportExporter()
    sim = EscalationSim()
    result = sim.simulate(20, 100, 5)
    
    # Test summary generation
    summary = exporter.generate_summary(result)
    assert summary is not None
    assert "Final:" in summary
    
    # Test CSV export
    test_data = [{"month": i, "value": i * 100} for i in range(3)]
    csv_file = exporter.to_csv(test_data, "test.csv")
    assert csv_file == "test.csv"
    
    # Test JSON export
    json_file = exporter.to_json(result, "test.json")
    assert json_file == "test.json"