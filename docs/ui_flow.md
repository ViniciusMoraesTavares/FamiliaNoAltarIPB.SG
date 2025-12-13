Atualizações de layout e fluxo

Tela principal
- Campo de número visível no cabeçalho, com validação (1–999).
- Padrão visual consistente com o aplicativo.
- Abre a tela de sorteio com ou sem número; se sem número, o campo estará disponível na tela de sorteio.

Tela de sorteio
- Campo de número removido inicialmente e exibido somente após a tela estar ativa e validações concluídas.
- Transição suave (fade-in) ao disponibilizar o campo, com indicador “Pronto para digitar”.
- Fotos exibidas com proporção (sem cortes), usando componente responsivo.
- Persistência e emissão de evento mantidas para finalizar sorteio no painel.

Técnico
- Importações e inicializações revisadas para garantir abertura estável.
- Estado do campo sincronizado com estado da tela: bloqueado até validações.
- Testes adicionados para abertura consistente e comportamento do campo.
