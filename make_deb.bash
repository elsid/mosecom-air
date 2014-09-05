#!/bin/bash

NAME=$(python setup.py --name)
VERSION=$(python setup.py --version)

rm -r dist
python setup.py sdist &&
cd dist &&
py2dsc $NAME-$VERSION.tar.gz &&
cd deb_dist/mosecom-air-$VERSION &&
sed -i 's/^Package: python-mosecom-air/Package: mosecom-air/' debian/control &&
sed -i 's/python-all/python/' debian/control &&
sed -iE 's/^Depends:.*/\0, libossp-uuid-perl/' debian/control &&
sed -iE 's/^Depends:.*/\0, nginx-extras/' debian/control &&
echo '
override_dh_auto_install:
	python setup.py install --root=debian/mosecom-air --install-layout=deb \
		--install-scripts=/usr/share/mosecom-air/bin
override_dh_auto_build:
' >> debian/rules &&
echo '
/usr/share/mosecom-air/bin/manage.py /usr/bin/mosecom-air-manage
/usr/share/mosecom-air/bin/request.py /usr/bin/mosecom-air-request
/usr/share/mosecom-air/bin/parse_html.py /usr/bin/mosecom-air-parse-html
/usr/share/mosecom-air/etc/nginx.conf /etc/nginx/conf.d/mosecom-air.conf
/usr/share/mosecom-air/etc/init.sh /etc/init.d/mosecom-air
' > debian/links &&
echo '
etc/init.sh /usr/share/mosecom-air/etc
etc/nginx.conf /usr/share/mosecom-air/etc
' > debian/install &&
echo '
30	*	*	*	*	root	curl localhost:13710/api/update
*	*	*	*	*	root	if [ "$(curl localhost:13710/api/ping)" != "pong" ]; then service mosecom-air restart; fi
' > debian/mosecom-air.cron.d
echo '
mkdir -p /var/log/mosecom-air &&
mkdir -p /var/log/nginx/mosecom-air && {
	/etc/init.d/mosecom-air stop
	/etc/init.d/mosecom-air start
	true
}
' > debian/postinst &&
echo '
/etc/init.d/mosecom-air stop
' > debian/prerm &&
debuild
