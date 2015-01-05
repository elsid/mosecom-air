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
sed -Ei 's/^Depends:.*/\0, libossp-uuid-perl/' debian/control &&
sed -Ei 's/^Depends:.*/\0, nginx-extras/' debian/control &&
echo '
override_dh_auto_install:
	python setup.py install --root=debian/mosecom-air --install-layout=deb \
		--install-scripts=/usr/share/mosecom-air/bin
override_dh_auto_build:
' >> debian/rules &&
cp ../../../debian/cron.d debian/mosecom-air.cron.d &&
cp ../../../debian/install debian/ &&
cp ../../../debian/links debian/ &&
cp ../../../debian/postinst debian/ &&
cp ../../../debian/prerm debian/ &&
debuild
