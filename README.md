# Pipeline de candidatos — eleições 2026, Rio de Janeiro (versão AWS)

Projeto **de estudo**, feito para aprender um fluxo de dados ponta a ponta (pandas, S3, Glue Python shell e Athena) a partir de um interesse pessoal: **analisar dados dos candidatos do estado do Rio de Janeiro nas eleições gerais de 2026**.

Não é produto do TSE, não é ferramenta de campanha e não substitui o [DivulgaCand](https://divulgacandcontas.tse.jus.br/) nem o portal de [dados abertos do TSE](https://dadosabertos.tse.jus.br/dataset/candidatos-2026). Os CSV são um snapshot público. O **bronze** no S3 ainda contém campos sensíveis do arquivo original (por exemplo CPF). O **silver** deste pipeline **não republica CPF**.

A análise é descritiva: perfil das chapas, competitividade (candidatos por vaga), declaração de bens e recortes de gênero, raça, idade e escolaridade. **Não há resultado eleitoral** neste dump — a extração é anterior ao pleito; situação de urna, votação e cassação vêm vazias ou como sentinela do TSE (`#NULO`, `#NE`).

Região AWS de estudo: **`us-east-1`**.

## Dois repositórios

| Repositório | Papel |
|-------------|--------|
| `pipeline-candidatos-rj` | Regras de negócio, testes e gold **em disco**. Melhor lugar para estudar o pandas. |
| **Este** (`pipeline-candidatos-aws`) | As **mesmas** regras, lendo e gravando um data lake no **S3**; job Glue opcional; SQL no Athena. |

`leitura.py`, `limpeza.py`, `silver.py`, `gold.py` e os testes foram copiados do repo local de propósito: a nuvem troca origem e destino, não a lógica.

## O que a aplicação faz

1. Lê cinco CSV do TSE no prefixo `bronze/` (candidatos, complementar, bens, redes, vagas — só **RJ** / 2026).
2. Monta o **silver**: uma ficha por candidato (`dim_candidato`), vagas por cargo, fatos 1:N de bens e redes.
3. Monta o **gold**: competitividade, patrimônio (sem imputar R$ 0 em quem não declarou), representatividade por cargo/partido, cruzamento gênero × raça.
4. Grava silver e gold no S3, **uma pasta por tabela** (`gold/competitividade/competitividade.csv`), para o Athena não misturar arquivos.
5. (Opcional) O mesmo `executar()` roda num job Glue Python shell. O Athena consulta o gold com SQL.

Perguntas típicas do gold:

- Quantos candidatos por vaga em cada cargo?
- Nas listas de deputado (cota de gênero), qual a fração de mulheres?
- Como se distribuem raça, idade e escolaridade?
- Qual a mediana de patrimônio **entre quem declarou**?

Fonte: conjunto *Candidatos 2026* do TSE, arquivos da UF **RJ**.

## Arquitetura

```text
CSV TSE  →  S3 bronze  →  pandas (laptop ou Glue Python shell)
                              →  S3 silver / gold  →  Athena
```

Não há RDS, Spark, VPC nem crawler. O volume é da ordem de milhares de linhas: Glue **Python shell** (pandas) é o recorte certo; Spark seria desproporcional.

| Prefixo S3 | Conteúdo |
|------------|----------|
| `bronze/` | Cópia fiel dos CSV (separador `;`, encoding Latin-1) |
| `silver/` | Dimensões e fatos (`dim_candidato`, `dim_vagas`, `fato_bens`, `fato_redes`) |
| `gold/` | Tabelas para análise (competitividade, patrimônio, representatividade, …) |
| `jobs/` | `job.py` e `pipeline_src.zip` usados pelo Glue |
| `athena-results/` | Saída das queries do Athena (não é dado de negócio) |

No laptop, o `boto3` usa o **perfil** do AWS CLI. No Glue, usa a **role** do job (`AWS_PROFILE` ausente).

## Estrutura do repositório

```text
pipeline-candidatos-aws/
├── README.md                 # este arquivo
├── Makefile                  # all, clean, fclean, re (+ test, run, Glue)
├── pyproject.toml            # Python ≥ 3.12, pandas, boto3, pytest (uv)
├── uv.lock
├── .env_example              # copie para .env (o Git ignora .env)
├── .gitignore
├── glue/
│   └── job.py                # entrada do Glue (baixa o zip, chama executar)
├── iam/
│   └── s3-pipeline.json      # policy: ler bronze, gravar silver/gold/jobs
├── sql/
│   └── athena.sql            # CREATE TABLE + SELECT de exemplo
├── scripts/
│   └── run_pipeline.py       # uv run python scripts/run_pipeline.py
├── src/
│   ├── caminhos.py           # chaves S3 do bronze
│   ├── s3_io.py              # download/upload boto3
│   ├── leitura.py            # CSV TSE → DataFrame
│   ├── limpeza.py            # tipos, datas, plataforma, faixa etária
│   ├── silver.py             # dim e fatos
│   ├── gold.py               # agregações
│   └── pipeline.py           # orquestra bronze → silver → gold
└── tests/
    ├── test_limpeza.py
    └── test_gold.py
```

O bronze **não** vive neste Git. Os CSV sobem uma vez para `s3://…/bronze/` a partir do repo local (`pipeline-candidatos-rj/data/raw/`) ou do download do TSE.

## Como usar

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/)
- AWS CLI v2 e um perfil configurado (`aws configure --profile …`)
- Conta AWS com um bucket **privado** em `us-east-1` e a policy de `iam/s3-pipeline.json` no usuário IAM
- Python 3.12 no `.venv` (o `make` / `make all` resolve)

### 1. Ambiente local

```bash
cd pipeline-candidatos-aws
cp .env_example .env
```

Edite o `.env` (não commite este arquivo):

```text
AWS_REGION=us-east-1
AWS_PROFILE=pipeline-candidatos
S3_BUCKET=candidatos-rj-SEU_ACCOUNT_ID
```

`S3_BUCKET` é só o nome do bucket, sem `s3://`.

```bash
make
make test
```

`make test` **não** fala com a AWS. Precisa passar antes de `make run`.

### 2. Bronze no S3 (uma vez, ou quando atualizar o dump)

Os cinco CSV do RJ, no prefixo `bronze/`, com os nomes em `src/caminhos.py`:

- `consulta_cand_2026_RJ.csv`
- `consulta_cand_complementar_2026_RJ.csv`
- `bem_candidato_2026_RJ.csv`
- `rede_social_candidato_2026_RJ.csv`
- `consulta_vagas_2026_RJ.csv`

Exemplo a partir do repo local (ajuste o caminho):

```bash
export AWS_PROFILE=pipeline-candidatos
export S3_BUCKET=seu-bucket

aws s3 cp /caminho/para/pipeline-candidatos-rj/data/raw/ \
  "s3://${S3_BUCKET}/bronze/" \
  --recursive --exclude "*" --include "*.csv"
```

Confira:

```bash
aws s3 ls "s3://${S3_BUCKET}/bronze/"
```

O bucket deve estar com **Block Public Access** ligado. Não habilite site estático.

### 3. Rodar o pipeline (laptop → S3)

```bash
make run
```

Equivale a `uv run python scripts/run_pipeline.py`. O working directory tem que ser a **raiz** deste repo (para o `.env` e o pacote `src`).

O script:

1. Baixa o bronze para arquivos temporários
2. Monta silver e gold em memória
3. Envia cada tabela para `s3://bucket/silver/<nome>/<nome>.csv` e `s3://bucket/gold/<nome>/<nome>.csv`
4. Imprime um resumo no terminal (linhas, competitividade, representatividade, NaNs de patrimônio)

Listar o gold:

```bash
make ls-gold S3_BUCKET=seu-bucket
```

(O Make **não** lê o `.env` sozinho; passe `S3_BUCKET` ou faça `set -a && source .env && set +a` antes.)

Atalho completo: `make verify` (testes + pipeline).

### 4. Glue (opcional — mesma lógica na nuvem)

Depois de alterar o `src/`:

```bash
make upload-glue S3_BUCKET=seu-bucket
```

Isso gera `/tmp/pipeline_src.zip` e envia o zip e `glue/job.py` para `s3://bucket/jobs/`.

No console Glue (`us-east-1`): job **Python shell**, role com `AWSGlueServiceRole` + a policy S3, parâmetro `--S3_BUCKET`, módulos extras `pandas==2.2.3` (o shell clássico é Python 3.9; o venv local usa pandas 3). Timeout curto (por exemplo 10 min). **Run job** e acompanhe o CloudWatch.

O `glue/job.py` não deve ser executado no laptop (`awsglue` só existe no Glue).

### 5. Athena (consultar o gold)

1. Console Athena, região `us-east-1`.
2. Local de resultados: `s3://SEU_BUCKET/athena-results/` (prefixo privado).
3. Substitua o bucket em [`sql/athena.sql`](sql/athena.sql) e rode os `CREATE DATABASE` / `CREATE EXTERNAL TABLE` / `SELECT`.

Cada `LOCATION` aponta para **uma pasta** (`gold/competitividade/`), não para `gold/` inteiro. Database de estudo: `candidatos_rj`.

Exemplo: listas proporcionais e cota de gênero — `WHERE lista_proporcional = 'True'` (texto, com aspas).

## Makefile (resumo)

`make` sem alvo é `all` (padrão da Escola 42): instala o `.venv`. `make help` lista os alvos. `clean` / `fclean` **não** apagam o bucket S3.

| Alvo | Função |
|------|--------|
| `make` / `make all` | `uv sync --group dev` (equivale a `make setup`) |
| `make test` | pytest (sem S3) |
| `make run` | Pipeline pandas contra o S3 |
| `make verify` | `test` e em seguida `run` |
| `make ls-gold` | `aws s3 ls` no prefixo gold |
| `make zip-glue` / `make upload-glue` | Pacote e upload do código para o Glue |
| `make clean` | Caches Python e zip local do Glue |
| `make fclean` | `clean` e remove o `.venv` |
| `make re` | `fclean` e em seguida `all` |

## Créditos AWS

Com créditos de estudo, **manter** bucket, job e tabelas Athena para demo é razoável: Glue e Athena **parados não cobram**; S3 deste volume é barato. Não publique o bucket e não agende o job em loop.

Teardown, se quiser zerar: tabelas/database Athena → job Glue → role → esvaziar e apagar o bucket → log groups → policy/usuário. O Git permanece.

## Licença dos dados

Dados eleitorais: termos do TSE / dados abertos. Este repositório é material de estudo pessoal.

## Referências

- [Candidatos 2026 — dados abertos TSE](https://dadosabertos.tse.jus.br/dataset/candidatos-2026)
- [Preços S3](https://aws.amazon.com/s3/pricing/) · [Glue](https://aws.amazon.com/glue/pricing/) · [Athena](https://aws.amazon.com/athena/pricing/)
