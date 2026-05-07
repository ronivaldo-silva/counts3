---
trigger: model_decision
description: File manager clipboard copiar colar navegar rota routing
---

# Regras de Serviços e Arquitetura Avançada: Flet

Sempre que a solicitação do usuário envolver troca de telas, seleção de arquivos ou interação com a área de transferência do sistema, você **DEVE** evitar alucinações baseadas em versões antigas ou em outros frameworks. Acesse e leia a documentação específica listada abaixo antes de escrever o código:

## 1. Sistema de Rotas e Navegação (Multi-page)
**Link obrigatório:** `https://flet.dev/docs/cookbook/navigation-and-routing/`
* **Diretriz:** Nunca construa um sistema de múltiplas telas gambiarrado (como apenas esconder/mostrar Containers). Você deve ler a documentação de roteamento para entender como usar corretamente `page.route`, `page.views`, `page.go()` e o evento `page.on_route_change`. O Flet utiliza uma pilha de visualizações (Views) que permite integração nativa com o botão de "voltar" do navegador e do celular.

## 2. Manipulação de Arquivos (File Picker)
**Link obrigatório:** `https://flet.dev/docs/services/filepicker`
* **Diretriz:** Se a tarefa pedir para abrir caixas de diálogo do sistema operacional (para selecionar, salvar ou fazer upload de arquivos/diretórios), você não pode tentar usar bibliotecas padrão do Python (como `tkinter` ou `os` diretamente para a UI). Leia a documentação do `ft.FilePicker`. Estude como ele é adicionado como um *overlay* na página (`page.overlay.append`) e como manipular os eventos assíncronos e a resposta (`on_result`).

## 3. Área de Transferência (Clipboard)
**Link obrigatório:** `https://flet.dev/docs/services/clipboard`
* **Diretriz:** Para funcionalidades como "Copiar texto", "Copiar link" ou "Colar", leia esta seção da documentação. Verifique a sintaxe correta para ler e escrever na área de transferência (geralmente usando métodos vinculados ao objeto `page`, como `page.set_clipboard(text)` e `page.get_clipboard()`).

## Instrução de Execução:
Ao detectar que a tarefa precisa de um desses 3 recursos, faça silenciosamente uma requisição HTTP para o link obrigatório correspondente, leia o material mais atualizado, preste atenção aos trechos de código de exemplo lá descritos e só então inicie o desenvolvimento.