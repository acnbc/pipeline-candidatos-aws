NAME		:= pipeline-candidatos-aws
UV			:= uv
AWS			:= aws
RM			:= rm -f
PYTEST_CACHE	:= .pytest_cache
VENV		:= .venv
GLUE_ZIP	:= /tmp/pipeline_src.zip
BUCKET		:= $(S3_BUCKET)

all: setup

setup:
	@command -v $(UV) >/dev/null 2>&1 || { \
		echo "uv não está no PATH. https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; }
	$(UV) sync --group dev

test:
	$(UV) run pytest -q

run:
	$(UV) run python scripts/run_pipeline.py

verify: test run

ls-gold:
	@test -n "$(BUCKET)" || { echo "Defina S3_BUCKET no ambiente ou make ls-gold S3_BUCKET=..."; exit 1; }
	$(AWS) s3 ls "s3://$(BUCKET)/gold/"

zip-glue:
	zip -r $(GLUE_ZIP) src -x "*.pyc" -x "*__pycache__*"
	@echo "gerado $(GLUE_ZIP)"

upload-glue: zip-glue
	@test -n "$(BUCKET)" || { echo "Defina S3_BUCKET"; exit 1; }
	$(AWS) s3 cp $(GLUE_ZIP) "s3://$(BUCKET)/jobs/pipeline_src.zip"
	$(AWS) s3 cp glue/job.py "s3://$(BUCKET)/jobs/job.py"
	$(AWS) s3 ls "s3://$(BUCKET)/jobs/"

help:
	@echo "$(NAME) (AWS, uv) — regras 42: all clean fclean re"
	@echo "  make / make all   $(UV) sync --group dev"
	@echo "  make test         pytest (sem S3)"
	@echo "  make run          bronze S3 → silver/gold S3 (precisa .env)"
	@echo "  make verify       test + run"
	@echo "  make ls-gold      lista gold/ no bucket (S3_BUCKET=...)"
	@echo "  make zip-glue     gera $(GLUE_ZIP)"
	@echo "  make upload-glue  sobe zip e glue/job.py para s3://bucket/jobs/"
	@echo "  make clean        caches Python e zip local do Glue"
	@echo "  make fclean       clean + remove $(VENV) (não apaga o S3)"
	@echo "  make re           fclean e em seguida all"

clean:
	$(RM) -r $(PYTEST_CACHE)
	$(RM) -r src/__pycache__ tests/__pycache__ scripts/__pycache__ glue/__pycache__
	$(RM) $(GLUE_ZIP)

fclean: clean
	$(RM) -r $(VENV)

re:
	$(MAKE) fclean
	$(MAKE) all

.PHONY: all setup test run verify ls-gold zip-glue upload-glue help clean fclean re
