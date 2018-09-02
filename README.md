# ControlCAD

Application designed and developed for my degree project with the purpose of manage scanned blueprints as well as CAD files in the company I was working for. It provides a simple control versioning system for CAD files using the MD5 algorithm to detect changes on the file structure.

The application is built on Django/Python and SQLite and it is configured to be launched using the WSGI web server provided by Python.

Once the application is running use the user `admin` and password `admin` in order to log into the administration panel.

### Running ControlCAD

#### Vagrant

After cloning the repo, provision the VM using the following command:

`$ vagrant up --provision`

#### Docker

If you are using Docker you can build and image with all the tools using:

`docker build -t local/django .`

That image will have all the tools and ControlCAD inside to create containers using:

`docker run --rm -d -p 8080:8000 local/django`

Argument `-d` will make the the container to run on the background, remove it and it will show the output
of the Python WSGI server.

If you are running Docker client and server on the same host you can also mount the development folder on the
container to update the changes automatically. Use the following command:
`docker run --rm -d --mount type=bind,source="$(pwd)",target=/controlcad -p 8080:8000 local/django` 

ControlCAD should be running then on `http://localhost:8080` and show this welcome page:

![alt text](https://github.com/moraleslazaro/controlcad/blob/master/docs/welcome.png "ControlCAD welcome page")

You can also sign in as one of the predefined users. Use username `finol` and password `finol` to login as a project manager.

![alt text](https://github.com/moraleslazaro/controlcad/blob/master/docs/main.png "ControlCAD main page")
