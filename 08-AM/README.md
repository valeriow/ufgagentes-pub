# Pipeline (Notebooks) para Predição de Autoimunidade Induzida por Fármacos

Este diretório consolida uma sequência de notebooks para análise exploratória, baseline, engenharia de features, otimização de hiperparâmetros, treinamento do modelo final, interpretabilidade e simulação/avaliação com dados faltantes.

## Dados de entrada

- Descritores RDKit (pré-computados):
  - `DataSet/DIA_trainingset_RDKit_descriptors.csv`
  - `DataSet/DIA_testset_RDKit_descriptors.csv`

### Tamanho e distribuição de classes

A partir dos CSVs de descritores:

- Treino: **477** amostras, **198** colunas (inclui `Label`)
  # Predição de Autoimunidade Induzida por Fármacos (08-AM)

  Este diretório contém os notebooks e artefatos do trabalho de AM (aprendizado de máquina) para predição de DIA (drug-induced autoimmunity) a partir de descritores RDKit.

  O conjunto atual de notebooks cobre:
  - EDA + limpeza e geração de datasets “cleaned”
  - Baselines
  - Feature engineering
  - Otimização de hiperparâmetros (Random Search) + consolidação de métricas

  ## Dados (como o projeto obtém os CSVs)

  Os notebooks utilizam os descritores RDKit do dataset InterDIA e **fazem download a partir de URLs públicas** (não é necessário manter `DataSet/` localmente para executar o fluxo padrão).

  Ainda assim, este diretório já inclui artefatos gerados (CSVs “cleaned”, planilha e resultados) para facilitar inspeção e reprodutibilidade.

  ## Ambiente (instalação com `uv`)

  O projeto tem dependências declaradas em [08-AM/pyproject.toml](08-AM/pyproject.toml) e fixa a versão do Python em `==3.9.19`.

  ### 1) Instalar o `uv`

  No Linux, a forma mais comum é via instalador oficial:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  Depois, abra um novo terminal (ou recarregue o shell) e valide:

  ```bash
  uv --version
  ```

  ### 2) Criar o ambiente e instalar dependências

  Execute a partir da pasta [08-AM](08-AM):

  ```bash
  cd 08-AM
  uv python install 3.9.19
  uv venv --python 3.9.19
  uv sync
  ```

  Observação: este diretório também possui [08-AM/requirements.txt](08-AM/requirements.txt), mas ele está no formato “legado” e pode não refletir o estado mais atual. Para reprodução, prefira `uv sync`.

  ### 3) Habilitar execução de notebooks (VS Code / Jupyter)

  Para executar os `.ipynb` localmente, você precisa de um kernel.

  - Se você usa VS Code (extensão Jupyter), normalmente basta garantir `ipykernel`.
  - Se você quer rodar via terminal com Jupyter Lab/Notebook, instale `jupyter` também.

  Com `uv`:

  ```bash
  cd 08-AM
  uv pip install ipykernel jupyter
  uv run python -m ipykernel install --user --name dis008-am --display-name "dis008-am (uv)"
  ```

  Para iniciar o Jupyter:

  ```bash
  uv run jupyter lab
  ```

  ## Como reproduzir (ordem recomendada)

  Execute os notebooks nesta ordem:

  1) [08-AM/1.0.%20EDA.ipynb](08-AM/1.0.%20EDA.ipynb)
     - Faz download dos CSVs de descritores.
     - Gera artefatos “cleaned” e arquivos de apoio.

  2) [08-AM/2.0%20Baseline%20Inicial.ipynb](08-AM/2.0%20Baseline%20Inicial.ipynb)
     - Baselines e comparações iniciais.

  3) [08-AM/3.0.%20Melhorando%20com%20Feature%20Engineering.ipynb](08-AM/3.0.%20Melhorando%20com%20Feature%20Engineering.ipynb)
     - Explora variações de pré-processamento/seleção/modelos.

  4) [08-AM/4.0%20Otimiza%C3%A7%C3%A3o%20Hyperpar%C3%A2metros%20RandomSearch.ipynb](08-AM/4.0%20Otimiza%C3%A7%C3%A3o%20Hyperpar%C3%A2metros%20RandomSearch.ipynb)
     - RandomizedSearchCV e consolidação dos resultados.

  ## Artefatos (arquivos gerados e versionados)

  - [08-AM/1.1.EDA-df_summary_types.csv](08-AM/1.1.EDA-df_summary_types.csv): inventário de tipos + listas de features constantes/alta correlação.
  - [08-AM/1.1.EDA-df_train-cleaned.csv](08-AM/1.1.EDA-df_train-cleaned.csv) e [08-AM/1.1.EDA-df_test-cleaned.csv](08-AM/1.1.EDA-df_test-cleaned.csv): datasets pós-limpeza (149 colunas).
  - [08-AM/estatisticas_descritivas.xlsx](08-AM/estatisticas_descritivas.xlsx): estatísticas descritivas.
  - [08-AM/2.2.Modeling-Resultados-combinados.csv](08-AM/2.2.Modeling-Resultados-combinados.csv): consolidação de métricas por configuração.
  - [08-AM/4.1.df_resultados_rs_combinado.pkl](08-AM/4.1.df_resultados_rs_combinado.pkl): resultados detalhados serializados.

  Também estão incluídos os arquivos do artigo: [08-AM/Artigo_SBC.md](08-AM/Artigo_SBC.md) e `Artigo_SBC.docx`.

  ## Notas de reprodutibilidade

  - A etapa de Random Search pode demorar (CPU) dependendo dos grids/iterações.
  - Alguns estimadores geram pastas de log (por exemplo, `catboost_info/`) durante o treino; elas podem aparecer após a execução, mesmo que não estejam versionadas.
