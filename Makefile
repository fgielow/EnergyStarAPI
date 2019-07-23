run:
	docker container run -v $(PWD):/opt/EnergyStar --rm energystar python playground/play.py

bash:
	docker container run -it -v $(PWD):/opt/EnergyStar --rm energystar bash

exec:
	docker container exec -it energystarapi_EnergyStarApi_1 python playground/play.py

build:
	docker-compose build

ssh:
	docker container exec -it energystarapi_EnergyStarApi_1 bash