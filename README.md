# Yuyu

Yuyu provide ability to manage openstack billing by listening to every openstack event. Yuyu is a required component to use Yuyu Dashboard. There are 3 main component in Yuyu: API, Cron, Event Monitor

## Yuyu API

Main component to communicate with Yuyu Dashboard.

## Yuyu Cron

Provide invoice calculation and rolling capabilities that needed to run every month.

## Yuyu Event Monitor

Monitor event from openstack to calculate billing spent.

# System Requirement

- Python 3
- Openstack
- Virtualenv
- Linux environment with Systemd

# Pre-Installation

### Virtualenv

Make sure you installed virtualenv before installing Yuyu

```bash
pip3 install virtualenv
```

### Timezone

Billing is a time sensitive application, please make sure you set a correct time and timezone on you machine.

### Openstack Service Notification

You need to enable notification for this openstack service:

- Nova (nova.conf)
- Cinder (cinder.conf)
- Neutron (neutron.conf)
- Keystone (keystone.conf)

### Nova

Add configuration below on `[oslo_messaging_notifications]`

```
driver = messagingv2 
topics = notifications
```

Add configuration below on `[notifications]`

```
notify_on_state_change = vm_and_task_state
notification_format = unversioned
```

### Cinder & Neutron & Keystone

Add configuration below on `[oslo_messaging_notifications]`

```
driver = messagingv2 
topics = notifications
```

### Kolla Note

If you using Kolla, please add configuration above on all service container. For example on Nova you should put the
config on `nova-api`, `nova-scheduler`, etc.

# Installation

Clone the latest source code and put it on any directory you want. Here i assume you put it on `/var/yuyu/`

```bash
cd /var/yuyu/
git clone {repository}
cd yuyu
```

Then create virtualenv and activate it

```bash
virtualenv env --python=python3.8
source env/bin/activate
pip install -r requirements.txt
```

Then create a configuration file, just copy from sample file and modify as your preference.

```bash
cp yuyu/local_settings.py.sample yuyu/local_settings.py
```

Please read [Local Setting Configuration](#local-setting-configuration) to get to know about what configuration you
should change.

Then run the database migration

```bash
python manage.py migrate
```

Then create first superuser

```bash
python manage.py createsuperuser
```

## Local Setting Configuration

### YUYU_NOTIFICATION_URL (required)

A Messaging Queue URL that used by Openstack, usually it is a RabbitMQ URL.

Example:

```
YUYU_NOTIFICATION_URL = "rabbit://openstack:password@127.0.0.1:5672/"
```

### YUYU_NOTIFICATION_TOPICS (required)

A list of topic notification topic that is configured on each openstack service

Example:

```
YUYU_NOTIFICATION_TOPICS = ["notifications"]
```

### DATABASE

By default, it will use Sqlite. If you want to change it to other database please refer to Django Setting documentation.

- https://docs.djangoproject.com/en/3.2/ref/settings/#databases
- https://docs.djangoproject.com/en/3.2/ref/databases/

## API Installation

To install Yuyu API, you need to execute this command.

```bash
./bin/setup_api.sh
```

This will install `yuyu_api` service

To start the service use this command

```bash
systemctl enable yuyu_api
systemctl start yuyu_api
```

An API server will be open on port `8182`.

## Event Monitor Installation

To install Yuyu API, you need to execute this command.

```bash
./bin/setup_event_monitor.sh
```

This will install `yuyu_event_monitor` service

To start the service use this command

```bash
systemctl enable yuyu_event_monitor
systemctl start yuyu_event_monitor
```

## Cron Installation

There is a cronjob that needed to be run every month on 00:01 AM. This cronjob will finish all in progress invoice and
start new invoice for the next month.

To install it, you can use `crontab -e`.

Put this expression on the crontab

```
1 0 1 * * $yuyu_dir/bin/process_invoice.sh 
```

Replace $yuyu_dir with the directory of where yuyu is located. Example

```
1 0 1 * * /var/yuyu/bin/process_invoice.sh
```

# Updating Yuyu

To update Yuyu manually, you can just pull the latest code

```bash
git pull release/xx.xx
```

Activate the virtualenv.

```bash
source env/bin/activate
```

Change the setting if needed.

```bash
nano yuyu/local_settings.py
```

Update the python package.

```bash
pip install -r requirements.txt
```

Run database migration

```bash
python manage.py migrate
```

Restart all the service

```bash
systemctl restart yuyu_api
systemctl restart yuyu_event_monitor
```

# Other Feature

Yuyu also have other feature that need to be setup to use.

## Unpaid Invoice Handling

Unpaid invoice handling can run a task on a specific day after invoice is issued and not yet paid.

For example, you can send email to remind customer to pay the invoice or delete all instance on a specific day.

Available action for unpaid invoice handling consist of:

- send_message : Sending a message to a customer
- stop_instance : Will stop, compute instance
- delete_instance : Will delete compute, image, router, snapshot or volume

### Enabling Unpaid Invoice Handling

1. Download `clouds.yaml` configuration from Openstack API Dashboard
2. Make sure you also set the password in `clouds.yaml`. Example:
   ```yaml
   clouds:
     openstack:
       auth:
         auth_url: http://172.10.10.150:5000
         username: "admin"
         password: "your_password"
         project_id: 0000000000000000000000000
         project_name: "admin"
         user_domain_name: "Default"
       region_name: "ID"
       interface: "public"
       identity_api_version: 3
   ```
3. Put `clouds.yaml` in one of the following directory.
    - Current Yuyu Directory
    - ~/.config/openstack
    - /etc/openstack
4. Setup the configuration in `local_settings.py`. See **Configuration** for detail.

   Example config can follow
   ```python
   CLOUD_CONFIG_NAME = "openstack"
   UNPAID_INVOICE_HANDLER_CONFIG = [
       {
           "day": 5,
           "action": "send_message",
           "message_title": "Your invoice has been expired. Please pay now!",
           "message_short_description": "Your invoice has been expired. Please pay now!",
           "message_content": "Your invoice has been expired. Please pay now!",
       },
       {
           "day": 10,
           "action": "stop_instance",
       },
       {
           "day": 10,
           "action": "send_message",
           "message_title": "Your compute instance will be stopped",
           "message_short_description": "Your compute instance will be stopped",
           "message_content": "Your compute instance will be stopped because you have unpaid invoice",
       },
       {
           "day": 15,
           "action": "send_message",
           "message_title": "All of your instance has been deleted",
           "message_short_description": "All of your instance has been deleted",
           "message_content": "All of your instance has been deleted because you have unpaid invoice",
       },
       {
           "day": 15,
           "action": "delete_instance",
       },
   ]
   ```
5. Setup `cronjob` to run the action every day at 1 AM or change it your preferred time to run

   To install it, you can use `crontab -e`.

   Put this expression on the crontab

   ```
   0 1 * * * $yuyu_dir/bin/handle_unpaid_invoice.sh 
   ```

   Replace $yuyu_dir with the directory of where yuyu is located. Example
   ```
   0 1 * * * /var/yuyu/bin/handle_unpaid_invoice.sh
   ```
6. Check the connection to openstack with
   ```
   ./bin/check_openstack_connection.sh
   ```
   Make sure it doesn't return error.
7. Done

### Configuration

To use Unpaid Invoice Handling you need to set up the following variable in `local_settings.py`

- CLOUD_CONFIG_NAME
- UNPAID_INVOICE_HANDLER_CONFIG

#### CLOUD_CONFIG_NAME

CLOUD_CONFIG_NAME Is configuration in `clouds.yaml` that you want to use to connect to openstack.

Example: Your `clouds.yaml` is

```yaml
clouds:
  openstack:
    auth:
      auth_url: http://172.10.10.150:5000
      username: "admin"
      password: "your_password"
      project_id: 0000000000000000000000000
      project_name: "admin"
      user_domain_name: "Default"
    region_name: "ID"
    interface: "public"
    identity_api_version: 3
```

You can put `openstack` as `CLOUD_CONFIG_NAME`

So it will be

```python
CLOUD_CONFIG_NAME = "openstack"
```

### UNPAID_INVOICE_HANDLER_CONFIG

UNPAID_INVOICE_HANDLER_CONFIG Is configuration for an action that will be run on a particular day after invoice is
issued and still unpaid

The available action that can be used is

- send_message : Sending a message to a customer
- stop_instance : Will stop, compute instance
- delete_instance : Will delete compute, image, router, snapshot or volume

UNPAID_INVOICE_HANDLER_CONFIG is list of dictionary, you can add as many config as you want to the list that will be run
on a particular day.

The format for config dictionary is

```python
{
    "day": 0,
    "action": "the_action",
}
```

The most important part is `day` and `action`.

- `day`: The day of the action that will be run. For example if you put `5` it will run in 5 day after invoice is issued
  and still unpaid
- `action`: The action that you want to run. It can be `send_message`/`stop_instance`/`delete_instance`.

If you use `send_message` action, you need to add additional config.

- `message_title` : The title or subject of the message
- `message_short_description` : The short description of message
- `message_content`: The content of the message

Example:

```python
{
    "day": 0,
    "action": "send_message",
    "message_title": "Title",
    "message_short_description": "Short Description",
    "message_content": "The Content",
}
```

This is example config that you can use as a reference

```python
CLOUD_CONFIG_NAME = "openstack"
UNPAID_INVOICE_HANDLER_CONFIG = [
    {
        "day": 5,
        "action": "send_message",
        "message_title": "Your invoice has been expired. Please pay now!",
        "message_short_description": "Your invoice has been expired. Please pay now!",
        "message_content": "Your invoice has been expired. Please pay now!",
    },
    {
        "day": 10,
        "action": "stop_instance",
    },
    {
        "day": 10,
        "action": "send_message",
        "message_title": "Your compute instance will be stopped",
        "message_short_description": "Your compute instance will be stopped",
        "message_content": "Your compute instance will be stopped because you have unpaid invoice",
    },
    {
        "day": 15,
        "action": "send_message",
        "message_title": "All of your instance has been deleted",
        "message_short_description": "All of your instance has been deleted",
        "message_content": "All of your instance has been deleted because you have unpaid invoice",
    },
    {
        "day": 15,
        "action": "delete_instance",
    },
]
```