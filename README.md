 # <img src="https://slackmojis.com/emojis/123839-he_is_brighter/download" width="50"> IoT Energy Consumption Analysis 

> End-to-end IoT data engineering solution for real-time energy monitoring and analytics

## 🟢 Table of Contents

[Overview](#overview)  
[System Architecture](#system-architecture)  
[Features](#features)  
[Database Design](#database-design)  
[Dashboard](#dashboard)  
[Installation](#installation)  
[Usage](#usage)  

## Overview

This project implements a production-grade IoT data pipeline that processes and visualizes energy consumption data from residential environments. The system integrates the Appliances Energy Prediction dataset (19,735 records spanning 4.5 months) with a real-time ingestion architecture and interactive dashboard.

### Key Highlights

▸ **Real-time data processing** with MQTT publish-subscribe pattern  
▸ **Normalized database schema** following Third Normal Form (3NF)  
▸ **Interactive dashboard** with auto-refresh capabilities  
▸ **Zero message loss** during 48-hour continuous testing  
▸ **2.2-second end-to-end latency** from ingestion to visualization

## System Architecture

The system implements a decoupled, event-driven architecture with five main components:

```
CSV Dataset → MQTT Publisher → CloudAMQP Broker → MQTT Subscriber → PostgreSQL Database
                                                                              ↓
                                                                    Streamlit Dashboard
```

### Component Details

#### 1. MQTT Publisher
▸ Reads CSV dataset using Pandas  
▸ Serializes data to JSON with ISO 8601 timestamps  
▸ Publishes to topic-based channels via MQTTS  

#### 2. CloudAMQP Broker
▸ Managed MQTT broker with MQTTS encryption  
▸ QoS Level 1 (at-least-once delivery)  
▸ 99.9% uptime with automatic failover  
▸ Message queuing prevents data loss during disconnections  

#### 3. MQTT Subscriber
▸ Receives and parses JSON messages  
▸ Executes atomic transactions to PostgreSQL  
▸ Automatic rollback on error  

#### 4. PostgreSQL Database
▸ Three normalized tables with foreign key relationships  
▸ ACID transactions ensure data integrity  
▸ Indexed queries for optimal performance  

#### 5. Streamlit Dashboard
▸ Real-time visualization with 2-second polling  
▸ SQL JOIN queries for unified data views  
▸ Interactive charts and analytics  

## Features

### Data Processing
▸ Handles 19,735 sensor readings from residential monitoring  
▸ Synchronizes heterogeneous data sources (ZigBee sensors + Weather API)  
▸ 10-minute sampling intervals  
▸ JSON serialization for MQTT transmission  

### Visualization Components
▸ **KPI Metrics** - Real-time system status indicators  
▸ **Consumption Distribution** - Histogram analysis  
▸ **Time-Series Charts** - Temporal pattern identification  
▸ **Correlation Heatmap** - Multivariate relationship analysis  
▸ **Temperature Comparison** - Indoor vs outdoor thermal analysis  
▸ **Humidity Variability** - Sensor health monitoring  
▸ **Scatter Plots** - Non-linear relationship exploration  
▸ **Raw Data Table** - Debugging and validation  

### Analytics Capabilities
▸ Baseload consumption detection (50-60 Wh)  
▸ Peak demand forecasting (evening patterns 18:00-22:00)  
▸ HVAC efficiency analysis via thermal lag  
▸ Sensor drift detection for predictive maintenance  

## Database Design

### Schema Structure

The database implements a normalized relational schema with three tables:

#### Table 1: consumo_energia
```sql
▸ date (TIMESTAMPTZ) - Primary Key
▸ appliances (INTEGER) - Energy consumption (10-1080 Wh)
▸ lights (INTEGER) - Lighting consumption (0-70 Wh)
```

#### Table 2: ambiente_interno
```sql
▸ date (TIMESTAMPTZ) - Primary Key, Foreign Key
▸ T1-T9 (FLOAT) - Temperature sensors across 9 zones
▸ RH_1-RH_9 (FLOAT) - Relative humidity sensors (0-100%)
```

#### Table 3: clima_externo
```sql
▸ date (TIMESTAMPTZ) - Primary Key, Foreign Key
▸ T_out (FLOAT) - Outdoor temperature (-6.1 to 28.3°C)
▸ RH_out (FLOAT) - Outdoor humidity
▸ Pressure (FLOAT) - Atmospheric pressure
▸ Windspeed (FLOAT) - Wind speed (0-14 km/h)
▸ Visibility, Tdewpoint (FLOAT) - Additional weather metrics
```

### Relationships
▸ One-to-one relationships via timestamp foreign keys  
▸ CASCADE deletion maintains referential integrity  
▸ Indexed date columns for optimized queries  

### Design Benefits
▸ 90% reduction in I/O for single-table queries  
▸ ~350KB storage optimization (significant at city scale)  
▸ Easy extensibility for new sensor types  

## Dashboard

### Interface Organization

<img width="1317" height="754" alt="image" src="https://github.com/user-attachments/assets/e77ed173-bb17-4305-b1f4-12d8595fe249" />

The dashboard follows a hierarchical information architecture:

**Zone 1: KPI Cards**
▸ Total record count  
▸ Average consumption  
▸ Current indoor temperature (T1)  
▸ Current humidity (RH_1)  

**Zone 2: Distribution Analysis**
▸ Consumption histogram with automatic binning  
▸ Identifies baseload and outliers  

**Zone 3: Temporal Patterns**
▸ Consumption over time (100-record window ≈ 16.6 hours)  
▸ Diurnal cycle visualization  

**Zone 4: Environmental Correlation**
▸ Internal vs external temperature comparison  
▸ Correlation heatmap (Pearson coefficients)  
▸ Humidity variability box plots  

**Zone 5: Detailed Analysis**
▸ Temperature vs consumption scatter plot  
▸ Raw data table (collapsible)  

### UX Features
▸ Auto-refresh with countdown indicator  
▸ Dark mode aesthetic for reduced eye strain  
▸ High-contrast color scheme (#00d4ff accents)  
▸ Collapsible sections for advanced features  

## Installation

### Prerequisites
▸ Python 3.8+  
▸ PostgreSQL 12+  
▸ CloudAMQP account (or local Mosquitto broker)  

### Dependencies

```bash
pip install pandas
pip install paho-mqtt
pip install psycopg2-binary
pip install streamlit
pip install plotly
pip install numpy
```

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/karencardiel/iot_energy_pipeline
cd iot_energy_pipeline
```

2. Configure database credentials:
```bash
# Create .env file
DB_HOST=localhost
DB_NAME=iot_energy
DB_USER=your_user
DB_PASSWORD=your_password
```

3. Configure MQTT broker:
```bash
MQTT_BROKER=your-cloudamqp-instance.rmq.cloudamqp.com
MQTT_PORT=8883
MQTT_USER=your_user
MQTT_PASSWORD=your_password
```

4. Initialize database:
```bash
psql -U your_user -d iot_energy -f schema.sql
```

## Usage

### Running the Pipeline

**Step 1: Start the MQTT Subscriber**
```bash
python subscriber.py
```

**Step 2: Launch the Publisher**
```bash
python publisher.py --dataset data/appliances_energy.csv
```

**Step 3: Start the Dashboard**
```bash
streamlit run dashboard.py
```
