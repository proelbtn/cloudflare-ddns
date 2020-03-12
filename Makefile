TAG = proelbtn/cloudflare-ddns

all:

build:
	DOCKER_BUILDKIT=1 docker build -t ${TAG} .

start:
	bash -c 'source .env; docker run --restart=always -d --name cloudflare-ddns \
		-e CLOUDFLARE_TOKEN=$${CLOUDFLARE_TOKEN} \
		-e CLOUDFLARE_NAME=$${CLOUDFLARE_NAME} \
		-e CLOUDFLARE_ZONE_ID=$${CLOUDFLARE_ZONE_ID} \
		${TAG}'
	

stop:
	docker rm -f cloudflare-ddns
