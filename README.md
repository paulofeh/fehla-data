# Portfólio de projetos em Jornalismo de Dados

Aplicação Python, utilizando o framework Flask, que reúne um [portfólio de trabalhos](https://fehla-data.onrender.com/) realizados pelo autor no Master em Jornalismo de Dados, Automação e Data Storytelling do Insper.

A aplicação está dividida em 3 canais principais:

1. Biografia resumida do autor
2. Lista de trabalhos realizados
3. Aplicação [Imóveis Caixa](https://fehla-data.onrender.com/imoveis) (detalhada abaixo)

O site foi implementado com a utilização dos frameworks Flask (Python) e Tailwind (CSS), além de componentes DaisyUI. Foi desenvolvido como trabalho final da disciplina "Algoritmos de Automação", ministrada por Álvaro Justen no primeiro trimestre de 2024.

O deploy foi feito no Render e o site está disponível [aqui](https://fehla-data.onrender.com/).

## O projeto "Imóveis Caixa"

Trata-se de uma aplicação web que permite visualizar estatísticas de imóveis disponíveis para venda pela Caixa, filtradas por estado. Os dados incluem imóveis com os maiores e menores preços, maior desconto, preço médio dos imóveis, entre outras informações.

### Motivações

O projeto nasce de uma motivação pessoal: facilitar o acesso à pesquisa de imóveis vendidos pela Caixa. A plataforma tem uma navegação complexa e uma busca pouco amigável; por outro lado, o banco disponibiliza periodicamente arquivos CSV organizados por UF e incluindo as mesmas informações, o que facilita o uso automatizado desses dados.

A segunda motivação é jornalística, já que os dados servem também como termômetro do mercado imobiliário e da situação econômica do país. Imóveis retomados podem ser um indicador de inadimplência e de crise econômica; a Caixa, além de ser um banco público, é também o maior financiador imobiliário do país, com 67% de participação no mercado (2021).

### Métodos e resultados

A Caixa disponibiliza um banco de dados público sobre imóveis usados de todo o Brasil (casas, apartamentos e terrenos aptos para uso), disponíveis para venda em diferentes modalidades. Os imóveis listados são de propriedade da Caixa, em geral provenientes de execuções de garantias de contratos de financiamento, e podem ser vendidos com descontos consideráveis em relação aos seus valores de mercado.

Este projeto recupera periodicamente os CSVs disponibilizados para cada estado, trata os seus dados e consolida-os em uma planilha do Google Sheets, permitindo consultas detalhadas. A mesma planilha serve de base de dados para o cálculo das estatísticas apresentadas na aplicação Flask, como imóveis mais baratos e mais caros, maiores descontos, preços médios e modalidades de venda mais comuns para cada UF.

- [Fonte dos dados](https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp)
- [Planilha atualizada](https://docs.google.com/spreadsheets/d/1GC_cPnLsJ2W5Jvv1aMmT46rFHbZbfaAqusq4fdz1B5Y/edit?usp=sharing)

### Principais dificuldades e possíveis melhorias

As principais dificuldades enfrentadas referem-se à utilização das APIs do Google (Sheets e Maps), bem como limitações de processamento. Os limites de uso da API do Sheets foram contornados com a inclusão de tempos de espera entre as consultas, mas um dos recursos planejados previa a exibição de um mapa com todos os imóveis de cada estado, o que se mostrou inviável dada a demora no processamento em casos como São Paulo, onde o número de imóveis supera 5000. 

Entre as possíveis melhorias, a principal dela talvez esteja relacionada à performance, já que muitos dos cálculos são feitos em tempo real, a partir da requisição do usuário. Isso poderia ser contornado com a implementação de uma lógica de cálculo periódico e alimentação de uma aba específica para as estatísticas na própria planilha. Outras melhorias incluem a implementação dos mapas, a filtragem por município e uma página com estatísticas nacionais.