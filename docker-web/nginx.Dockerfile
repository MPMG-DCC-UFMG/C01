# Nginx application
FROM nginx:1.19.10

# Create nginx configuration for our Django app
RUN rm /etc/nginx/conf.d/default.conf
COPY docker-web/c01-web.conf /etc/nginx/conf.d/c01-web.conf

# This section is based on this
# https://gonzalo123.com/2020/12/14/running-python-django-docker-containers-with-non-root-user/

RUN chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    chmod -R 766 /var/log/nginx/

RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Create the folder for the staticfiles volume
RUN mkdir -p /home/nginx/staticfiles
RUN chown -R nginx:nginx /home/nginx

# Change to the nginx user
USER nginx
