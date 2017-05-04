# Pyekaboo

Pyekaboo is a proof-of-concept program that is able to to hijack/hook/proxy Python module(s) thanks to $PYTHONPATH variable. It's like "DLL Search Order Hijacking" for Python.

It was released as part of the [Backdooring Your Python Programs](http://thotcon.org/schedule.html) talk given at THOTCON 0x8 conference by Itzik Kotler from [SafeBreach Labs](http://www.safebreach.com).

Slides are availble [here](http://www.ikotler.org/InYourPythonPath.pdf)

### Version
0.1.0

### Installation

Pyekaboo requires [Python](https://python.org/) and was tested with Python 2.7.10.

```sh
$ git clone https://github.com/SafeBreach-Labs/pyekaboo.git
$ cd pyekaboo
$ cd pyekaboo
$ python mkpyekaboo.py -h
```

### Example: Debugging Python's sockets Module

```sh
# assume pyekaboo root directory
$ cd scripts
$ python ../pyekaboo/mkpyekaboo.py -l 6 socket
$ ./enable_pyekaboo.sh -i
$ python ../test_apps/django_test/blog/manage.py runserver
```

License
----

BSD 3-Clause

###
