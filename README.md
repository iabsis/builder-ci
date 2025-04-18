# Builder CI

Builder CI is an automated build system designed to support Continuous Integration (CI) across various types of development projects. It was created with the goal of simplifying and automating build pipelines in a more efficient way than traditional tools like Jenkins.

It’s designed to optionally integrate with [Redmine](https://www.redmine.org/) via a [dedicated plugin](https://github.com/iabsis/redmine-builder-ci), allowing better visibility into builds directly within project management workflows.

[Redmine Screenshot](https://raw.githubusercontent.com/iabsis/builder-ci/master/doc/redmine_screenshot.png)

---

## Features

- Automatically detects the build type (e.g., `.deb`, `.rpm`)
- Exposes a REST API to trigger builds (authentication coming soon)
- Creates Debian or Red Hat repositories after each build
- Modular and extensible — build your own plugin if needed
- Lightweight: built with Python and minimal dependencies
- Easy to install and update with a single command on Debian Buster
- Uses MongoDB and Flask at the core
- Optional Docker support for isolated build environments
- Supports pre-build setup with a `hooks` directory
- "Build as Code": configure builds using a `builder.yml` file

---

## Supported Build Types

- Debian/Ubuntu packages (`pbuilder`)
- Red Hat/CentOS packages (`rpmbuild`)
- Ionic and Flutter APKs (via Docker)
- NPM packages

---

## Publication Options

- Host build artifacts as a `.deb` or `.rpm` repository on the server
- Publish files directly into a Redmine project (as uploads)

---

## Upcoming Improvements

- Support for distributed builds using multiple workers
- Addition of new builder types
- Extended documentation and integration guides

---

## Installation Guide (Takes ~2 Minutes)

> Note: All commands should be run as `root`.

### Install MongoDB (Required)

```bash
curl -s https://www.mongodb.org/static/pgp/server-${VERSION}.asc | apt-key add -
echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" > /etc/apt/sources.list.d/mongo.list
apt update && apt install mongodb-server

echo -e "replication:\n   replSetName: \"rs0\"" >> /etc/mongod.conf
systemctl enable --now mongod

mongo
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" }
  ]
})
```

---

### Install Docker (Optional, Recommended)

```bash
curl -s https://download.docker.com/linux/debian/gpg | apt-key add -
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian buster stable" > /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce
```

---

### Install Builder CI

```bash
echo "deb [trusted=yes] https://projects.iabsis.com/repository/builder-ci/debian buster main" > /etc/apt/sources.list.d/iabsis.list
apt update && apt install builder-ci
```

---

## Trigger Your First Build

```bash
curl -X 'POST' \
  'http://<your-build-server-ip>:5000/build' \
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
```

---

## Check or Clean Builds

```bash
builder-ci list
rm -rf /var/lib/repo/builder-ci
```

---

## How It Works

Builder CI runs two main services:

- `builder-ci-api`: A REST API server running on port 5000
- `build-ci-worker`: Listens for MongoDB events and processes builds automatically

**Build Lifecycle:**

```
sources → builder → publish
```

1. **sources**: Clones the Git project  
2. **builder**: Detects or uses the build type from `builder.yml`  
3. **publish**: Publishes output to a Redmine project or server repository

---

## Frequently Asked Questions

### Is Builder CI stable for production use?

Yes. It's used in production with frameworks like Laravel, Symfony, Ionic, Flutter, NestJS, Angular, and React across platforms such as Android, Debian, Ubuntu, Red Hat, and CentOS.

### Is there complete documentation?

Not yet. Work is in progress to auto-generate method documentation and integration guides for Redmine.

### Can I trigger builds automatically on code push?

Yes. Use the provided Git hook:

```bash
/usr/share/doc/builder-ci/helpers/git-core.py
```

Copy it into:

```bash
/usr/share/git-core/templates/hooks
<your_git_repo>/.git/hooks/
```

### How do I view build status?

Install the [Redmine Builder CI Plugin](https://github.com/iabsis/redmine-builder-ci) to visualize build status within Redmine.

### How do I view build logs?

```bash
builder-ci list
builder-ci logs <build_id>
```

### Why is my build marked as "Duplicate"?

This happens when the same version has already been successfully built. Update the version to trigger a new build.

---

## Security Notice

The current version exposes the Builder CI API without authentication. If deploying in a shared or production environment, it is highly recommended to:

- Use NGINX as a reverse proxy with IP whitelisting and rate limiting
- Add firewall-level restrictions
- Avoid exposing the API directly to the public internet

---

## Contributing

We welcome contributions of all kinds — including code, documentation, bug reports, and feature suggestions.

While formal contributing guidelines are coming soon, you can:

- Fork the repository
- Create a new branch for your changes
- Open a pull request
- Share feedback via comments or discussions

---

## License

Builder CI is licensed under the [GPL-3.0 License](LICENSE).

