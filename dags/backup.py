from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
# import json

# JSON_FILE = '/home/avyuthan-shah/Desktop/F1Intern/WeekendTask/Airflow/credentials.json'
# with open(JSON_FILE, 'r') as f:
#     credentials = json.load(f)['smtp_credentials']

# Define default arguments
default_args = {
    'owner': 'avyu',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 17),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=10),  # Retry every 30 seconds in case of failure
    'catchup':False,
}

# Define DAG with cron scheduling
dag = DAG(
    'Backup_Database',
    default_args=default_args,
    description='Daily backup of database and email notification',
    #schedule_interval=timedelta(minutes=5),  
    schedule_interval='0 0 * * *',  # m hr d mon day
)

backup_task=BashOperator(
    task_id='backup_task',
    bash_command='/home/avyuthan-shah/Desktop/F1Intern/WeekendTask/Airflow/bashScripts/backup.sh ',
    # template_undefined=True,
    do_xcom_push=True,
    dag=dag,
)
def parse_message_out(**kwargs):
    ti = kwargs['ti']
    message_out = ti.xcom_pull(task_ids='backup_task')
    if '|' in message_out:
        status, space_check = message_out.split('|', 1)
        formatted_content = f"""
            <p><strong>Status:</strong> {status.strip()}</p>
            <p><strong>Space Check:</strong> {space_check.strip()}</p>
        """
    else:
        formatted_content = f"<p>{message_out.strip()}</p>"

    # Push formatted content to XCom
    ti.xcom_push(key='email_content', value=formatted_content)

parse_task = PythonOperator(
    task_id='parse_task',
    python_callable=parse_message_out,
    provide_context=True,
    dag=dag,
)

send_mail = EmailOperator(
    task_id='send_mail',
    to='avyuthan364@gmail.com',
    subject='Database Backup Status',
    html_content="{{ task_instance.xcom_pull(task_ids='parse_task', key='email_content') }}",
    
    # smtp_conn_id=None,
    # smtp_user=credentials['smtp_user'],
    # smtp_password=credentials['smtp_password'],
    #email operator didnt allow to manual declaration of smtp credentials
    dag=dag,
)

backup_task >> parse_task >> send_mail
