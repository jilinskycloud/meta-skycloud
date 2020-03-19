
SUMMARY = "Web Interface"
DESCRIPTION = "Gateway  web Interface flask framework based "
HOMEPAGE = ""
LICENSE = "CLOSED"

SRC_URI = "file://daemons/ \
          file://gw_web/ \
          file://drivers/"


do_install() {
install -d ${D}/etc/init.d
install -d ${D}/www/web
install -d ${D}/lib/modules/4.1.15-1.2.0+g439d301/kernel/drivers



cp -r --no-dereference --preserve=mode,links -v ${WORKDIR}/daemons/* ${D}/etc/init.d
cp -r --no-dereference --preserve=mode,links -v ${WORKDIR}/gw_web/* ${D}/www/web
cp -r --no-dereference --preserve=mode,links -v ${WORKDIR}/drivers/* ${D}/lib/modules/4.1.15-1.2.0+g439d301/kernel/drivers


#cp -r --no-dereference --preserve=mode,links -v ${WORKDIR}/libssl/* ${D}/lib



chown -R root:root ${D}/www/web/_netw/ble_read
chmod -R 777 ${D}/www/web/_netw/ble_read

chown -R root:root ${D}/www/web/_netw/mqtt_post
chmod -R 777 ${D}/www/web/_netw/mqtt_post

chown -R root:root ${D}/etc/init.d/hb_daemon
chmod -R 777 ${D}/etc/init.d/hb_daemon
chown -R root:root ${D}/etc/init.d/http_daemon
chmod -R 777 ${D}/etc/init.d/http_daemon
chown -R root:root ${D}/etc/init.d/logs_daemon
chmod -R 777 ${D}/etc/init.d/logs_daemon
chown -R root:root ${D}/etc/init.d/flask_daemon
chmod -R 777 ${D}/etc/init.d/flask_daemon
chown -R root:root ${D}/etc/init.d/autoC_daemon
chmod -R 777 ${D}/etc/init.d/autoC_daemon

chown -R root:root ${D}/www/web/_autoConfig/gpio_led
chmod -R 777 ${D}/www/web/_autoConfig/gpio_led


chown -R root:root ${D}/www/web/_netw/scan_ble.py
chmod -R 777 ${D}/www/web/_netw/scan_ble.py






}

FILES_${PN} += "/etc/init.d/*"
FILES_${PN} += "/www/web/*"
FILES_${PN} += "/lib/modules/4.1.15-1.2.0+g439d301/kernel/drivers/*"


INSANE_SKIP_${PN} = "ldflags"
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
INHIBIT_PACKAGE_STRIP = "1"


