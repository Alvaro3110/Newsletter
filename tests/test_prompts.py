import os
import pytest
from src.core.validator import validate_essay_seniority

def test_validate_essay_seniority_valid():
    # Long text to satisfy word count (> 1000 words)
    long_text = """# Título Técnico Otimizado
    
    A concorrência em sistemas de banco de dados distribuídos é um desafio de 99.9%. 
    Nesta análise, exploramos as limitações de concorrência e escalabilidade.
    
    ## Seção de Trade-offs
    
    | Prós | Contras | Decisão Técnica |
    | :--- | :--- | :--- |
    | Alta taxa de transferência local (10ms) | Sem replicação distribuída nativa | SQLiteSaver para threads isoladas |
    
    > Staff Insight:
    > Bancos locais reduzem a latência significativamente.
    
    Consulte a documentação técnica oficial: https://www.sqlite.org/threadsafe.html.
    
    """ + " detalhe técnico adicional sobre arquitetura de software" * 150
    
    errors = validate_essay_seniority(long_text)
    assert len(errors) == 0

def test_validate_essay_seniority_invalid_word_count():
    short_text = "# Título curto\nTexto de apenas 10 palavras. Latência 10ms. https://docs.org. | Prós | Contras | Decisão Técnica |"
    errors = validate_essay_seniority(short_text)
    assert any("Word count" in e for e in errors)

def test_validate_essay_seniority_invalid_fluff():
    long_text = """# Título Técnico Otimizado
    
    A concorrência em sistemas de banco de dados distribuídos é um desafio incrível e revolucionário. 
    Nesta análise, exploramos as limitações de concorrência e escalabilidade.
    
    ## Seção de Trade-offs
    
    | Prós | Contras | Decisão Técnica |
    | :--- | :--- | :--- |
    | Alta taxa de transferência local (10ms) | Sem replicação distribuída nativa | SQLiteSaver para threads isoladas |
    
    > Staff Insight:
    > Bancos locais reduzem a latência significativamente.
    
    Consulte a documentação técnica oficial: https://www.sqlite.org/threadsafe.html.
    
    """ + " detalhe técnico adicional sobre arquitetura de software" * 150
    
    errors = validate_essay_seniority(long_text)
    assert any("fluff" in e.lower() for e in errors)

def test_validate_essay_seniority_missing_metrics():
    long_text = """# Título Técnico Otimizado
    
    A concorrência em sistemas de banco de dados distribuídos é um desafio. 
    Nesta análise, exploramos as limitações de concorrência e escalabilidade.
    
    ## Seção de Trade-offs
    
    | Prós | Contras | Decisão Técnica |
    | :--- | :--- | :--- |
    | Alta taxa de transferência local | Sem replicação distribuída nativa | SQLiteSaver para threads isoladas |
    
    > Staff Insight:
    > Bancos locais reduzem a latência significativamente.
    
    Consulte a documentação técnica oficial: https://www.sqlite.org/threadsafe.html.
    
    """ + " detalhe técnico adicional sobre arquitetura de software" * 150
    
    # We removed all numbers/metrics
    long_text = "".join([c for c in long_text if not c.isdigit()])
    
    errors = validate_essay_seniority(long_text)
    assert any("metrics" in e for e in errors)

def test_prompt_files_exist_and_conform():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompts_dir = os.path.join(base_dir, "src", "prompts")
    assert os.path.exists(os.path.join(prompts_dir, "research_expert.prompt"))
    assert os.path.exists(os.path.join(prompts_dir, "pragmatic_writer.prompt"))
    assert os.path.exists(os.path.join(prompts_dir, "technical_reviewer.prompt"))
    
    with open(os.path.join(prompts_dir, "pragmatic_writer.prompt"), "r") as f:
        content = f.read()
    assert "Gergely Orosz" in content
    assert "trade-off" in content.lower()
