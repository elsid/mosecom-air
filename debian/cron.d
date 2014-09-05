30	*	*	*	*	root	curl localhost:13710/api/update
*	*	*	*	*	root	if [ "$(curl localhost:13710/api/ping)" != "pong" ]; then service mosecom-air restart; fi
