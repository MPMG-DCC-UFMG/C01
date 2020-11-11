Settings
================

This page covers the various settings contained within the Rest service. The sections are broken down by functional component.

Core
----

**FLASK_LOGGING_ENABLED**

Default: ``True``

Enable Flask application logging, independent of Scrapy Cluster logging.

**FLASK_PORT**

Default: ``5343``

The default port for the Rest service to listen on. The abbreviation ``SC`` equals ``5343`` in hexidecimal.

**SLEEP_TIME**

Default: ``0.1``

The number of seconds the main threads will sleep between checking for items.

**HEARTBEAT_TIMEOUT**

Default: ``120``

The amount of time the heartbeat key the Rest service instance lives to self identify to the rest of the cluster. Used for retrieving stats about the number of Rest service instances currently running.

**DAEMON_THREAD_JOIN_TIMEOUT**

Default: ``10``

The amount of time provded to the daemon threads to safely close when the instance is shut down.

.. _wait_for_response_time:

**WAIT_FOR_RESPONSE_TIME**

Default: ``5``

The amount of time the Rest service will wait for a response from Kafka before converting the request into a ``poll``.

**SCHEMA_DIR**

Default: ``'schemas/'``

The directory for the Rest Service to automatically load JSON Schemas that can be used by the application.

Redis
-----

**REDIS_HOST**

Default: ``'localhost'``

The Redis host.

**REDIS_PORT**

Default: ``6379``

The port to use when connecting to the ``REDIS_HOST``.

**REDIS_DB**

Default: ``0``

The Redis database to use when connecting to the ``REDIS_HOST``.

**REDIS_PASSWORD**

Default: ``None``

The password to use when connecting to the ``REDIS_HOST``.

**REDIS_SOCKET_TIMEOUT**

Default: ``10``

The number of seconds to wait while establishing a TCP connection, or to wait for a response from an existing TCP connection before timing out.

Kafka
-----

**KAFKA_HOSTS**

Default: ``'localhost:9092'``

The Kafka host. May have multiple hosts separated by commas within the single string like ``'h1:9092,h2:9092'``.

**KAFKA_TOPIC_PREFIX**

Default: ``'demo'``

The Kafka Topic prefix used for listening for Redis Monitor results.

**KAFKA_FEED_TIMEOUT**

Default: ``10``

How long to wait (in seconds) before timing out when trying to feed a JSON string into the ``KAFKA_INCOMING_TOPIC``

**KAFKA_CONSUMER_AUTO_OFFSET_RESET**

Default: ``'latest'``

When the Kafka Consumer encounters and unexpected error, move the consumer offset to the 'latest' new message, or the 'earliest' available.

**KAFKA_CONSUMER_TIMEOUT**

Default: ``50``

Time in ms spent to wait for a new message during a ``feed`` call that expects a response from the Redis Monitor

**KAFKA_CONSUMER_COMMIT_INTERVAL_MS**

Default: ``5000``

How often to commit Kafka Consumer offsets to the Kafka Cluster

**KAFKA_CONSUMER_AUTO_COMMIT_ENABLE**

Default: ``True``

Automatically commit Kafka Consumer offsets.

**KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES**

Default: ``10 * 1024 * 1024``

The maximum size of a single message to be consumed by the Kafka Consumer. Defaults to 10 MB

**KAFKA_CONSUMER_SLEEP_TIME**

Default: ``1``

The length of time to sleep by the main thread before checking for new Kafka messages

**KAFKA_PRODUCER_TOPIC**

Default: ``demo.incoming``

The topic that the Kafka Monitor is litening for requests on.

**KAFKA_PRODUCER_BATCH_LINGER_MS**

Default: ``25``

The time to wait between batching multiple requests into a single one sent to the Kafka cluster.

**KAFKA_PRODUCER_BUFFER_BYTES**

Default: ``4 * 1024 * 1024``

The size of the TCP send buffer when transmitting data to Kafka

Logging
-------

**LOGGER_NAME**

Default: ``'rest-service'``

The logger name.

**LOG_DIR**

Default: ``'logs'``

The directory to write logs into. Only applicable when ``LOG_STDOUT`` is set to ``False``.

**LOG_FILE**

Default: ``'rest_service.log'``

The file to write the logs into. When this file rolls it will have ``.1`` or ``.2`` appended to the file name. Only applicable when ``LOG_STDOUT`` is set to ``False``.

**LOG_MAX_BYTES**

Default: ``10 * 1024 * 1024``

The maximum number of bytes to keep in the file based log before it is rolled.

**LOG_BACKUPS**

Default: ``5``

The number of rolled file logs to keep before data is discarded. A setting of ``5`` here means that there will be one main log and five rolled logs on the system, generating six log files total.

**LOG_STDOUT**

Default: ``True``

Log to standard out. If set to ``False``, will write logs to the file given by the ``LOG_DIR/LOG_FILE``

**LOG_JSON**

Default: ``False``

Log messages will be written in JSON instead of standard text messages.

**LOG_LEVEL**

Default: ``'INFO'``

The log level designated to the logger. Will write all logs of a certain level and higher.

.. note:: More information about logging can be found in the utilities :ref:`Log Factory <log_factory>` documentation.
