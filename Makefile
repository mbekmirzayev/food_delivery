.PHONY: mig

mig:
	uv run alembic revision --autogenerate -m " "
	uv run alembic upgrade head