# Consultas Athena (versão AWS)

O ETL local grava `data/processed/gold/`. A versão nuvem está no repositório
`pipeline-candidatos-aws`: S3 (bronze/silver/gold), Glue Python shell e Athena.

DDL e SELECT oficiais: `pipeline-candidatos-aws/sql/athena.sql`

Database: `candidatos_rj` (us-east-1)

Exemplos (os mesmos do gold local):
- competitividade por cargo
- representatividade (cota, `lista_proporcional = 'True'`)
- mediana de patrimônio por gênero (NaN ≠ 0)