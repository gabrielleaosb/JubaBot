# JubaBot

Bot de Discord para colecionar personagens de universos como **Marvel** e **Invencível**. Os jogadores fazem rolls para obter personagens aleatórios, acumulam poder, sobem de rank e competem no ranking do servidor.

---

## 🎲 Sistema de Rolls

A cada hora, o jogador pode fazer um roll que retorna **10 personagens aleatórios**. A raridade de cada personagem é sorteada com as seguintes probabilidades:

| Raridade | Chance | Poder Base |
|----------|--------|------------|
| ⚪ Common | 47% | 100 |
| 🟢 Uncommon | 33.75% | 150 |
| 🔵 Rare | 15% | 250 |
| 🟣 Epic | 4% | 500 |
| 🟡 Legendary | 0.25% | 10.000 |

---

## ⭐ Sistema de Estrelas

Ao obter um personagem que já está na coleção, ele recebe **+1 estrela** (máximo de 20). Cada estrela aumenta o poder do personagem em 10% do seu poder base:

```
Poder Final = power_base × (1 + estrelas × 0.1)
```

---

## 💰 Economia

Os jogadores ganham moedas por meio de três fontes:

- **`!daily`** — recompensa diária com valor baseado no rank atual do jogador
- **`!work`** — trabalho aleatório com raridade e recompensa variáveis, disponível a cada hora
- **Promoção de rank** — ao subir de rank, o jogador recebe uma recompensa automática em moedas

---

## 🏅 Ranks de Poder

O poder total do jogador é a soma do poder de todos os seus personagens (com bônus de estrelas). Com base nisso, ele é classificado em um dos seguintes ranks:

| Rank | Poder mínimo |
|------|-------------|
| 👑 Supremo | 20.000 |
| 🌌 Celestial | 15.000 |
| 🌟 Divino | 10.000 |
| 🔥 Lendário | 8.000 |
| ⚡ Mítico | 6.000 |
| 🛡️ Elite | 4.000 |
| ⚔️ Herói | 2.500 |
| 🎯 Guerreiro | 1.000 |
| 🏹 Aventureiro | 500 |
| 🐣 Iniciante | 0 |

---

## 🌐 Universos

- **Marvel** — Vingadores, X-Men, Guardiões da Galáxia, Defensores e mais
- **Invencível** — Invencível, Omni-Man, Thragg e outros personagens do universo Kirkman

---

## 📋 Comandos

| Comando | Descrição |
|--------|-----------|
| `!register` | Cria sua conta no bot |
| `!roll` | Rola 10 personagens aleatórios |
| `!daily` | Resgata sua recompensa diária |
| `!work` | Realiza um trabalho por moedas |
| `!rewards` | Vê o status das suas recompensas |
| `!profile` | Exibe seu perfil e coleção |
| `!rank` | Mostra o ranking do servidor |
| `!infopower` | Lista todos os ranks e requisitos |
| `!chars` / `!heroes` / `!villains` | Navega pelos personagens disponíveis |
