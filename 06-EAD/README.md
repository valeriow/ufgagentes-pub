# Extração Automática de Dados - Pós-graduação Agentes e Sistemas Inteligentes - UFG

# Tema: Streaming buzz (JustWatch × Google Notícias). 

## Do Hype à Tela: Como Notícias Impactam Rankings de Filmes e Séries.

- Nome: Valério Viégas Wittler - valeriow@gmail.com

- Vídeo de apresentação: https://youtu.be/GwGZFUnN9w8

- Powerpoint: [06-EAD/TrabalhoFinalEAD-ValérioViégasWittler.pptx](https://github.com/valeriow/ufgagentes-pub/raw/refs/heads/main/06-EAD/TrabalhoFinalEAD-Val%C3%A9rioVi%C3%A9gasWittler.pptx)





## Introdução

O JustWatch é uma plataforma alemã criada em 2014 que funciona como um guia de busca universal para filmes e séries de streaming e permite aos usuários descobrir onde assistir seus conteúdos favoritos entre mais de 85 serviços de streaming diferentes. A ferramenta é especialmente útil para quem possui assinaturas de múltiplos serviços de streaming e quer evitar perder tempo procurando um filme ou série em cada plataforma separadamente

A plataforma oferece rankings abrangentes através dos JustWatch Streaming Charts, que são atualizados diariamente e representam uma das principais funcionalidades da plataforma. Os JustWatch Streaming Charts são calculados com base na atividade de mais de 40 milhões de usuários mensais e oferecem insights sobre mais de 10.000 filmes, programas e temporadas. Os dados são coletados através de três tipos principais de interação dos usuários:

* Cliques em ofertas de streaming

* Adição de títulos às listas de favoritos

* Marcação de títulos como "vistos"

Os rankings são calculados considerando a atividade dos usuários nas últimas 24 horas, 7 dias ou 30 dias, proporcionando uma visão tanto de tendências imediatas quanto de popularidade sustentada. O sistema coleta dados de mais de 50 milhões de fãs de filmes e programas de TV por mês e é atualizado diariamente para 140 países e 4.500 serviços de streaming.

Já o Google Notícias é a funcionalidade do Google que agrega notícias de diversas fontes, permitindo que os usuários acompanhem as últimas notícias sobre tópicos de interesse. A plataforma é amplamente utilizada para se manter atualizado sobre eventos atuais, tendências e tópicos específicos, como filmes e séries. 


## Objetivo

O objetivo deste trabalho é demonstrar a extração automática de dados do JustWatch e do Google Notícias, utilizando técnicas de web scraping e processamento de linguagem natural. A extração é realizada diariamente, coletando dados do JustWatch e notícias relacionadas aos títulos mencionados nos rankings diários.

Após a extração dos dados, é possível analisar as tendências de popularidade dos filmes e séries, bem como identificar quais títulos estão gerando mais buzz na mídia. Essa análise pode ser útil para entender o comportamento dos usuários em relação ao consumo de conteúdo de streaming e para identificar oportunidades de marketing e promoção de títulos específicos.

A principal hipótese a ser testada é que os títulos mais populares no JustWatch também geram mais buzz na mídia, refletindo uma correlação entre a popularidade dos títulos e a cobertura de notícias sobre eles. Além disso, espera-se que os rankings diários do JustWatch possam ser utilizados para prever quais títulos terão maior sucesso no futuro, com base em seu desempenho atual.


## Metodologia

A metodologia utilizada para a extração automática de dados envolve as seguintes etapas:

1. Coleta de Dados do JustWatch
2. Coleta de Dados do Google Notícias
3. Processamento e Análise dos Dados


## Coleta de Dados 

A coleta de dados do JustWatch é realizada através da raspagem dos dados do ranking diário com a ferramenta Selenium. A extração é feita diariamente, coletando os dados mais recentes disponíveis na plataforma.

A coleta de dados do Google Notícias é realizada através da raspagem das notícias relacionadas aos títulos mencionados nos rankings do JustWatch. Também utiliza a ferramenta Selenium. A extração é feita diariamente, buscando as notícias mais recentes e relevantes para cada título. 

## Processamento e Análise dos Dados

Os dados coletados são processados e analisados utilizando técnicas de processamento de linguagem natural (NLP) e análise de dados. As notícias são analisadas para identificar quais títulos estão gerando mais buzz na mídia, com base em métricas como o número de menções, o sentimento das notícias e a relevância dos títulos.

Além disso, os dados do JustWatch são utilizados para identificar tendências de popularidade e prever quais títulos podem se tornar mais relevantes no futuro. A análise é realizada em diferentes níveis, incluindo a comparação entre títulos, a identificação de padrões ao longo do tempo e a correlação entre a popularidade no JustWatch e o buzz na mídia.

## Como executar o código

Para executar o código deste projeto, é necessário ter o Python instalado (versão 3.13 ou superior) e uma IDE ou editor de código, como o Jupyter Notebook ou o Visual Studio Code. 

Depois é necessário seguir os seguintes passos:

1. Clonar o repositório do projeto.

```bash
git clone https://github.com/valeriow/ufgagentes-pub.git

cd ufgagentes-pub/06-EAD

```

2. O projeto está configurado com o uv (https://github.com/astral-sh/uv) para facilitar a instalação das dependências. Para criar o ambiente virtual, execute o seguinte comando no terminal:

3. Certifique-se de que o arquivo pyproject.toml está presente. Esse arquivo deve listar as dependências do seu projeto. 

2. Instale o uv (https://github.com/astral-sh/uv)

No terminal, execute:

```bash
pip install uv
```

3. Dentro da pasta "ufgagentes-pub/06-EAD", execute o seguinte comando para criar o ambiente virtual e instalar as dependências:

```bash
uv sync
```

4. Ative o ambiente virtual

Antes de rodar seu código, ative o ambiente virtual criado. No terminal, execute:

```bash
source venv/bin/activate
```

5. Execute o jupyter notebook ou o Visual Studio Code para abrir o projeto:

```bash
jupyter notebook
```

Obs: é necessário instalar o Jupyter Notebook se você ainda não o tiver instalado. Você pode fazer isso com o seguinte comando:

```bash 
pip install jupyter
```

6. Abra o arquivo `main.ipynb` no Jupyter Notebook ou no Visual Studio Code e siga as instruções no notebook para executar o código.

7. Os dados serão coletados automaticamente e salvos em arquivos CSV na pasta `data/`. Você pode analisar os dados coletados utilizando ferramentas de análise de dados, como o Pandas, ou visualizá-los diretamente no Jupyter Notebook.


## Arquitetura do Projeto
O projeto está estruturado da seguinte forma:

```
ufgagentes-pub/06-EAD/
├── data/                  # Pasta onde os dados coletados serão salvos    
├── extractors.py            # Arquivo principal que contém a função de extração diária
├── justwatch_extractor.py  # Extrator de dados do JustWatch
├── google_news_extractor.py  # Extrator de dados do Google Notícias
├── Main.ipynb          # Notebook principal para executar o código de extração e análise
├── pyproject.toml          # Configuração do projeto
├── README.md               # Documentação do projeto
```


## Conclusão

A extração automática de dados do JustWatch e do Google Notícias permite analisar as tendências de popularidade dos filmes e séries, bem como identificar quais títulos estão gerando mais buzz na mídia. A metodologia apresentada neste trabalho demonstra como é possível coletar e processar dados de forma eficiente, utilizando técnicas de web scraping e processamento de linguagem natural.
A análise dos dados coletados pode fornecer insights valiosos sobre o comportamento dos usuários em relação ao consumo de conteúdo de streaming e ajudar a identificar oportunidades de marketing e promoção de títulos específicos.




