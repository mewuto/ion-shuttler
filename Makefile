##################
# In Host
##################
build:
	docker build --no-cache -t ion_shuttler .

run:
	docker run -p 8888:8888 -v $(shell pwd):/home/jovyan/work -d --name ion_shuttler_container_dev ion_shuttler

jn:
	jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

get_token:
	docker logs ion_shuttler_container

clean:
	docker rm -f ion_shuttler_container
	docker rmi ion_shuttler

##################
# In Container
##################
test:
	pytest -v

testall:
	pytest -v --nbmake --ignore=run.ipynb

fmt:
	black .
	nbqa black .

# コミット前に実行
c:
	make testall
	make fmt

countgate:
	python3 scripts/countGate.py