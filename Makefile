format:
	isort --skip migrations medscan/
	black --line-length 100 --exclude migrations medscan/
	flake8 medscan/ --statistics

cache_clean:
	find . | grep -E "(/__pycache__$$|\.pyc$$|\.pyo$$)" | xargs rm -rf

publish:
	docker build -f api.dockerfile -t ghcr.io/vshelke/medscan/api:latest .
	docker image push ghcr.io/vshelke/medscan/api:latest
