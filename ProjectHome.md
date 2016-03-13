# Overview #

`drupal2mail` is a Python library that enables developers to automate the management of email redirections based on Drupal's usernames and their respective registered email addresses.

Currently, the configuration of the mailserver only supports [WebFaction](http://www.webfaction.com).

`drupal2mail` is distributed under the [GNU General Public License v3](http://www.gnu.org/licenses/gpl.html).

# A Quick Example #
```
import drupal2mail

# Initializes the library
drupal2mail.Init()

# Reads the usernames and their registered email addresses
sources = drupal2mail.GetSources()

# Reads the current mail directions from the mail server
targets = drupal2mail.GetTargets()

# Updates or creates redirections
drupal2mail.UpdateEmails(sources, targets)
```

By default, the logs will be written into `drupal2mail.log` in the current directory.  This is configurable in `drupal2mail.yaml`.

Also, the library has a `DRY_RUN` boolean variable that is set to `True` by default, which means nothing will be written.  Set this variable to `False` to enable the write mode.  This is not very clean and will be moved to the configuration file shortly (see http://code.google.com/p/drupal2mail/issues/detail?id=1).

# Configuration #
The library is configured through `drupal2mail.yaml` ([sample configuration](http://code.google.com/p/drupal2mail/source/browse/trunk/drupal2mail.yaml.sample)).