.PHONY: server testdb pytest

server:
	docker-compose up web

testdb:
	docker-compose up -d test_db

pgadmin:
	docker-compose up pgadmin

pytest: testdb
	# 等待 test_db 啟動（可用 sleep 或 healthcheck）
	sleep 5
	pytest

down:
	docker-compose down
