---
trigger: always_on
---

# Regras de Documentação: Flet UI Framework

Sempre que a sua tarefa envolver a criação, modificação ou depuração de código utilizando o framework Flet (`import flet as ft`), você **DEVE** priorizar a leitura da documentação oficial antes de gerar o código. O Flet recebe atualizações frequentes e os parâmetros dos controles podem mudar.

## Diretrizes de Pesquisa e Navegação:
1. **Página Base:** A documentação principal está em `https://flet.dev/docs`. Use-a para entender conceitos gerais (roteamento, layout, animações).
2. **Obrigatoriedade de Submódulos:** A página inicial contém apenas a introdução. Para utilizar um controle específico, você é **obrigado** a acessar a página exata daquele controle para verificar os parâmetros e atributos suportados.
3. **Padrão de URL de Controles:** Você deve deduzir a URL do controle necessário convertendo o nome da classe para letras minúsculas e anexando ao caminho `/docs/controls/`.
   - **Formato:** `https://flet.dev/docs/controls/<nome_do_controle_em_minusculo>`
   - **Exemplo 1:** Se precisar usar `ft.AlertDialog`, acesse -> `https://flet.dev/docs/controls/alertdialog`
   - **Exemplo 2:** Se precisar usar `ft.ElevatedButton`, acesse -> `https://flet.dev/docs/controls/elevatedbutton`
   - **Exemplo 3:** Se precisar usar `ft.Container`, acesse -> `https://flet.dev/docs/controls/container`
4. **Execução:** Quando identificar quais controles serão necessários para o componente solicitado pelo usuário, acesse silenciosamente as URLs correspondentes, leia os argumentos, métodos e exemplos disponíveis na página, e só então gere a solução. Não adivinhe parâmetros.