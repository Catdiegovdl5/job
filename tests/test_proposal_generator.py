import sys
import os

# Add src to sys.path in a portable way
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proposal_generator import generate_proposal

def test_freelancer_proposal():
    desc = "Need a video for my website"
    proposal = generate_proposal("freelancer", desc)
    assert "### Proposal for Freelancer.com" in proposal
    assert "Pipeline Veo 3" in proposal
    assert "Test Keywords" in proposal
    assert "Language: English" in proposal

def test_99freelas_proposal():
    desc = "Preciso de tráfego pago"
    proposal = generate_proposal("99freelas", desc)
    assert "### Proposta para 99Freelas" in proposal
    assert "Projeto Piloto" in proposal
    assert "Idioma: Português" in proposal

def test_upwork_proposal():
    desc = "Looking for an SEO expert"
    questions = ["How do you handle SEO?"]
    proposal = generate_proposal("upwork", desc, questions)
    assert "### Proposal for Upwork" in proposal
    assert "Screening Questions" in proposal
    assert "GEO (Generative Engine Optimization)" in proposal

def test_invalid_platform():
    proposal = generate_proposal("invalid", "test")
    assert "Error: Unsupported platform" in proposal
