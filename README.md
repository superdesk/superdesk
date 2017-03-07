# Superdesk
[![Build Status](https://travis-ci.org/superdesk/superdesk.png?branch=master)](https://travis-ci.org/superdesk/superdesk)
[![Code Health](https://landscape.io/github/superdesk/superdesk/master/landscape.svg?style=flat)](https://landscape.io/github/superdesk/superdesk/master)
[![Coverage Status](https://coveralls.io/repos/superdesk/superdesk/badge.svg)](https://coveralls.io/r/superdesk/superdesk)
[![Code Climate](https://codeclimate.com/github/superdesk/superdesk/badges/gpa.svg)](https://codeclimate.com/github/superdesk/superdesk)
[![Requirements Status](https://requires.io/github/superdesk/superdesk/requirements.svg?branch=master)](https://requires.io/github/superdesk/superdesk/requirements/?branch=master)

Superdesk is an open source end-to-end news creation, production, curation,
distribution and publishing platform developed and maintained by Sourcefabric
with the sole purpose of making the best possible software for journalism. It
is scaleable to suit news organizations of any size. See the [Superdesk website] (http://www.superdesk.org) for more information.

Looking to stay up to date on the latest news? [Subscribe] (http://eepurl.com/bClQlD) to our monthly newsletter.

The Superdesk server provides the API to process all client requests. The client
provides the user interface. Server and client are separate applications using
different technologies.

Find more information about the client configuration in the README file of the repo:
[https://github.com/superdesk/superdesk-client-core](https://github.com/superdesk/superdesk-client-core "")

## Installation on fresh Ubuntu 16.04

```sh
# replace <you_ip_or_domain> with domain where Superdesk will be accessible
(echo HOST=<you_ip_or_domain>; curl https://raw.githubusercontent.com/superdesk/fireq/master/files/superdesk/install) | sudo bash
```
Details you can find [here][fireq] or just read [superdesk/install][fireq-install] file.

###Questions and issues

- Our [issue tracker] (https://dev.sourcefabric.org/projects/SD) is only for bug reports and feature requests.
- Questions regarding the installation should be posted to [fireq issues][fireq-issues].
- Anything else, such as questions or general feedback, should be posted in the [forum] (https://forum.sourcefabric.org/categories/superdesk-dev).

###A special thanks to...

Users, developers and development partners that have contributed to the Superdesk project. Also, to all the other amazing open-source projects that make Superdesk possible!

###License

Superdesk is available under the [AGPL version 3] (https://www.gnu.org/licenses/agpl-3.0.html) open source license.

[fireq]: https://github.com/superdesk/fireq
[fireq-install]: https://github.com/superdesk/fireq/blob/master/files/superdesk/install
[fireq-issues]: https://github.com/superdesk/fireq/issues
