CREATE EXTERNAL TABLE candidatos_rj.competitividade (
  codigo_cargo string,
  cargo string,
  qtd_candidatos int,
  qtd_vagas double,
  data_posse string,
  candidatos_por_vaga double
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '"'
)
STORED AS TEXTFILE
LOCATION 's3://BUCKET/gold/competitividade/'
TBLPROPERTIES ('skip.header.line.count' = '1');

CREATE EXTERNAL TABLE candidatos_rj.representatividade_cargo (
  codigo_cargo string,
  cargo string,
  qtd_candidatos int,
  pct_mulheres double,
  pct_preta double,
  pct_parda double,
  pct_branca double,
  pct_18_29 double,
  pct_superior double,
  pct_nascidos_rj double,
  qtd_quilombola double,
  mediana_idade double,
  lista_proporcional string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '"'
)
STORED AS TEXTFILE
LOCATION 's3://BUCKET/gold/representatividade_cargo/'
TBLPROPERTIES ('skip.header.line.count' = '1');

CREATE EXTERNAL TABLE candidatos_rj.patrimonio_genero (
  genero string,
  qtd_candidatos int,
  qtd_com_patrimonio int,
  mediana_patrimonio double,
  pct_com_patrimonio double
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '"'
)
STORED AS TEXTFILE
LOCATION 's3://BUCKET/gold/patrimonio_genero/'
TBLPROPERTIES ('skip.header.line.count' = '1');

SELECT cargo,
       qtd_candidatos,
       qtd_vagas,
       candidatos_por_vaga
FROM candidatos_rj.competitividade
ORDER BY candidatos_por_vaga DESC;

SELECT cargo,
       qtd_candidatos,
       pct_mulheres,
       pct_preta,
       pct_parda,
       pct_branca
FROM candidatos_rj.representatividade_cargo
WHERE lista_proporcional = 'True'
ORDER BY pct_mulheres;

SELECT genero,
       qtd_candidatos,
       qtd_com_patrimonio,
       mediana_patrimonio,
       pct_com_patrimonio
FROM candidatos_rj.patrimonio_genero;