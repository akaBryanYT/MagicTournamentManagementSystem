# Tournament Management System

A comprehensive web application for managing tournament events, players, decks, and matches. This system is particularly suited for card game tournaments like Magic: The Gathering.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Project Structure](#project-structure)
- [Database Setup](#database-setup)
  - [PostgreSQL Setup on Windows](#postgresql-setup-on-windows)
  - [PostgreSQL Setup on Fedora/Linux](#postgresql-setup-on-fedoralinux)
  - [MongoDB Setup on Windows](#mongodb-setup-on-windows)
  - [MongoDB Setup on Fedora/Linux](#mongodb-setup-on-fedoralinux)
  - [MongoDB Atlas Setup](#mongodb-atlas-setup)
- [Starting the Database](#starting-the-database)
  - [Starting PostgreSQL](#starting-postgresql)
  - [Starting MongoDB](#starting-mongodb)
  - [Verifying Database Connection](#verifying-database-connection)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This Tournament Management System (TMS) enables organizers to create and manage tournaments, register players, record match results, and track player statistics. The application consists of a Python Flask backend API and a React TypeScript frontend.

## Features

- Tournament creation and management
- Player registration and profiles
- Deck registration and validation
- Swiss pairing generation
- Tournament standings and statistics
- Match result recording
- Card database integration

## System Requirements

- Python 3.8+
- Node.js 18+ and npm
- PostgreSQL 14+ or MongoDB 6.0+
- Git

## Project Structure

The project is organized into two main directories:

- **backend/**: Flask-based API server
- **frontend/**: React TypeScript application

## Database Setup

### PostgreSQL Setup on Windows

1. **Download PostgreSQL**
   - Visit the [PostgreSQL Download page](https://www.postgresql.org/download/windows/)
   - Download the PostgreSQL installer from EnterpriseDB
   - Choose the latest stable version (14.x or 15.x)

2. **Run the installer**
   - Launch the downloaded executable
   - Follow the installation wizard
   - When prompted, set a password for the `postgres` superuser (remember this password)
   - Keep the default port `5432`
   - Select your locale
   - Ensure "pgAdmin 4" is selected for installation (GUI management tool)

3. **Verify installation**
   - After installation completes, open the Start menu and find "pgAdmin 4"
   - Launch pgAdmin 4 and enter your master password when prompted
   - Connect to the PostgreSQL server with the `postgres` user and password you created

4. **Create the Tournament Management database**
   - In pgAdmin, right-click on "Databases" in the browser tree
   - Select "Create" > "Database..."
   - Enter `tournament_management` as the database name
   - Set owner to `postgres`
   - Click "Save"

5. **Create a database user**
   - Right-click on "Login/Group Roles" in the browser tree
   - Select "Create" > "Login/Group Role..."
   - On the "General" tab, set the name to `tms_user`
   - On the "Definition" tab, set a password
   - On the "Privileges" tab, enable "Can login?" and "Create database"
   - Click "Save"

6. **Grant privileges to the user**
   - Right-click the `tournament_management` database
   - Select "Properties"
   - Click on the "Security" tab
   - Click the "+" button to add a new privilege
   - Select "tms_user" from the dropdown
   - Check ALL privilege boxes (CONNECT, CREATE, TEMPORARY, USAGE)
   - Click "Save"
   
   - Next, expand the "tournament_management" database
   - Expand "Schemas"
   - Right-click on the "public" schema
   - Select "Properties"
   - Go to the "Security" tab
   - Click "+" to add a privilege
   - Select "tms_user"
   - Check ALL privileges
   - Click "Save"
   
   - Finally, open the Query Tool for the tournament_management database
     (Right-click on the database and select "Query Tool")
   - Run these commands:
     ```sql
     ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tms_user;
     ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO tms_user;
     ```

7. **Additional pgAdmin 4 Configuration**
   - In pgAdmin 4, ensure the server is running by checking the server status
   - If the server isn't running, right-click on the PostgreSQL server in the browser tree and select "Connect Server"
   - If you encounter connection errors, check that the PostgreSQL service is running in Windows Services
   - To configure automatic startup, go to Windows Services, find postgresql-x64-[version], right-click and select "Properties", then set "Startup type" to "Automatic"

8. **Update your `.env` file**
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB_NAME=tournament_management
   POSTGRES_USERNAME=tms_user  # or postgres
   POSTGRES_PASSWORD=your_password
   ```

### PostgreSQL Setup on Fedora/Linux

1. **Install PostgreSQL**
   ```bash
   # On Fedora
   sudo dnf install postgresql postgresql-server postgresql-contrib
   
   # Initialize the database
   sudo postgresql-setup --initdb
   
   # Start and enable the PostgreSQL service
   sudo systemctl enable postgresql
   sudo systemctl start postgresql
   ```

2. **Set up the PostgreSQL user**
   ```bash
   # Switch to the postgres user
   sudo -i -u postgres
   
   # Create a password for postgres user
   psql -c "ALTER USER postgres WITH PASSWORD 'your_password';"
   
   # Exit postgres user shell
   exit
   ```

3. **Configure PostgreSQL to accept password authentication**
   ```bash
   # Edit the pg_hba.conf file
   sudo nano /var/lib/pgsql/data/pg_hba.conf
   ```
   
   Find the lines that look like:
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            ident
   # IPv6 local connections:
   host    all             all             ::1/128                 ident
   ```
   
   Change `ident` to `md5`:
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            md5
   # IPv6 local connections:
   host    all             all             ::1/128                 md5
   ```
   
   Save and close the file.

4. **Restart PostgreSQL to apply changes**
   ```bash
   sudo systemctl restart postgresql
   ```

5. **Create the database and user**
   ```bash
   # Switch to postgres user
   sudo -i -u postgres
   
   # Create the database
   createdb tournament_management
   
   # Create a user for the application
   psql -c "CREATE USER tms_user WITH PASSWORD 'your_password';"
   
   # Grant privileges
   psql -c "GRANT ALL PRIVILEGES ON DATABASE tournament_management TO tms_user;"
   
   # Connect to the database to set schema privileges
   psql -d tournament_management -c "ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO tms_user;"
   psql -d tournament_management -c "ALTER DEFAULT PRIVILEGES GRANT ALL ON SEQUENCES TO tms_user;"
   
   # Exit postgres user shell
   exit
   ```

6. **Update your `.env` file**
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB_NAME=tournament_management
   POSTGRES_USERNAME=tms_user
   POSTGRES_PASSWORD=your_password
   ```

7. **Additional Linux Configuration**
   - Check PostgreSQL log for any errors:
     ```bash
     sudo journalctl -u postgresql
     ```
   - Configure PostgreSQL to listen on all interfaces if needed:
     ```bash
     sudo nano /var/lib/pgsql/data/postgresql.conf
     ```
     Change the `listen_addresses` line to:
     ```
     listen_addresses = '*'
     ```
   - Ensure the firewall allows PostgreSQL traffic:
     ```bash
     sudo firewall-cmd --permanent --add-service=postgresql
     sudo firewall-cmd --reload
     ```

### MongoDB Setup on Windows

1. **Download MongoDB Community Server**
   - Visit the [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Select "Windows" as the platform
   - Choose the latest version with the "msi" package
   - Click "Download"

2. **Run the installer**
   - Launch the downloaded MSI file
   - Follow the installation wizard
   - Choose "Complete" installation
   - Check "Install MongoDB as a Service"
   - Choose "Run service as Network Service user"
   - Keep the default data directory (`C:\Program Files\MongoDB\Server\X.X\data`)
   - Complete the installation

3. **Verify installation**
   - Open a Command Prompt
   - Type `mongosh` and press Enter
   - You should see the MongoDB shell starting and connecting to localhost

4. **Create the database and user**
   ```
   # In the MongoDB shell
   use tournament_management
   
   db.createUser({
     user: "tms_user",
     pwd: "your_password",
     roles: [{ role: "readWrite", db: "tournament_management" }]
   })
   
   # Create a test collection to ensure the database is created
   db.test.insertOne({ test: "data" })
   
   # Verify the user was created
   db.auth("tms_user", "your_password")
   
   # Exit the shell
   exit
   ```

5. **Enable authentication (optional but recommended)**
   - Create or edit the MongoDB configuration file:
     - Navigate to `C:\Program Files\MongoDB\Server\X.X\bin`
     - Create a file named `mongod.cfg` (if it doesn't exist)
     - Add the following content:
       ```yaml
       security:
         authorization: enabled
       ```
   - Restart the MongoDB service:
     - Open Services (services.msc)
     - Find MongoDB service, right-click and select "Restart"

6. **Update your `.env` file**
   ```
   DB_TYPE=mongodb
   MONGO_HOST=localhost
   MONGO_PORT=27017
   MONGO_DB_NAME=tournament_management
   MONGO_USERNAME=tms_user
   MONGO_PASSWORD=your_password
   ```

### MongoDB Setup on Fedora/Linux

1. **Install MongoDB**
   ```bash
   # Create a repo file for MongoDB
   sudo nano /etc/yum.repos.d/mongodb-org.repo
   ```
   
   Add the following content:
   ```
   [mongodb-org-6.0]
   name=MongoDB Repository
   baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/6.0/x86_64/
   gpgcheck=1
   enabled=1
   gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
   ```
   
   Save and close the file.

2. **Install MongoDB packages**
   ```bash
   sudo dnf install -y mongodb-org
   ```

3. **Start and enable MongoDB service**
   ```bash
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

4. **Verify installation**
   ```bash
   mongosh
   ```

5. **Create the database and user**
   ```
   # In the MongoDB shell
   use tournament_management
   
   db.createUser({
     user: "tms_user",
     pwd: "your_password",
     roles: [{ role: "readWrite", db: "tournament_management" }]
   })
   
   # Create a test collection
   db.test.insertOne({ test: "data" })
   
   # Verify the user
   db.auth("tms_user", "your_password")
   
   # Exit the shell
   exit
   ```

6. **Enable authentication**
   ```bash
   sudo nano /etc/mongod.conf
   ```
   
   Add or modify the security section:
   ```yaml
   security:
     authorization: enabled
   ```
   
   Save and close the file.

7. **Restart MongoDB**
   ```bash
   sudo systemctl restart mongod
   ```

8. **Configure firewall (if needed)**
   ```bash
   sudo firewall-cmd --permanent --add-port=27017/tcp
   sudo firewall-cmd --reload
   ```

9. **Update your `.env` file**
   ```
   DB_TYPE=mongodb
   MONGO_HOST=localhost
   MONGO_PORT=27017
   MONGO_DB_NAME=tournament_management
   MONGO_USERNAME=tms_user
   MONGO_PASSWORD=your_password
   ```

### MongoDB Atlas Setup

If you prefer a cloud-hosted MongoDB solution:

1. **Create a MongoDB Atlas account**
   - Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
   - Sign up for a free account

2. **Create a new cluster**
   - Choose the "Free" tier (M0)
   - Select your preferred cloud provider and region
   - Click "Create Cluster" (this may take a few minutes)

3. **Set up database access**
   - In the left navigation menu, go to "Database Access"
   - Click "Add New Database User"
   - Choose "Password" authentication method
   - Enter a username and password
   - Set privileges to "Read and write to any database"
   - Click "Add User"

4. **Configure network access**
   - In the left navigation menu, go to "Network Access"
   - Click "Add IP Address"
   - To allow access from anywhere (not recommended for production), select "Allow Access from Anywhere"
   - For better security, add your specific IP address
   - Click "Confirm"

5. **Get your connection string**
   - Return to the "Database" section
   - Click "Connect" on your cluster
   - Select "Connect your application"
   - Copy the provided connection string

6. **Update your `.env` file**
   ```
   DB_TYPE=mongodb
   MONGO_URI=mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/tournament_management?retryWrites=true&w=majority
   ```

   Replace `your_username`, `your_password`, and the rest of the URI with your actual connection string.

## Starting the Database

Before running the application, you need to ensure your database service is running.

### Starting PostgreSQL

#### Windows
1. **Using Services Manager**
   - Press `Win + R`, type `services.msc` and press Enter
   - Find "postgresql-x64-[version]" or similar in the list
   - Right-click on it and select "Start"

2. **Using Command Prompt (alternative)**
   ```cmd
   net start postgresql-x64-[version]
   ```
   Replace `[version]` with your installed PostgreSQL version

3. **Using pgAdmin 4**
   - Open pgAdmin 4
   - If the server appears with a red "X", right-click on it and select "Connect Server"
   - Enter your master password when prompted

#### Fedora/Linux
```bash
# Start the service
sudo systemctl start postgresql

# Check status to verify it's running
sudo systemctl status postgresql
```

### Starting MongoDB

#### Windows
1. **Using Services Manager**
   - Press `Win + R`, type `services.msc` and press Enter
   - Find "MongoDB Server" in the list
   - Right-click and select "Start"

2. **Using Command Prompt (alternative)**
   ```cmd
   net start MongoDB
   ```

#### Fedora/Linux
```bash
# Start the service
sudo systemctl start mongod

# Check status to verify it's running
sudo systemctl status mongod
```

### Verifying Database Connection

After starting your database service, verify you can connect:

#### PostgreSQL
```bash
# Windows
psql -U tms_user -d tournament_management -h localhost

# Linux
psql -U tms_user -d tournament_management -h localhost

# Enter your password when prompted
# You should see a prompt like: tournament_management=>
```

#### MongoDB
```bash
# Windows or Linux
mongosh "mongodb://localhost:27017/tournament_management" --username tms_user --password your_password

# You should see a prompt like: tournament_management>
```

## Setup Instructions

### Backend Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd tournament-management-system
```

2. **Create a Python virtual environment**

```bash
cd backend
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On Fedora/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the `backend/` directory based on the appropriate database configuration from the previous sections:

```
# Database configuration (choose MongoDB or PostgreSQL)
DB_TYPE=postgresql

# PostgreSQL configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB_NAME=tournament_management
POSTGRES_USERNAME=tms_user
POSTGRES_PASSWORD=your_password

# Flask configuration
SECRET_KEY=your_secret_key
FLASK_APP=app.py
FLASK_ENV=development
```

5. **Initialize the database**

```bash
# Make sure your database is running
python scripts/init_db.py

# Create tables
python scripts/create_tables.py

# Add remaining columns to Table
python scripts/add_structure_column.py
python scripts/add_structure_config_column.py
```

### Frontend Setup

1. **Navigate to the frontend directory**

```bash
cd frontend
```

2. **Install dependencies**

```bash
npm install
```

3. **Configure environment variables**

Create a `.env` file in the `frontend/` directory:

```
REACT_APP_API_URL=http://localhost:5000/api
```

## Running the Application

1. **Start your database** (See "Starting the Database" section)

2. **Start the backend server**

```bash
# In the backend directory with the virtual environment activated
python app.py
```

The API server will start at http://localhost:5000

3. **Start the frontend application**

```bash
# In the frontend directory
npm start
```

The frontend application will be available at http://localhost:3000

## API Documentation

The API provides the following endpoints:

- `/api/tournaments`: Tournament management
- `/api/players`: Player management
- `/api/decks`: Deck management
- `/api/matches`: Match management
- `/api/cards`: Card database access

For detailed API documentation, check the route files in the `backend/app/routes` directory.

## Troubleshooting

### Database Connection Issues

#### PostgreSQL

1. **Connection refused errors**
   - Check if PostgreSQL service is running
   - Verify the port (default: 5432) is not blocked by firewall
   - Ensure your pg_hba.conf file allows password authentication

2. **Authentication failures**
   - Double-check username and password in `.env` file
   - Verify the user has appropriate privileges
   - In pgAdmin, check if the user exists and has the correct permissions
   - Ensure you're using the correct authentication method (md5 or scram-sha-256)

3. **Database doesn't exist**
   - Create the database manually:
     ```bash
     sudo -u postgres createdb tournament_management
     ```
   - In pgAdmin, right-click on Databases and select "Create" > "Database..."

4. **pgAdmin issues**
   - If pgAdmin shows "server not found", ensure PostgreSQL service is running
   - If pgAdmin asks for a master password repeatedly, reset it by deleting the pgAdmin data directory (usually in `%APPDATA%\pgAdmin` on Windows)
   - If server connection fails, check the server properties and ensure the host, port, and credentials are correct

#### MongoDB

1. **Connection issues**
   - Ensure MongoDB service is running
   - Check MongoDB logs:
     ```bash
     # Linux
     sudo cat /var/log/mongodb/mongod.log
     # Windows
     type "C:\Program Files\MongoDB\Server\X.X\log\mongod.log"
     ```

2. **Authentication failures**
   - Verify the authentication database is correct
   - Check user credentials in your connection string
   - Ensure authentication is enabled in mongod.conf
   - Try connecting with the mongo shell to isolate authentication issues

### Backend Issues

1. **Missing dependencies**
   - Ensure all packages are installed: `pip install -r requirements.txt`
   - Check if virtual environment is activated

2. **Environment configuration**
   - Verify `.env` file exists and has correct database settings
   - Check Flask settings and secret key
   - Ensure the correct database type is selected in `.env`

3. **Database initialization errors**
   - Check database connection first
   - Look for error messages in console output
   - Try running init_db.py with --verbose flag (if available)
   - Check database permissions

### Frontend Issues

1. **Node.js errors**
   - Verify Node.js version (use v18+)
   - Try clearing npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

2. **API connection issues**
   - Check if backend server is running
   - Verify API URL in `.env` file
   - Check browser console for CORS errors
   - Ensure your backend is configured to allow CORS requests

3. **Build errors**
   - Update Node.js to the latest LTS version
   - Check for TypeScript errors in the console
   - Try using an older version of Node.js if necessary
   - Check for conflicting dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.