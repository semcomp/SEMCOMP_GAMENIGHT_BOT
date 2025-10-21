build:
	@echo "Construindo a imagem Docker..."
	docker build -t gamenight .

run:
	@echo "Iniciando container em segundo plano..."

	docker run -d \
		--log-driver local --log-opt max-size=10m \
		--restart unless-stopped \
		--name gamenight-bot \
		gamenight
	@echo "Container iniciado."

stop:
	@echo "Parando container..."
	@docker stop gamenight-bot || true
	@docker rm gamenight-bot || true
	@echo "Container parado e removido."


clean: stop
	@echo "Removendo imagem..."
	@docker rmi gamenight || true
	@echo "Limpeza concluída."

restart:
	make clean
	make build
	make run

.PHONY: build run stop clean restart