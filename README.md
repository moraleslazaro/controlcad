# ControlCAD

Application designed and developed for my degree project with the purpose of manage scanned blueprints as well as CAD files in the company I was working for. It provides a simple control versioning system for CAD files using the MD5 algorithm to detect changes on the file structure.

The application is built on Django/Python and SQLite and it is configured to be launched using the WSGI web server provided by Python.

Once the application is running use the user `admin` and password `admin` in order to log into the administration panel.

## Running ControlCAD

After cloning the repo, provision the VM using vagrant:

`$ vagrant up --provision`

ControlCAD should be running on `http://localhost:8080`
