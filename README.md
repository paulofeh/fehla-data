# Portfólio de projetos em Jornalismo de Dados de Paulo Fehlauer

Este site reúne um portfólio de trabalhos realizados pelo autor no Master em Jornalismo de Dados, Automação e Data Storytelling do Insper.

Trata-se de uma aplicação Flask dividida em 3 canais principais:

1. Biografia resumida do autor
2. Lista de trabalhos realizados
3. Aplicação "Imóveis Caixa" (detalhada abaixo)

O site foi implementado com a utilização dos frameworks Flask (Python) e Tailwind (CSS), incluindo componentes DaisyUI. Foi desenvolvido como trabalho final da disciplina "Algoritmos de Automação", ministrada por Álvaro Justen no primeiro trimestre de 2024.

## O projeto "Imóveis Caixa"

Trata-se de uma aplicação web que permite visualizar estatísticas de imóveis disponíveis para venda pela Caixa, filtradas por estado. Os dados incluem imóveis com os maiores e menores preços, maior desconto, preço médio dos imóveis, entre outras informações.

### De onde vêm os dados?

A Caixa disponibiliza um banco de dados público sobre imóveis usados de todo o Brasil (casas, apartamentos e terrenos aptos para uso), disponíveis para venda em diferentes modalidades. Os imóveis são de propriedade da Caixa, em geral provenientes de execuções de garantias de contratos de financiamento. No entanto, a navegação é complexa e a busca pouco amigável. Por outro lado, a Caixa também disponibiliza periodicamente arquivos CSV organizados por unidade da federação e incluindo as mesmas informações. Este projeto recupera e consolida tais planilhas, trata os seus dados e então propõe algumas leituras estatísticas por UF.

### Por quê?

O portal de imóveis da Caixa é uma fonte de dados valiosa não apenas para quem busca imóveis para compra, mas também como termômetro do mercado imobiliário e da situação econômica do país. Imóveis retomados podem ser um indicador de inadimplência e de crise econômica; a Caixa, além de ser um banco público, é também o maior financiador imobiliário do país, com 67% de participação no mercado (2021).

### Funcionalidades

- Recuperação e tratamento de dados por estado a partir dos CSVs disponibilizados pela Caixa
- Consolidação dos dados em uma planilha do Google Sheets
- Recuperação dos dados da planilha para análise e exibição
- Cálculo de estatísticas básicas, como imóveis mais baratos/caros, maiores descontos, preços médios e modalidades de venda mais comuns
- Apresentação das estatísticas no frontend por meio de uma aplicação web Flask
