# Aplicação da Tese aos Métodos de Geração

## 📊 Resumo da Tese Extraída

Baseado em 10.000 simulações (5.000 por sorteio × 2 draws):
- **Total de vencedores (>11 acertos): 767**
- **Taxa de sucesso: 0.959%**
- **Melhor método: M4_par_impar_balanceado (11.19% de taxa de >11)**

### Padrões Identificados

#### 1. Dezenas Críticas (maior frequência em vencedores)
```
22 (652×) → 85.1% dos vencedores
2  (651×) → 84.9% dos vencedores
18 (650×) → 84.7% dos vencedores
10 (645×) → 84.1% dos vencedores
14 (635×) → 82.8% dos vencedores
```

#### 2. Padrão de Soma
- **Média: 198.8** (±17.7)
- **Moda: 200** (mais frequente)
- **Range: 143-253** (esperado: 120-325)
- **Distribuição: concentrada em 190-210**

#### 3. Padrão de Paridade (pares vs. ímpares)
- **Média de pares: 7.6**
- **Moda: 8 pares** (7 ímpares)
- **Distribuição: 6-10 pares é comum**

---

## 🎯 Estratégias de Aplicação

### OPÇÃO 1: Criar Novo Método M9 - "Tese Direta"

Um método que **forçadamente inclui** as dezenas críticas e respeita os padrões:

```python
def metodo_tese_direta(rng):
    """
    M9: Tese Direta
    - Sempre inclui as 5 dezenas críticas: {22, 2, 18, 10, 14}
    - Completa com 10 dezenas aleatórias
    - Busca soma próxima a 198-200
    - Alvo: 7-8 pares
    """
    rng = _rng_or_default(rng)
    dezenas_criticas = {22, 2, 18, 10, 14}  # soma = 66
    
    # Precisa de 10 mais, com soma buscando ~132-134 para chegar a ~198-200
    for _ in range(500):
        candidato_adicional = rng.sample([d for d in TODAS_DEZENAS if d not in dezenas_criticas], 10)
        soma = sum(dezenas_criticas) + sum(candidato_adicional)
        pares = sum(1 for d in candidato_adicional if d % 2 == 0) + sum(1 for d in dezenas_criticas if d % 2 == 0)
        
        if 190 <= soma <= 210 and 7 <= pares <= 9:
            return dezenas_criticas | set(candidato_adicional)
    
    # Fallback: relaxa soma
    return dezenas_criticas | set(rng.sample([d for d in TODAS_DEZENAS if d not in dezenas_criticas], 10))
```

**Características:**
- ✅ Aproveita as 5 dezenas mais frequentes em vencedores
- ✅ Força o padrão de soma 198-200
- ✅ Controla paridade
- ⚠️ Reduz diversidade (sempre mesmas 5 dezenas)

---

### OPÇÃO 2: Ajustar Constantes dos Métodos Existentes

Com base na tese, refinar os ranges dos métodos M5 e M6:

**Método M5 (Soma Faixa Comum) - AJUSTAR:**
```python
# ANTES:
SOMA_AVANCADA_MIN = 185
SOMA_AVANCADA_MAX = 215

# DEPOIS (mais preciso baseado na tese):
SOMA_TESE_MIN = 190        # reduz de 185 para 190
SOMA_TESE_MAX = 210        # reduz de 215 para 210 (foco em 198-200)
```

**Método M4 (Par/Ímpar Balanceado) - AJUSTAR:**
```python
# ANTES: alvo de 8 pares
# DEPOIS: testar alvo de 7-8 pares (média 7.6)
def metodo_par_impar_balanceado_tese(rng, alvo_pares=8, max_tentativas=500):
    """Tenta 8, se falhar tenta 7"""
    for alvo in [8, 7]:
        for _ in range(max_tentativas):
            candidato = rng.sample(TODAS_DEZENAS, 15)
            pares = sum(1 for d in candidato if d % 2 == 0)
            if pares == alvo:
                return set(candidato)
    return metodo_aleatorio_puro(rng)
```

---

### OPÇÃO 3: Incorporar Dezenas Críticas como Preferência

Ajustar os métodos de **frequência** para **preferir** as dezenas críticas:

```python
def metodo_tese_frequentes(rng, freq):
    """
    M2 melhorado: 
    - Prioriza as 5 dezenas críticas da tese
    - Depois as mais frequentes gerais
    """
    dezenas_criticas = {22, 2, 18, 10, 14}
    outras_dezenas = [d for d in TODAS_DEZENAS if d not in dezenas_criticas]
    
    # Ordena outras por frequência
    outras_dezenas.sort(key=lambda d: freq[d], reverse=True)
    
    # Toma as 5 críticas + 10 mais frequentes
    return dezenas_criticas | set(outras_dezenas[:10])
```

---

### OPÇÃO 4: Método Híbrido "Tese + Frequência"

Combina a tese com dados estatísticos reais:

```python
def metodo_tese_hibrido(rng, freq, atraso):
    """
    M10: Tese Híbrida
    - 5 dezenas críticas (obrigatório)
    - 5 mais frequentes (fora das críticas)
    - 5 mais atrasadas (fora das críticas)
    - Busca soma 198-200 via ajustes
    """
    dezenas_criticas = {22, 2, 18, 10, 14}
    
    # Mais frequentes (excluindo críticas)
    freq_outras = sorted(
        [d for d in TODAS_DEZENAS if d not in dezenas_criticas],
        key=lambda d: freq[d],
        reverse=True
    )[:5]
    
    # Mais atrasadas (excluindo críticas e frequentes)
    atraso_outras = sorted(
        [d for d in TODAS_DEZENAS if d not in (dezenas_criticas | set(freq_outras))],
        key=lambda d: atraso[d],
        reverse=True
    )[:5]
    
    return dezenas_criticas | set(freq_outras) | set(atraso_outras)
```

---

## 🔧 Implementação Recomendada

### Passo 1: Adicionar M9 ao `lotofacil_lib.py`

```python
METODOS = [
    "M1_aleatorio_puro",
    "M2_mais_frequentes",
    "M3_mais_atrasadas",
    "M4_par_impar_balanceado",
    "M5_soma_faixa_comum",
    "M6_filtros_combinados",
    "M7_cobertura_pares",
    "M8_repeticao_controlada",
    "M9_tese_direta",  # NOVO
]

# Na função gerar_todos_metodos():
return {
    ...existing methods...,
    "M9_tese_direta": metodo_tese_direta(rng),
}
```

### Passo 2: Ajustar Constantes

Refinar `SOMA_AVANCADA_MIN/MAX` e `PARES_AVANCADO_MIN/MAX` para:
```python
SOMA_AVANCADA_MIN = 190  # era 185
SOMA_AVANCADA_MAX = 210  # era 215
PARES_AVANCADO_MIN = 7   # era 7 (mantém)
PARES_AVANCADO_MAX = 9   # era 9 (mantém)
```

### Passo 3: Criar Script de Validação

```bash
python scripts/validar_tese.py
```

Testa os novos métodos contra:
- Histórico de 3.727 concursos
- Simula 1.000 testes por método
- Compara resultados com M4

### Passo 4: Integrar ao Painel

- Adicionar M9 ao `painel_jogos_v2.html`
- Mostrar taxa de sucesso vs. M4
- Destacar dezenas críticas em diferentes cores

---

## 📈 Métricas de Sucesso

| Métrica | M4 Atual | M9 Esperado | Meta |
|---------|----------|-------------|------|
| Taxa >11 | 11.19% | ≥12% | +5% |
| Taxa >12 | 2.2% | ≥2.5% | +10% |
| Taxa >13 | 0.1% | ≥0.2% | +50% |
| Média acertos | 9.042 | ≥9.2 | +2% |

---

## ⚠️ Limitações da Tese

1. **Pequena amostra de vencedores**: 767 em 10.000 (0.959%)
   - Pode não ser representativo
   - Requer validação com mais histórico

2. **Dezenas críticas podem ser coincidência**
   - Com distribuição uniforme, esperado ~750-800 vencedores
   - A frequência das 5 dezenas pode ser ruído aleatório

3. **Padrão de soma**
   - Distribuição normal esperada, nada excepcional
   - Não há vantagem estatística clara

4. **Sem causalidade**
   - Padrões observados no passado ≠ padrões futuros
   - Loteria é aleatória independente

---

## ✅ Próximas Etapas

- [ ] Implementar M9 no código
- [ ] Validar contra histórico completo
- [ ] Testar com 20.000 simulações adicionais
- [ ] Comparar M9 vs. M4 em últimos 100 concursos
- [ ] Se M9 > M4 em 2+ métricas, integrar ao painel
- [ ] Documentar limites e advertências ao usuário
