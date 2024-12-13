import json
import os
import random
import pymysql
import apps

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'actowiz',
    'database': 'jmax',
}

config_path = 'configs/config.json'


# Database connection
def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )


def help_commands():
    descriptions = {}
    with open(f'{os.getcwd()}\configs\help_description.txt', 'r') as f:
        for line in f.readlines():
            if line.strip():
                command, description = line.split(":", 1)
                descriptions[command.strip()] = description.strip()
    return descriptions


def counts(project_id, from_date, to_date):
    # Load the JSON config file
    with open(config_path, 'r') as file:
        config = json.load(file)

    # Get the function configuration for the project
    func_name = config['counts'].get(str(project_id), {}).get('count_func_name')
    
    if not func_name:
        return f"**The function is not defined in config.**"
    
    # Call the function from the apps module
    try:
        return getattr(apps, func_name)(from_date, to_date)
    except AttributeError:
        return f"The function **{func_name}** is not defined in the apps module."


def generate_random_id():
    return f"{random.randint(0, 9999):04}"


def generate_id(project_name):
    conn = get_db_connection()
    cur = conn.cursor()
    
    while True:
        project_id = generate_random_id()
        cur.execute(f'select * from projects where project_name = %s', project_name)
        if cur.fetchone():
            return f"Project with **{project_name}** already available in database.."
        
        try:
            # Attempt to insert into the database
            cur.execute("INSERT INTO projects (project_id, project_name) VALUES (%s, %s)", (project_id, project_name))
            conn.commit()
            break  # Break the loop if insertion is successful
        except pymysql.IntegrityError:
            # If duplicate ID, regenerate and retry
            continue
    try:
        with open(config_path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {"counts": {}}

    # Update the JSON data
    data["counts"][str(project_id)] = {"count_func_name": ""}

    # Save the updated JSON file
    with open(config_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    conn.close()
    
    return f"Project **'{project_name}'** created with ID: **{project_id}**"
    
    