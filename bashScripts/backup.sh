#!/bin/bash

source /home/avyuthan-shah/Desktop/F1Intern/WeekendTask/Airflow/bashScripts/delete.sh

current_date=$(date +"%Y%m%d_%H%M%S")

backupPath="/home/avyuthan-shah/Desktop/F1Intern/WeekendTask/Airflow/sqlDumps"
mysql_host="localhost"
mysql_port="3306"
db_name="mydB"

# SQL query to get the total size of the database in bytes
SQL_QUERY="SELECT SUM(data_length + index_length) FROM information_schema.tables WHERE table_schema='${db_name}';"
# Execute the SQL query and store the result in a variable
DB_SIZE_BYTES=$(mysql -h ${mysql_host} -P ${mysql_port} -sse "${SQL_QUERY}")
DB_SIZE=$(echo "scale=2; ${DB_SIZE_BYTES}/1000^3" | bc)

# echo ${DB_SIZE}

#Calculate total availabe space in the system
TOTAL_FREE_SPACE_KB=$(df --output=avail -x tmpfs -x devtmpfs -x squashfs -x overlay -x aufs | awk 'NR>1 {sum += $1} END {print sum}')
# Convert total free space from KB to GB (For 1000 block size)
FREE_SPACE=$(echo "scale=2; ${TOTAL_FREE_SPACE_KB}/1000^2" | bc)


if [ $(echo "${DB_SIZE} < ${FREE_SPACE}" | bc) -eq 1 ];then
    
    start_time=$(date +%s)

    BACKUP_FILE="${backupPath}/${db_name}_${current_date}.sql.gz"
    mysqldump -h ${mysql_host} -P ${mysql_port} ${db_name} | gzip > ${BACKUP_FILE}

    deleteFile ${backupPath}

    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    echo "Backup completed in ${elapsed_time} seconds"

    messageOut="Backup Success in location: ${backupPath}|Required Space: ${DB_SIZE}GB, Available Space: ${FREE_SPACE}GB"

else
    messageOut="Backup Failed.|Required Space: ${DB_SIZE}GB, Available Space: ${FREE_SPACE}GB"
fi

echo "$messageOut" #output message for Airflow to pick up