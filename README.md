Builder CI is an automated Build system used to do Continuous Integration of any kind of development project. I made this software as I wish to configure the build pipeline in a much more automated way than any other product does, for example Jenkins. This builder is made to work optionaly with [Redmine](https://www.redmine.org/) thanks to a [Redmine plugin](https://github.com/iabsis/redmine-builder-ci) that will be released soon.

![Redmine Screenshot](https://raw.githubusercontent.com/iabsis/builder-ci/master/doc/redmine_screenshot.png)

## Features

* Automatic detection of the build type (deb, rpm).
* Exposed REST API interface to trigger builds (it will be secured in a future release).
* Create Debian or Redhat repository automatically after build.
* Modular, extend it by creating your own builder plugin.
* Very lightweight, built with love using python and only a few other modules.
* Very easy to install and update using just one command (on Debian Buster).
* Built on top of Mongo and Flask.
* Can use Docker (optional) for a clean build environment for each execution.
* Support hooks folder used to prepare your build environment.
* Build as Code, provide parameters within the builder.yml file inside the project.

## Types of builds supported so far

* Debian/Ubuntu packages (pbuilder).
* Redhat/Centos packages (rpmbuild).
* Ionic and Flutter APK (docker).
* NPM Package.

## Types of publication

* Create repository on server itself (rpm and deb)
* Publish file into a Redmine files project.

## To come

* Install several workers and distribute builds.
* Add more build packages.
* Improve documentation.
* Any requests ?

## How to install (~2 minutes)

Requirement : run all these commands as root.

~~~ bash
# Install Mongo (Mandatory)
curl -s https://www.mongodb.org/static/pgp/server-${VERSION}.asc | apt-key add -
echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" \
    > /etc/apt/sources.list.d/mongo.list
apt update && apt install mongodb-server
echo -e "replication:\n   replSetName: \"rs0\"" >> /etc/mongod.conf
systemctl enable --now mongod
mongo
rs.initiate({
   _id: "rs0",
   members:[
      {
         _id: 0,
         host: "localhost:27017"
      }
   ]
})

# Install Docker (Optional)
curl -s https://download.docker.com/linux/debian/gpg | apt-key add -
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian buster stable" \
    > /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce

# Install Builder CI
echo "deb [trusted=yes] https://projects.iabsis.com/repository/builder-ci/debian buster main" \
    > /etc/apt/sources.list.d/iabsis.list
apt update && apt install builder-ci 

# Post your first build
curl -X 'POST' \
  'http://<url or ip of your build server>:5000/build' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "project": "builder-ci",
  "sources": {
    "method": "git",
    "options": {
      "url": "https://projects.iabsis.com/git/builder-ci",
      "branch": "master"
    }
  },
  "builder": {
    "method": "docker",
    "options": {
      "image": "builder-bullseye"
    }
  }
}'

# Check your build and delete it
builder-ci list
find /var/lib/repo && rm -rf /var/lib/repo/builder-ci
~~~

## Frequently asked questions

### How does it work

Two services run on a server :

- API called `builder-ci-api` running on port 5000. Use this to manually trigger a build.
- Worker called `build-ci-worker`. This service listen to Mongo events and immediately starts a build when required.

When a new build is added into `queue` table of Mongo, the Worker executes steps in this order.

-> sources -> builder -> publish

Source step usually calls a git method (new method to come) in order to get the source code to be built.
Then builder step attempt to define what kind of build to do unless it has been manually defined (in API call or builder.yml).
Then publish copies the built files either into a local repository or by posting into a specific area, like a Redmine project files.

### Is it ready for production ?

I personnally use this product for my dev company and it manages 99% of our requirements while we are building with various different frameworks (Laravel, Symfony, Ionic, Flutter, NestJS, Angular, React, ...) whilst targetting various Operating System (Android, Debian, Ubuntu, Redhat, Centos, ...).

In other word I consider it to be stable enough for production use.

### Is there complete documentation ?

Not yet, I'm looking into generating documentation based on methods and their parameter lists. I will also provide guides on how to configure the system and on the integration with Redmine.

### How to trigger a build when code is pushed ?

Simply copy and adapt `/usr/share/doc/builder-ci/helpers/git-core.py` into `/usr/share/git-core/templates/hooks` and `<git bare>/.git/hooks/`.

### How can I have a visual way to see my build status ?

Simply install the Redmine module called `Redmine Builder CI`.

### My build failed, how do I view the logs ?

Get the list of builds using the command `builder-ci list` and then view the logs with `builder-ci logs <id_from_list>`.

### Why does my build have the status Duplicate ?

This happens when the build version already exists with a sucess status. You can increment the version and rebuild to complete a new build.

### Can I expose Builder-CI API on Internet ?

This is not recommended unless you protect the entry points with nginx and authentication. I strongly do not recommend that you expose your server on the internet. Just keep it private and secret.

### Can I use Podman instead of Docker ?

Sure, it will come soon, wait a bit, be patient.
