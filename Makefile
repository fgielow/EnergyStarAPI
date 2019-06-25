build:
	docker-compose build

ssh:
	docker container exec -it energystarapi_EnergyStarApi_1 bash

play:
	docker container exec -it energystarapi_EnergyStarApi_1 python playground/play.py