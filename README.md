Builder CI is a automated Build system used to do Continuous Integration of any kind of development. I made this software as I wish to configure pipeline in much more automated way than any other product like Jenkins does. This builder is made to work with Redmine thanks to a Redmine plugin (will be released soon).

## Features

* Detect automatically what kind of build to do (deb, rpm).
* Exposed unsecure (yet) API used to trigger builds.
* Create Debian or Redhat repository automatically after build.
* Modulable, extend it by creating your own builder plugin.
* Very lightweight, built with love with python and only few modules.
* Very easy to install and update all in one command (on Debian Buster).
* Built on top of Mongo and Flask.
* Use Docker (or not) to have clean environment at each build.
* Support hooks folder used to prepare your build environment.
* Build as Code, provide few parameters within builder.yml file.

## Type of build supported so far

* Debian/Ubuntu packages (pbuilder).
* Redhat/Centos packages (rpmbuild).
* Ionic and Flutter APK (docker).
* NPM Package.

## Type of publication

* Create repository on server itself (rpm and deb)
* Publish file on Redmine files project.

## To come

* Install several workers and distribute builds.
* More kind of packages.
* A much better documentation.
* Any requests ?

## How to install (~2 minutes)

Requirement : run all those command as root.

~~~ bash
# Install Mongo (Mandatory)
curl -s https://download.docker.com/linux/debian/gpg | apt-key add -
echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" \
    > /etc/apt/sources.list.d/mongo.list
apt update && apt install mongodb-server
systemctl enable --now mongod

# Install Docker (Optional)
curl -s https://www.mongodb.org/static/pgp/server-${VERSION}.asc | apt-key add -
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian buster stable" \
    > /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce

# Install Builder CI
echo "deb [trusted=yes] https://projects.iabsis.com/repository/api-auto-builder/debian buster main" \
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
  }
}'

# Check your build and delete it
builder-ci list
find /tmp/reprepo && rm -rf /tmp/reprepo
~~~

## Frequently asked questions

### How does it work

Two services are run on the server :

- API called `builder-ci-api` running on port 5000. Use this to manually trigger a build.
- Worker called `build-ci-worker`. This service listen on Mongo event and immediately start a build when required.

When a new build is added into `queue` table of Mongo, the Worker execute steps in this order.

-> sources -> builder -> publish

Source step usually calls git method (new method to come) in order to get source code of the app. Then builder step attempt to define kind of build to do unless it has been manually defined (in API call or builder.yml). At the end, publish step copy the result, either into local repository, or do a post into specific area, like Redmine project files.

### Is it ready for production ?

I personnally use this product for my dev company and this is answering to 99% of our requirements while we are building various kind of framework (Laravel, Symfony, Ionic, Flutter, NestJS, Angular, React, ...) in target of various Operating System (Android, Debian, Ubuntu, Redhat, Centos, ...).

In other word, it may not fit for your requirements, but I consider it's stable enough.

### Is there a complete documentation ?

Not yet, I'm looking to generate documentation based on methods and argument required for each. I will also provide a more concrete guide to cover various configuration and how to integrate with Redmine.

### How to trigger a build when code is pushed ?

Simply copy and adapt `/usr/share/doc/builder-ci/helpers/git-core.py` into `/usr/share/git-core/templates/hooks` and `<git bare>/.git/hooks/`.

### How can I have a visual way to see my build status ?

Simply install the Redmine module called `Redmine Builder CI`.

### My build failed, how I can see logs ?

Simply get the list of builds with `builder-ci list` and then get logs with `builder-ci logs <id_from_list>`.

### Why my build has status Duplicate ?

This is normal behaviour, builder-ci guess to get package version, if this version already exists with success status, the build is cancelled in a second.

### Can I expose Builder-CI API on Internet ?

No, unless you protect it with nginx and authentication, I strongly not recommend to expose your server on internet. Just keep it private and secret.

### Can I use Podman instead of Docker ?

I didn't tried yet, make a try and let me know ;-)
