.DEFAULT_GOAL := run

install_server:
	cd backend && uv sync

install_frontend:
	cd frontend && npm install

install_all: install_server install_frontend

run_server:
	cd backend && uv run python -m proxmox_api

run_frontend:
	cd frontend && ng serve --host=127.0.0.1 --disable-host-check

run:
	echo "Starting server ..."
	make run_server & \
	echo "Starting frontend on http://hosting-local.minet.net:4200/ ..." && \
	make run_frontend

clean:
	rm -rf pycache