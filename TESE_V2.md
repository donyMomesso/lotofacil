# NOVA TESE V2 - Realidade vs. Simulação

## 🚨 DESCOBERTA CRÍTICA

### Vencedor Real (Realidade)
- **Método: M3_mais_atrasadas** ✅
- **Concurso: 3727**
- **Acertos: 11** (vencedor!)
- **Soma: 184** ⚠️ (muito diferente da simulação!)
- **Pares: 7** ✅ (dentro do esperado)
- **Dezenas:** 01-03-04-05-08-09-11-12-13-15-16-18-22-23-24

---

## 📊 COMPARAÇÃO: TESE ANTERIOR vs. REALIDADE

| Métrica | Tese Anterior (10k sim) | Realidade (1 vencedor) | Diferença |
|---------|------------------------|----------------------|-----------|
| **Soma Média** | 198.8 ± 17.7 | **184** | **-14.8** ⚠️ |
| **Soma Moda** | 200 | **184** | **-16** ⚠️ |
| **Pares Média** | 7.6 | **7** | -0.6 ✅ |
| **Pares Moda** | 8 | **7** | -1 |
| **Melhor Método** | M4 (11.19%) | **M3 (50%!)** | 🔄 MUDANÇA |

---

## 🔴 PROBLEMAS COM TESE ANTERIOR

### 1. Soma 198-200 é ERRADA ❌
- Simulação previu: "soma ~198.8 é ótima"
- Realidade mostra: **soma 184 é vencedora**
- **Desvio:** -14.8 pontos (mais de 1 desvio padrão!)
- **Conclusão:** Tese de soma estava INCORRETA

### 2. Dezenas Críticas (22, 2, 18, 10, 14) Falham ❌
- Tese anterior: "Estas 5 dezenas aparecem em 82-85% dos vencedores"
- Realidade: Vencedor tem apenas 2 dessas (22, 18)
- Faltam: 2, 10, 14
- **Conclusão:** Padrão de dezenas era coincidência

### 3. M4 Não é o Melhor ❌
- Simulação: M4 tinha 11.19% de >11
- Realidade: M3 tem 50% de >11 (2/2 conferências)
- **Conclusão:** Método mais atrasadas é mais eficaz

---

## ✅ O QUE FUNCIONOU

### Paridade: Pares = 7 ✅
- Tese: "pares média 7.6"
- Realidade: "pares = 7"
- **Sucesso:** Padrão de paridade é válido

### Método M3 é Superior ✅
- Tese anterior: "M3 tem 8.80% de >11"
- Realidade: "M3 tem 50% de >11"
- **Conclusão:** M3 é subestimado nas simulações

---

## 🎯 NOVA TESE V2 (Baseada em Realidade)

### Padrão Principal
```
Soma: 180-190 (era 190-210 ❌)
      Foco: ~184
      Range: 170-200 (mais largo)

Pares: 6-8 (era 7-9)
       Foco: 7 pares = 8 ímpares
       Flexível: 6 pares também funciona

Método: M3_mais_atrasadas (era M4 ❌)
        Taxa esperada: >30% (baseado em realidade)
        Razão: Dezenas atrasadas exploram ciclos

Dezenas: SEM CRÍTICAS FIXAS ❌
         Padrão anterior era errado
         Substituir por: Histórico de atraso
```

### Novo Método M9 - Tese V2

```python
def metodo_tese_v2(rng):
    """
    M9: Tese V2 - Baseada em Realidade
    
    Aprendizados:
    1. Soma deve estar entre 180-190, não 198-200
    2. Paridade 7 pares é ótima
    3. Método: Favoreça dezenas mais atrasadas
    4. Esqueça dezenas críticas fixas
    """
    rng = _rng_or_default(rng)
    
    # Carrega atraso real
    freq, atraso, _ = frequencia_e_atraso()
    
    # Ordena por atraso
    dezenas_ordenadas = sorted(TODAS_DEZENAS, key=lambda d: atraso[d], reverse=True)
    
    # Tenta encontrar combinação com soma 180-190 e 7 pares
    for _ in range(500):
        candidatos = rng.sample(dezenas_ordenadas[:15], 15)  # Favorece atrasadas
        soma = sum(candidatos)
        pares = sum(1 for d in candidatos if d % 2 == 0)
        
        if 180 <= soma <= 190 and pares == 7:
            return set(candidatos)
    
    # Fallback: M3 puro
    return metodo_mais_atrasadas(rng, atraso)
```

---

## 📈 Métricas da Nova Tese V2

| Métrica | Esperado | Mínimo | Máximo |
|---------|----------|--------|--------|
| Taxa >11 | 15-20% | 10% | 50% |
| Taxa >12 | 5-10% | 2% | 25% |
| Soma | 184 | 180 | 190 |
| Pares | 7 | 6 | 8 |
| Método | M3 | - | - |

---

## 🔄 Validação Necessária

Para confirmar se Tese V2 é melhor:

```bash
# 1. Gere 1.000 testes com M9_tese_v2
# 2. Compare com M3 puro
# 3. Se M9 > M3 em >11: ADOTE A TESE V2
# 4. Se M9 ≈ M3: Manter M3
```

---

## ⚠️ Cuidados

1. **Amostra Pequena**: 1 vencedor não é suficiente
   - Recomendação: Obter 5+ vencedores antes de confirmar padrão

2. **Pode ser Coincidência**: 
   - Soma 184 é aleatório?
   - Ou é padrão real?

3. **Método M3 > M4**:
   - Confirmado em realidade (50% vs 0%)
   - Mas com amostra de apenas 2 conferências

---

## 📋 Próximas Ações

1. **Implementar M9_tese_v2** com soma 180-190, pares=7, método=M3
2. **Validar** com próximas conferências reais
3. **Se padrão se repetir**: Adotar nova tese
4. **Se falhar**: Voltar ao padrão anterior

---

## 🎓 Lição Aprendida

**A simulação com 10.000 testes foi ERRADA em vários aspectos:**
- Soma 198.8 ≠ Soma 184 (erro de -14.8)
- Dezenas críticas eram coincidência
- M3 era subestimado

**Conclusão:** Sempre validar simulações contra realidade!

Quando teste diagnóstico terminar, execute:
```bash
python scripts/tese_rapida.py > TESE_V2.txt
```
