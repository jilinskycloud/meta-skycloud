SUMMARY = "WSGI HTTP Server for UNIX"
DESCRIPTION = "\
  Gunicorn Green Unicorn is a Python WSGI HTTP Server for UNIX. Its \
  a pre-fork worker model ported from Rubys Unicorn project. The \
  Gunicorn server is broadly compatible with various web frameworks, \
  simply implemented, light on server resource usage, and fairly speedy. \
  " 
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=19a2e253a273e390cd1b91d19b6ee236"

SRC_URI = "https://pypi.python.org/packages/source/g/gunicorn/${BPN}-${PV}.tar.gz"


#SRC_URI = "https://files.pythonhosted.org/packages/33/b8/f5fd32e1f46fcfefd7cb5c84dee1cf657ab3540ee92b8a09fc40e4887bf0/gunicorn-20.0.4.tar.gz"
#RC_URI[md5sum] = "543669fcbb5739ee2af77184c5e571a1"
#SRC_URI[sha256sum] = "1904bb2b8a43658807108d59c3f3d56c2b6121a701161de0ddf9ad140073c626"

SRC_URI[md5sum] = "eaa72bff5341c05169b76ce3dcbb8140"
SRC_URI[sha256sum] = "82715511fb6246fad4ba66d812eb93416ae8371b464fa88bf3867c9c177daa14"

inherit setuptools
