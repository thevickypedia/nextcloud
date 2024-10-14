NEXTCLOUD_CONTAINER_NAME="nextcloud_server"
USERNAME="my-username"

cleanup() {
  docker volume rm $(docker volume ls -qf dangling=true)
	docker system prune
  sudo rm -rf data/ nextcloud/
}

startup() {
  docker-compose up -d

  # Login through the UI to instantiate and install nextcloud
  # Alternate:
	#	https://docs.nextcloud.com/server/30/admin_manual/installation/command_line_installation.html
	# sudo vi nextcloud/config/config.php -> Set 'dbhost' to 'db' [docker-compose.yml]
	#	docker exec -u 33 nextcloud_server chown -R www-data:www-data /var/www/html/
	#	docker exec -u 33 nextcloud_server php occ maintenance:install \
	#		--database "mysql" \
	#		--database-name "nextcloud" \
	#		--database-user "nextcloud" \
	#		--database-pass="${MYSQL_PASSWORD}" \
	#		--admin-user "${USERNAME}" \
	#		--admin-pass "${PASSWORD}"

  docker-compose down

  # Uncomment the volume mount on the particular user profile

  docker-compose up -d

  # Sync files from mounted volume

  docker exec -u www-data ${NEXTCLOUD_CONTAINER_NAME} php occ files:scan --all

  # docker exec -u www-data ${NEXTCLOUD_CONTAINER_NAME} php occ files:scan ${USERNAME}

  # sudo vi nextcloud/config/config.php -> Add new IPs to the allowed list
}

set_permissions() {
	# Steps to rename disks
	# 1. Open 'disks' app in Ubuntu
	# 2. Select the partition of your choice in the Volume section
	# 3. Click Edit Filesystem (Label)
	# 4. Enter a name in the field and click on Apply to validate.

   sudo chown -R www-data:www-data /var/www/html/data/${USERNAME}/files/photos

   sudo chown -R www-data:www-data "/media/${USER}/Pictures/DCIM"
   sudo chmod -R 755 "/media/${USER}/Pictures/DCIM"
}
