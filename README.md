# README - Sistema Família no Altar

## Visão Geral para Todos os Públicos

Família no Altar é uma solução desktop offline, criada para organizar e conduzir o sorteio semanal de famílias da igreja. Com uma interface simples e objetiva, o sistema permite cadastrar, editar e gerenciar famílias, realizar sorteios e manter o histórico de participação, trazendo agilidade e confiança ao processo.

### Principais Recursos
- Cadastro, edição e exclusão de famílias
- Sorteio com validações e marcação automática de status
- Busca e filtros por status, com indicadores visuais
- Visualização da última família sorteada
- Modal de foto em tela cheia para conferência
- Reset do ciclo quando todas as famílias forem sorteadas

## Detalhes Técnicos para Desenvolvedores

### Arquitetura do Sistema
- Frontend: PySide6 (Qt para Python) com componentes customizados
- Backend: Python (aplicativo desktop offline)
- Banco de Dados: arquivos JSON (`dados/familias.json` e `dados/sorteio.json`)

### Padrões e Práticas
- Estrutura modular centralizada em `DataManager` (persistência, validação e reset)
- Escrita atômica de JSON para evitar corrupção
- Logs de auditoria para operações sensíveis (alteração de status, persistência)
- Testes automatizados com `unittest` em `tests/`

### Como Executar
1. Instale Python 3.10+ no Windows
2. Crie e ative um ambiente virtual (opcional):
   - `python -m venv venv`
   - `venv\Scripts\activate`
3. Instale dependências (se necessário):
   - `pip install PySide6`
   - `pip install pywin32` (para criação de atalho no Windows)
4. Execute o sistema:
   - `python main.py`

## Métricas de Qualidade
- Cobertura de testes: validações novas cobertas em `tests/test_data_validation.py`
- Tempo de inicialização: leve; validações rodam em milissegundos em PC comum
- Operação offline: 100%

## Documentação
- Fluxo de dados e validação: `docs/fluxo_dados.md`
- Otimizações de desempenho: `docs/performance.md`
- UI e fluxo do painel: `docs/ui_flow.md`

## Contato
Para dúvidas ou sugestões, abra uma issue no repositório ou entre em contato com a equipe responsável localmente na igreja.

---

Pronto para começar? Consulte a documentação acima e execute `python main.py`.*** End Patch