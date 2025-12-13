Otimizações de desempenho

Imagens
- Compressão e redimensionamento automáticos ao adicionar/editar fotos (`DataManager._optimize_image`).
- Geração de miniaturas em `imagens/thumbs` para uso na galeria (`DataManager._generate_thumb`).
- Carregamento preguiçoso: imagens dos cards são carregadas somente quando visíveis (`FamilyCard.ensure_image_loaded`).
- Renderização incremental: a galeria cria cards em lotes, adicionando mais ao rolar (`PainelPrincipal.render_next_batch`).

Carregamento
- Cache em memória das famílias no `DataManager` evita leituras repetidas.
- Importações tardias para janelas pesadas (`JanelaSorteio`, `JanelaEditarFamilia`).
- Pré-processamento de miniaturas durante a validação inicial.

Banco de dados
- O sistema usa arquivos JSON; as otimizações focam em E/S de disco e imagens.
- Paginação lógica na UI via lotes substitui a necessidade de indexação.

Feedback visual
- Overlays de carregamento e banners de salvamento já existentes indicam operações em progresso.

Testes de desempenho
- `tests/perf_benchmark.py` avalia tempo de adição de várias imagens.
- Métricas recomendadas: tempo de renderização da galeria e latência do carregamento de cards.
