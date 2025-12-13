Fluxo de dados e validação

Centralização
- Todo acesso a `dados/familias.json` e `dados/sorteio.json` é feito via `DataManager`.
- Arquivos legados (`src/utils.py`, `src/utils_familias.py`, `src/resetar.py`) continuam existindo, mas apenas encaminham chamadas para `DataManager` mantendo a mesma interface.

Validação automática
- Na inicialização (`main.py`), o sistema executa validações com `DataManager.executar_validacao_inicial()`.
- Estrutura dos dados é verificada e corrigida quando possível:
  - Campos obrigatórios: `nome` (não vazio), `numero` (inteiro).
  - `foto`: caminho relativo em `imagens/familias/...` com extensão `.png`, `.jpg` ou `.jpeg`.
  - `sorteado`: booleano.
  - `data_sorteio`: formato `dd/mm/aaaa` quando presente.
- Registros inválidos são removidos ou ajustados; logs detalham cada ocorrência.
- Em caso de erro de leitura, um backup (`familias.json.bak`) é gerado e o sistema usa lista vazia como fallback.
- `sorteio.json` é validado e removido se inválido.

Fallback
- Dados inválidos disparam logs e são corrigidos; quando não corrigíveis, são descartados para garantir consistência.
- Arquivo de sorteio inválido é apagado e o cache é limpo.

Retrocompatibilidade
- As funções `carregar_familias`, `salvar_familias`, `contar_familias`, `resetar_sorteio` continuam acessíveis pelos módulos legados, mas a implementação é do `DataManager`.

Logs
- As validações registram mensagens de `info`, `warning` e `error` via `logging`.

Desempenho
- As validações são leves, usam apenas operações de leitura/escrita em JSON e não aumentam o tempo de inicialização significativamente.
